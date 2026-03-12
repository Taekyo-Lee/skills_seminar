# /// script
# dependencies = [
#   "requests>=2.32.0",
# ]
# ///

"""
JIRA Update Issue — update fields on an existing issue.

Usage:
  update_issue.py --issue-key DEMO-1 --fields '{"summary": "New title", "priority": {"name": "High"}}'
  update_issue.py --issue-key DEMO-1 --fields '{"labels": ["frontend", "urgent"]}'

Exit codes:
  0  Issue updated successfully
  1  Error (auth, not found, API failure)
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


def run_update(issue_key: str, fields_json: str) -> int:
    print("=" * WIDTH)
    print("  JIRA Update Issue")
    print("=" * WIDTH)

    config = get_auth()
    if not config:
        return 1

    base_url, auth = config

    try:
        fields = json.loads(fields_json)
    except json.JSONDecodeError as e:
        print(f"\n  ERROR  Invalid JSON: {e}")
        return 1

    print(f"\n  Issue ............ {issue_key}")
    print(f"  Fields to update:")
    for key, value in fields.items():
        print(f"    {key}: {json.dumps(value) if isinstance(value, (dict, list)) else value}")

    # ── Fetch current issue (before) ──────────────────────
    try:
        resp = requests.get(
            f"{base_url}/rest/api/3/issue/{issue_key}",
            params={"fields": ",".join(fields.keys())},
            auth=auth,
            timeout=15,
        )
        if resp.status_code == 200:
            current = resp.json().get("fields", {})
            print(f"\n  Before:")
            for key in fields:
                val = current.get(key)
                if isinstance(val, dict):
                    val = val.get("name", val.get("displayName", str(val)))
                print(f"    {key}: {val}")
        elif resp.status_code == 404:
            print(f"\n  [FAIL]  Issue {issue_key} not found")
            return 1
    except requests.RequestException:
        pass

    # ── Update issue ──────────────────────────────────────
    try:
        resp = requests.put(
            f"{base_url}/rest/api/3/issue/{issue_key}",
            json={"fields": fields},
            auth=auth,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if resp.status_code == 204:
            print(f"\n  [PASS]  Updated: {issue_key}")
            print(f"    URL ................ {base_url}/browse/{issue_key}")
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
    parser = argparse.ArgumentParser(description="Update a JIRA issue")
    parser.add_argument("--issue-key", required=True, help="Issue key (e.g., DEMO-1)")
    parser.add_argument("--fields", required=True, help="JSON object of fields to update")
    args = parser.parse_args()
    sys.exit(run_update(args.issue_key, args.fields))
