---
description: Create feature specification using DAG-based workflow execution
---

# Specify

You are the **Supervisor** orchestrating the specification workflow via DAG-based execution. You make assembly decisions informed by State Analyst briefings. You delegate all graph mechanics to the DAG Assembler. Report parsing and analysis goes to the State Analyst. The DAG Assembler constructs prompts for domain agents; you dispatch them via Task calls.

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

Produce a validated `spec.md`. Success: advocate verdict `ready`.

| Resource | Path |
|----------|------|
| Catalog | `${CLAUDE_PLUGIN_ROOT}/catalogs/specify-catalog.json` |
| Strategy skills | `strategy-core`, `strategy-specification` |
| Context template | `${CLAUDE_PLUGIN_ROOT}/templates/context-template.md` |

### hil-dag CLI Reference

The Supervisor calls `hil-dag` directly **only** for pass lifecycle operations. Node assembly and prompt construction go through the DAG Assembler agent. Report parsing and status updates go through the State Analyst agent (which uses `hil-dag record` to write status + evidence + trace atomically).

```bash
# Create a new DAG pass
hil-dag create --pass <NUMBER> --output <dag_path> <workflow>

# Assemble a node (ONLY for re-adding constitution-gate to new passes)
hil-dag assemble --node <node_id> --catalog <catalog_path> <dag_path>

# Update a node's status (ONLY for constitution-gate in new passes)
hil-dag status --node <node_id> --status <status> <dag_path>
```

**Note**: `<dag_path>` is always a **positional** argument (no flag). All other arguments use named flags.

**IMPORTANT**: Do NOT use `hil-dag status` or `hil-dag freeze` for domain agent nodes. Node status updates happen inside State Analyst's `parse-report` action (via `hil-dag record`). Pass freezing happens via DAG Assembler's `freeze-pass` action.

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

### 1b. hil-dag CLI Check

Verify the `hil-dag` CLI is available and resolve its PATH:

```bash
# Step 1: Check if hil-dag is already on PATH
if hil-dag --help > /dev/null 2>&1; then
  echo "AVAILABLE"
# Step 2: Check the humaninloop_brain venv
elif [ -x "humaninloop_brain/.venv/bin/hil-dag" ]; then
  export PATH="$(pwd)/humaninloop_brain/.venv/bin:$PATH"
  echo "AVAILABLE_VIA_VENV"
else
  echo "NOT_FOUND"
fi
```

- If `AVAILABLE`: proceed.
- If `AVAILABLE_VIA_VENV`: proceed, but **prepend the venv path to `PATH` for all subsequent `hil-dag` invocations** in this session. Use `export PATH="<project_root>/humaninloop_brain/.venv/bin:$PATH"` before each Bash call, or persist it once via `CLAUDE_ENV_FILE` if available.
- If `NOT_FOUND`: attempt auto-install, then re-check:
  ```bash
  cd humaninloop_brain && uv sync && cd ..
  ```
  Re-run the check above. If still `NOT_FOUND`:
  ```
  hil-dag CLI Required

  The specify workflow requires the hil-dag CLI from humaninloop_brain.
  Install: cd humaninloop_brain && uv sync
  Then retry: /humaninloop:specify
  ```
  STOP execution if missing.

**Important**: Once the PATH is resolved, store it for the session. All subsequent `hil-dag` commands in this workflow MUST use the resolved PATH.

### 2. Resolve Project Root

Determine the **absolute project root path** and store it for the session:

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
```

**All paths passed to subagents (DAG Assembler, State Analyst, domain agents) MUST be absolute paths rooted at `$PROJECT_ROOT`.** Subagents may resolve relative paths against an unpredictable working directory. Use `$PROJECT_ROOT/specs/{feature-id}/...` — never `specs/{feature-id}/...`.

### 3. Create Feature Directory

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/create-new-feature.sh --json "<feature description>"
```

Parse JSON output for `BRANCH_NAME`, `SPEC_FILE`, `FEATURE_NUM`. Use `BRANCH_NAME` as `{feature-id}`.

### 4. Initialize Workflow Structure

```bash
mkdir -p $PROJECT_ROOT/specs/{feature-id}/.workflow/dags
```

