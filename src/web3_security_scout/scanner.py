import re
from pathlib import Path
from typing import List, Dict
from .severity import classify, aggregate_score, severity_label

# Simple regex patterns for demo purposes. Production should use Slither or similar.
PATTERNS = {
    # Detect low-level call forwarding value: both .call{value: ...} and call(value: ...)
    "reentrancy": r"\bcall\s*(?:{|\()\s*value\s*:\s*[^,)]+\s*(?:}|\))",
    "unchecked_low_level_call": r"\b(?:call\|delegatecall\|staticcall)\s*\([^)]*\)\s*(?!\s*returns?\([^)]*\bboolean\b)",
    "integer_overflow": r"\b(\w+)\s*\+\=?\s*(\w+)\s*;",
    "timestamp_dependency": r"\bblock\.timestamp\b",
    "assembly_usage": r"\bassembly\s*\{",
    "event_missing": r"function\s+\w+\s*\([^)]*\)\s*(?:public|external)\s*(?!.*emit\s+\w+)",
    "solidity_version_old": r"pragma solidity\s+([<>=!]+\s*)?0\.\d\.",
}

def scan_file(path: Path) -> List[Dict]:
    text = path.read_text(errors="ignore")
    vulns = []
    for vtype, pattern in PATTERNS.items():
        for m in re.finditer(pattern, text):
            line_no = text[:m.start()].count('\n') + 1
            snippet = text[m.start():m.end()].strip()
            vulns.append({"type": vtype, "file": str(path), "line": line_no, "snippet": snippet})
    return vulns

def scan_directory(dir_path: str) -> Dict:
    root = Path(dir_path)
    all_vulns = []
    for file in root.rglob("*.sol"):
        all_vulns.extend(scan_file(file))
    total = len(all_vulns)
    agg_score = aggregate_score(all_vulns)
    summary = {
        "total_findings": total,
        "aggregate_severity": agg_score,
        "severity_label": severity_label(agg_score),
        "by_type": {},
        "findings": all_vulns,
    }
    # Count by type
    for v in all_vulns:
        t = v["type"]
        summary["by_type"][t] = summary["by_type"].get(t, 0) + 1
    return summary