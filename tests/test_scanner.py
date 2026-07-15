import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scanner.core import scan_directory, generate_report
from scanner.cli import run_scan


def test_scan_solidity_reentrancy_heuristic(tmp_path):
    sol = tmp_path / "Vulnerable.sol"
    sol.write_text(
        """
contract Vulnerable {
    uint public balance;
    function withdraw() public {
        msg.sender.call{value: balance}("");
        balance = 0;
    }
}
"""
    )
    result = scan_directory(tmp_path, "ethereum")
    assert any(f["type"] == "potential_reentrancy" for f in result["findings"])


def test_scan_solana_arithmetic(tmp_path):
    rs = tmp_path / "lib.rs"
    rs.write_text(
        """
pub fn add(a: u64, b: u64) -> u64 {
    a + b  // no overflow check
}
"""
    )
    result = scan_directory(tmp_path, "solana")
    assert any(f["type"] == "unchecked_arithmetic" for f in result["findings"])


def test_scan_empty_dir(tmp_path):
    result = scan_directory(tmp_path, "ethereum")
    assert result["total_findings"] == 0


def test_solidity_access_control_detected(tmp_path):
    sol = tmp_path / "Owner.sol"
    sol.write_text(
        """
contract Token {
    mapping(address => uint) balances;
    function mint(address to, uint amt) public {
        balances[to] = amt;
    }
}
"""
    )
    result = scan_directory(tmp_path, "ethereum")
    assert any(f["type"] == "missing_access_control" for f in result["findings"])


def test_solidity_access_control_ok_with_owner(tmp_path):
    sol = tmp_path / "Owner.sol"
    sol.write_text(
        """
contract Token {
    mapping(address => uint) balances;
    function mint(address to, uint amt) public onlyOwner {
        balances[to] = amt;
    }
}
"""
    )
    result = scan_directory(tmp_path, "ethereum")
    assert not any(
        f["type"] == "missing_access_control"
        and f["line"] == 5  # the mint function line
        for f in result["findings"]
    )


def test_solidity_tx_origin_detected(tmp_path):
    sol = tmp_path / "Auth.sol"
    sol.write_text(
        """
contract Auth {
    address owner;
    function isOwner() public view returns (bool) {
        return tx.origin == owner;
    }
}
"""
    )
    result = scan_directory(tmp_path, "ethereum")
    assert any(f["type"] == "tx_origin_usage" for f in result["findings"])


def test_generate_report_json():
    result = {"blockchain": "ethereum", "total_findings": 0, "findings": []}
    out = generate_report(result, "json")
    assert out.strip().startswith("{")


def test_generate_report_html():
    result = {
        "blockchain": "ethereum",
        "total_findings": 1,
        "findings": [
            {
                "type": "tx_origin_usage",
                "severity": "medium",
                "file": "Auth.sol",
                "line": 5,
                "message": "tx.origin used",
                "remediation": "use msg.sender",
            }
        ],
    }
    out = generate_report(result, "html")
    assert out.strip().startswith("<!doctype html>")
    assert "tx_origin_usage" in out


def test_cli_run_scan_json_prints_and_exit_code(tmp_path, capsys):
    sol = tmp_path / "V.sol"
    sol.write_text(
        """
contract V {
    uint balance;
    function w() public { msg.sender.call{value: balance}(""); balance = 0; }
}
"""
    )
    report, code = run_scan(str(tmp_path), "ethereum", fmt="json")
    assert code == 1  # high-severity finding -> non-zero exit
    assert "potential_reentrancy" in report


def test_cli_run_scan_html_output_file(tmp_path):
    sol = tmp_path / "V.sol"
    sol.write_text("contract V { uint b; function w() public { b = 1; } }")
    out_file = tmp_path / "report.html"
    _, code = run_scan(str(tmp_path), "ethereum", fmt="html", output=str(out_file))
    assert code == 0
    assert out_file.read_text().startswith("<!doctype html>")


def test_cli_run_scan_missing_dir(tmp_path, capsys):
    report, code = run_scan(str(tmp_path / "nope"), "ethereum")
    assert code == 1
    assert "does not exist" in report
