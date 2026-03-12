# /// script
# dependencies = [
#   "requests>=2.32.0",
# ]
# ///

"""
JIRA Create Issue — create an issue from a JSON config (stdin or --config file).

Config format (JSON):
  {
    "project": "DEMO",
    "issuetype": "Bug",
    "summary": "Login page timeout",
    "description": "Users experience a timeout on the login page...",
    "priority": "High",
    "assignee": "alice@company.com",
    "labels": ["frontend", "urgent"]
  }

Usage:
  echo '{"project":"DEMO","issuetype":"Bug","summary":"Fix login"}' | create_issue.py
  create_issue.py --config issue.json

Exit codes:
  0  Issue created successfully
  1  Error (auth, validation, API failure)
"""

import argparse
import json
import os
import sys

import requests


WIDTH = 52


def get_auth():
    base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
    email = os.environ.get("JIRA_USER_EMAIL", "")
    token = os.environ.get("JIRA_API_TOKEN", "")
    if not all([base_url, email, token]):
        print("  ERROR  Missing JIRA env vars")
        return None
    return base_url, (email, token)


def load_config(config_path: str | None) -> dict | None:
    try:
        if config_path:
            with open(config_path) as f:
                return json.load(f)
        elif not sys.stdin.isatty():
            return json.load(sys.stdin)
        else:
            print("  ERROR  No config provided. Use --config or pipe JSON to stdin.")
            return None
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"  ERROR  {e}")
        return None


def resolve_account_id(base_url: str, auth: tuple, email: str) -> str | None:
    """Look up a user's account ID by email."""
    try:
        resp = requests.get(
            f"{base_url}/rest/api/3/user/search",
            params={"query": email},
            auth=auth,
            timeout=15,
        )
        if resp.status_code == 200:
            users = resp.json()
            for user in users:
                if user.get("emailAddress", "").lower() == email.lower():
                    return user["accountId"]
            if users:
                return users[0]["accountId"]
    except requests.RequestException:
        pass
    return None


def run_create(config_path: str | None) -> int:
    print("=" * WIDTH)
    print("  JIRA Create Issue")
    print("=" * WIDTH)

    config = get_auth()
    if not config:
        return 1

    base_url, auth = config
    issue_config = load_config(config_path)
    if not issue_config:
        return 1

    # ── Validate required fields ──────────────────────────
    project = issue_config.get("project") or os.environ.get("JIRA_PROJECT_KEY", "")
    summary = issue_config.get("summary", "")
    issuetype = issue_config.get("issuetype", "Task")

    if not project or not summary:
        print("\n  ERROR  'project' and 'summary' are required")
        return 1

    print(f"\n  Project .......... {project}")
    print(f"  Type ............. {issuetype}")
    print(f"  Summary .......... {summary}")

    # ── Build API payload ─────────────────────────────────
    fields = {
        "project": {"key": project},
        "summary": summary,
        "issuetype": {"name": issuetype},
    }

    if issue_config.get("description"):
        fields["description"] = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": issue_config["description"]}],
                }
            ],
        }

    if issue_config.get("priority"):
        fields["priority"] = {"name": issue_config["priority"]}
        print(f"  Priority ......... {issue_config['priority']}")

    if issue_config.get("labels"):
        fields["labels"] = issue_config["labels"]
        print(f"  Labels ........... {', '.join(issue_config['labels'])}")

    if issue_config.get("assignee"):
        assignee_email = issue_config["assignee"]
        account_id = resolve_account_id(base_url, auth, assignee_email)
        if account_id:
            fields["assignee"] = {"accountId": account_id}
            print(f"  Assignee ......... {assignee_email}")
        else:
            print(f"  WARN  Could not resolve assignee: {assignee_email}")

    # ── Create issue ──────────────────────────────────────
    try:
        resp = requests.post(
            f"{base_url}/rest/api/3/issue",
            json={"fields": fields},
            auth=auth,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if resp.status_code in (200, 201):
            result = resp.json()
            issue_key = result.get("key", "?")
            issue_id = result.get("id", "?")
            issue_url = f"{base_url}/browse/{issue_key}"
            print(f"\n  [PASS]  Created: {issue_key}")
            print(f"    ID ................. {issue_id}")
            print(f"    URL ................ {issue_url}")
            print("\n" + "=" * WIDTH)
            return 0
        else:
            error = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
            errors = error.get("errors", {})
            messages = error.get("errorMessages", [])
            print(f"\n  [FAIL]  HTTP {resp.status_code}")
            for msg in messages:
                print(f"    {msg}")
            for field, msg in errors.items():
                print(f"    {field}: {msg}")
            print("\n" + "=" * WIDTH)
            return 1

    except requests.RequestException as e:
        print(f"\n  ERROR  {e}")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a JIRA issue")
    parser.add_argument("--config", help="Path to JSON config file")
    args = parser.parse_args()
    sys.exit(run_create(args.config))
