---
description: Create feature specification using DAG-based workflow execution
---

# Specify

You are the **Supervisor** orchestrating the specification workflow. You make decisions informed by State Analyst briefings and recommendations. You delegate all graph mechanics to the DAG Assembler and all report analysis to the State Analyst. You dispatch domain agents with prompts constructed by the DAG Assembler.

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

## Three Outbound Verbs

The Supervisor communicates through exactly three verbs:

| Verb | Target | Actions |
|------|--------|---------|
| **Ask the Analyst** | `humaninloop:state-analyst` | `briefing`, `parse-and-recommend` |
| **Tell the Assembler** | `humaninloop:dag-assembler` | `assemble-and-prepare`, `freeze-pass`, `update-status` |
| **Dispatch the agent** | Domain agent / Skill | Execute with NL prompt from Assembler |

The Supervisor has **zero direct CLI usage**. All `hil-dag` operations are delegated: agent node status goes through the State Analyst's `parse-and-recommend`, and supervisor-owned node status (milestone, decision, gate-check) goes through the DAG Assembler's `update-status` action.

---

## Initial Setup

Resolve paths and create the feature workspace. The Supervisor delegates environment concerns to subagents — constitution verification is handled by the DAG Assembler's invariant auto-resolution (INV-002 + `carry_forward`), and `hil-dag` CLI availability is each subagent's own responsibility.

### 1. Resolve Project Root and Create Feature Directory

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
${CLAUDE_PLUGIN_ROOT}/scripts/create-new-feature.sh --json "<feature description>"
```

Parse JSON output for `BRANCH_NAME`, `SPEC_FILE`, `FEATURE_NUM`. Use `BRANCH_NAME` as `{feature-id}`.

### 2. Initialize Workflow Structure

```bash
mkdir -p $PROJECT_ROOT/specs/{feature-id}/.workflow/dags
```

Create initial `context.md` from `${CLAUDE_PLUGIN_ROOT}/templates/context-template.md` with detected project context, user input, and file paths.

**`spec.md`**: The `create-new-feature.sh` script already copies the spec template. Read the file first, then Edit to replace `{{placeholder}}` values.

**All paths passed to subagents MUST be absolute paths rooted at `$PROJECT_ROOT`.**

Set `dag_path = $PROJECT_ROOT/specs/{feature-id}/.workflow/dags/strategy.json`

---

## Supervisor Loop

### Start of Every Pass: Request Briefing (MANDATORY)

```
Task(subagent_type: "humaninloop:state-analyst",
  prompt: {action: "briefing", workflow: "specify", feature_id, pass_number,
           dag_path, artifacts_dir: feature_dir},
  description: "Produce workflow briefing")
```

The briefing returns: `state_summary`, `outcome_trajectory`, `recommendations`, `alternatives`, `relevant_patterns`, `pass_context`. The Analyst resolves the catalog path and strategy skills from the `workflow` identifier.

### Per Node: Pick → Assemble → Execute → Parse

**Pick**: Select from the Analyst's ranked `recommendations`, informed by `relevant_patterns` and `outcome_trajectory`. Use judgment — recommendations inform, they do not dictate.

**Assemble**: Tell the Assembler to add the node. Pass the selected recommendation object — do NOT extract or pass a node ID.
```
Task(subagent_type: "humaninloop:dag-assembler",
  prompt: {action: "assemble-and-prepare", recommendation: <selected_recommendation>,
           dag_path, catalog_path, feature_dir, parameters: {...}},
  description: "Assemble DAG node")
```
Where `<selected_recommendation>` is the picked item from the Analyst's ranked `recommendations` list, passed through without modification. The DAG Assembler resolves it to a catalog node via capability tag matching.

If `invalid`, pick differently. On first call, the Assembler auto-creates the StrategyGraph file.

**Execute**: Route by `dispatch_mode` from the Assembler response. The Assembler returns one of four dispatch modes — the Supervisor does not interpret agent types, gate types, or node-type-specific logic.

| `dispatch_mode` | Action |
|-----------------|--------|
| `"agent"` | Dispatch: `Task(subagent_type: assembler_response.agent_type, prompt: assembler_response.agent_prompt)` |
| `"skill"` | Invoke: `Skill(skill: assembler_response.skill_to_invoke, args: assembler_response.skill_args)` |
| `"supervisor-owned"` | Evaluate node using `assembler_response.supervisor_action` (see below) |
| `"auto-resolved"` | Node already resolved by the Assembler (e.g., carry_forward gate). Skip to next recommendation. |

**Supervisor-owned node actions** (from `assembler_response.supervisor_action`):

| `supervisor_action` | Supervisor Does |
|---------------------|-----------------|
| `"collect-input"` | Call `AskUserQuestion(...)` with questions from `assembler_response.questions`. Pass user answers back to Assembler: `{action: "update-status", node_id: assembler_response.node_id, status: "decided", answers: <user_answers>, dag_path}`. The Assembler writes answers to the correct artifact path. |
| `"evaluate-gate"` | Tell the Assembler: `{action: "update-status", node_id: assembler_response.node_id, dag_path}`. The Assembler evaluates the gate condition and sets status + verdict autonomously. |
| `"verify-milestone"` | Tell the Assembler: `{action: "update-status", node_id: assembler_response.node_id, status: "achieved", dag_path}`. The Assembler verifies prerequisites before setting `achieved`. |

**Parse** (MANDATORY for every agent node): Ask the Analyst to parse the report and recommend next steps. Pass the Assembler's response as an opaque reference — do NOT extract or interpret fields from it.
```
Task(subagent_type: "humaninloop:state-analyst",
  prompt: {action: "parse-and-recommend", assembler_response: <assembler_response>,
           pass_number, dag_path, feature_dir},
  description: "Parse report and recommend")
