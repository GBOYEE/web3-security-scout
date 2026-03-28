# CI Failure Analysis Prompt

A GitHub Actions workflow failed. Diagnose the likely cause and suggest next steps.

## Context

**Repository:** {{repository.full_name}}
**Workflow:** {{workflow_run.name}} (ID: {{workflow_run.id}})
**Branch:** {{workflow_run.head_branch}}
**Commit:** {{workflow_run.head_commit.message}}
**Author:** {{workflow_run.head_commit.author.name}}

## Conclusion

{{workflow_run.conclusion}}

## Log Snippet (last 500 lines)

```
{{workflow_log_snippet}}
```

## Task

1. Identify the specific step that failed and why.
2. Explain the root cause in plain language.
3. Suggest concrete next steps: dependency update, config change, code fix, etc.
4. If it's an intermittent issue, recommend a workaround (e.g., retry with cache clear).
5. Indicate whether this failure blocks the PR/merge.

Be helpful and actionable. Include file names and line numbers when relevant.
