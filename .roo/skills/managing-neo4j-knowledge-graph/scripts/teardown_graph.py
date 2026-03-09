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
Teardown Graph — demonstrates delete operations on the AI Research Lab graph.

Demonstrates:
  - Delete relationships by type
  - Delete relationships by start/end criteria
  - Delete nodes by criteria (DETACH DELETE)
  - Bulk cleanup with delete_all(namespace=...)
  - Verification: confirm 0 nodes / 0 rels

Exit codes:
  0  Teardown completed successfully
  1  Error occurred
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "a2g_neo4j"))

from a2g_neo4j import Neo4jManager
from a2g_neo4j.neo4j_schemas.entity_search_schemas import (
    NodeSearch, RelationshipSearch,
)

NAMESPACE = "seminar_demo"
WIDTH = 52


def run() -> int:
    print("=" * WIDTH)
    print("  Teardown Graph — AI Research Lab")
    print("=" * WIDTH)

    manager = Neo4jManager(log_level="warning")

    # Show starting state
    n_resp = manager.get_nodes(namespace=NAMESPACE)
    r_resp = manager.get_rels(namespace=NAMESPACE)
    print(f"\n  Starting state: {len(n_resp.result)} nodes, {len(r_resp.result)} rels")

    # ── 1. Delete relationships by type ───────────────────────
    print("\n  [1] Delete rels by type — CITES")
    resp = manager.delete_rels(
        RelationshipSearch(rel_type="CITES"),
        namespace=NAMESPACE,
    )
    ctx = resp.execution
    print(f"      Deleted: {ctx.affected_count} CITES rels")

    # ── 2. Delete relationships by start/end criteria ─────────
    print("\n  [2] Delete rels by start criteria — Dan's AUTHORED")
    resp = manager.delete_rels(
        RelationshipSearch(
            rel_type="AUTHORED",
            start=NodeSearch(label="Researcher", email="dan@lab.ai"),
        ),
        namespace=NAMESPACE,
    )
    ctx = resp.execution
    print(f"      Deleted: {ctx.affected_count} rels")

    # ── 3. Delete nodes by criteria (DETACH DELETE) ───────────
    print("\n  [3] Delete nodes by criteria — all Technology nodes")
    resp = manager.delete_nodes(
        NodeSearch(label="Technology"),
        namespace=NAMESPACE,
    )
    ctx = resp.execution
    print(f"      Deleted: {ctx.affected_count} Technology nodes (+ attached rels)")

    # Check remaining state
    n_resp = manager.get_nodes(namespace=NAMESPACE)
    r_resp = manager.get_rels(namespace=NAMESPACE)
    print(f"\n  After selective deletes: {len(n_resp.result)} nodes, {len(r_resp.result)} rels")

    # ── 4. Bulk cleanup — delete_all(namespace=...) ───────────
    print("\n  [4] Bulk cleanup — delete_all(namespace)")
    result = manager.delete_all(namespace=NAMESPACE)
    print(f"      Deleted {result['nodes_deleted']} nodes, "
          f"{result['relationships_deleted']} rels")
    print(f"      Status: {result['status']}")

    # ── 5. Verify empty ──────────────────────────────────────
    print("\n  [5] Verify empty")
    n_resp = manager.get_nodes(namespace=NAMESPACE)
    r_resp = manager.get_rels(namespace=NAMESPACE)
    n_count = len(n_resp.result)
    r_count = len(r_resp.result)
    print(f"      Nodes .............. {n_count}")
    print(f"      Relationships ...... {r_count}")

    # ── Summary ───────────────────────────────────────────────
    ok = n_count == 0 and r_count == 0
    print("\n" + "-" * WIDTH)
    if ok:
        print("  PASS  Graph fully torn down (0 nodes, 0 rels)")
    else:
        print(f"  FAIL  Expected 0/0, got {n_count}/{r_count}")
    print("=" * WIDTH)
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception as e:
        print(f"\n  FAIL  {e}")
        sys.exit(1)