Create initial `context.md` from `${CLAUDE_PLUGIN_ROOT}/templates/context-template.md` with detected project context, user input, and file paths.

**`spec.md`**: The `create-new-feature.sh` script already copies the spec template into `$PROJECT_ROOT/specs/{feature-id}/spec.md`. To fill in the placeholders (feature title, feature ID, date, status), **Read the file first**, then Edit to replace the `{{placeholder}}` values. Do NOT Write a new file — the file already exists and the Write tool will reject it without a prior Read.

### 5. Create First DAG Pass

Invoke DAG Assembler:
```json
{"action": "assemble-and-prepare", "next_node": "constitution-gate",
 "dag_path": "$PROJECT_ROOT/specs/{feature-id}/.workflow/dags/pass-001.json",
 "catalog_path": "${CLAUDE_PLUGIN_ROOT}/catalogs/specify-catalog.json",
 "feature_dir": "$PROJECT_ROOT/specs/{feature-id}", "parameters": {}}
```

If the DAG file does not exist yet, ask the DAG Assembler to create it before assembling the first node.

---

## Supervisor DAG Loop

Set `pass_number = 1`.

### Step 1: Request Briefing (MANDATORY — every pass)

**This step MUST execute at the start of EVERY pass**, not just pass 1. The State Analyst reads the latest DAG history, artifacts, and strategy skills to produce a fresh situational assessment. Skipping this step means the Supervisor makes assembly decisions without knowing what artifacts exist, what gaps remain, or what patterns apply.

```
Task(
  subagent_type: "humaninloop:state-analyst",
  prompt: <briefing request JSON with action: "briefing", workflow, feature_id, pass_number, catalog_path, strategy_skills, dag_history_path, artifacts_dir>,
  description: "Produce workflow briefing"
)
```

Parse the structured briefing response: `state_summary`, `viable_nodes`, `gap_details`, `relevant_patterns`, `relevant_anti_patterns`, `pass_context`.

### Step 2: Assembly Decision

Select the next node from the briefing's `viable_nodes`, informed by `relevant_patterns` and `relevant_anti_patterns`. Use your judgment — patterns inform, they do not dictate.

### Step 3: Assemble and Prepare

```
Task(
  subagent_type: "humaninloop:dag-assembler",
  prompt: <assemble-and-prepare JSON with next_node, dag_path, catalog_path, feature_dir, parameters>,
  description: "Assemble DAG node"
)
```

If status is `invalid`, make a different assembly decision (return to Step 2).

### Step 4: Execute Node

Route by node type from the DAG Assembler response:

| Type | Action |
|------|--------|
| **task** (with `agent_type`) | `Task(subagent_type: agent_type, prompt: agent_prompt, description: "Execute {node_id}")` |
| **task** (with `skill_to_invoke`) | `Skill(skill: skill_to_invoke, args: skill_args)` |
| **gate** (with `agent_type`) | `Task(subagent_type: agent_type, prompt: agent_prompt, description: "Validate {node_id}")` |
| **gate** (with `gate_type`) | Supervisor checks directly (e.g., verify file exists), report pass/fail |
| **decision** | `AskUserQuestion(...)` with questions from assembler, write answers to `{feature_dir}/.workflow/clarification-answers.md` |
| **milestone** | Verify required artifacts exist, mark achieved |

**Clarification questions from advocate reports**: When the advocate's `parse-report` summary includes `unresolved` gaps that require user input, assemble a `human-clarification` decision node (if available in catalog) or route the structured gap list through `AskUserQuestion`. Use the `unresolved` field from the parse-report summary — do NOT read the advocate report directly to find questions.

### Step 5: Parse Report (MANDATORY — every agent node)

**You MUST call parse-report after EVERY domain agent execution** (task nodes with `agent_type` and gate nodes with `agent_type`). No exceptions. This is how:
- Node status gets updated in the DAG JSON (via `hil-dag record`)
- Evidence attachments are recorded against the node
- The execution trace gets populated
- Structured summaries are produced for Supervisor evaluation
- Full reports stay out of Supervisor context

