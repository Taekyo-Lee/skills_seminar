# /// script
# dependencies = [
#   "requests>=2.32.0",
# ]
# ///

"""
JIRA Transition Issue — move an issue through its workflow.

Usage:
  transition_issue.py --issue-key DEMO-1 --transition "In Progress"
  transition_issue.py --issue-key DEMO-1 --transition "Done"

Exit codes:
  0  Transition completed successfully
  1  Error (auth, invalid transition, API failure)
"""

import argparse
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


def run_transition(issue_key: str, transition_name: str) -> int:
    print("=" * WIDTH)
    print("  JIRA Transition Issue")
    print("=" * WIDTH)

    config = get_auth()
    if not config:
        return 1

    base_url, auth = config

    print(f"\n  Issue ............ {issue_key}")
    print(f"  Target ........... {transition_name}")

    # ── Get current status ────────────────────────────────
    try:
        resp = requests.get(
            f"{base_url}/rest/api/3/issue/{issue_key}",
            params={"fields": "status"},
            auth=auth,
            timeout=15,
        )
        if resp.status_code == 200:
            current_status = resp.json()["fields"]["status"]["name"]
            print(f"  Current status ... {current_status}")
        elif resp.status_code == 404:
            print(f"\n  [FAIL]  Issue {issue_key} not found")
            return 1
    except requests.RequestException as e:
        print(f"\n  ERROR  {e}")
        return 1

    # ── Get available transitions ─────────────────────────
    try:
        resp = requests.get(
            f"{base_url}/rest/api/3/issue/{issue_key}/transitions",
            auth=auth,
            timeout=15,
        )
        if resp.status_code != 200:
            print(f"\n  [FAIL]  Could not get transitions: HTTP {resp.status_code}")
            return 1

        transitions = resp.json().get("transitions", [])
        if not transitions:
            print(f"\n  [FAIL]  No transitions available from '{current_status}'")
            return 1

        # Find matching transition (case-insensitive)
        target = None
        for t in transitions:
            if t["name"].lower() == transition_name.lower():
                target = t
                break

        if not target:
            available = [t["name"] for t in transitions]
            print(f"\n  [FAIL]  Transition '{transition_name}' not available")
            print(f"  Available transitions:")
            for name in available:
                print(f"    - {name}")
            return 1

        print(f"\n  Available transitions:")
        for t in transitions:
            marker = " <<" if t["id"] == target["id"] else ""
            print(f"    - {t['name']}{marker}")

    except requests.RequestException as e:
        print(f"\n  ERROR  {e}")
        return 1

    # ── Execute transition ────────────────────────────────
    try:
        resp = requests.post(
            f"{base_url}/rest/api/3/issue/{issue_key}/transitions",
            json={"transition": {"id": target["id"]}},
            auth=auth,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if resp.status_code == 204:
            print(f"\n  [PASS]  {current_status} -> {target['name']}")
            print(f"    URL ................ {base_url}/browse/{issue_key}")
            print("\n" + "=" * WIDTH)
            return 0
        else:
            print(f"\n  [FAIL]  Transition failed: HTTP {resp.status_code}")
            print("\n" + "=" * WIDTH)
            return 1

    except requests.RequestException as e:
        print(f"\n  ERROR  {e}")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transition a JIRA issue")
    parser.add_argument("--issue-key", required=True, help="Issue key (e.g., DEMO-1)")
    parser.add_argument("--transition", required=True, help="Transition name (e.g., 'In Progress', 'Done')")
    args = parser.parse_args()
    sys.exit(run_transition(args.issue_key, args.transition))
