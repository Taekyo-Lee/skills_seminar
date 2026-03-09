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
Update Graph — demonstrates update semantics via upsert on the AI Research Lab graph.

Demonstrates:
  - Modify existing property (before/after)
  - Add new property to existing node
  - Remove property by setting to None
  - Update relationship properties
  - Bulk update with execution context

Exit codes:
  0  All updates succeeded
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
    print("  Update Graph — AI Research Lab")
    print("=" * WIDTH)

    manager = Neo4jManager(log_level="warning")

    # ── 1. Modify existing property (before/after) ────────────
    print("\n  [1] Modify existing property — Carol's h_index")

    # Before
    resp = manager.get_nodes(
        NodeSearch(label="Researcher", email="carol@lab.ai"),
        namespace=NAMESPACE,
    )
    carol = resp.result[0]
    print(f"      Before: h_index = {carol.properties['h_index']}")

    # Update via upsert (same label + primary_key = update)
    updated = manager.create_nodes({
        "label": "Researcher", "primary_key": "email",
        "email": "carol@lab.ai",
        "h_index": 8,
    }, namespace=NAMESPACE)
    resp = manager.upsert_nodes([updated])
    print(f"      Upserted: affected = {resp.execution.affected_count}")

    # After
    resp = manager.get_nodes(
        NodeSearch(label="Researcher", email="carol@lab.ai"),
        namespace=NAMESPACE,
    )
    carol = resp.result[0]
    print(f"      After:  h_index = {carol.properties['h_index']}")

    # ── 2. Add new property to existing node ──────────────────
    print("\n  [2] Add new property — PROJ-RL gets 'priority'")

    resp = manager.get_nodes(
        NodeSearch(label="Project", code="PROJ-RL"),
        namespace=NAMESPACE,
    )
    proj = resp.result[0]
    print(f"      Before: priority = {proj.properties.get('priority', '<missing>')}")

    updated = manager.create_nodes({
        "label": "Project", "primary_key": "code",
        "code": "PROJ-RL",
        "priority": "high",
    }, namespace=NAMESPACE)
    resp = manager.upsert_nodes([updated])
    print(f"      Upserted: affected = {resp.execution.affected_count}")

    resp = manager.get_nodes(
        NodeSearch(label="Project", code="PROJ-RL"),
        namespace=NAMESPACE,
    )
    proj = resp.result[0]
    print(f"      After:  priority = {proj.properties.get('priority', '<missing>')}")

    # ── 3. Remove property by setting to None ─────────────────
    print("\n  [3] Remove property — PROJ-CV drops 'budget'")

    resp = manager.get_nodes(
        NodeSearch(label="Project", code="PROJ-CV"),
        namespace=NAMESPACE,
    )
    proj = resp.result[0]
    print(f"      Before: budget = {proj.properties.get('budget', '<missing>')}")

    updated = manager.create_nodes({
        "label": "Project", "primary_key": "code",
        "code": "PROJ-CV",
        "budget": None,
    }, namespace=NAMESPACE)
    resp = manager.upsert_nodes([updated])
    print(f"      Upserted: affected = {resp.execution.affected_count}")

    resp = manager.get_nodes(
        NodeSearch(label="Project", code="PROJ-CV"),
        namespace=NAMESPACE,
    )
    proj = resp.result[0]
    print(f"      After:  budget = {proj.properties.get('budget', '<missing>')}")

    # ── 4. Update relationship properties ─────────────────────
    print("\n  [4] Update relationship — Carol's WORKS_ON PROJ-NLP role")

    resp = manager.get_rels(
        RelationshipSearch(
            rel_type="WORKS_ON",
            start=NodeSearch(label="Researcher", email="carol@lab.ai"),
            end=NodeSearch(label="Project", code="PROJ-NLP"),
        ),
        namespace=NAMESPACE,
    )
    if resp.result:
        print(f"      Before: role = {resp.result[0].properties.get('role', '<missing>')}")

    # Upsert with updated property
    carol_ref = {"label": "Researcher", "primary_key": "email", "email": "carol@lab.ai", "namespace": NAMESPACE}
    nlp_ref   = {"label": "Project", "primary_key": "code", "code": "PROJ-NLP", "namespace": NAMESPACE}
    updated_rel = manager.create_rels({
        "start": carol_ref, "end": nlp_ref,
        "rel_type": "WORKS_ON",
        "role": "Co-Lead",
    })
    resp = manager.upsert_rels([updated_rel])
    ctx = resp.execution
    print(f"      Upserted: operation = {ctx.operation}, affected = {ctx.affected_count}")

    resp = manager.get_rels(
        RelationshipSearch(
            rel_type="WORKS_ON",
            start=NodeSearch(label="Researcher", email="carol@lab.ai"),
            end=NodeSearch(label="Project", code="PROJ-NLP"),
        ),
        namespace=NAMESPACE,
    )
    if resp.result:
        print(f"      After:  role = {resp.result[0].properties.get('role', '<missing>')}")

    # ── 5. Bulk update with execution context ─────────────────
    print("\n  [5] Bulk update — bump all Publication citations +10")

    resp = manager.get_nodes(
        NodeSearch(label="Publication"),
        namespace=NAMESPACE,
    )
    pubs = resp.result
    print(f"      Publications found: {len(pubs)}")

    bulk_nodes = []
    for p in pubs:
        updated = manager.create_nodes({
            "label": "Publication", "primary_key": "doi",
            "doi": p.properties["doi"],
            "citations": p.properties["citations"] + 10,
        }, namespace=NAMESPACE)
        bulk_nodes.append(updated)

    resp = manager.upsert_nodes(bulk_nodes)
    ctx = resp.execution
    print(f"      Operation ........ {ctx.operation}")
    print(f"      Affected ......... {ctx.affected_count}")

    # Verify
    resp = manager.get_nodes(
        NodeSearch(label="Publication"),
        namespace=NAMESPACE,
    )
    for n in resp.result:
        print(f"      {n.properties['doi']}: citations = {n.properties['citations']}")

    # ── Summary ───────────────────────────────────────────────
    print("\n" + "-" * WIDTH)
    print("  PASS  All updates completed")
    print("=" * WIDTH)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception as e:
        print(f"\n  FAIL  {e}")
        sys.exit(1)
