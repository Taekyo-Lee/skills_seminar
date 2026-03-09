# Skills Seminar
Hello Claude Code! You only need to care about Claude Code — ignore other agent platforms (e.g., Gemini CLI, Roo Code).

## Overview

This is a **demo project** that showcases how to build and use **agent skills** across multiple AI-assisted coding platforms. It serves as a teaching resource for an upcoming seminar, demonstrating practical integration of specialized skill modules.

### Platforms Covered

- **Gemini CLI** — skills defined in `.gemini/skills/`
- **Claude Code** — skills defined in `.claude/skills/`
- **Roo Code** — skills defined in `.roo/skills/`

## What are Claude Code Skills?

Claude Code skills are specialized modules that extend Claude Code with specific workflows, knowledge, or tools.

## Project Structure

| Path | Purpose |
|---|---|
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
