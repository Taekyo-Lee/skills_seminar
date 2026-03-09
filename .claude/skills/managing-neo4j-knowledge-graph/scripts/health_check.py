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

try:
    graph_manager = Neo4jManager(log_level="info")
    print(f"Currently Neo4j is healthy.")
except Exception as e:
    print(f"Error connecting to Neo4j: {e}")
    sys.exit(1)