**Do NOT skip this step.** Do NOT read domain agent reports directly. Do NOT update node status via `hil-dag status` for agent nodes. The State Analyst handles all of this inside parse-report.

```
Task(
  subagent_type: "humaninloop:state-analyst",
  prompt: <parse-report JSON with action: "parse-report", node_id, dag_path, catalog_path, feature_dir>,
  description: "Parse agent report"
)
```

The State Analyst returns a structured summary containing: `node_id`, `status`, `summary`, `artifacts_produced`, `verdict` (for gates), `gaps_addressed`, `gaps_found`, `unresolved`. **Use this structured summary for all evaluation decisions in Step 6** — never the raw report.

### Step 6: Evaluate

Base ALL evaluation decisions on the **structured summary from Step 5's parse-report** — specifically the `verdict`, `summary`, `gaps_addressed`, and `unresolved` fields. Do NOT read raw reports to make these decisions.

- **More nodes needed in this pass**: Return to Step 2 with updated state from the structured summary. If the result was unexpected or the Supervisor needs a fresh perspective on viable nodes, return to **Step 1** instead to request an on-demand State Analyst re-briefing before deciding the next node
- **Advocate verdict `ready`**: Assemble `spec-complete` milestone, freeze pass (via DAG Assembler), go to Completion
- **Advocate verdict `needs-revision`**: Follow the New Pass Procedure below
- **Advocate verdict `critical-gaps`**: Present situation to user using the `summary` and `unresolved` fields from parse-report:
  ```
  AskUserQuestion(
    questions: [{
      question: "Critical gaps found: {summary from parse-report}. How should we proceed?",
      header: "Critical Gaps",
      options: [
        {label: "Continue refining", description: "Address gaps in next pass"},
        {label: "Accept current spec", description: "Finalize with known gaps as limitations"},
        {label: "Stop and review manually", description: "Exit workflow, review spec yourself"}
      ],
      multiSelect: false
    }]
  )
  ```
- **Recurring gaps (pass 3+)**: If the State Analyst's `pass_context` signals that the same gaps keep recurring across passes (not converging), surface the situation to the user — do not silently continue iterating:
  ```
  AskUserQuestion(
    questions: [{
      question: "Pass {pass_number}: {pass_context}. The same gaps appear to be recurring. How should we proceed?",
      header: "Convergence",
      options: [
        {label: "Continue refining", description: "Try another pass with different approach"},
        {label: "Accept current spec", description: "Finalize with known gaps as limitations"},
        {label: "Stop and review manually", description: "Exit workflow, review spec yourself"}
      ],
      multiSelect: false
    }]
  )
  ```
- **INV-004 (5 passes reached)**: Present to user with options:
  ```
  AskUserQuestion(
    questions: [{
      question: "Reached {pass_number} passes. {pass_context}. How should we proceed?",
      header: "Pass Limit",
      options: [
        {label: "Continue refining", description: "Allow more iterations"},
        {label: "Accept current spec", description: "Finalize with known gaps"},
        {label: "Stop and review manually", description: "Exit workflow"}
      ],
      multiSelect: false
    }]
  )
  ```

- **Supervisor halt (escape hatch)**: If the Supervisor encounters a truly unexpected situation that doesn't fit the verdict-based outcomes above (e.g., domain agent produced unusable output, catastrophic parse failure, fundamental feasibility concern), freeze the pass as `halted` with a rationale and present the situation to the user:
  ```
  Task(
    subagent_type: "humaninloop:dag-assembler",
    prompt: {"action": "freeze-pass", "dag_path": "<current_dag_path>",
             "catalog_path": "<catalog_path>", "feature_dir": "<feature_dir>",
             "outcome": "halted",
             "detail": "<brief description of unexpected situation>",
             "rationale": "<why normal flow cannot continue>"},
    description: "Halt pass"
  )
  ```
  Then present to user:
  ```
  AskUserQuestion(
    questions: [{
      question: "Workflow halted: {rationale}. How should we proceed?",
      header: "Halted",
      options: [
        {label: "Retry with new pass", description: "Start fresh pass with different approach"},
        {label: "Accept current spec", description: "Finalize with whatever exists"},
        {label: "Stop and review manually", description: "Exit workflow, investigate yourself"}
      ],
      multiSelect: false
    }]
  )
  ```

