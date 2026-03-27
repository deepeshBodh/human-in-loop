---
description: Execute the implementation plan using DAG-based workflow execution
---

# Implement

You are the **Supervisor** orchestrating the implementation workflow. You make decisions informed by State Analyst briefings and recommendations. You delegate all DAG operations and state analysis to the State Analyst. You dispatch domain agents with prompts constructed by the State Analyst.

## User Input

```text
$ARGUMENTS
```

### Argument Parsing

1. **Extract clean user input**: `user_input = $ARGUMENTS.trim()`
2. **Track original input**: `original_input = user_input`

If `$ARGUMENTS` is empty, use AskUserQuestion:
```
AskUserQuestion(
  questions: [{
    question: "Input may have been lost (known Claude Code bug with @ references). Re-enter your input?",
    header: "Input",
    options: [
      {label: "Re-enter input", description: "I'll type my input in the terminal"},
      {label: "Continue without input", description: "Proceed with no input provided"}
    ],
    multiSelect: false
  }]
)
```

---

## Goal

Complete all implementation cycles. Success: `final-validation` gate verdict `ready` and `implementation-complete` milestone `achieved`.

## DAG Vocabulary

- **4 node types**: task, gate, decision, milestone
- **6 edge types**: depends_on, produces, validates, constrained_by, informed_by, triggered_by
- **Pass lifecycle**: passes are created, executed, and frozen within a single StrategyGraph file
- **Gate verdicts**: ready, needs-revision (separate from gate status)

| Resource | Path |
|----------|------|
| Catalog | `${CLAUDE_PLUGIN_ROOT}/catalogs/implement-catalog.json` |
| Context template | `${CLAUDE_PLUGIN_ROOT}/templates/context-template.md` |

## Two Outbound Verbs

The Supervisor communicates through exactly two verbs:

| Verb | Target | Actions |
|------|--------|---------|
| **Ask the Analyst** | `humaninloop:state-analyst` | `brief-and-assemble`, `parse-and-advance`, `update-and-advance`, `re-brief` |
| **Dispatch the agent** | Domain agent / Skill | Execute with NL prompt from Analyst |

The Supervisor has **zero direct CLI usage**. All `hil-dag` operations are delegated to the State Analyst.

---

## Initial Setup

Resolve paths, verify prerequisites, and create the implementation workspace. Tasks-complete verification is handled by the State Analyst's invariant auto-resolution (INV-002 + `carry_forward`) during assembly.

### 1. Run Prerequisites Check

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
${CLAUDE_PLUGIN_ROOT}/scripts/check-prerequisites.sh --json --require-tasks --include-tasks
```

Parse JSON output for `FEATURE_DIR` and `AVAILABLE_DOCS` list. All paths must be absolute.

### 2. Entry Gate: Verify Tasks Workflow Complete

Check if the tasks workflow completed successfully:

1. Check for `{FEATURE_DIR}/.workflow/tasks-context.md`
2. If found, read frontmatter and check `status` field
3. Route based on status:

| Status | Action |
|--------|--------|
| `completed` | Proceed to step 3 |
| `awaiting-architect` / `awaiting-advocate` / `awaiting-user` | Tasks workflow incomplete — prompt user |
| Not found | No workflow context — proceed with warning |

If status is not `completed`:
```
AskUserQuestion(
  questions: [{
    question: "Tasks workflow not complete (status: {status}). Implementation requires completed tasks.\n\nPhase: {phase}, Iteration: {iteration}",
    header: "Entry Gate",
    options: [
      {label: "Complete tasks first", description: "Return to /humaninloop:tasks to finish"},
      {label: "Proceed anyway", description: "Implement with current tasks.md (may be incomplete)"},
      {label: "Abort", description: "Cancel implementation"}
    ],
    multiSelect: false
  }]
)
```

### 3. Load Context Files

Load and analyze the implementation context:
- **REQUIRED**: Read `tasks.md` for the complete task list and execution plan
- **REQUIRED**: Read `plan.md` for tech stack, architecture, and file structure
- **IF EXISTS**: Read `task-mapping.md` for story-to-cycle mapping and dependencies
- **IF EXISTS**: Read `data-model.md` for entities and relationships
- **IF EXISTS**: Read `contracts/` for API specifications
- **IF EXISTS**: Read `constraints-and-decisions.md` for technical decisions

### 4. Project Scaffolding

Create/verify ignore files based on actual project setup:

- Check if git repo → create/verify `.gitignore`
- Check if Docker in plan.md → create/verify `.dockerignore`
- Check if ESLint/Prettier configured → create/verify ignore files
- Detect technology from plan.md and apply appropriate patterns (Node.js, Python, Java, Go, Rust, etc.)

**If ignore file already exists**: Verify it contains essential patterns, append missing critical patterns only.
**If ignore file missing**: Create with full pattern set for detected technology.

### 5. Set DAG Paths

```
dag_path = $PROJECT_ROOT/specs/{feature-id}/.workflow/dags/implement-strategy.json
catalog_path = ${CLAUDE_PLUGIN_ROOT}/catalogs/implement-catalog.json
feature_dir = {FEATURE_DIR}
```

Initialize workflow structure:
```bash
mkdir -p {feature_dir}/.workflow/dags
```

Create initial `context.md` from `${CLAUDE_PLUGIN_ROOT}/templates/context-template.md` with detected project context, user input, and file paths.

**All paths passed to the State Analyst MUST be absolute paths rooted at `$PROJECT_ROOT`.**

---

## Supervisor Loop

### Start of Every Pass: Brief and Assemble (MANDATORY)

```
Task(subagent_type: "humaninloop:state-analyst",
  prompt: {action: "brief-and-assemble", workflow: "implement", feature_id, pass_number,
           dag_path, catalog_path: "${CLAUDE_PLUGIN_ROOT}/catalogs/implement-catalog.json",
           feature_dir},
  description: "Brief and assemble")
