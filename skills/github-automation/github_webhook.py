#!/usr/bin/env python3
"""
GitHub Webhook Handler Skill for OpenClaw

This script receives GitHub webhook events, transforms them into xander-operator
tasks, and returns a natural language summary for chat channels.

Usage: Called by OpenClaw when /hooks/github receives an event.
"""

import os
import sys
import hmac
import hashlib
import json
import logging
from typing import Dict, Any, Optional

# Ensure xander-operator is importable by adding common paths
_known_xander_paths = [
    "/root/.openclaw/workspace/polish/xander-operator",
    "/root/.openclaw/workspace/.venv/lib/python3.12/site-packages",
]
for p in _known_xander_paths:
    if p not in sys.path:
        sys.path.insert(0, p)

# xander-operator integration
try:
    from xander_operator import add_task, TaskStore
    XANDER_AVAILABLE = True
except ImportError as e:
    XANDER_AVAILABLE = False
    logging.getLogger(__name__).error(f"xander-operator not available: {e}")

log = logging.getLogger(__name__)

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify X-Hub-Signature-256 header."""
    if not signature:
        return False
    expected = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

def handle_github_webhook(event: str, payload: Dict[str, Any]) -> str:
    """
    Route GitHub event to appropriate xander-operator task.
    Returns a human-readable message for OpenClaw to post.
    """
    if not XANDER_AVAILABLE:
        return "❌ xander-operator not available. Install and configure it first."

    repository = payload.get("repository", {}).get("full_name", "unknown/repo")

    # Initialize task store (uses default workspace memory dir)
    store = TaskStore()

    if event == "pull_request":
        action = payload.get("action")
        if action in ("opened", "synchronize", "reopened"):
            pr = payload["pull_request"]
            # Create a research task to review the PR
            desc = f"Review PR #{pr['number']} in {repository}: {pr['title']}"
            # Compose a prompt for LLM-based review
            diff_url = pr["_links"]["html"]["href"]
            task_desc = f"""
You are a senior code reviewer. Analyze this pull request:

Repository: {repository}
PR #{pr['number']}: {pr['title']}
Author: {pr['user']['login']}
Branch: {pr['head']['ref']} → {pr['base']['ref']}

Description:
{pr.get('body', '(no description)')}

Changed files: {len(pr.get('files', []))} files
Diff URL: {diff_url}

Please provide: summary, potential bugs/security issues, suggestions, test coverage gaps, and a final verdict (Approve/Request Changes/Comment).
""".strip()
            task_id = add_task(
                task_desc=desc,
                task_type="research",
                query=task_desc,
                max_results=3,
                follow_up_browse=True
            )
            return f"🤖 Started PR review for {repository}#{pr['number']}. Task ID: {task_id[:8]}"
        else:
            return f"⏭️ Ignoring PR action: {action}"

    elif event == "workflow_run":
        run = payload["workflow_run"]
        if run["conclusion"] in ("failure", "cancelled"):
            repo = repository
            wf_name = run["name"]
            wf_id = run["id"]
            branch = run["head_branch"]
            commit_msg = run["head_commit"]["message"]
            # Fetch logs? Could use gh api or playwright; for now just summarize
            desc = f"CI failure in {repo}: {wf_name} on {branch}"
            query = f"""
A GitHub Actions workflow failed.

Repository: {repo}
Workflow: {wf_name} (ID {wf_id})
Branch: {branch}
Commit: {commit_msg}

This indicates a problem in the CI pipeline. Based on typical CI failures for this repo, what are likely causes and next steps?
""".strip()
            task_id = add_task(
                task_desc=desc,
                task_type="research",
                query=query,
                max_results=3,
                follow_up_browse=False
            )
            return f"🚨 CI failure detected in {repo}. Investigating (task {task_id[:8]})"
        else:
            return f"✅ CI workflow {run['name']} completed with status: {run['conclusion']}"

    elif event == "issues":
        action = payload.get("action")
        if action in ("opened", "edited"):
            issue = payload["issue"]
            repo = repository
            labels = [l["name"] for l in issue.get("labels", [])]
            desc = f"New/updated issue in {repo}: {issue['title']}"
            query = f"""
