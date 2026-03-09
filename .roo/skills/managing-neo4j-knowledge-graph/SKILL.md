---
name: managing-neo4j-knowledge-graph
description: >-
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

## Available Scripts on Demand

All scripts are run from the **project root** directory with:

```bash
uv run --native-tls --env-file /home/jetlee/workspace/skills_seminar/.env .roo/skills/managing-neo4j-knowledge-graph/scripts/<script_name>.py
```

- **`.roo/skills/managing-neo4j-knowledge-graph/scripts/at_first_glance.py`** — Get a quick overview of the current Neo4j instance (node count, relationship count, and their details). Run this first to understand what's in the graph.
- **`.roo/skills/managing-neo4j-knowledge-graph/scripts/health_check.py`** — Verify connectivity to the Neo4j instance. Run this to confirm the database is reachable and credentials are valid.
