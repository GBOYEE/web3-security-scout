import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scanner.core import scan_directory

def test_scan_solidity_reentrancy_heuristic(tmp_path):
    sol = tmp_path / "Vulnerable.sol"
    sol.write_text("""
contract Vulnerable {
    uint public balance;
    function withdraw() public {
        msg.sender.call{value: balance}("");
        balance = 0;
    }
}
""")
    result = scan_directory(tmp_path, "ethereum")
    assert any(f["type"] == "potential_reentrancy" for f in result["findings"])

def test_scan_solana_arithmetic(tmp_path):
    rs = tmp_path / "lib.rs"
    rs.write_text("""
pub fn add(a: u64, b: u64) -> u64 {
    a + b  // no overflow check
}
""")
    result = scan_directory(tmp_path, "solana")
    assert any(f["type"] == "unchecked_arithmetic" for f in result["findings"])

def test_scan_empty_dir(tmp_path):
    result = scan_directory(tmp_path, "ethereum")
    assert result["total_findings"] == 0
