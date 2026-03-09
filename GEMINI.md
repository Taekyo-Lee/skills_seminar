# Skills Seminar
Hello Gemini-CLI! You only need to care about Gemini CLI — ignore other agent platforms (e.g., Roo Code, Claude Code).

## Overview

This is a **demo project** that showcases how to build and use **agent skills** across multiple AI-assisted coding platforms. It serves as a teaching resource for an upcoming seminar, demonstrating practical integration of specialized skill modules.

### Platforms Covered

- **Gemini CLI** — skills defined in `.gemini/skills/`
- **Claude Code** — skills defined in `.claude/skills/`
- **Roo Code** — skills defined in `.roo/skills/`

## What are Gemini Skills?

Gemini skills are specialized modules that extend the Gemini CLI with specific workflows, knowledge, or tools.

## Project Structure

| Path | Purpose |
|---|---|
| `GEMINI.md` | Project documentation and Gemini CLI context |
| `CLAUDE.md` | Project documentation and Claude Code context |
| `AGENT.md` | Project documentation for other agent platforms |
| `env.example` | Shared environment variables for all skills |
| `.gemini/skills/` | Skill definitions for **Gemini CLI** |
| `.claude/skills/` | Skill definitions for **Claude Code** |
| `.roo/skills/` | Skill definitions for **Roo Code** |

## Running Scripts

All skill scripts use `uv run --native-tls --env-file .env` with the shared `.env` at the project root. Copy `env.example` to `.env` and fill in your credentials. Follow the instruction for running scripts for each skill.

### Script Execution Working Directory

Each platform runs skill scripts from a different working directory. This affects how paths (e.g., to `.env` or script files) are specified in each skill's `SKILL.md`:

- **Claude Code** — runs scripts from the **skill directory** itself (e.g., `.claude/skills/<skill-name>/`), so relative paths like `../../../.env` are used.
- **Gemini CLI** — runs scripts from the **project root**, so `.env` is referenced directly and script paths use absolute paths.
- **Roo Code** — runs scripts from the **project root**, same as Gemini CLI.

## Available Skills

| Skill | Description |
|---|---|
| `managing-neo4j-knowledge-graph` | Manages Neo4j graph database operations (health, connectivity, querying, CRUD, schema inspection) |

---

**Note:** This document will be updated as we make progress in preparing for the seminar.
