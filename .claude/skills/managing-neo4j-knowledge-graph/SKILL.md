---
name: managing-neo4j-knowledge-graph
description:
  Use for ANY user request related to Neo4j or the graph database — including
  health checks, connectivity, querying, browsing,
  creating/reading/updating/deleting nodes or relationships, graph overview,
  schema inspection, or any other graph DB operation. This skill handles all
  interactions with the user's Neo4j instance and knowledge graph. Do NOT use
  for general educational questions about graph theory or Neo4j concepts
  unrelated to the user's instance.
---

# Managing Knowledge Graph

This skill performs CRUD (Create, Read, Update, Delete) operations on a Neo4j knowledge graph using the `a2g_neo4j` package.

## Prerequisites

- A running Neo4j instance
- The `a2g_neo4j` package (located at `/home/jetlee/workspace/main/research/a2g_packages/src/a2g_neo4j`)
- Environment variables for Neo4j connection (loaded from `/home/jetlee/workspace/main/research/a2g_packages/envs/.env`)

## Core Concepts

### Neo4jManager

`Neo4jManager` is the single entry point for all graph operations. It is initialized with a `namespace` for multi-tenant isolation.

### Entities

- **Node** — has a `label`, a `primary_key` (the property used for matching), and `properties` (dict)
- **Relationship** — connects two nodes with a `rel_type`, carries its own `properties`

### Search Criteria

- **NodeSearch** — defines query filters for nodes (label + property conditions)
- **RelationshipSearch** — defines query filters for relationships
- **Q operators** — fluent filtering: `Q.gte(30)`, `Q.contains("text")`, `Q.not_equal("value")`, etc.

## Operations

### Create / Update (Upsert)

Upsert semantics — creates if not exists, updates if exists (matched by primary key + namespace).

- `manager.upsert_nodes(nodes)` — upsert a list of Node objects
- `manager.upsert_rels(rels)` — upsert a list of Relationship objects

### Read

- `manager.get_nodes(criteria)` — retrieve nodes matching a NodeSearch
- `manager.get_rels(criteria)` — retrieve relationships matching a RelationshipSearch

### Delete

- `manager.delete_nodes(criteria)` — delete nodes matching criteria
- `manager.delete_rels(criteria)` — delete relationships matching criteria

## References

- `references/` — supplementary materials (e.g., schema docs, example data)

## Important Behavioral Rules

1. **Do NOT run health_check.py** unless the user explicitly asks about connectivity, health, or status. Go straight to the query.
2. **Do NOT use `python3 -c` or `uv run -c`** — they lack the required dependencies.
3. **All paths must be absolute** — relative paths cause files to be written to wrong locations.
4. All commands run from the project root: `<PROJECT_ROOT>`

## Running Ad-Hoc Queries

For any user request that is NOT an exact match for a pre-built script, follow these 3 steps:

**Step 1.** Write a temporary script to this absolute path:
`<PROJECT_ROOT>/.claude/skills/managing-neo4j-knowledge-graph/scripts/_adhoc.py`

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
from a2g_neo4j import Neo4jManager
from a2g_neo4j.neo4j_schemas.entity_search_schemas import NodeSearch, NodeSearchUnion, RelationshipSearch
from a2g_neo4j.query_tools import Q

NAMESPACE = "seminar_demo"
manager = Neo4jManager(log_level="warning")

# --- YOUR QUERY HERE ---
```

**Step 2.** Run it:
```bash
uv run --native-tls --env-file .env .claude/skills/managing-neo4j-knowledge-graph/scripts/_adhoc.py
```

**Step 3.** Delete the file after execution:
```bash
rm .claude/skills/managing-neo4j-knowledge-graph/scripts/_adhoc.py
```

### Common query patterns

```python
# Find nodes by label + property
resp = manager.get_nodes(NodeSearch(label="Project", status="active"), namespace=NAMESPACE)
for n in resp.result:
    print(f"{n.properties['code']}: {n.properties['title']}")

# Q operators (gte, gt, lt, lte, contains, ne, in_list, is_null, is_not_null)
resp = manager.get_nodes(NodeSearch(label="Researcher", h_index=Q.gte(10)), namespace=NAMESPACE)

# OR logic with NodeSearchUnion builder
search = NodeSearchUnion.builder().add(label="Researcher", role="PhD Student").add(label="Researcher", role="Postdoc").build()
resp = manager.get_nodes(search, namespace=NAMESPACE)

# Relationships by type + start/end criteria
resp = manager.get_rels(RelationshipSearch(rel_type="WORKS_ON", start=NodeSearch(label="Researcher", email="alice@lab.ai")), namespace=NAMESPACE)
for r in resp.result:
    print(f"{r.start.properties.get('name')} —[{r.rel_type}]→ {r.end.properties.get('code', r.end.properties.get('title'))}")

# Create + upsert a node
node = manager.create_nodes({"label": "Researcher", "primary_key": "email", "email": "eve@lab.ai", "name": "Dr. Eve Kim"}, namespace=NAMESPACE)
manager.upsert_nodes([node])

# Delete by criteria
manager.delete_nodes(NodeSearch(label="Technology", name="ROS2"), namespace=NAMESPACE)
```

## Available Scripts on Demand

Run from the project root (`<PROJECT_ROOT>`):

```bash
uv run --native-tls --env-file .env .claude/skills/managing-neo4j-knowledge-graph/scripts/<script_name>.py
```

- **`health_check.py`** — Verify connectivity. Only run when the user explicitly asks about health, status, or connectivity.
- **`create_graph.py`** — Build an AI Research Lab knowledge graph (14 nodes, 19 relationships).
- **`query_graph.py`** — Full query demo: NodeSearch, Q operators, NodeSearchUnion, RelationshipSearch.
- **`update_graph.py`** — Update demo: modify/add/remove properties, update relationships, bulk updates.
- **`teardown_graph.py`** — Delete demo: selective deletes, bulk cleanup, verification.
