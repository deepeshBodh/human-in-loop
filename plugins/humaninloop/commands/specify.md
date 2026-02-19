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

Parse `$ARGUMENTS` for flags before processing:

1. **Extract `--skip-brainstorm` flag**: If present, set `skip_brainstorm = true` and remove from input
2. **Extract clean user input**: `user_input = $ARGUMENTS.replace("--skip-brainstorm", "").trim()`
3. **Track original input**: `original_input = user_input`

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
| Strategy skills | `strategy-core`, `strategy-specification` |
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

### 1. Constitution Check

Check `.humaninloop/memory/constitution.md` exists. If NOT found:
```
Constitution Required

The HumanInLoop specify workflow requires a project constitution.
Run: /humaninloop:setup
Then retry: /humaninloop:specify
```
STOP execution if missing.

### 2. hil-dag CLI Check (for subagent environment)

Verify the `hil-dag` CLI is available for subagents (State Analyst, DAG Assembler) and resolve its PATH:

```bash
if hil-dag --help > /dev/null 2>&1; then
  echo "AVAILABLE"
elif [ -x "humaninloop_brain/.venv/bin/hil-dag" ]; then
  export PATH="$(pwd)/humaninloop_brain/.venv/bin:$PATH"
  echo "AVAILABLE_VIA_VENV"
else
  echo "NOT_FOUND"
fi
```

- If `AVAILABLE`: proceed.
- If `AVAILABLE_VIA_VENV`: prepend the venv path to `PATH` for all subsequent `hil-dag` invocations.
- If `NOT_FOUND`: attempt `cd humaninloop_brain && uv sync && cd ..`, re-check. STOP if still missing.

### 3. Resolve Project Root

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
```

**All paths passed to subagents MUST be absolute paths rooted at `$PROJECT_ROOT`.**

### 4. Create Feature Directory

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/create-new-feature.sh --json "<feature description>"
```

Parse JSON output for `BRANCH_NAME`, `SPEC_FILE`, `FEATURE_NUM`. Use `BRANCH_NAME` as `{feature-id}`.

### 5. Initialize Workflow Structure

```bash
mkdir -p $PROJECT_ROOT/specs/{feature-id}/.workflow/dags
```

Create initial `context.md` from `${CLAUDE_PLUGIN_ROOT}/templates/context-template.md` with detected project context, user input, and file paths.

**`spec.md`**: The `create-new-feature.sh` script already copies the spec template. Read the file first, then Edit to replace `{{placeholder}}` values.

Set `dag_path = $PROJECT_ROOT/specs/{feature-id}/.workflow/dags/strategy.json`

---

## Supervisor Loop

### Start of Every Pass: Request Briefing (MANDATORY)

```
Task(subagent_type: "humaninloop:state-analyst",
  prompt: {action: "briefing", workflow: "specify", feature_id, pass_number,
           catalog_path, strategy_skills: ["strategy-core", "strategy-specification"],
           dag_path, artifacts_dir: feature_dir},
  description: "Produce workflow briefing")
```

The briefing returns: `state_summary`, `gap_details`, `recommendations`, `alternatives`, `relevant_patterns`, `relevant_anti_patterns`, `outcome_trajectory`, `pass_context`.

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

**Execute**: Route by node type from the Assembler response:

| Type | Action |
|------|--------|
| **task** (with `agent_type`) | `Task(subagent_type: agent_type, prompt: agent_prompt)` |
| **task** (with `skill_to_invoke`) | `Skill(skill: skill_to_invoke, args: skill_args)` |
| **gate** (with `agent_type`) | `Task(subagent_type: agent_type, prompt: agent_prompt)` |
| **gate** (with `gate_type`) | Tell the Assembler to evaluate and update: `{action: "update-status", node_id, dag_path}`. The Assembler evaluates the gate condition and sets status + verdict. |
| **decision** | `AskUserQuestion(...)` with questions from Assembler, write answers to `{feature_dir}/.workflow/clarification-answers.md`, then tell Assembler: `{action: "update-status", node_id, status: "decided", dag_path}` |
| **milestone** | Tell the Assembler to verify and update: `{action: "update-status", node_id, status: "achieved", dag_path}`. The Assembler verifies prerequisite nodes are complete before setting `achieved`. |

**Parse** (MANDATORY for every agent node): Ask the Analyst to parse the report and recommend next steps.
```
Task(subagent_type: "humaninloop:state-analyst",
  prompt: {action: "parse-and-recommend", node_id, pass_number, dag_path, catalog_path, feature_dir},
  description: "Parse report and recommend")
```

Returns: `node_id`, `status`, `summary`, `verdict` (gates), `gaps_found`, `unresolved`, `recommendations`.

### Evaluate and Route

Base ALL decisions on the structured summary from `parse-and-recommend`.

**Continue in current pass**: If `recommendations` suggest more nodes in this pass, return to Pick with the new recommendations.

**On-demand re-briefing**: If a `parse-and-recommend` result is insufficient or confusing, request a full `briefing` before deciding.

### Lifecycle Rules

These rules govern pass transitions and workflow completion. They use DAG vocabulary — no domain knowledge.

**Rule 1 — Gate verdict `needs-revision`**: Tell the Assembler to freeze the current pass with trigger_source (the gate node) and triggered_nodes. Return to Start of Every Pass for the new pass.
```
Task(subagent_type: "humaninloop:dag-assembler",
  prompt: {action: "freeze-pass", dag_path, catalog_path, feature_dir,
           outcome: "completed", detail: "advocate-verdict-needs-revision",
           trigger_source: <gate_node_id from parse-and-recommend>,
           triggered_nodes: [nodes to re-execute], reason: <from summary>},
  description: "Freeze pass")
```

**Rule 2 — Gate verdict `ready`** (Completion Procedure):
1. Tell the Assembler to assemble the milestone node
2. Tell the Assembler to mark milestone achieved: `{action: "update-status", node_id: <milestone_id>, status: "achieved", dag_path}`. The Assembler verifies prerequisite nodes are complete before setting `achieved` — if invalid, the Assembler returns the reason.
3. Tell the Assembler to freeze the pass with outcome `completed`, detail `ready`
4. Go to Completion

**Rule 3 — Gate verdict `critical-gaps`**: Present to user with options (continue / accept current / stop).

**Rule 4 — `parse-and-recommend` has `unresolved` items**: Tell the Assembler to assemble a decision node. Collect user input via `AskUserQuestion`. Write answers to `{feature_dir}/.workflow/clarification-answers.md`. Tell the Assembler to mark decided: `{action: "update-status", node_id: <decision_id>, status: "decided", dag_path}`. Continue with Analyst's recommendation.

**Rule 5 — Convergence stall** (same gap count 2+ passes, from `outcome_trajectory`): Surface to user — do not silently continue.

**Rule 6 — 5 passes reached** (from `pass_context`): Surface to user with options.

**Rule 7 — Unexpected situation**: Tell the Assembler to freeze as `halted`. Present to user.

---

## Completion

Update context status to `completed`. Output:

```markdown
## Specification Complete

**Feature**: {feature_id}
**Passes**: {pass_number}
**Final Verdict**: ready

### Files Created
- Spec: `specs/{feature-id}/spec.md`
- Workflow: `specs/{feature-id}/.workflow/`
- DAG: `specs/{feature-id}/.workflow/dags/strategy.json`

### Summary
{From parse-and-recommend structured summary: user story count, requirement count}

### Next Steps
1. Review the spec at `specs/{feature-id}/spec.md`
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
