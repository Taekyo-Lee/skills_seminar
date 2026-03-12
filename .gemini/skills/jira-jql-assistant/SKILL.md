---
name: jira-jql-assistant
description: >-
  Use for ANY user request related to JIRA search, JQL queries, filters, or
  finding issues — including translating natural language to JQL, explaining JQL
  syntax, building complex queries, or helping with JIRA search filters. Do NOT
  use for creating, updating, transitioning, or managing JIRA issues — those
  requests should use the jira-issue-manager skill instead.
---

# JIRA JQL Assistant

This skill helps translate natural language into precise JIRA Query Language (JQL) and explains JQL syntax. It is a **knowledge-only skill** — no scripts, no API calls. It teaches the user JQL by always showing the query used.

## JQL Fundamentals

### Structure

A JQL query consists of **fields**, **operators**, **values**, and **keywords**:

```
field operator value [keyword field operator value ...]
```

### Operators

| Operator | Description | Example |
|---|---|---|
| `=` | Equals | `status = "In Progress"` |
| `!=` | Not equals | `status != Done` |
| `>`, `>=`, `<`, `<=` | Comparison | `priority >= High` |
| `~` | Contains text | `summary ~ "login bug"` |
| `!~` | Does not contain | `summary !~ "test"` |
| `IN` | In list | `status IN ("To Do", "In Progress")` |
| `NOT IN` | Not in list | `assignee NOT IN (alice, bob)` |
| `IS` | Is empty/null | `assignee IS EMPTY` |
| `IS NOT` | Is not empty | `fixVersion IS NOT EMPTY` |
| `WAS` | Previous value | `status WAS "In Progress"` |
| `CHANGED` | Field changed | `status CHANGED FROM "To Do" TO "In Progress"` |

### Keywords

| Keyword | Description |
|---|---|
| `AND` | Both conditions must be true |
| `OR` | Either condition can be true |
| `NOT` | Negation |
| `ORDER BY` | Sort results (`ASC` or `DESC`) |

### Functions

| Function | Description |
|---|---|
| `currentUser()` | The logged-in user |
| `now()` | Current date/time |
| `startOfDay()` | Start of today |
| `endOfDay()` | End of today |
| `startOfWeek()` | Start of current week |
| `endOfWeek()` | End of current week |
| `startOfMonth()` | Start of current month |
| `startOfYear()` | Start of current year |
| `membersOf("group")` | All members of a group |
| `updatedBy(user)` | Issues updated by user |
| `linkedIssue = KEY` | Issues linked to KEY |

### Relative Dates

Use offsets with date functions: `startOfDay(-7d)` = 7 days ago, `endOfWeek(+1w)` = end of next week.

Shorthand units: `m` (minutes), `h` (hours), `d` (days), `w` (weeks).

## Common Fields Mapping

| Human Term | JQL Field |
|---|---|
| "assigned to me" | `assignee = currentUser()` |
| "unassigned" | `assignee IS EMPTY` |
| "my team's issues" | `assignee IN membersOf("team-name")` |
| "bugs" | `issuetype = Bug` |
| "stories" | `issuetype = Story` |
| "tasks" | `issuetype = Task` |
| "epics" | `issuetype = Epic` |
| "high priority" | `priority = High` |
| "critical/urgent" | `priority IN (Critical, Highest)` |
| "open" / "not done" | `status != Done` |
| "in progress" | `status = "In Progress"` |
| "blocked" | `status = Blocked` |
| "this sprint" | `sprint IN openSprints()` |
| "last sprint" | `sprint IN closedSprints()` |
| "overdue" | `due < now() AND status != Done` |
| "created today" | `created >= startOfDay()` |
| "updated this week" | `updated >= startOfWeek()` |
| "no fix version" | `fixVersion IS EMPTY` |
| "has comments" | `comment IS NOT EMPTY` |

## Query Patterns by Use Case

### My Work

```
assignee = currentUser() AND status != Done ORDER BY priority DESC, updated DESC
```

### Sprint Issues

```
project = {PROJECT_KEY} AND sprint IN openSprints() ORDER BY rank ASC
```

### Stale Tickets (no update in 14 days)

```
project = {PROJECT_KEY} AND status != Done AND updated <= startOfDay(-14d) ORDER BY updated ASC
```

### Recently Resolved (last 7 days)

```
project = {PROJECT_KEY} AND status = Done AND resolved >= startOfDay(-7d) ORDER BY resolved DESC
```

### Blockers and Critical Issues

```
project = {PROJECT_KEY} AND priority IN (Critical, Highest, Blocker) AND status != Done ORDER BY priority DESC
```

### Bugs Assigned to Me, Overdue

```
assignee = currentUser() AND issuetype = Bug AND due < now() AND status != Done ORDER BY due ASC
```

### Unassigned in Current Sprint

```
project = {PROJECT_KEY} AND sprint IN openSprints() AND assignee IS EMPTY ORDER BY priority DESC
```

### Issues Created vs Resolved (This Week)

```
project = {PROJECT_KEY} AND created >= startOfWeek() ORDER BY created DESC
project = {PROJECT_KEY} AND resolved >= startOfWeek() ORDER BY resolved DESC
```

### Issues by Label

```
project = {PROJECT_KEY} AND labels = "frontend" AND status != Done ORDER BY priority DESC
```

### Issues with No Epic

```
project = {PROJECT_KEY} AND "Epic Link" IS EMPTY AND issuetype != Epic AND status != Done
```

## Output Formatting Rules

1. **Always show the JQL** — even if you cannot execute it. This teaches the user JQL.
2. **Format results as markdown tables** when presenting hypothetical or example output.
3. **Suggest refinements** — after providing a query, offer 1-2 variants (e.g., add date range, narrow by component).
4. **Explain non-obvious syntax** — if using `WAS`, `CHANGED`, functions, or relative dates, briefly explain what they do.

## Behavioral Rules

1. **Show JQL even if you cannot execute it.** The purpose of this skill is to teach JQL, not to run queries.
2. **For ambiguous requests, suggest variants.** If the user says "find my bugs," offer both "assigned to me" and "reported by me" versions.
3. **Redirect mutations to `jira-issue-manager`.** If the user asks to create, update, transition, or delete an issue, tell them to use the `jira-issue-manager` skill instead (or invoke it if available).
4. **Use project key placeholder.** Use `{PROJECT_KEY}` in queries unless the user specifies a project. If the env var `JIRA_PROJECT_KEY` is known, use that.
5. **Prefer readable JQL.** Use quoted strings for multi-word values. Use `ORDER BY` for useful default sorting.