You are a triage assistant. Categorize this GitHub issue.

Repository: {repo}
Issue #{issue['number']}: {issue['title']}
Reporter: {issue['user']['login']}
Current labels: {', '.join(labels) if labels else 'none'}

Body:
{issue.get('body', '(no body)')}

Determine:
- Type: bug / feature / question / documentation / security
- Severity: critical / high / medium / low
- Whether more information is needed (e.g., reproduction steps)
- Suggested labels from set: bug, enhancement, question, docs, security, priority:high, priority:low
- A short, helpful response to the reporter (if needed)
""".strip()
            task_id = add_task(
                task_desc=desc,
                task_type="research",
                query=query,
                max_results=2,
                follow_up_browse=False
            )
            return f"📋 Issue triage started for {repo}#{issue['number']} (task {task_id[:8]})"
        else:
            return f"⏭️ Ignoring issue action: {action}"

    elif event == "push":
        # Optional: trigger smoke tests if main branch and CI passed
        ref = payload.get("ref", "")
        if ref == "refs/heads/main":
            # Could create a browse task to check the live site
            repo = repository
            commit = payload["head_commit"]["message"][:50]
            return f"🚀 Push to main in {repo}: {commit}… (smoke test optional)"
        return f"⏭️ Push to {ref} ignored"

    elif event == "release":
        release = payload.get("release", {})
        repo = repository
        tag = release.get("tag_name")
        return f"🏷️ New release {repo}@{tag} published — consider deployment verification"

    else:
        return f"📡 Received unhandled GitHub event: {event}"

def process_webhook(body: bytes, signature: str, secret: str) -> str:
    """
    Entry point for OpenClaw webhook handler.
    Verifies signature, parses event, routes to handler.
    """
    if not verify_signature(body, signature, secret):
        return "❌ Invalid webhook signature..Request rejected."

    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as e:
        return f"❌ Invalid JSON: {e}"

    event = payload.get("action", "unknown")
    event_type = payload.get("hook", {}).get("events", ["unknown"])[0]

    # Prefer the event type from the top-level 'hook' or 'action' context
    # GitHub sends a dedicated event name via the 'X-GitHub-Event' header typically,
    # but this simplified version infers from payload shape.
    if "pull_request" in payload:
        event_type = "pull_request"
    elif "workflow_run" in payload:
        event_type = "workflow_run"
    elif "issue" in payload and "comment" not in payload:
        event_type = "issues"
    elif "commits" in payload:
        event_type = "push"
    elif "release" in payload:
        event_type = "release"

    try:
        response = handle_github_webhook(event_type, payload)
        return response
    except Exception as e:
        log.exception("Webhook handling failed")
        return f"❌ Error processing {event_type}: {str(e)}"

# This function will be called by OpenClaw if this skill is enabled as a webhook handler.
# Signature: webhook_handler(body: bytes, headers: dict) -> str
def webhook_handler(body: bytes, headers: dict) -> str:
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    signature = headers.get("X-Hub-Signature-256", "")
    return process_webhook(body, signature, secret)

if __name__ == "__main__":
    # Quick test
    test_token = os.getenv("GITHUB_WEBHOOK_SECRET", "testsecret")
    test_payload_dict = {
        "hook": {"events": ["pull_request"]},
        "action": "opened",
        "repository": {"full_name": "test/repo"},
        "pull_request": {
            "number": 1,
            "title": "Test PR",
            "user": {"login": "tester"},
            "head": {"ref": "feature"},
            "base": {"ref": "main"},
            "_links": {"html": {"href": "https://github.com/test/repo/pull/1"}},
        },
    }
    test_payload = json.dumps(test_payload_dict)
    sig = "sha256=" + hmac.new(test_token.encode(), test_payload.encode(), hashlib.sha256).hexdigest()
    print(process_webhook(test_payload.encode(), sig, test_token))
