# TODO: JIRA Skills (3 Levels) for Seminar Demo

## Context

Three JIRA-based skills at increasing complexity, demonstrating what agent skills are and why they matter. Replaces the Neo4j knowledge graph skill.

---

## Phase 1: Foundation

- [x] Create and switch to `jira` branch
- [x] Remove neo4j skill directories (all 3 platforms)
- [x] Update `env.example` — replace Neo4j vars with JIRA vars

## Phase 2: Level 1 — `jira-jql-assistant` (Simple Skill)

- [x] Create SKILL.md for Claude Code
- [x] Adapt and copy to Gemini CLI and Roo Code

## Phase 3: Level 2 — `jira-issue-manager` (Bundled Skill)

- [x] Create `health_check.py` — verify connectivity, auth, project access, permissions
- [x] Create `search_issues.py` — search via JQL with formatted table output
- [x] Create `create_issue.py` — create issue from JSON config
- [x] Create `update_issue.py` — update fields on existing issue
- [x] Create `transition_issue.py` — move issue through workflow
- [x] Create SKILL.md for Claude Code
- [x] Copy scripts + SKILL.md to Gemini CLI and Roo Code

## Phase 4: Level 3 — `jira-sprint-review` (Composite Skill)

- [x] Create SKILL.md for Claude Code
- [x] Adapt and copy to Gemini CLI and Roo Code

## Phase 5: Documentation & Cleanup

- [x] Update CLAUDE.md — replace neo4j with 3 JIRA skills
- [x] Update AGENT.md
- [x] Update GEMINI.md
- [x] Update SKILL_USE_EXAMPLES.md with JIRA scenarios
- [x] Update TODO.md
- [x] Update `.claude/settings.local.json` — allowlist JIRA scripts

---

## Verification

1. **Level 1**: Ask *"How do I find all unresolved bugs from last week?"* → agent produces JQL, no scripts
2. **Level 2**: Run `health_check.py` → verify connectivity. Ask agent to create an issue → verify in JIRA
3. **Level 3**: Ask *"Generate a sprint review for the current sprint"* → agent dispatches sub-tasks → `sprint_review.md`
