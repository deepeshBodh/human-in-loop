---
description: Create feature specification using DAG-based workflow execution
---

# Specify

You are the **Supervisor** orchestrating the specification workflow. You make decisions informed by State Analyst briefings and recommendations. You delegate all DAG operations and state analysis to the State Analyst. You dispatch domain agents with prompts constructed by the State Analyst.

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

Produce a validated `spec.md`. Success: a gate node verdict `ready` and a milestone node `achieved`.

## DAG Vocabulary

- **4 node types**: task, gate, decision, milestone
- **6 edge types**: depends_on, produces, validates, constrained_by, informed_by, triggered_by
- **Pass lifecycle**: passes are created, executed, and frozen within a single StrategyGraph file
- **Gate verdicts**: ready, needs-revision, critical-gaps (separate from gate status)

| Resource | Path |
|----------|------|
| Catalog | `${CLAUDE_PLUGIN_ROOT}/catalogs/specify-catalog.json` |
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

Resolve paths and create the feature workspace. Constitution verification is handled by the State Analyst's invariant auto-resolution (INV-002 + `carry_forward`) during assembly.

### 1. Resolve Project Root

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
${CLAUDE_PLUGIN_ROOT}/scripts/create-new-feature.sh --json "<feature description>"
```

Verify `hil-dag` MCP tools are available (the State Analyst connects to the `hil-dag` MCP server). If MCP tools are not reachable, instruct the user to install humaninloop-brain and configure the MCP server:
```
uv tool install "humaninloop-brain @ git+https://github.com/deepeshBodh/human-in-loop.git#subdirectory=humaninloop_brain"
```
Then add to `.claude/settings.json`:
```json
{"mcpServers": {"hil-dag": {"command": "hil-dag"}}}
```

Parse JSON output for `BRANCH_NAME`, `SPEC_FILE`, `FEATURE_NUM`. Use `BRANCH_NAME` as `{feature-id}`.

### 2. Initialize Workflow Structure

```bash
mkdir -p $PROJECT_ROOT/specs/{feature-id}/.workflow/dags
```

Create initial `context.md` from `${CLAUDE_PLUGIN_ROOT}/templates/context-template.md` with detected project context, user input, and file paths.

**`spec.md`**: The `create-new-feature.sh` script already copies the spec template. Read the file first, then Edit to replace `{{placeholder}}` values.

**All paths passed to the State Analyst MUST be absolute paths rooted at `$PROJECT_ROOT`.**

Set `dag_path = $PROJECT_ROOT/specs/{feature-id}/.workflow/dags/specify-strategy.json`

---

## Supervisor Loop

### Start of Every Pass: Brief and Assemble (MANDATORY)

```
Task(subagent_type: "humaninloop:state-analyst",
  prompt: {action: "brief-and-assemble", workflow: "specify", feature_id, pass_number,
           dag_path, catalog_path: "${CLAUDE_PLUGIN_ROOT}/catalogs/specify-catalog.json",
           feature_dir},
  description: "Brief and assemble")
```

The Analyst returns: `briefing` (state_summary, outcome_trajectory, pass_context, relevant_patterns), `selected` (the auto-selected recommendation), `alternatives`, `assembled` (node details), and `dispatch` (mode + prompt).

**Override**: If you disagree with the `selected` recommendation, use `re-brief` with `override_recommendation` set to your preferred alternative:
```
Task(subagent_type: "humaninloop:state-analyst",
  prompt: {action: "re-brief", workflow: "specify", feature_id, pass_number,
           dag_path, catalog_path, feature_dir,
           override_recommendation: <alternative>},
  description: "Re-brief with override")
```

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

**Rule 1 — `advance.action_taken` is `freeze_and_new_pass`**: New pass needed (gate verdict was `needs-revision`). Increment `pass_number`. Return to Start of Every Pass.

**Rule 2 — `advance.action_taken` is `completion`**: Gate verdict was `ready`, milestone achieved, pass frozen. Go to Completion.

**Rule 3 — `advance.action_taken` is `escalate`**: Gate verdict was `critical-gaps`. Present to user with options (continue / accept current / stop).

**Rule 4 — `advance.action_taken` is `supervisor_owned`**: The next node requires Supervisor interaction. Handle the `supervisor_action` (collect input via `AskUserQuestion`), then send `update-and-advance`. The Analyst handles the rest.

**Rule 5 — Convergence stall** (same gap count 2+ passes, from `briefing.outcome_trajectory`): Surface to user — do not silently continue.

**Rule 6 — 5 passes reached** (from `briefing.pass_context`): Surface to user with options.

**Rule 7 — Unexpected situation**: The Analyst returns an error. Present to user.

---

## Completion

Update context status to `completed`. Output a summary:

```markdown
## Specification Complete

**Feature**: {feature_id}
**Passes**: {pass_number}
**Final Verdict**: ready
**Milestone**: achieved

### Summary
{From the Analyst's final parse-and-advance structured summary}

### Artifacts
{feature_dir} — all workflow artifacts are in this directory

### Next Steps
1. Review the specification in the feature directory
2. Run `/humaninloop:plan` to create implementation plan
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
