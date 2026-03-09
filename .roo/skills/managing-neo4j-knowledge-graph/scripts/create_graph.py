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
Create Graph — builds an AI Research Lab knowledge graph from scratch.

Demonstrates:
  - Clean slate with delete_all(namespace=...)
  - Factory methods: create_nodes() single + batch, create_rels() batch
  - Upsert all to DB with execution context

Domain: 4 Researchers, 3 Projects, 3 Publications, 4 Technologies
        19 relationships (WORKS_ON, AUTHORED, USES, CITES)

Exit codes:
  0  Graph created successfully
  1  Error occurred
"""

import sys

from a2g_neo4j import Neo4jManager

NAMESPACE = "seminar_demo"
WIDTH = 52


def run() -> int:
    print("=" * WIDTH)
    print("  Create Graph — AI Research Lab")
    print("=" * WIDTH)

    manager = Neo4jManager(log_level="warning")

    # ── 1. Clean slate ─────────────────────────────────────────
    print("\n  [1] Clean slate")
    result = manager.delete_all(namespace=NAMESPACE)
    print(f"      Deleted {result['nodes_deleted']} nodes, "
          f"{result['relationships_deleted']} rels")

    # ── 2. Create single node (factory demo) ──────────────────
    print("\n  [2] Create single node (factory demo)")
    lead = manager.create_nodes({
        "label": "Researcher", "primary_key": "email",
        "email": "alice@lab.ai",
        "name": "Dr. Alice Chen",
        "role": "Principal Investigator",
        "h_index": 42,
        "years_active": 15,
    }, namespace=NAMESPACE)
    print(f"      {lead.label}: {lead.properties['name']}")

    # ── 3. Create batch nodes (factory demo) ──────────────────
    print("\n  [3] Create batch nodes (factory demo)")

    researcher_configs = [
        {"label": "Researcher", "primary_key": "email",
         "email": "bob@lab.ai", "name": "Dr. Bob Martinez",
         "role": "Senior Researcher", "h_index": 28, "years_active": 10},
        {"label": "Researcher", "primary_key": "email",
         "email": "carol@lab.ai", "name": "Carol Park",
         "role": "PhD Student", "h_index": 5, "years_active": 3},
        {"label": "Researcher", "primary_key": "email",
         "email": "dan@lab.ai", "name": "Dan Okafor",
         "role": "Postdoc", "h_index": 12, "years_active": 6},
    ]

    project_configs = [
        {"label": "Project", "primary_key": "code",
         "code": "PROJ-NLP", "title": "Large Language Model Safety",
         "status": "active", "budget": 500000, "year": 2024},
        {"label": "Project", "primary_key": "code",
         "code": "PROJ-CV", "title": "Medical Image Analysis",
         "status": "active", "budget": 350000, "year": 2023},
        {"label": "Project", "primary_key": "code",
         "code": "PROJ-RL", "title": "Autonomous Robotics",
         "status": "planning", "budget": 200000, "year": 2025},
    ]

    publication_configs = [
        {"label": "Publication", "primary_key": "doi",
         "doi": "10.1234/safety-2024", "title": "Alignment Techniques for LLMs",
         "venue": "NeurIPS", "year": 2024, "citations": 87},
        {"label": "Publication", "primary_key": "doi",
         "doi": "10.1234/medical-2023", "title": "Deep Learning in Radiology",
         "venue": "Nature Medicine", "year": 2023, "citations": 156},
        {"label": "Publication", "primary_key": "doi",
         "doi": "10.1234/robot-2024", "title": "Sim-to-Real Transfer Learning",
         "venue": "ICRA", "year": 2024, "citations": 34},
    ]

    technology_configs = [
        {"label": "Technology", "primary_key": "name",
         "name": "PyTorch", "category": "Framework", "version": "2.3"},
        {"label": "Technology", "primary_key": "name",
         "name": "Transformers", "category": "Architecture", "version": "4.40"},
        {"label": "Technology", "primary_key": "name",
         "name": "CUDA", "category": "Hardware", "version": "12.4"},
        {"label": "Technology", "primary_key": "name",
         "name": "ROS2", "category": "Framework", "version": "humble"},
    ]

    all_configs = researcher_configs + project_configs + publication_configs + technology_configs
    batch_nodes = manager.create_nodes(all_configs, namespace=NAMESPACE)
    for n in batch_nodes:
        print(f"      {n.label}: {n.properties.get(n.primary_key)}")

    # ── 4. Create relationships (factory demo) ────────────────
    print("\n  [4] Create relationships (factory demo)")

    # Short-hand node refs (must include namespace for proper scoping)
    ns = NAMESPACE
    alice = {"label": "Researcher", "primary_key": "email", "email": "alice@lab.ai", "namespace": ns}
    bob   = {"label": "Researcher", "primary_key": "email", "email": "bob@lab.ai", "namespace": ns}
    carol = {"label": "Researcher", "primary_key": "email", "email": "carol@lab.ai", "namespace": ns}
    dan   = {"label": "Researcher", "primary_key": "email", "email": "dan@lab.ai", "namespace": ns}

    nlp = {"label": "Project", "primary_key": "code", "code": "PROJ-NLP", "namespace": ns}
    cv  = {"label": "Project", "primary_key": "code", "code": "PROJ-CV", "namespace": ns}
    rl  = {"label": "Project", "primary_key": "code", "code": "PROJ-RL", "namespace": ns}

    pub_safe = {"label": "Publication", "primary_key": "doi", "doi": "10.1234/safety-2024", "namespace": ns}
    pub_med  = {"label": "Publication", "primary_key": "doi", "doi": "10.1234/medical-2023", "namespace": ns}
    pub_rob  = {"label": "Publication", "primary_key": "doi", "doi": "10.1234/robot-2024", "namespace": ns}

    pytorch      = {"label": "Technology", "primary_key": "name", "name": "PyTorch", "namespace": ns}
    transformers = {"label": "Technology", "primary_key": "name", "name": "Transformers", "namespace": ns}
    cuda         = {"label": "Technology", "primary_key": "name", "name": "CUDA", "namespace": ns}
    ros2         = {"label": "Technology", "primary_key": "name", "name": "ROS2", "namespace": ns}

    rel_configs = [
        # WORKS_ON  (Researcher -> Project)
        {"start": alice, "end": nlp, "rel_type": "WORKS_ON", "role": "Lead"},
        {"start": bob,   "end": nlp, "rel_type": "WORKS_ON", "role": "Co-Lead"},
        {"start": carol, "end": nlp, "rel_type": "WORKS_ON", "role": "Contributor"},
        {"start": alice, "end": cv,  "rel_type": "WORKS_ON", "role": "Advisor"},
        {"start": bob,   "end": cv,  "rel_type": "WORKS_ON", "role": "Lead"},
        {"start": dan,   "end": rl,  "rel_type": "WORKS_ON", "role": "Lead"},
        {"start": carol, "end": rl,  "rel_type": "WORKS_ON", "role": "Contributor"},

        # AUTHORED  (Researcher -> Publication)
        {"start": alice, "end": pub_safe, "rel_type": "AUTHORED", "contribution": "first_author"},
        {"start": bob,   "end": pub_safe, "rel_type": "AUTHORED", "contribution": "co_author"},
        {"start": bob,   "end": pub_med,  "rel_type": "AUTHORED", "contribution": "first_author"},
        {"start": dan,   "end": pub_rob,  "rel_type": "AUTHORED", "contribution": "first_author"},
        {"start": carol, "end": pub_rob,  "rel_type": "AUTHORED", "contribution": "co_author"},

        # USES  (Project -> Technology)
        {"start": nlp, "end": pytorch,      "rel_type": "USES"},
        {"start": nlp, "end": transformers, "rel_type": "USES"},
        {"start": cv,  "end": pytorch,      "rel_type": "USES"},
        {"start": cv,  "end": cuda,         "rel_type": "USES"},
        {"start": rl,  "end": ros2,         "rel_type": "USES"},
        {"start": rl,  "end": pytorch,      "rel_type": "USES"},

        # CITES  (Publication -> Publication)
        {"start": pub_safe, "end": pub_med, "rel_type": "CITES"},
    ]

    rels = manager.create_rels(rel_configs)
    print(f"      Created {len(rels)} relationship objects")

    # ── 5. Upsert to database ─────────────────────────────────
    print("\n  [5] Upsert to database")

    # Upsert all nodes first (lead + batch)
    all_nodes_list = [lead] + batch_nodes
    node_resp = manager.upsert_nodes(all_nodes_list)
    print(f"      Nodes  — affected: {node_resp.execution.affected_count}")

    # Upsert relationships
    rel_resp = manager.upsert_rels(rels)
    ctx = rel_resp.execution
    print(f"      Rels   — operation: {ctx.operation}, affected: {ctx.affected_count}")

    # ── 6. Verify ─────────────────────────────────────────────
    print("\n  [6] Verify")
    all_nodes = manager.get_nodes(namespace=NAMESPACE)
    all_rels  = manager.get_rels(namespace=NAMESPACE)
    n_count = len(all_nodes.result)
    r_count = len(all_rels.result)
    print(f"      Nodes .............. {n_count}")
    print(f"      Relationships ...... {r_count}")

    # ── Summary ───────────────────────────────────────────────
    print("\n" + "-" * WIDTH)
    if n_count >= 14 and r_count >= 19:
        print(f"  PASS  Graph created ({n_count} nodes, {r_count} rels)")
    else:
        print(f"  WARN  Expected >=14 nodes / >=19 rels, "
              f"got {n_count} / {r_count}")
    print("=" * WIDTH)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception as e:
        print(f"\n  FAIL  {e}")
        sys.exit(1)
