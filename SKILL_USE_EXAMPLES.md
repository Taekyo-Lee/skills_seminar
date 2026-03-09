# Skill-Use Scenarios: `managing-neo4j-knowledge-graph`

Example user prompts that trigger the Neo4j knowledge graph skill. These demonstrate how natural-language requests map to specific CRUD operations and scripts.

---

## Health Check / Connectivity

| Prompt | Expected Behavior |
|---|---|
| "Is my Neo4j database running?" | Run `health_check.py` |
| "Check the graph database connection" | Run `health_check.py` |
| "Can you ping Neo4j?" | Run `health_check.py` |
| "What version of Neo4j am I running?" | Run `health_check.py`, report server version |

---

## Create (Build Graph)

| Prompt | Expected Behavior |
|---|---|
| "Build the demo knowledge graph" | Run `create_graph.py` |
| "Create the AI Research Lab graph with researchers and projects" | Run `create_graph.py` |
| "Set up the seminar demo data" | Run `create_graph.py` |
| "Add a new Researcher node for Dr. Eve Kim with email eve@lab.ai" | Use `create_nodes()` + `upsert_nodes()` |
| "Create a WORKS_ON relationship between Eve and PROJ-NLP" | Use `create_rels()` + `upsert_rels()` |
| "Insert 3 new Technology nodes: TensorFlow, JAX, MLflow" | Use `create_nodes()` batch + `upsert_nodes()` |

---

## Read (Query Graph)

| Prompt | Expected Behavior |
|---|---|
| "Run the query demo" | Run `query_graph.py` |
| "Show me all nodes in the graph" | `get_nodes(namespace=...)`, group by label |
| "How many nodes and relationships are in the graph?" | `get_nodes()` + `get_rels()`, report counts |
| "Find all active projects" | `NodeSearch(label="Project", status="active")` |
| "Who has an h-index of at least 10?" | `NodeSearch(label="Researcher", h_index=Q.gte(10))` |
| "Show publications with more than 100 citations" | `NodeSearch(label="Publication", citations=Q.gt(100))` |
| "Find projects that mention 'Model' in the title" | `NodeSearch(label="Project", title=Q.contains("Model"))` |
| "List all PhD Students or Postdocs" | `NodeSearchUnion` with builder pattern |
| "What does Alice work on?" | `RelationshipSearch(start=NodeSearch(email="alice@lab.ai"))` |
| "Who authored the robotics paper?" | `RelationshipSearch(rel_type="AUTHORED", end=NodeSearch(doi="10.1234/robot-2024"))` |
| "Which technologies does project NLP use?" | `RelationshipSearch(rel_type="USES", start=NodeSearch(code="PROJ-NLP"))` |

---

## Update

| Prompt | Expected Behavior |
|---|---|
| "Run the update demo" | Run `update_graph.py` |
| "Change Carol's h-index to 8" | `create_nodes()` with updated value + `upsert_nodes()` |
| "Add a priority field to PROJ-RL and set it to high" | `create_nodes()` with new property + `upsert_nodes()` |
| "Remove the budget from PROJ-CV" | `create_nodes()` with `budget=None` + `upsert_nodes()` |
| "Update Carol's role on PROJ-NLP from Contributor to Co-Lead" | `create_rels()` with updated property + `upsert_rels()` |
| "Bump all publication citation counts by 10" | Batch `create_nodes()` + `upsert_nodes()` loop |

---

## Delete (Teardown)

| Prompt | Expected Behavior |
|---|---|
| "Run the teardown demo" | Run `teardown_graph.py` |
| "Delete all CITES relationships" | `delete_rels(RelationshipSearch(rel_type="CITES"))` |
| "Remove Dan's authorship relationships" | `delete_rels(RelationshipSearch(rel_type="AUTHORED", start=...))` |
| "Delete all Technology nodes" | `delete_nodes(NodeSearch(label="Technology"))` |
| "Wipe the entire seminar_demo namespace" | `delete_all(namespace="seminar_demo")` |
| "Clean up the graph completely" | `delete_all(namespace="seminar_demo")` + verify 0/0 |

---

## How It Works: Script vs Ad-Hoc

The skill serves two types of requests:

| Request Type | How the Agent Handles It |
|---|---|
| "Run the query demo" | Runs pre-built `query_graph.py` directly |
| "Find all active projects" | Writes a temporary `_adhoc.py` script with the query, runs it, deletes it |

**Why ad-hoc scripts?** The `a2g_neo4j` package requires dependencies (`neo4j`, `pydantic`, etc.) declared in a `# /// script` header. Inline `python3 -c` or `uv run -c` commands can't declare these dependencies, so they fail. The skill instructs the agent to write a temp file with the proper header instead.

---

## Non-Matching Prompts (should NOT trigger the skill)

| Prompt | Why it doesn't match |
|---|---|
| "Explain what a graph database is" | General educational question |
| "What's the difference between Neo4j and PostgreSQL?" | Conceptual comparison, not instance-specific |
| "Write a Python function to sort a list" | Unrelated to Neo4j |
| "How does the PageRank algorithm work?" | Graph theory concept, not a DB operation |

---

## Full Lifecycle Demo (run in order)

```
1. "Check if Neo4j is up"                    --> health_check.py
2. "Build the demo knowledge graph"          --> create_graph.py
3. "Run the query demo"                      --> query_graph.py
4. "Run the update demo"                     --> update_graph.py
5. "Tear down the demo graph"                --> teardown_graph.py
6. "Verify the graph is empty"               --> health_check.py
```
