# /// script
# dependencies = [
#   "requests>=2.32.0",
# ]
# ///

"""
JIRA Search — search issues via JQL with formatted table output.

Usage:
  search_issues.py --jql "project = DEMO AND status != Done"
  search_issues.py --jql "assignee = currentUser()" --max-results 50

Exit codes:
  0  Search completed successfully
  1  Error (auth, network, invalid JQL)
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


def truncate(text: str, length: int) -> str:
    if not text:
        return ""
    return text[:length - 1] + "~" if len(text) > length else text


def run_search(jql: str, max_results: int) -> int:
    print("=" * WIDTH)
    print("  JIRA Search")
    print("=" * WIDTH)
    print(f"\n  JQL: {jql}")

    config = get_auth()
    if not config:
        return 1

    base_url, auth = config

    try:
        resp = requests.get(
            f"{base_url}/rest/api/3/search",
            params={
                "jql": jql,
                "maxResults": max_results,
                "fields": "summary,status,assignee,priority,issuetype,created,updated",
            },
            auth=auth,
            timeout=30,
        )

        if resp.status_code != 200:
            error = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
            messages = error.get("errorMessages", [])
            print(f"\n  ERROR  HTTP {resp.status_code}")
            for msg in messages:
                print(f"    {msg}")
            return 1

        data = resp.json()
        issues = data.get("issues", [])
        total = data.get("total", 0)

        print(f"\n  Results: {len(issues)} of {total} total")
        print("-" * WIDTH)

        if not issues:
            print("  (no matching issues)")
            print("=" * WIDTH)
            return 0

        # ── Table header ──────────────────────────────────
        print(f"  {'Key':<12} {'Type':<8} {'Pri':<8} {'Status':<14}")
        print(f"  {'':─<12} {'':─<8} {'':─<8} {'':─<14}")

        for issue in issues:
            key = issue["key"]
            fields = issue["fields"]
            itype = (fields.get("issuetype") or {}).get("name", "?")
            priority = (fields.get("priority") or {}).get("name", "?")
            status = (fields.get("status") or {}).get("name", "?")
            summary = fields.get("summary", "")
            assignee = (fields.get("assignee") or {}).get("displayName", "Unassigned")

            print(f"  {key:<12} {truncate(itype, 8):<8} {truncate(priority, 8):<8} {truncate(status, 14):<14}")
            print(f"    {truncate(summary, WIDTH - 6)}")
            print(f"    -> {assignee}")

        print("-" * WIDTH)
        if total > len(issues):
            print(f"  Showing {len(issues)} of {total} — refine JQL or increase --max-results")
        print("=" * WIDTH)
        return 0

    except requests.RequestException as e:
        print(f"\n  ERROR  {e}")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search JIRA issues via JQL")
    parser.add_argument("--jql", required=True, help="JQL query string")
    parser.add_argument("--max-results", type=int, default=20, help="Max results (default: 20)")
    args = parser.parse_args()
    sys.exit(run_search(args.jql, args.max_results))
