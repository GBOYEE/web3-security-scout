#!/usr/bin/env python3
"""
Xander Maintainer — AI PR Review CLI

Usage:
  xander-review-pr <PR_URL> [--output report.md] [--json]

Exit codes:
  0 = success
  1 = error

Environment:
  OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL (default: stepfun/step-1-flash)
"""

import os
import sys
import json
import argparse
import subprocess
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add xander-operator to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "polish" / "xander-operator"))

from xander_operator.llm import generate_response

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)
log = logging.getLogger("xander-maintainer")

def parse_pr_url(url: str) -> tuple[str, int]:
    """Extract owner/repo and PR number from GitHub URL."""
    parts = url.strip().split("/")
    if "pull" not in parts:
        raise ValueError("Invalid PR URL — missing /pull/NUMBER")
    idx = parts.index("pull")
    if idx < 2 or idx + 1 >= len(parts):
        raise ValueError("Malformed PR URL")
    owner = parts[idx-2]
    repo = parts[idx-1]
    try:
        number = int(parts[idx+1])
    except ValueError:
        raise ValueError("PR number must be integer")
    return f"{owner}/{repo}", number

def gh_run(cmd: list[str], retries: int = 3, delay: float = 2.0) -> str:
    """Run gh command with retries and timeout."""
    for attempt in range(1, retries + 1):
        try:
            log.debug(f"gh attempt {attempt}: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout
            else:
                err = result.stderr.strip() or "unknown error"
                log.warning(f"gh error: {err}")
                if attempt < retries:
                    time.sleep(delay)
                else:
                    raise RuntimeError(f"gh failed: {err}")
        except subprocess.TimeoutExpired:
            log.warning(f"gh timeout (attempt {attempt})")
            if attempt < retries:
                time.sleep(delay)
            else:
                raise RuntimeError("gh command timed out")
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            raise

def fetch_pr_data(owner_repo: str, pr_number: int) -> Dict[str, Any]:
    """Fetch PR metadata via gh."""
    cmd = [
        "gh", "pr", "view", str(pr_number),
        "--repo", owner_repo,
        "--json", "title,body,author,baseRefName,headRefName,files,state,createdAt,updatedAt,number",
        "--jq", "."
    ]
    output = gh_run(cmd)
    data = json.loads(output)
    return data

def fetch_pr_diff(owner_repo: str, pr_number: int) -> str:
    """Get unified diff."""
    cmd = ["gh", "pr", "diff", str(pr_number), "--repo", owner_repo]
    return gh_run(cmd)

def build_review_prompt(owner_repo: str, pr_data: Dict[str, Any], diff: str) -> str:
    title = pr_data["title"]
    body = pr_data.get("body", "(no description)")
    author = pr_data["author"]["login"]
    files_changed = len(pr_data.get("files", []))
    base = pr_data["baseRefName"]
    head = pr_data["headRefName"]
    pr_number = pr_data["number"]
    state = pr_data.get("state")
    created = pr_data.get("createdAt")

    return f"""You are a senior code reviewer. Analyze this pull request thoroughly.

## Context
Repository: {owner_repo}
PR #{pr_number}: {title}
Author: {author}
Branch: {head} → {base}
State: {state}
Created: {created}

## Description
{body}

## Changed Files
{files_changed} files changed.

## Diff
```diff
{diff}
```

## Task
Provide a structured review in **Markdown** with these sections:

1. **Summary** (2-3 sentences)
2. **Potential Bugs** (logic errors, race conditions, edge cases)
3. **Security Concerns** (injection, auth bypass, reentrancy, etc.)
4. **Suggestions** (improvements, better patterns, refactoring)
5. **Test Coverage Gaps** (are new features tested?)
6. **Final Verdict** (APPROVE / REQUEST CHANGES / COMMENT)

Be concise but specific. Reference file names and line numbers.

Output only Markdown. No extra commentary.""".strip()

def generate_ai_review(pr_data: Dict[str, Any], diff: str, owner_repo: str) -> str:
    prompt = build_review_prompt(owner_repo, pr_data, diff)
    model = os.getenv("OPENAI_MODEL", "stepfun/step-1-flash")
    log.info(f"Generating review using {model}")
    
    response = generate_response(
        prompt,
        model=model,
        max_tokens=2000,
        temperature=0.3,
        use_cache=True
    )
    if not response:
        raise RuntimeError("AI did not return a review")
    return response

def compose_report(pr_data: Dict[str, Any], ai_review: str, owner_repo: str) -> str:
    pr_number = pr_data["number"]
    title = pr_data["title"]
    author = pr_data["author"]["login"]
    base = pr_data["baseRefName"]
    head = pr_data["headRefName"]
    files_count = len(pr_data.get("files", []))
    model = os.getenv("OPENAI_MODEL", "stepfun/step-1-flash")

    return f"""# AI PR Review — Xander Maintainer

> PR #{pr_number}: {title}
> Repository: {owner_repo}
> Generated: {datetime.now():%Y-%m-%d %H:%M} (Europe/Berlin)

{ai_review}

---

**Metadata**
- Author: {author}
- Base: {base}
- Head: {head}
- Files changed: {files_count}
- State: {pr_data.get('state')}
- AI model: {model}
- Service: Xander Maintainer (beta)

---

*This review was generated autonomously. Human oversight recommended.*
"""

def main():
    parser = argparse.ArgumentParser(
        description="Generate an AI-powered PR review using Xander Maintainer"
    )
    parser.add_argument(
        "pr_url",
        help="GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Write report to file (Markdown). Default: stdout"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also output JSON metadata to stderr (for automation)"
    )
    args = parser.parse_args()

    try:
        owner_repo, pr_number = parse_pr_url(args.pr_url)
        log.info(f"Reviewing PR #{pr_number} in {owner_repo}")

        # Fetch data
        pr_data = fetch_pr_data(owner_repo, pr_number)
        diff = fetch_pr_diff(owner_repo, pr_number)

        # Generate
        ai_review = generate_ai_review(pr_data, diff, owner_repo)
        report = compose_report(pr_data, ai_review, owner_repo)

        # Output
        if args.output:
            Path(args.output).write_text(report, encoding="utf-8")
            log.info(f"Report written to {args.output}")
        else:
            print(report)

        # Optional JSON for automation
        if args.json:
            meta = {
                "pr": pr_number,
                "repo": owner_repo,
                "title": pr_data["title"],
                "author": pr_data["author"]["login"],
                "generated_at": datetime.now().isoformat(),
                "model": os.getenv("OPENAI_MODEL", "stepfun/step-1-flash")
            }
            print(json.dumps(meta), file=sys.stderr)

        log.info("Review complete")
        return 0

    except Exception as e:
        log.error(f"Failed: {e}")
        import traceback
        log.debug(traceback.format_exc())
        if args.json:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
