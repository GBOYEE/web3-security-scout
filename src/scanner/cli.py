import argparse
import sys
from pathlib import Path
from typing import Optional
from .core import scan_directory, generate_report


def run_scan(directory: str, blockchain: str, fmt: str = 'json', output: Optional[str] = None):
    """Run a scan and return (report_text, exit_code). Pure/testable."""
    root = Path(directory)
    if not root.exists():
        return f"Error: {root} does not exist", 1

    result = scan_directory(root, blockchain)
    report = generate_report(result, fmt)

    high_sevs = sum(
        1 for f in result["findings"] if f["severity"] in ("critical", "high")
    )
    exit_code = 1 if high_sevs > 0 else 0

    if output:
        Path(output).write_text(report)
    else:
        print(report)

    return report, exit_code


def main():
    parser = argparse.ArgumentParser(description="Web3 Security Scout")
    parser.add_argument("directory", type=str, help="Directory containing smart contracts")
    parser.add_argument("--blockchain", choices=["ethereum", "solana"], default="ethereum",
                        help="Blockchain type")
    parser.add_argument("--output", type=str, help="Output file (JSON or HTML)")
    parser.add_argument("--format", choices=["json", "html"], default="json",
                        help="Report format")
    args = parser.parse_args()

    _, exit_code = run_scan(args.directory, args.blockchain, args.format, args.output)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
