import pytest
from pathlib import Path
from web3_security_scout.scanner import scan_file, scan_directory

SAMPLE_CONTRACT = """
pragma solidity ^0.8.0;
contract Reentrancy {
    uint256 public balance;
    function withdraw() external {
        uint256 amt = balance;
        (bool success, ) = msg.sender.call{value: amt}("");
        require(success);
        balance = 0;
    }
}
"""

def test_scan_file_detects_reentrancy(tmp_path):
    f = tmp_path / "Reentrancy.sol"
    f.write_text(SAMPLE_CONTRACT)
    findings = scan_file(f)
    types = [v['type'] for v in findings]
    assert 'reentrancy' in types

def test_scan_directory_empty(tmp_path):
    sub = tmp_path / "empty"
    sub.mkdir()
    summary = scan_directory(str(sub))
    assert summary['total_findings'] == 0

def test_scan_directory_aggregate_score():
    # We'll test severity module separately
    from web3_security_scout.severity import aggregate_score, severity_label
    dummy = [{'type':'reentrancy'}, {'type':'integer_overflow'}]
    score = aggregate_score(dummy)
    assert score >= 0
    label = severity_label(score)
    assert label in ("Low","Medium","High","Critical")