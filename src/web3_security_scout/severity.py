"""
Severity scoring for vulnerabilities.

We use a CVSS-inspired 0–10 scale:
0–3: Low
4–6: Medium
7–8: High
9–10: Critical

Mapping by vulnerability class (simplified). Extend as needed.
"""

SEVERITY_MAP = {
    # Critical
    "reentrancy": 9.5,
    "delegatecall_injection": 9.0,
    " uncontrolled_ether_withdrawal": 9.8,
    # High
    "integer_overflow": 7.5,
    "integer_underflow": 7.5,
    "unchecked_low_level_call": 7.0,
    "timestamp_dependency": 7.2,
    "front_runnable": 7.0,
    # Medium
    "assembly_usage": 5.0,  # benign if justified, but flag for review
    "solidity_version_old": 5.5,
    "gas_insufficient": 5.0,
    # Low
    "event_missing": 2.0,
    "naming_convention": 1.5,
}

def classify(vuln_type: str) -> float:
    """Return base severity score 0–10 for a given vulnerability type."""
    return SEVERITY_MAP.get(vuln_type, 3.0)  # default low

def aggregate_score(vulns):
    """
    Given a list of vulnerability dicts with at least a 'type' key,
    compute a weighted aggregate severity score.
    Simple max-based approach: highest single severity drives overall risk,
    but we also compute a weighted average to reflect cumulative risk.
    """
    if not vulns:
        return 0.0
    scores = [classify(v.get("type", "unknown")) for v in vulns]
    max_score = max(scores)
    avg_score = sum(scores) / len(scores)
    # Combine: give 70% weight to the worst, 30% to average
    return round(0.7 * max_score + 0.3 * avg_score, 1)

def severity_label(score: float) -> str:
    if score >= 9.0:
        return "Critical"
    if score >= 7.0:
        return "High"
    if score >= 4.0:
        return "Medium"
    return "Low"