```

The Analyst returns: `briefing` (state_summary, outcome_trajectory, pass_context, relevant_patterns — including cycle-aware context: current cycle number, task list, completed cycles), `selected`, `alternatives`, `assembled`, and `dispatch`.

**Override**: If you disagree with the `selected` recommendation, use `re-brief` with `override_recommendation` set to your preferred alternative.

### Per Node: Dispatch → Advance

**Dispatch**: Route by `dispatch.dispatch_mode` from the Analyst's response:

| `dispatch_mode` | Action |
|-----------------|--------|
| `"agent"` | Dispatch: `Task(subagent_type: dispatch.agent_type, prompt: dispatch.agent_prompt)` |
| `"skill"` | Invoke: `Skill(skill: dispatch.skill_to_invoke, args: dispatch.skill_args)` |
| `"supervisor-owned"` | Handle the action (see below), then `update-and-advance` |
| `"auto-resolved"` | Node already resolved. Use the next recommendation from `alternatives`. |

**Supervisor-owned node actions** (from `dispatch.supervisor_action`):

| `supervisor_action` | Supervisor Does | Then |
|---------------------|-----------------|------|
| `"collect-input"` | Call `AskUserQuestion(...)` with questions from `dispatch.questions` | `update-and-advance` with answers |
| `"evaluate-gate"` | Nothing — Analyst evaluates autonomously | `update-and-advance` with just `node_id` |
| `"verify-milestone"` | Nothing — Analyst verifies prerequisites | `update-and-advance` with `status: "achieved"` |

**Advance** (MANDATORY after every agent/skill execution):
```
Task(subagent_type: "humaninloop:state-analyst",
  prompt: {action: "parse-and-advance", node_id: <assembled.node_id>,
           pass_number, dag_path, catalog_path, feature_dir},
  description: "Parse and advance")
```

**Advance** (after supervisor-owned node handling):
```
Task(subagent_type: "humaninloop:state-analyst",
  prompt: {action: "update-and-advance", node_id: <assembled.node_id>,
           dag_path, catalog_path, feature_dir, pass_number,
           status: <status>, answers: <answers if decision>},
  description: "Update and advance")
