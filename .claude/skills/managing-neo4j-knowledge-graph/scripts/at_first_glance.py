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

# Make a2g_neo4j importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "a2g_neo4j"))

from a2g_neo4j import Neo4jManager
from a2g_neo4j.sample_graphs.A2G_graph import tech_vision_nodes, tech_vision_rels

graph_manager = Neo4jManager(log_level="info")

if not len(graph_manager.get_nodes().result):
    graph_manager.upsert_nodes(tech_vision_nodes)
if not len(graph_manager.get_rels().result):
    graph_manager.upsert_rels(tech_vision_rels)

all_nodes = graph_manager.get_nodes().result
all_rels = graph_manager.get_rels().result

num_nodes = len(all_nodes)
num_rels = len(all_rels)



print(f"Currently there are {num_nodes} nodes, {num_rels} relationships")
print()
print(f"Nodes: \n{all_nodes}")
print()
print(f"Relationships: \n{all_rels}")