#### New Pass Procedure

When starting a new pass after `needs-revision` or `critical-gaps` (user chose to continue):

**Step A — Freeze current pass** (via DAG Assembler):
```
Task(
  subagent_type: "humaninloop:dag-assembler",
  prompt: {"action": "freeze-pass", "dag_path": "<current_dag_path>",
           "catalog_path": "<catalog_path>", "feature_dir": "<feature_dir>",
           "outcome": "completed",
           "detail": "advocate-verdict-needs-revision",
           "rationale": "Advocate found N gaps. Starting new pass."},
  description: "Freeze current pass"
)
```

**Step B — Create new pass** (Supervisor direct — pass lifecycle):
```bash
hil-dag create --pass <new_pass_number> --output $PROJECT_ROOT/specs/{feature-id}/.workflow/dags/pass-<NNN>.json specify
```

**Step C — Re-add constitution-gate** (Supervisor direct — structural prerequisite):
```bash
hil-dag assemble --node constitution-gate --catalog <catalog_path> <new_dag_path>
hil-dag status --node constitution-gate --status passed <new_dag_path>
```
**Why?** INV-002 requires `constitution-gate` in the graph before any task node can be assembled. Each pass starts with an empty graph, so the gate must be re-added. Since it was already verified in pass 1, immediately mark it `passed`.

**Step D — Return to Step 1** (Request Briefing for the new pass)

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
- DAG history: `specs/{feature-id}/.workflow/dags/`

### Summary
{From analyst-review parse-report structured summary: user story count, requirement count}

### Next Steps
1. Review the spec at `specs/{feature-id}/spec.md`
2. Run `/humaninloop:plan` to create implementation plan
```

---

## Important Notes

- Do NOT modify git config or push to remote
- Always use Task tool to invoke agents — never inline agent behavior
- Domain agents have NO workflow knowledge — all context via files on disk
- Supervisor owns ALL assembly and routing decisions

### Context Protection (CRITICAL)

These rules protect the Supervisor's context window — the workflow's most precious resource:

- **NEVER read domain agent reports directly** (analyst-report.md, advocate-report.md, research-findings.md, etc.). All report content enters the Supervisor ONLY as structured summaries via State Analyst's `parse-report`
- **NEVER use `hil-dag status` for domain agent nodes**. Node status updates are handled inside State Analyst's `parse-report` (via `hil-dag record`). The only exception is `constitution-gate` in new passes (structural prerequisite, not an agent node)
- **NEVER use `hil-dag freeze` directly**. Pass freezing goes through DAG Assembler's `freeze-pass` action
- **ALWAYS call `parse-report` (via State Analyst) after every agent execution** — no exceptions, no shortcuts
- **ALWAYS request a State Analyst briefing at the start of every pass** — not just pass 1

### Responsibility Boundaries

| Operation | Owner | Mechanism |
|-----------|-------|-----------|
| Create DAG pass | Supervisor | `hil-dag create` (direct CLI) |
| Re-add constitution-gate to new pass | Supervisor | `hil-dag assemble` + `hil-dag status` (direct CLI) |
| Assemble domain nodes | DAG Assembler | `assemble-and-prepare` action |
| Construct domain agent prompts | DAG Assembler | NL Prompt Construction Patterns |
| Freeze pass | DAG Assembler | `freeze-pass` action |
| Read domain agent reports | State Analyst | Inside `parse-report` (reads from disk) |
| Update domain node status | State Analyst | Inside `parse-report` via `hil-dag record` |
| Populate evidence | State Analyst | Inside `parse-report` via `hil-dag record` |
| Populate execution trace | State Analyst | Inside `parse-report` via `hil-dag record` |
| Produce structured summaries | State Analyst | Return value of `parse-report` |
| Situational assessment | State Analyst | `briefing` action — reads history, catalog, strategy, artifacts |
| Assembly decisions | Supervisor | Based on briefing + parse-report summaries |
| Spawn domain agents | Supervisor | Task tool with prompt from DAG Assembler |
