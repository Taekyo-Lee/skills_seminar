---
name: jira-sprint-review
description: >-
  Use for ANY user request to generate a sprint review, sprint summary, sprint
  report, or sprint retrospective document. This skill orchestrates the
  jira-issue-manager skill to gather sprint data and produces a comprehensive
  sprint review markdown document. Do NOT use for individual issue operations
  or JQL queries — those should use jira-issue-manager or jira-jql-assistant.
---

# JIRA Sprint Review

This skill generates a comprehensive sprint review document by orchestrating the `jira-issue-manager` sub-skill. It is a **composite skill** — pure orchestration logic with no scripts of its own.

## Arguments

- `$0` — Sprint name (e.g., `"Sprint 23"`) or `current` for the active sprint
- `$1` — (optional) `--format brief` or `--format detailed` (default: `detailed`)

## Critical: Fresh Sub-Task Agents

Each sub-skill invocation MUST be a **fresh agent instance**. Do NOT reuse conversation context between sub-task steps. This ensures:

- Each step starts clean without accumulated context pollution
- Failures in one step don't cascade state into the next
- The orchestrator maintains control of the overall workflow

## Progress Tracking

Create and maintain a progress file at `sprint_review_progress.md` in the project root:

```markdown
# Sprint Review Progress: {sprint_name}

- [ ] Step 1: Gather sprint metadata
- [ ] Step 2: Categorize completed work
- [ ] Step 3: Identify carryover items
- [ ] Step 4: Analyze metrics
- [ ] Step 5: Generate review document
```

Update each checkbox as steps complete. If a step fails, mark it with `[x] FAILED: {reason}` and continue with available data.

## Workflow

### Step 1: Gather Sprint Metadata

**Sub-task**: Use the `jira-issue-manager` skill to search for all issues in the sprint.

**JQL** (for named sprint):
```
sprint = "{sprint_name}" AND project = {PROJECT_KEY}
```

**JQL** (for current sprint):
```
sprint IN openSprints() AND project = {PROJECT_KEY}
```

Request fields: `summary, status, issuetype, assignee, priority, story_points, created, updated, resolved`

**Capture**: total issue count, sprint name confirmation, date range.

### Step 2: Categorize Completed Work

**Sub-task**: Use the `jira-issue-manager` skill to search for completed issues.

**JQL**:
```
sprint = "{sprint_name}" AND project = {PROJECT_KEY} AND status = Done ORDER BY issuetype ASC, priority DESC
```

**Capture**: Group results by issue type (Stories, Bugs, Tasks). Record key, summary, assignee, priority for each.

### Step 3: Identify Carryover Items

**Sub-task**: Use the `jira-issue-manager` skill to search for incomplete issues.

**JQL**:
```
sprint = "{sprint_name}" AND project = {PROJECT_KEY} AND status != Done ORDER BY status ASC, priority DESC
```

**Capture**: Group by status (In Progress, Blocked, To Do). Record key, summary, assignee, status, priority.

### Step 4: Analyze Metrics

**No API call** — compute from data gathered in Steps 1-3:

- **Completion rate**: completed / total (percentage)
- **Carryover count**: total - completed
- **Blocked count**: issues with status = Blocked
- **By-type breakdown**: stories vs bugs vs tasks completed
- **Team contributions**: count completions per assignee

### Step 5: Generate Review Document

Assemble the final `sprint_review.md` in the project root using this template:

```markdown
# Sprint Review: {sprint_name}

**Date**: {current_date}
**Project**: {PROJECT_KEY}

## Summary

- Completed **{completed}** of **{total}** issues ({completion_pct}%)
- **{carryover}** items carried over
- **{blocked}** items blocked

## Completed Work

### Stories
| Key | Summary | Assignee | Priority |
|-----|---------|----------|----------|
| ... | ...     | ...      | ...      |

### Bugs
| Key | Summary | Assignee | Priority |
|-----|---------|----------|----------|
| ... | ...     | ...      | ...      |

### Tasks
| Key | Summary | Assignee | Priority |
|-----|---------|----------|----------|
| ... | ...     | ...      | ...      |

## Carryover Items

### In Progress
| Key | Summary | Assignee | Priority |
|-----|---------|----------|----------|
| ... | ...     | ...      | ...      |

### Blocked
| Key | Summary | Assignee | Priority |
|-----|---------|----------|----------|
| ... | ...     | ...      | ...      |

## Team Contributions

| Team Member | Completed | In Progress | Blocked |
|-------------|-----------|-------------|---------|
| ...         | ...       | ...         | ...     |

## Retrospective Talking Points

- {auto-generated observations based on data}
- Example: "Bug completion rate was high (X/Y) — team prioritized stability"
- Example: "N items blocked — review blockers in retro"
- Example: "{member} completed the most items ({count})"
```

## Error Handling

- **Empty sprint**: If no issues found, output "No issues found for sprint '{sprint_name}'. Verify the sprint name exists in project {PROJECT_KEY}."
- **API failure**: If a sub-task fails, log the error in progress file, skip that step, and continue. The final document should note which sections have incomplete data.
- **No completed items**: Still generate the document with empty Completed Work section and note "No items completed in this sprint."
