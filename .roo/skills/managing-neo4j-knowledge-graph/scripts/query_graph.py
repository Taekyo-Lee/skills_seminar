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
Query Graph — demonstrates search and read patterns on the AI Research Lab graph.

Demonstrates:
  - Get all nodes (no criteria), group by label
  - Simple NodeSearch with label + property (AND logic)
  - Q operators: Q.gte(), Q.gt(), Q.contains()
  - NodeSearchUnion with builder pattern (OR logic)
  - RelationshipSearch with start/end node criteria
  - Execution context inspection

Exit codes:
  0  All queries succeeded
  1  Error occurred
"""

import sys

from a2g_neo4j import Neo4jManager
from a2g_neo4j.neo4j_schemas.entity_search_schemas import (
    NodeSearch, NodeSearchUnion, RelationshipSearch,
)
from a2g_neo4j.query_tools import Q

NAMESPACE = "seminar_demo"
WIDTH = 52


def run() -> int:
    print("=" * WIDTH)
    print("  Query Graph — AI Research Lab")
    print("=" * WIDTH)

    manager = Neo4jManager(log_level="warning")

    # ── 1. Get all nodes, group by label ──────────────────────
    print("\n  [1] All nodes (no criteria)")
    resp = manager.get_nodes(namespace=NAMESPACE)
    nodes = resp.result
    print(f"      Total: {len(nodes)}")

    by_label = {}
    for n in nodes:
        by_label.setdefault(n.label, []).append(n)
    for label in sorted(by_label):
        print(f"      {label}: {len(by_label[label])}")

    # ── 2. Simple NodeSearch — label + property (AND) ─────────
    print("\n  [2] NodeSearch: active Projects")
    resp = manager.get_nodes(
        NodeSearch(label="Project", status="active"),
        namespace=NAMESPACE,
    )
    for n in resp.result:
        print(f"      {n.properties['code']}: {n.properties['title']}")

    # ── 3. Q operators ────────────────────────────────────────
    print("\n  [3a] Q.gte — Researchers with h_index >= 10")
    resp = manager.get_nodes(
        NodeSearch(label="Researcher", h_index=Q.gte(10)),
        namespace=NAMESPACE,
    )
    for n in resp.result:
        print(f"      {n.properties['name']} (h={n.properties['h_index']})")

    print("\n  [3b] Q.gt — Publications with citations > 50")
    resp = manager.get_nodes(
        NodeSearch(label="Publication", citations=Q.gt(50)),
        namespace=NAMESPACE,
    )
    for n in resp.result:
        print(f"      {n.properties['title']} ({n.properties['citations']} cites)")

    print("\n  [3c] Q.contains — Projects with 'Model' in title")
    resp = manager.get_nodes(
        NodeSearch(label="Project", title=Q.contains("Model")),
        namespace=NAMESPACE,
    )
    for n in resp.result:
        print(f"      {n.properties['code']}: {n.properties['title']}")

    # ── 4. NodeSearchUnion — OR logic (builder) ───────────────
    print("\n  [4] NodeSearchUnion: PhD Students OR Postdocs")
    search = (
        NodeSearchUnion.builder()
        .add(label="Researcher", role="PhD Student")
        .add(label="Researcher", role="Postdoc")
        .build()
    )
    resp = manager.get_nodes(search, namespace=NAMESPACE)
    for n in resp.result:
        print(f"      {n.properties['name']} ({n.properties['role']})")

    # ── 5. RelationshipSearch — start/end criteria ────────────
    print("\n  [5a] RelationshipSearch: all WORKS_ON")
    resp = manager.get_rels(
        RelationshipSearch(rel_type="WORKS_ON"),
        namespace=NAMESPACE,
    )
    for r in resp.result:
        print(f"      {r.start.properties.get('name', r.start.properties.get('code', '?'))} "
              f"—[WORKS_ON]→ "
              f"{r.end.properties.get('code', r.end.properties.get('title', '?'))}")

    print("\n  [5b] RelationshipSearch: Alice's relationships")
    resp = manager.get_rels(
        RelationshipSearch(
            start=NodeSearch(label="Researcher", email="alice@lab.ai"),
        ),
        namespace=NAMESPACE,
    )
    for r in resp.result:
        end_name = (r.end.properties.get('code')
                    or r.end.properties.get('title')
                    or r.end.properties.get('doi', '?'))
        print(f"      —[{r.rel_type}]→ {end_name}")

    # ── 6. Execution context inspection ───────────────────────
    print("\n  [6] Execution context (last query)")
    ctx = resp.execution
    print(f"      Operation ........ {ctx.operation}")
    print(f"      Entity type ...... {ctx.entity_type}")
    print(f"      Affected count ... {ctx.affected_count}")
    print(f"      Cypher (human) ... {ctx.cypher_human[:80]}...")

    # ── Summary ───────────────────────────────────────────────
    print("\n" + "-" * WIDTH)
    print("  PASS  All queries completed")
    print("=" * WIDTH)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception as e:
        print(f"\n  FAIL  {e}")
        sys.exit(1)
