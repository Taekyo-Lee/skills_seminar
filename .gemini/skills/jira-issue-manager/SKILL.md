---
name: jira-issue-manager
description: >-
  Use for ANY user request to create, update, transition, or manage JIRA issues —
  including creating bugs/stories/tasks, updating fields, changing status,
  assigning issues, adding comments, or performing any JIRA CRUD operation via
  the REST API. Also use for health checks and searching issues. Do NOT use for
  pure JQL syntax questions or query building — those should use the
  jira-jql-assistant skill instead.
---

# JIRA Issue Manager

This skill performs CRUD operations on JIRA issues via the Atlassian REST API. It includes scripts for health checks, searching, creating, updating, and transitioning issues.

## Prerequisites

- JIRA Cloud instance with API access
- API token from https://id.atlassian.com/manage-profile/security/api-tokens
- Environment variables (loaded from `.env` at the project root):
  - `JIRA_BASE_URL` — e.g., `https://your-domain.atlassian.net`
  - `JIRA_USER_EMAIL` — your Atlassian account email
  - `JIRA_API_TOKEN` — your API token
  - `JIRA_PROJECT_KEY` — default project key (e.g., `DEMO`)

## Important Behavioral Rules

1. **Do NOT run health_check.py** unless the user explicitly asks about connectivity, health, or status. Go straight to the operation.
2. **Do NOT use `python3 -c` or `uv run -c`** — they lack the required dependencies.
3. All commands run from the project root: `<PROJECT_ROOT>`

## Running Ad-Hoc Operations

For any JIRA API request that is NOT an exact match for a pre-built script, follow these 3 steps:

**Step 1.** Write a temporary script to this absolute path:
`<PROJECT_ROOT>/.gemini/skills/jira-issue-manager/scripts/_adhoc.py`

```python
# /// script
# dependencies = [
#   "requests>=2.32.0",
# ]
# ///

import os
import requests

BASE_URL = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
AUTH = (os.environ.get("JIRA_USER_EMAIL", ""), os.environ.get("JIRA_API_TOKEN", ""))
PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY", "")

# --- YOUR API CALL HERE ---
```

**Step 2.** Run it:
```bash
uv run --native-tls --env-file .env <PROJECT_ROOT>/.gemini/skills/jira-issue-manager/scripts/_adhoc.py
```

**Step 3.** Delete the file after execution:
```bash
rm <PROJECT_ROOT>/.gemini/skills/jira-issue-manager/scripts/_adhoc.py
```

## Common API Patterns

```python
import os
import requests

BASE_URL = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
AUTH = (os.environ.get("JIRA_USER_EMAIL", ""), os.environ.get("JIRA_API_TOKEN", ""))

# Search issues via JQL
resp = requests.get(f"{BASE_URL}/rest/api/3/search",
    params={"jql": "project = DEMO AND status != Done", "maxResults": 10},
    auth=AUTH)
for issue in resp.json()["issues"]:
    print(f"{issue['key']}: {issue['fields']['summary']}")

# Create an issue
resp = requests.post(f"{BASE_URL}/rest/api/3/issue",
    json={"fields": {
        "project": {"key": "DEMO"},
        "summary": "New issue",
        "issuetype": {"name": "Task"},
    }},
    auth=AUTH, headers={"Content-Type": "application/json"})

# Update an issue
requests.put(f"{BASE_URL}/rest/api/3/issue/DEMO-1",
    json={"fields": {"summary": "Updated title"}},
    auth=AUTH, headers={"Content-Type": "application/json"})

# Transition an issue
transitions = requests.get(f"{BASE_URL}/rest/api/3/issue/DEMO-1/transitions", auth=AUTH).json()
tid = next(t["id"] for t in transitions["transitions"] if t["name"] == "Done")
requests.post(f"{BASE_URL}/rest/api/3/issue/DEMO-1/transitions",
    json={"transition": {"id": tid}},
    auth=AUTH, headers={"Content-Type": "application/json"})

# Add a comment
requests.post(f"{BASE_URL}/rest/api/3/issue/DEMO-1/comment",
    json={"body": {"type": "doc", "version": 1,
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": "My comment"}]}]}},
    auth=AUTH, headers={"Content-Type": "application/json"})
```

## Available Scripts on Demand

Run from the project root (`<PROJECT_ROOT>`):

```bash
uv run --native-tls --env-file .env <PROJECT_ROOT>/.gemini/skills/jira-issue-manager/scripts/<script_name>.py [args]
```

| Script | Purpose | Example |
|---|---|---|
| `health_check.py` | Verify connectivity, auth, project access, permissions | `scripts/health_check.py` |
| `search_issues.py` | Search via JQL with formatted output | `scripts/search_issues.py --jql "project = DEMO"` |
| `create_issue.py` | Create issue from JSON config | `echo '{"summary":"Fix bug"}' \| scripts/create_issue.py` |
| `update_issue.py` | Update issue fields | `scripts/update_issue.py --issue-key DEMO-1 --fields '{"priority":{"name":"High"}}'` |
| `transition_issue.py` | Move issue through workflow | `scripts/transition_issue.py --issue-key DEMO-1 --transition "Done"` |
