#!/usr/bin/env python3
import json, sys, argparse
from pathlib import Path
from .scanner import scan_directory

def main():
    parser = argparse.ArgumentParser(description="Web3 Security Scout – severity-aware scanner")
    parser.add_argument("path", help="Directory or Solidity file to scan")
    parser.add_argument("--json", action="store_true", help="Output full JSON report")
    args = parser.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"Error: path does not exist: {target}")
        sys.exit(1)

    if target.is_file() and target.suffix == ".sol":
        # Single file
        from .scanner import scan_file
        findings = scan_file(target)
        summary = {
            "total_findings": len(findings),
            "findings": findings,
        }
    else:
        summary = scan_directory(str(target))

    if args.json:
        json.dump(summary, sys.stdout, indent=2)
    else:
        print(f"\n=== Web3 Security Scout Report ===")
        print(f"Target: {target}")
        print(f"Total findings: {summary['total_findings']}")
        print(f"Aggregate severity: {summary.get('aggregate_severity')} ({summary.get('severity_label')})")
        if "by_type" in summary:
            print("\nBy type:")
            for t, c in summary["by_type"].items():
                print(f"  {t}: {c}")
        print("\nTop findings (first 10):")
        for f in summary["findings"][:10]:
            print(f"- {f['file']}:{f['line']} {f['type']} | {f['snippet']}")
        if summary["total_findings"] > 10:
            print(f"... and {summary['total_findings']-10} more")
    return 0

if __name__ == "__main__":
    sys.exit(main())