```

### Evaluate and Route

Base ALL decisions on the `advance` field from the Analyst's response:

| `advance.action_taken` | Supervisor Action |
|-------------------------|-------------------|
| `"assemble_next"` | Dispatch the next agent/skill from `advance.dispatch`. Loop back to Dispatch. |
| `"freeze_and_new_pass"` | Increment `pass_number`. Return to Start of Every Pass. |
| `"completion"` | Go to Completion. |
| `"escalate"` | Present to user with options (continue / accept current / stop). |
| `"supervisor_owned"` | Handle the action, then `update-and-advance`. |

### Lifecycle Rules

**Rule 1 — `advance.action_taken` is `freeze_and_new_pass`**: New pass needed. Increment `pass_number`. Return to Start of Every Pass.

**Rule 2 — `advance.action_taken` is `completion`**: All cycles complete, final validation passed, milestone achieved. Go to Completion.

**Rule 3 — `advance.action_taken` is `escalate`**: Critical failure. Present to user with options.

**Rule 4 — `advance.action_taken` is `supervisor_owned`**: Handle `supervisor_action`, then `update-and-advance`.

**Rule 5 — Convergence stall** (same failure pattern 2+ passes, from `briefing.outcome_trajectory`): Surface to user — do not silently continue.

**Rule 6 — 3 retry attempts reached on a cycle** (from `briefing.pass_context`): Surface to user with options per INV-004.

**Rule 7 — Unexpected situation**: The Analyst returns an error. Present to user.

**Rule 8 — Cycle advancement**: After `freeze_and_new_pass`, the next `brief-and-assemble` identifies the next cycle from `tasks.md` checkboxes. The Analyst's strategy-implementation skill handles cycle sequencing.

**Rule 9 — Fix pass routing**: After final-validation verdict `needs-revision`, the next `brief-and-assemble` creates a fix pass. The Staff Engineer is dispatched in fix mode (unconstrained by cycle boundaries, scoped to specific failures). INV-004 applies (max 3 fix passes before user escalation).

**Rule 10 — carry_forward on tasks-complete**: The `tasks-complete` gate has `carry_forward: true`. After pass 1, the Analyst auto-resolves this gate during assembly. The Supervisor never knows this happened.

---

## Completion

Update context status to `completed`. Output a summary:

```markdown
## Implementation Complete

**Feature**: {feature_id}
**Passes**: {pass_number}
**Final Verdict**: ready
**Milestone**: achieved

### Cycle Summary
| Metric | Value |
|--------|-------|
| Foundation Cycles | {N}/{N} complete |
| Feature Cycles | {N}/{N} complete |
| Total Tasks | {N}/{N} complete |
| Fix Passes | {N} (if any) |

### Quality Gates
{From the final verification-report quality_gates section}

### Summary
{From the Analyst's final parse-and-advance structured summary}

### Artifacts
{feature_dir} — all workflow artifacts are in this directory

### Next Steps
1. Review the implementation in the feature directory
2. Run full test suite to verify
3. Deploy or continue with next feature
```

---

## Context Protection (CRITICAL)

- **NEVER read domain agent reports directly**. All report content enters via State Analyst's `parse-and-advance`.
- **NEVER call `hil-dag` directly** — zero CLI usage. All DAG operations go through the State Analyst.
- **ALWAYS call `parse-and-advance` after every agent execution** — no exceptions.
- **ALWAYS call `brief-and-assemble` at the start of every pass** — not just pass 1.

### Responsibility Boundaries

| Operation | Owner | Mechanism |
|-----------|-------|-----------|
| Override recommendation | Supervisor | `re-brief` with override |
| Dispatch domain agents | Supervisor | Task tool with prompt from Analyst |
| Collect human input | Supervisor | `AskUserQuestion` |
| Watch convergence | Supervisor | `outcome_trajectory` from Analyst |
| Watch retry count | Supervisor | `pass_context` from Analyst (INV-004: max 3 retries) |
| Briefings + assembly | State Analyst | `brief-and-assemble` |
| Report parsing + advance | State Analyst | `parse-and-advance` |
| Status updates + advance | State Analyst | `update-and-advance` |
| Pass freezing | State Analyst | Inside `parse-and-advance` |
| Prompt construction | State Analyst | Inside assembly steps |
| Graph invariant validation | State Analyst | Via `hil-dag` MCP tools |

### Important Notes

- Do NOT modify git config or push to remote
- Always use Task tool to invoke agents — never inline agent behavior
- Domain agents have NO workflow knowledge — all context via files on disk
- Supervisor has zero direct `hil-dag` CLI usage — all graph operations delegated to State Analyst
