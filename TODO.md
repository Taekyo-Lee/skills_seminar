# TODO: Full CRUD Demo Scripts for Neo4j Knowledge Graph Skill

## Context

Create professional seminar demo scripts covering the full CRUD lifecycle using `a2g_neo4j`. Domain: **AI Research Lab** knowledge graph (Researchers, Projects, Publications, Technologies). Namespace: `seminar_demo`.

---

## Phase 1: Create Scripts (Claude Code)

Target: `.claude/skills/managing-neo4j-knowledge-graph/scripts/`

- [x] **1.1** Create `create_graph.py` — Build the knowledge graph
  - Clean slate with `delete_all(namespace="seminar_demo")`
  - Factory methods: `create_nodes()` single + batch, `create_rels()` batch
  - Upsert all to DB, show execution context
  - 14 nodes (4 Researchers, 3 Projects, 3 Publications, 4 Technologies)
  - ~16 relationships (WORKS_ON, AUTHORED, USES, CITES)

- [x] **1.2** Create `query_graph.py` — Search and read patterns
  - Get all nodes (no criteria), group by label
  - Simple `NodeSearch` (label, property, AND logic)
  - Q operators: `Q.gte()`, `Q.gt()`, `Q.contains()`
  - `NodeSearchUnion` OR logic (builder pattern)
  - `RelationshipSearch` with start/end node criteria
  - Execution context inspection

- [x] **1.3** Create `update_graph.py` — Update semantics via upsert
  - Modify existing property (before/after)
  - Add new property to existing node
  - Remove property by setting to `None`
  - Update relationship properties
  - Bulk update with execution context

- [x] **1.4** Create `teardown_graph.py` — Delete operations
  - Delete relationships by type
  - Delete relationships by start/end criteria
  - Delete nodes by criteria (DETACH DELETE)
  - Bulk cleanup `delete_all(namespace=...)`
  - Verification: confirm 0 nodes/rels

## Phase 2: Test Scripts

- [x] **2.1** Run `health_check.py` — verify connectivity
- [x] **2.2** Run `create_graph.py` — verify exit code 0
- [x] **2.3** Run `query_graph.py` — verify exit code 0
- [x] **2.4** Run `update_graph.py` — verify exit code 0
- [x] **2.5** Run `teardown_graph.py` — verify exit code 0
- [x] **2.6** Run `health_check.py` again — confirm empty graph

## Phase 3: Deploy to Other Platforms

- [x] **3.1** Copy 4 scripts to `.gemini/skills/managing-neo4j-knowledge-graph/scripts/`
- [x] **3.2** Copy 4 scripts to `.roo/skills/managing-neo4j-knowledge-graph/scripts/`

## Phase 4: Update SKILL.md (all 3 platforms)

- [x] **4.1** Update `.claude/skills/managing-neo4j-knowledge-graph/SKILL.md` — add all 4 new scripts
- [x] **4.2** Update `.gemini/skills/managing-neo4j-knowledge-graph/SKILL.md` — add all 4 new scripts
- [x] **4.3** Update `.roo/skills/managing-neo4j-knowledge-graph/SKILL.md` — add all 4 new scripts

---

## Script Pattern (from health_check.py)

```python
# /// script
# dependencies = [
#   "colorlog>=6.10.1",
#   "json5>=0.12.1",
#   "neo4j>=6.0.3",
#   "pydantic>=2.12.5",
#   "python-dateutil>=2.9.0.post0",
# ]
# ///

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "a2g_neo4j"))
from a2g_neo4j import Neo4jManager  # + NodeSearch, Q, etc.

NAMESPACE = "seminar_demo"
WIDTH = 52
```

## Reference Files

- Pattern template: `.claude/skills/.../scripts/health_check.py`
- Core API: `/home/jetlee/workspace/main/research/a2g_packages/src/a2g_neo4j/managers/base_neo4j_manager.py`
- Search schemas: `/home/jetlee/workspace/main/research/a2g_packages/src/a2g_neo4j/neo4j_schemas/entity_search_schemas.py`
- Q operators: `/home/jetlee/workspace/main/research/a2g_packages/src/a2g_neo4j/query_tools/query_operators.py`

## Verification Command

```bash
cd /home/jetlee/workspace/skills_seminar
uv run --native-tls --env-file .env .claude/skills/managing-neo4j-knowledge-graph/scripts/<script>.py
```
