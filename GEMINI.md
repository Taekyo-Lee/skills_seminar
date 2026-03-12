# Skill-Use Scenarios: JIRA Skills (3 Levels)

Example user prompts that trigger each JIRA skill. These demonstrate how natural-language requests map to specific skill invocations.

---

## Level 1: `jira-jql-assistant` (Simple Skill)

### Query Building

| Prompt | Expected Behavior |
|---|---|
| "Find all high-priority bugs assigned to me that are overdue" | Show JQL: `assignee = currentUser() AND issuetype = Bug AND priority = High AND due < now() AND status != Done` |
| "How do I find all unresolved bugs from last week?" | Show JQL: `issuetype = Bug AND status != Done AND created >= startOfWeek(-1w) AND created <= endOfWeek(-1w)` |
| "Show me issues in the current sprint" | Show JQL: `project = {PROJECT_KEY} AND sprint IN openSprints()` |
| "What's the JQL for finding stale tickets?" | Explain syntax + show: `updated <= startOfDay(-14d) AND status != Done` |
| "Find tickets assigned to Alice or Bob" | Show JQL: `assignee IN (alice, bob) AND status != Done` |

### Syntax Help

| Prompt | Expected Behavior |
|---|---|
| "What does the ~ operator do in JQL?" | Explain contains/text search operator with examples |
| "How do I use date functions in JQL?" | Explain `startOfDay()`, `endOfWeek()`, relative offsets |
| "What's the difference between WAS and CHANGED?" | Explain historical operators with examples |

### Non-Matching Prompts (should NOT trigger this skill)

| Prompt | Why it doesn't match |
|---|---|
| "Create a bug ticket for the login issue" | Mutation → `jira-issue-manager` |
| "Move DEMO-1 to In Progress" | Transition → `jira-issue-manager` |
| "Generate a sprint review" | Sprint review → `jira-sprint-review` |

---

## Level 2: `jira-issue-manager` (Bundled Skill)

### Health Check

| Prompt | Expected Behavior |
|---|---|
| "Check my JIRA connection" | Run `health_check.py` |
| "Is JIRA accessible?" | Run `health_check.py` |
| "Verify my API token works" | Run `health_check.py` |

### Search

| Prompt | Expected Behavior |
|---|---|
| "Search for all open bugs in DEMO" | Run `search_issues.py --jql "project = DEMO AND issuetype = Bug AND status != Done"` |
| "Show me my assigned tickets" | Run `search_issues.py --jql "assignee = currentUser() AND status != Done"` |

### Create

| Prompt | Expected Behavior |
|---|---|
| "Create a bug ticket for the login page timeout issue and assign it to Alice" | Run `create_issue.py` with config JSON |
| "Make a new story: Implement dark mode" | Run `create_issue.py` with `issuetype: Story` |
| "Add a task to update the README" | Run `create_issue.py` with `issuetype: Task` |

### Update

| Prompt | Expected Behavior |
|---|---|
| "Change the priority of DEMO-5 to Critical" | Run `update_issue.py --issue-key DEMO-5 --fields '{"priority":{"name":"Critical"}}'` |
| "Add the label 'frontend' to DEMO-3" | Run `update_issue.py` with labels field |
| "Update the summary of DEMO-1" | Run `update_issue.py` with summary field |

### Transition

| Prompt | Expected Behavior |
|---|---|
| "Move DEMO-1 to In Progress" | Run `transition_issue.py --issue-key DEMO-1 --transition "In Progress"` |
| "Mark DEMO-7 as Done" | Run `transition_issue.py --issue-key DEMO-7 --transition "Done"` |
| "Start working on DEMO-3" | Run `transition_issue.py` with "In Progress" |

### Ad-Hoc Operations

| Prompt | Expected Behavior |
|---|---|
| "Add a comment to DEMO-1 saying 'Fixed in latest deploy'" | Write `_adhoc.py` with comment API call, run, delete |
| "List all available transitions for DEMO-5" | Write `_adhoc.py` with transitions GET, run, delete |

### Non-Matching Prompts (should NOT trigger this skill)

| Prompt | Why it doesn't match |
|---|---|
| "What's the JQL syntax for date ranges?" | JQL syntax → `jira-jql-assistant` |
| "Generate a sprint review" | Sprint review → `jira-sprint-review` |

---

## Level 3: `jira-sprint-review` (Composite Skill)

### Sprint Review

| Prompt | Expected Behavior |
|---|---|
| "Generate a sprint review for our current sprint" | Run full 5-step workflow → produce `sprint_review.md` |
| "Create a sprint summary for Sprint 23" | Run workflow with `sprint_name = "Sprint 23"` |
| "Sprint review report for the last sprint" | Run workflow with `sprint IN closedSprints()` |
| "Give me a brief sprint summary" | Run workflow with `--format brief` |

### Non-Matching Prompts (should NOT trigger this skill)

| Prompt | Why it doesn't match |
|---|---|
| "Find all issues in Sprint 23" | Simple search → `jira-issue-manager` or `jira-jql-assistant` |
| "Create a bug ticket" | Create → `jira-issue-manager` |
| "What's the JQL for sprint queries?" | JQL help → `jira-jql-assistant` |

---

## How It Works: Skill Routing

The three skills form a clear routing hierarchy:

| Request Type | Skill | Why |
|---|---|---|
| JQL syntax, query building, search help | `jira-jql-assistant` | Knowledge-only, no API calls needed |
| CRUD operations, health checks, issue management | `jira-issue-manager` | Scripts interact with JIRA REST API |
| Sprint review / summary / report generation | `jira-sprint-review` | Orchestrates multiple `jira-issue-manager` calls |

---

## Full Demo Sequence (run in order)

```
1. "How do I find all bugs assigned to me?"              --> jira-jql-assistant (shows JQL)
2. "Check my JIRA connection"                            --> jira-issue-manager (health_check.py)
3. "Create a bug: Login page timeout, assign to Alice"   --> jira-issue-manager (create_issue.py)
4. "Search for all open issues in DEMO"                  --> jira-issue-manager (search_issues.py)
5. "Move DEMO-1 to In Progress"                         --> jira-issue-manager (transition_issue.py)
6. "Generate a sprint review for the current sprint"     --> jira-sprint-review (orchestrator)
```
