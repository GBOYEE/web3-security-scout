import argparse
import sys
from pathlib import Path
from .core import scan_directory
import json

def main():
    parser = argparse.ArgumentParser(description="Web3 Security Scout")
    parser.add_argument("directory", type=str, help="Directory containing smart contracts")
    parser.add_argument("--blockchain", choices=["ethereum", "solana"], default="ethereum", help="Blockchain type")
    parser.add_argument("--output", type=str, help="Output file (JSON)")
    parser.add_argument("--format", choices=["json", "html"], default="json", help="Report format")
    args = parser.parse_args()

    root = Path(args.directory)
    if not root.exists():
        print(f"Error: {root} does not exist")
        sys.exit(1)

    result = scan_directory(root, args.blockchain)

    high_sevs = sum(1 for f in result["findings"] if f["severity"] in ("critical", "high"))
    exit_code = 1 if high_sevs > 0 else 0

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output)

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
