# Skills Seminar
Welcome! This document is for agent platforms that don't have a dedicated long-term memory file (e.g., Roo Code). If you are Gemini CLI or Claude Code, refer to your platform-specific file instead (`GEMINI.md` or `CLAUDE.md`).

## Overview

This is a **demo project** that showcases how to build and use **agent skills** across multiple AI-assisted coding platforms. It serves as a teaching resource for an upcoming seminar, demonstrating practical integration of specialized skill modules.

### Platforms Covered

- **Gemini CLI** — skills defined in `.gemini/skills/`
- **Claude Code** — skills defined in `.claude/skills/`
- **Roo Code** — skills defined in `.roo/skills/`

## Project Structure

| Path | Purpose |
|---|---|
| `GEMINI.md` | Project documentation and Gemini CLI context |
| `CLAUDE.md` | Project documentation and Claude Code context |
| `AGENT.md` | Project documentation for other agent platforms |
| `.gemini/skills/` | Skill definitions for **Gemini CLI** |
| `.claude/skills/` | Skill definitions for **Claude Code** |
| `.roo/skills/` | Skill definitions for **Roo Code** |

## Running Scripts

All skill scripts use `uv run --native-tls --env-file` with an env-file for necessary credentials or environment variables. Follow the instruction for running scripts for each skill.

## Available Skills

| Skill | Description |
|---|---|
| `managing-neo4j-knowledge-graph` | Manages Neo4j graph database operations (health, connectivity, querying, CRUD, schema inspection) |

---

**Note:** This document will be updated as we make progress in preparing for the seminar.
