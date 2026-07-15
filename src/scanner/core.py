import json
from pathlib import Path
from typing import List, Dict, Any

def scan_solidity_file(path: Path) -> List[Dict[str, Any]]:
    findings = []
    try:
        code = path.read_text(errors='ignore')
    except Exception:
        return []
    lines = code.splitlines()
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
        if in_function:
            if '.call{' in stripped or 'call(' in stripped or 'delegatecall' in stripped:
                has_call = True
            if '= ' in stripped and not stripped.startswith('//'):
                has_state_write = True
            # count braces to detect function close (ignores } inside call{...})
            depth = stripped.count('{') - stripped.count('}')
            if '}' in stripped and depth < 0:
                # more } than { on this line -> function block closed
                if has_call and has_state_write:
                    findings.append({
                        "type": "potential_reentrancy",
                        "severity": "high",
                        "file": str(path),
                        "line": function_start + 1,
                        "message": "Low-level call followed by state modification; possible reentrancy.",
                        "remediation": "Use checks-effects-interactions pattern or reentrancy guard."
                    })
                in_function = False
                has_call = False
                has_state_write = False
                continue
    # Solidity access-control: public/external function that writes state
    # but lacks an owner/role check (require(msg.sender ...) / onlyRole / modifier)
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('function ') or \
           ('function ' in stripped and ('public' in stripped or 'external' in stripped)):
            fn_sig = stripped
            if any(m in fn_sig for m in ('onlyOwner', 'onlyRole', 'onlyAdmin', 'nonReentrant')):
                continue
            # look at the function body (next ~40 lines) for an access check
            body = "\n".join(lines[i:i + 40])
            has_check = any(
                t in body for t in ('require(msg.sender', 'require(_msgSender',
                                     'if (msg.sender', 'if(_msgSender', 'onlyOwner',
                                     'onlyRole', 'onlyAdmin', 'AccessControl')
            )
            writes_state = any(
                (t in body and '=' in body) for t in
                ('balances[', 'balance[', 'totalSupply', 'allowance[', 'owners[',
                 'stored', '_balances', 'mapping')
            )
            if writes_state and not has_check and ('public' in fn_sig or 'external' in fn_sig):
                findings.append({
                    "type": "missing_access_control",
                    "severity": "medium",
                    "file": str(path),
                    "line": i + 1,
                    "message": "State-changing public/external function lacks an access-control check.",
                    "remediation": "Add an `onlyOwner`/access-control modifier or require(msg.sender == owner)."
                })
    # Solidity front-running / phishing: tx.origin usage for authorization
    for i, line in enumerate(lines):
        stripped = line.strip()
        if 'tx.origin' in stripped:
            findings.append({
                "type": "tx_origin_usage",
                "severity": "medium",
                "file": str(path),
                "line": i + 1,
                "message": "Use of tx.origin for authorization (phishable, order-dependent).",
                "remediation": "Use msg.sender instead of tx.origin for access control."
            })
    # Unchecked low-level calls
    for i, line in enumerate(lines):
        if ('call(' in line or 'delegatecall' in line) and 'require(' not in line and 'if(' not in line:
            findings.append({
                "type": "unchecked_call",
                "severity": "medium",
                "file": str(path),
                "line": i + 1,
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
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('//'):
            continue
        if ' + ' in stripped or ' - ' in stripped or ' * ' in stripped:
            if 'checked_' not in stripped and 'overflowing_' not in stripped:
                findings.append({
                    "type": "unchecked_arithmetic",
                    "severity": "medium",
                    "file": str(path),
                    "line": i + 1,
                    "message": "Arithmetic operation without explicit overflow check.",
                    "remediation": "Use checked arithmetic (e.g., `checked_add` or `overflowing_add` with handling)."
                })
    for i, line in enumerate(lines):
        if 'pub fn ' in line and 'assert!' not in line and 'require!' not in line:
            findings.append({
                "type": "missing_access_control",
                "severity": "low",
                "file": str(path),
                "line": i + 1,
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

def generate_report(result: Dict[str, Any], fmt: str = 'json') -> str:
    """Render a scan result as JSON or HTML.

    HTML output is self-contained so it can be opened directly in a browser
    or attached to a CI artifact.
    """
    if fmt == 'html':
        findings = result.get('findings', [])
        rows = []
        for f in findings:
            rows.append(
                "<tr>"
                f"<td>{f.get('type', '')}</td>"
                f"<td>{f.get('severity', '')}</td>"
                f"<td>{f.get('file', '')}:{f.get('line', '')}</td>"
                f"<td>{f.get('message', '')}</td>"
                f"<td>{f.get('remediation', '')}</td>"
                "</tr>"
            )
        return (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>Web3 Security Scout Report</title>"
            "<style>body{font-family:sans-serif}table{border-collapse:collapse;width:100%}"
            "th,td{border:1px solid #ccc;padding:6px;text-align:left}"
            "th{background:#1a1a1a;color:#fff}</style></head><body>"
            f"<h1>Web3 Security Scout Report</h1>"
            f"<p>Blockchain: {result.get('blockchain','')} | "
            f"Total findings: {result.get('total_findings', 0)}</p>"
            "<table><tr><th>Type</th><th>Severity</th><th>Location</th>"
            "<th>Message</th><th>Remediation</th></tr>"
            + "".join(rows) + "</table></body></html>"
        )
    return json.dumps(result, indent=2, ensure_ascii=False)

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
            bc = sys.argv[idx + 1]
    result = scan_directory(root, bc)
    print(json.dumps(result, indent=2, ensure_ascii=False))
