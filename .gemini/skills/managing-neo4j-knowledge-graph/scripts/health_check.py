# /// script
# dependencies = [
#   "colorlog>=6.10.1",
#   "json5>=0.12.1",
#   "neo4j>=6.0.3",
#   "pydantic>=2.12.5",
#   "python-dateutil>=2.9.0.post0",
# ]
# ///

"""
Neo4j Health Check — verifies connectivity, server info, and basic database stats.

Exit codes:
  0  All checks passed
  1  Connection failed
  2  One or more checks failed
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "a2g_neo4j"))

from a2g_neo4j import Neo4jManager


def fmt_ms(seconds: float) -> str:
    return f"{seconds * 1000:.1f} ms"


def run_health_check() -> int:
    checks_passed = 0
    checks_failed = 0

    # ── 1. Connectivity ──────────────────────────────────────────────
    print("=" * 52)
    print("  Neo4j Health Check")
    print("=" * 52)

    try:
        t0 = time.perf_counter()
        manager = Neo4jManager(log_level="warning")
        connect_time = time.perf_counter() - t0
    except Exception as e:
        print(f"\n  FAIL  Connection failed: {e}")
        print("\n" + "=" * 52)
        return 1

    t0 = time.perf_counter()
    ping_ok = manager.ping()
    ping_time = time.perf_counter() - t0

    status = "PASS" if ping_ok else "FAIL"
    print(f"\n  [{status}]  Ping ................ {fmt_ms(ping_time)}")
    if ping_ok:
        checks_passed += 1
    else:
        checks_failed += 1

    # ── 2. Connection info ────────────────────────────────────────────
    print(f"\n  Connection")
    print(f"    URI ................ {manager.connector.url}")
    print(f"    Database ........... {manager.connector.database}")
    print(f"    Connect time ....... {fmt_ms(connect_time)}")

    # ── 3. Server components ──────────────────────────────────────────
    try:
        components = manager.connector.query(
            "CALL dbms.components() YIELD name, versions, edition "
            "RETURN name, versions, edition"
        )
        if components:
            c = components[0]
            version = c["versions"][0] if c.get("versions") else "unknown"
            edition = c.get("edition", "unknown")
            print(f"\n  Server")
            print(f"    Version ............ {version}")
            print(f"    Edition ............ {edition}")
            checks_passed += 1
        else:
            print(f"\n  [FAIL]  Could not retrieve server components")
            checks_failed += 1
    except Exception as e:
        print(f"\n  [FAIL]  Server components query failed: {e}")
        checks_failed += 1

    # ── 4. Database status ────────────────────────────────────────────
    try:
        databases = manager.connector.query("SHOW DATABASES")
        current_db = manager.connector.database
        db_info = next((d for d in databases if d.get("name") == current_db), None)
        if db_info:
            db_status = db_info.get("currentStatus", "unknown")
            label = "PASS" if db_status == "online" else "WARN"
            print(f"\n  [{label}]  Database status .... {db_status}")
            checks_passed += 1
        else:
            print(f"\n  [WARN]  Database '{current_db}' not found in SHOW DATABASES")
            checks_failed += 1
    except Exception:
        # SHOW DATABASES may require admin privileges; not a hard failure
        pass

    # ── 5. Graph statistics ───────────────────────────────────────────
    try:
        nodes = manager.get_nodes().result
        rels = manager.get_rels().result
        node_count = len(nodes)
        rel_count = len(rels)

        labels = sorted({n.label for n in nodes} if nodes else set())

        print(f"\n  Graph statistics")
        print(f"    Nodes .............. {node_count}")
        print(f"    Relationships ...... {rel_count}")
        if labels:
            print(f"    Labels ............. {', '.join(labels)}")
        checks_passed += 1
    except Exception as e:
        print(f"\n  [FAIL]  Could not retrieve graph stats: {e}")
        checks_failed += 1

    # ── 6. Constraints ────────────────────────────────────────────────
    try:
        constraints = manager.get_constraints().result
        constraint_count = len(constraints) if constraints else 0
        print(f"    Constraints ........ {constraint_count}")
        checks_passed += 1
    except Exception:
        pass

    # ── Summary ───────────────────────────────────────────────────────
    print("\n" + "-" * 52)
    if checks_failed == 0:
        print(f"  HEALTHY  ({checks_passed} checks passed)")
    else:
        print(f"  DEGRADED  ({checks_passed} passed, {checks_failed} failed)")
    print("=" * 52)

    return 2 if checks_failed else 0


if __name__ == "__main__":
    sys.exit(run_health_check())
