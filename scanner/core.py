import json
from pathlib import Path
from typing import List, Dict, Any

# Simple detectors for demo purposes
# Real version would wrap Slither/solhint; here we use heuristics

def scan_solidity_file(path: Path) -> List[Dict[str, Any]]:
    findings = []
    try:
        code = path.read_text(errors='ignore')
    except Exception:
        return []
    lines = code.splitlines()
    # Very naive reentrancy pattern: low-level call followed by state write
    in_function = False
    function_start = None
    has_call = False
    has_state_write = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('function '):
            in_function = True
            function_start = i
            has_call = False
            has_state_write = False
            continue
        if in_function and stripped == '}':
            in_function = False
            if has_call and has_state_write:
                findings.append({
                    "type": "potential_reentrancy",
                    "severity": "high",
                    "file": str(path),
                    "line": function_start + 1,
                    "message": "Low-level call followed by state modification; possible reentrancy.",
                    "remediation": "Use checks-effects-interactions pattern or reentrancy guard."
                })
            continue
        if in_function:
            if '.call{' in stripped or 'call(' in stripped or 'delegatecall' in stripped:
                has_call = True
            if '= ' in stripped and not stripped.startswith('//'):
                # naive state write
                has_state_write = True
    # Unchecked return value from low-level call
    for i, line in enumerate(lines):
        if ('call(' in line or 'delegatecall' in line) and 'require(' not in line and 'if(' not in line:
            findings.append({
                "type": "unchecked_call",
                "severity": "medium",
                "file": str(path),
                "line": i+1,
                "message": "Low-level call return value not checked.",
                "remediation": "Check the boolean return or use require/assert."
            })
    return findings

def scan_solana_file(path: Path) -> List[Dict[str, Any]]:
    findings = []
    try:
        code = path.read_text(errors='ignore')
    except Exception:
        return []
    lines = code.splitlines()
    # Check for arithmetic without overflow checks (very naive)
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('//'):
            continue
        if ' + ' in stripped or ' - ' in stripped or ' * ' in stripped:
            # Look for overflow checks like 'checked_add' or 'overflowing_add'
            if 'checked_' not in stripped and 'overflowing_' not in stripped:
                findings.append({
                    "type": "unchecked_arithmetic",
                    "severity": "medium",
                    "file": str(path),
                    "line": i+1,
                    "message": "Arithmetic operation without explicit overflow check.",
                    "remediation": "Use checked arithmetic (e.g., `checked_add` or `overflowing_add` with handling)."
                })
    # Access control: public function without any auth modifier
    for i, line in enumerate(lines):
        if 'pub fn ' in line and 'assert!' not in line and 'require!' not in line:
            findings.append({
                "type": "missing_access_control",
                "severity": "low",
                "file": str(path),
                "line": i+1,
                "message": "Public function may lack access control.",
                "remediation": "Add `assert!` or `require!` with condition (e.g., `msg.sender == owner`)."
            })
    return findings

def scan_directory(root: Path, blockchain: str = 'ethereum') -> Dict[str, Any]:
    findings = []
    if blockchain == 'ethereum':
        pattern = '**/*.sol'
    elif blockchain == 'solana':
        pattern = '**/*.rs'
    else:
        raise ValueError(f"Unsupported blockchain: {blockchain}")
    for file in root.glob(pattern):
        if blockchain == 'ethereum':
            findings.extend(scan_solidity_file(file))
        else:
            findings.extend(scan_solana_file(file))
    return {
        "scan_root": str(root),
        "blockchain": blockchain,
        "findings": findings,
        "total_findings": len(findings)
    }

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: scanner <directory> [--blockchain ethereum|solana]")
        sys.exit(1)
    root = Path(sys.argv[1])
    bc = 'ethereum'
    if '--blockchain' in sys.argv:
        idx = sys.argv.index('--blockchain')
        if idx + 1 < len(sys.argv):
            bc = sys.argv[idx+1]
    result = scan_directory(root, bc)
    print(json.dumps(result, indent=2, ensure_ascii=False))
