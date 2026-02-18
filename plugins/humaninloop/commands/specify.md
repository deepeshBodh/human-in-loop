---
description: Create feature specification using DAG-based workflow execution
---

# Specify

You are the **Supervisor** orchestrating the specification workflow via DAG-based execution. You make assembly decisions informed by State Briefer briefings. You delegate all graph mechanics to the DAG Assembler. The DAG Assembler constructs prompts for domain agents; you dispatch them via Task calls.

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

Verify the `hil-dag` CLI is available:
```bash
hil-dag --help > /dev/null 2>&1
```
If NOT found:
```
hil-dag CLI Required

The specify workflow requires the hil-dag CLI from humaninloop_brain.
Install: cd humaninloop_brain && uv sync
Then retry: /humaninloop:specify
```
STOP execution if missing.

### 2. Create Feature Directory

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/create-new-feature.sh --json "<feature description>"
```

Parse JSON output for `BRANCH_NAME`, `SPEC_FILE`, `FEATURE_NUM`. Use `BRANCH_NAME` as `{feature-id}`.

### 3. Initialize Workflow Structure

```bash
mkdir -p specs/{feature-id}/.workflow/dags
```

Create initial `context.md` from `${CLAUDE_PLUGIN_ROOT}/templates/context-template.md` with detected project context, user input, and file paths.

Create initial `spec.md` from `${CLAUDE_PLUGIN_ROOT}/templates/spec-template.md`.

### 4. Create First DAG Pass

Invoke DAG Assembler:
```json
{"action": "assemble-and-prepare", "next_node": "constitution-gate",
 "dag_path": "specs/{feature-id}/.workflow/dags/pass-001.json",
 "catalog_path": "${CLAUDE_PLUGIN_ROOT}/catalogs/specify-catalog.json",
 "feature_dir": "specs/{feature-id}", "parameters": {}}
```

If the DAG file does not exist yet, ask the DAG Assembler to create it before assembling the first node.

---

## Supervisor DAG Loop

Set `pass_number = 1`.

### Step 1: Request Briefing

```
Task(
  subagent_type: "humaninloop:state-briefer",
  prompt: <briefing request JSON with workflow, feature_id, pass_number, catalog_path, strategy_skills, dag_history_path, artifacts_dir>,
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

### Step 5: Parse Report

For nodes that produce reports (task and gate nodes with agents):

```
Task(
  subagent_type: "humaninloop:dag-assembler",
  prompt: <parse-report JSON with node_id, dag_path, catalog_path, feature_dir>,
  description: "Parse agent report"
)
```

### Step 6: Evaluate

Based on the parsed report and current state:

- **More nodes needed in this pass**: Return to Step 2 with updated state
- **Advocate verdict `ready`**: Assemble `spec-complete` milestone, freeze pass, go to Completion
- **Advocate verdict `needs-revision`**: Freeze pass, increment `pass_number`, create new DAG pass, return to Step 1
- **Advocate verdict `critical-gaps`**: Present situation to user with options:
  ```
  AskUserQuestion(
    questions: [{
      question: "Critical gaps found: {gap_summary}. How should we proceed?",
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

Freeze the pass via DAG Assembler before starting a new one:
```json
{"action": "freeze-pass", "dag_path": "...", "outcome": "completed",
 "outcome_detail": "advocate-verdict-needs-revision",
 "rationale": "Advocate found N gaps. Starting new pass."}
```

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
{From parsed analyst report: user story count, requirement count}

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
- Full agent reports stay on disk — only structured summaries enter Supervisor context
