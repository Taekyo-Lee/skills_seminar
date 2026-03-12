# /// script
# dependencies = [
#   "requests>=2.32.0",
# ]
# ///

"""
JIRA Health Check — verifies connectivity, authentication, and project access.

Exit codes:
  0  All checks passed
  1  Connection failed
  2  One or more checks failed
"""

import os
import sys
import time

import requests


WIDTH = 52


def get_auth():
    base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
    email = os.environ.get("JIRA_USER_EMAIL", "")
    token = os.environ.get("JIRA_API_TOKEN", "")
    project_key = os.environ.get("JIRA_PROJECT_KEY", "")

    if not all([base_url, email, token]):
        print("\n  FAIL  Missing environment variables.")
        print("        Required: JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN")
        return None
    return {
        "base_url": base_url,
        "email": email,
        "token": token,
        "project_key": project_key,
    }


def fmt_ms(seconds: float) -> str:
    return f"{seconds * 1000:.1f} ms"


def run_health_check() -> int:
    checks_passed = 0
    checks_failed = 0

    print("=" * WIDTH)
    print("  JIRA Health Check")
    print("=" * WIDTH)

    config = get_auth()
    if not config:
        print("\n" + "=" * WIDTH)
        return 1

    base_url = config["base_url"]
    auth = (config["email"], config["token"])

    # ── 1. Authentication ─────────────────────────────────
    try:
        t0 = time.perf_counter()
        resp = requests.get(f"{base_url}/rest/api/3/myself", auth=auth, timeout=15)
        latency = time.perf_counter() - t0
        if resp.status_code == 200:
            user = resp.json()
            display_name = user.get("displayName", "unknown")
            email_addr = user.get("emailAddress", "unknown")
            print(f"\n  [PASS]  Auth ................. {fmt_ms(latency)}")
            print(f"    User ................. {display_name}")
            print(f"    Email ................ {email_addr}")
            checks_passed += 1
        else:
            print(f"\n  [FAIL]  Auth ................. HTTP {resp.status_code}")
            checks_failed += 1
    except requests.RequestException as e:
        print(f"\n  [FAIL]  Connection failed: {e}")
        print("\n" + "=" * WIDTH)
        return 1

    # ── 2. Server Info ────────────────────────────────────
    try:
        resp = requests.get(f"{base_url}/rest/api/3/serverInfo", auth=auth, timeout=15)
        if resp.status_code == 200:
            info = resp.json()
            version = info.get("version", "unknown")
            deployment = info.get("deploymentType", "unknown")
            print(f"\n  Server")
            print(f"    Base URL ............. {base_url}")
            print(f"    Version .............. {version}")
            print(f"    Deployment ........... {deployment}")
            checks_passed += 1
        else:
            print(f"\n  [FAIL]  Server info .......... HTTP {resp.status_code}")
            checks_failed += 1
    except requests.RequestException as e:
        print(f"\n  [FAIL]  Server info: {e}")
        checks_failed += 1

    # ── 3. Project Access ─────────────────────────────────
    project_key = config["project_key"]
    if project_key:
        try:
            resp = requests.get(
                f"{base_url}/rest/api/3/project/{project_key}", auth=auth, timeout=15
            )
            if resp.status_code == 200:
                project = resp.json()
                project_name = project.get("name", "unknown")
                project_type = project.get("projectTypeKey", "unknown")
                lead = project.get("lead", {}).get("displayName", "unknown")
                print(f"\n  [PASS]  Project access")
                print(f"    Key .................. {project_key}")
                print(f"    Name ................. {project_name}")
                print(f"    Type ................. {project_type}")
                print(f"    Lead ................. {lead}")
                checks_passed += 1
            else:
                print(f"\n  [FAIL]  Project '{project_key}' .. HTTP {resp.status_code}")
                checks_failed += 1
        except requests.RequestException as e:
            print(f"\n  [FAIL]  Project access: {e}")
            checks_failed += 1
    else:
        print(f"\n  [SKIP]  Project access (JIRA_PROJECT_KEY not set)")

    # ── 4. Permissions ────────────────────────────────────
    try:
        resp = requests.get(
            f"{base_url}/rest/api/3/mypermissions",
            params={"permissions": "BROWSE_PROJECTS,CREATE_ISSUES,EDIT_ISSUES,TRANSITION_ISSUES"},
            auth=auth,
            timeout=15,
        )
        if resp.status_code == 200:
            perms = resp.json().get("permissions", {})
            perm_list = []
            for key in ["BROWSE_PROJECTS", "CREATE_ISSUES", "EDIT_ISSUES", "TRANSITION_ISSUES"]:
                perm = perms.get(key, {})
                have = perm.get("havePermission", False)
                perm_list.append(f"{'Y' if have else 'N'} {key}")
            print(f"\n  Permissions")
            for p in perm_list:
                print(f"    {p}")
            checks_passed += 1
        else:
            print(f"\n  [FAIL]  Permissions .......... HTTP {resp.status_code}")
            checks_failed += 1
    except requests.RequestException as e:
        print(f"\n  [FAIL]  Permissions: {e}")
        checks_failed += 1

    # ── Summary ───────────────────────────────────────────
    print("\n" + "-" * WIDTH)
    if checks_failed == 0:
        print(f"  HEALTHY  ({checks_passed} checks passed)")
    else:
        print(f"  DEGRADED  ({checks_passed} passed, {checks_failed} failed)")
    print("=" * WIDTH)

    return 2 if checks_failed else 0


if __name__ == "__main__":
    sys.exit(run_health_check())