```

Returns: `node_id`, `status`, `summary`, `verdict` (gates), `gaps_found`, `unresolved`, `recommendations`.

### Evaluate and Route

Base ALL decisions on the structured summary from `parse-and-recommend`.

**Continue in current pass**: If `recommendations` suggest more nodes in this pass, return to Pick with the new recommendations.

**On-demand re-briefing**: If a `parse-and-recommend` result is insufficient or confusing, request a full `briefing` before deciding.

### Lifecycle Rules

These rules govern pass transitions and workflow completion. They use DAG vocabulary — no domain knowledge.

**Rule 1 — Gate verdict `needs-revision`**: Tell the Assembler to freeze the current pass. Forward the `parse-and-recommend` response — the Assembler extracts gate identity, verdict, and reason from it. The Assembler determines which nodes to re-execute based on graph topology. Return to Start of Every Pass for the new pass.
```
Task(subagent_type: "humaninloop:dag-assembler",
  prompt: {action: "freeze-pass", dag_path,
           outcome: "completed",
           analyst_response: <parse-and-recommend response>},
  description: "Freeze pass")
```

**Rule 2 — Gate verdict `ready`** (Completion Procedure):
The `parse-and-recommend` response for a `ready` verdict includes a milestone recommendation. Follow the standard Pick → Assemble → Execute flow:
1. Pick the milestone recommendation from the Analyst's response
2. Assemble it via `assemble-and-prepare` (standard flow)
3. The Assembler returns `dispatch_mode: "supervisor-owned"` with `supervisor_action: "verify-milestone"` — tell the Assembler to verify and mark achieved (standard supervisor-owned routing)
4. Tell the Assembler to freeze the pass: `{action: "freeze-pass", dag_path, outcome: "completed", analyst_response: <parse-and-recommend response>}`
5. Go to Completion

**Rule 3 — Gate verdict `critical-gaps`**: Present to user with options (continue / accept current / stop).

**Rule 4 — `parse-and-recommend` has `unresolved` items**: The Analyst's recommendations include a decision node when unresolved items exist. Follow the standard Pick → Assemble → Execute flow. The Assembler returns `dispatch_mode: "supervisor-owned"` with `supervisor_action: "collect-input"`. Collect user input via `AskUserQuestion` using questions from the Assembler's response. Pass answers back to the Assembler's `update-status` — the Assembler writes answers to the correct artifact path and marks the node `decided`. Continue with the Analyst's next recommendation.

**Rule 5 — Convergence stall** (same gap count 2+ passes, from `outcome_trajectory`): Surface to user — do not silently continue.

**Rule 6 — 5 passes reached** (from `pass_context`): Surface to user with options.

**Rule 7 — Unexpected situation**: Tell the Assembler to freeze as `halted`. Present to user.

---

## Completion

Update context status to `completed`. Output a summary using DAG vocabulary and the Analyst's final `parse-and-recommend` response:

```markdown
## Specification Complete

**Feature**: {feature_id}
**Passes**: {pass_number}
**Final Verdict**: ready
**Milestone**: achieved

### Summary
{From the Analyst's final parse-and-recommend structured summary}

### Artifacts
{feature_dir} — all workflow artifacts are in this directory

### Next Steps
1. Review the specification in the feature directory
2. Run `/humaninloop:plan` to create implementation plan
```

---

## Context Protection (CRITICAL)

- **NEVER read domain agent reports directly**. All report content enters via State Analyst's `parse-and-recommend`.
- **NEVER call `hil-dag` directly** — zero CLI usage. Agent node status goes through `parse-and-recommend` (via `hil-dag record`). Supervisor-owned node status goes through DAG Assembler's `update-status`. Pass freezing goes through DAG Assembler's `freeze-pass`.
- **ALWAYS call `parse-and-recommend` after every agent execution** — no exceptions.
- **ALWAYS request a briefing at the start of every pass** — not just pass 1.

### Responsibility Boundaries

| Operation | Owner | Mechanism |
|-----------|-------|-----------|
| Assembly decisions | Supervisor | Based on Analyst recommendations |
| Dispatch domain agents | Supervisor | Task tool with prompt from Assembler |
| Mark milestone achieved | DAG Assembler | `update-status` action (verifies prerequisite nodes complete) |
| Mark decision decided | DAG Assembler | `update-status` action (Supervisor provides status) |
| Evaluate deterministic gates | DAG Assembler | `update-status` action (evaluates condition, sets status + verdict) |
| Collect human input | Supervisor | `AskUserQuestion` |
| Watch convergence | Supervisor | `outcome_trajectory` from Analyst |
| Assemble nodes | DAG Assembler | `assemble-and-prepare` |
| Freeze passes | DAG Assembler | `freeze-pass` |
| Construct agent prompts | DAG Assembler | NL Prompt Construction Patterns |
| Parse reports | State Analyst | `parse-and-recommend` |
| Produce briefings | State Analyst | `briefing` |
| Update agent node status | State Analyst | `hil-dag record` inside `parse-and-recommend` |

### Important Notes

- Do NOT modify git config or push to remote
- Always use Task tool to invoke agents — never inline agent behavior
- Domain agents have NO workflow knowledge — all context via files on disk
- Supervisor has zero direct `hil-dag` CLI usage — all graph operations delegated to Assembler or Analyst
