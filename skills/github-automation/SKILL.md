# GitHub Automation Skill for OpenClaw

## Purpose

Automate GitHub workflows using xander-operator:
- Pull request reviews with AI analysis
- CI/CD monitoring and failure alerts
- Issue triage and labeling
- Deploy notifications

## Prerequisites

1. OpenClaw configured with GitHub channel (see config.github.yaml.example)
2. `gh` CLI authenticated OR `GH_TOKEN` set
3. xander-operator installed and working (v1.1.0+)

## Skill Definition

**Trigger:** Incoming GitHub webhook events routed to OpenClaw

**Context:** The webhook payload is parsed and transformed into a task for xander-operator.

### Event Mappings

| GitHub Event | xander-operator Task | Prompt Template |
|--------------|---------------------|-----------------|
| `pull_request` (opened, synchronize) | `research` | Review PR diff, suggest improvements, identify security risks |
| `workflow_run` (failed) | `research` | Analyze CI failure logs, suggest fix |
| `issues` (opened) | `research` | Categorize issue, suggest labels, request missing info |
| `push` to main after CI passes | `browse` | Smoke test the deployed site (if URL known) |
| `release` (published) | `research` | Summarize changes, check for breaking updates |

### Prompts

**PR Review Prompt:**
```
You are a senior code reviewer. Analyze this pull request:

Repository: {{repository.full_name}}
PR #{{pull_request.number}}: {{pull_request.title}}
Author: {{pull_request.user.login}}
Branch: {{pull_request.head.ref}} → {{pull_request.base.ref}}

Description:
{{pull_request.body}}

Changed files:
{{#each pull_request.files}}
- {{filename}} ({{changes}})
{{/each}}

Diff:
{{pull_request.diff}}

Provide:
1. Summary of changes (2-3 sentences)
2. Potential bugs or security issues
3. Suggestions for improvement
4. Test coverage gaps
5. Approve / Request changes / Comment
```

**CI Failure Alert Prompt:**
```
A GitHub Actions workflow failed.

Repository: {{repository.full_name}}
Workflow: {{workflow_run.name}} (#{{workflow_run.id}})
Branch: {{workflow_run.head_branch}}
Commit: {{workflow_run.head_commit.message}} by {{workflow_run.head_commit.author.name}}

Failure reason: {{workflow_run.conclusion}}

Log excerpt:
{{workflow_log_snippet}}

Based on the log, what is the most likely cause and what should be done next?
```

**Issue Triage Prompt:**
"""
You are a triage assistant. Categorize this GitHub issue:

Repository: {{repository.full_name}}
Issue #{{issue.number}}: {{issue.title}}
Reporter: {{issue.user.login}}
Labels: {{#each issue.labels}}{{name}} {{/each}}

Body:
{{issue.body}}

Determine:
- Type: bug / feature / question / documentation / security
- Severity: critical / high / medium / low
- Whether more information is needed (e.g., reproduction steps)
- Suggested labels (from standard set: bug, enhancement, question, docs, security, priority:high)
- A short, helpful response to the reporter (if needed)
"""

## Implementation

### Step 1: Install the Skill

```bash
mkdir -p /root/.openclaw/workspace/skills/github-automation
# Copy this SKILL.md and prompts/ directory into that folder
# Then reload OpenClaw or run: openclaw skill reload github-automation
```

### Step 2: Configure Webhook

In your GitHub repository settings:

1. Go to **Settings → Webhooks → Add webhook**
2. Payload URL: `https://YOUR_OPENCLAW_URL/hooks/github`
3. Content type: `application/json`
4. Secret: `${WEBHOOK_SECRET}` (same as in config)
5. Which events? Select "Let me select individual events" and choose:
   - Pull requests
   - Issues
   - Issue comment
   - Workflow runs (and maybe Pushes, Releases)
6. Enable SSL verification
7. Add webhook

### Step 3: Test

- Open a PR in your repo → OpenClaw should receive event, run xander-operator researcher task, and post a review comment.
- Fail a CI workflow → OpenClaw should analyze logs and send alert to chat channel.
- Create an issue → OpenClaw should respond with categorization and request details if needed.

## Security Considerations

- The webhook endpoint verifies `X-Hub-Signature-256` using the secret.
- xander-operator's approval gate prevents accidental writes unless explicitly allowed.
- Use a dedicated bot account with least privilege (repo, workflow scopes).
- Do not expose OpenClaw dashboard publicly; keep behind auth or VPN.

## Customization

- Edit prompt templates in `prompts/` directory.
- Adjust which events trigger tasks in `config.github.yaml`.
- Change xander-operator task parameters (model, max_tokens) by editing skill execution code.
