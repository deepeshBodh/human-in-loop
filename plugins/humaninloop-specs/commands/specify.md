---
description: Create feature specification using multi-agent architecture with integrated checklist validation and priority loop
handoffs:
  - label: Build Technical Plan
    agent: humaninloop:plan
    prompt: Create a plan for the spec
---

# Unified Specify Workflow with Priority Loop

You are the **Supervisor Agent** orchestrating a multi-agent workflow that creates feature specifications with integrated quality validation. The workflow uses a Priority Loop to ensure all Critical and Important gaps are resolved before the spec is considered complete.

## User Input

```text
$ARGUMENTS
```

If `$ARGUMENTS` is empty or appears literally, check for resume state first, then ask for a feature description.

### Empty Input Check

If `$ARGUMENTS` is empty (blank string with no content), use AskUserQuestion to handle a known Claude Code bug where inputs containing `@` file references don't reach plugin commands:

```
AskUserQuestion(
  questions: [{
    question: "⚠️ Known Issue: Input may have been lost\n\nClaude Code has a bug where inputs containing @ file references don't reach plugin commands.\n\nWould you like to re-enter your input?",
    header: "Input",
    options: [
      {label: "Re-enter input", description: "I'll type my input in the terminal"},
      {label: "Continue without input", description: "Proceed with no input provided"}
    ],
    multiSelect: false
  }]
)
```

- If user selects "Re-enter input" → wait for user to type their input in the terminal, then use that as the effective `$ARGUMENTS`
- If user selects "Continue without input" → proceed with empty input (check resume state, then ask for feature description)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    UNIFIED SPECIFY WORKFLOW                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PHASE A: Initial Specification                                      │
│  ├── Scaffold Agent                                                  │
│  ├── Spec Writer Agent                                               │
│  ├── Checklist Agent (analyze + generate)                           │
│  └── Spec Clarify Agent (classify gaps)                             │
│                                                                      │
│  PHASE B: Priority Loop                                              │
│  WHILE (critical + important > 0) AND (iteration < 10):             │
│  ├── Read Gap Priority Queue from index.md                          │
│  ├── Check termination conditions                                    │
│  ├── Present gaps via AskUserQuestion                               │
│  ├── Spec Clarify Agent (apply answers)                             │
│  ├── Re-run Checklist Agent                                         │
│  ├── Re-run Spec Clarify (classify gaps)                            │
│  └── Update index.md state                                           │
│                                                                      │
│  PHASE C: Completion                                                 │
│  ├── Log deferred minor gaps                                         │
│  ├── Finalize traceability matrix                                   │
│  └── Report quality metrics                                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Agents Used

| Agent | File | Purpose |
|-------|------|---------|
| Scaffold | `${CLAUDE_PLUGIN_ROOT}/agents/scaffold-agent.md` | Create branch, directories, initialize unified index |
| Spec Writer | `${CLAUDE_PLUGIN_ROOT}/agents/spec-writer.md` | Write user stories, requirements, criteria |
| Checklist | `${CLAUDE_PLUGIN_ROOT}/agents/checklist-agent.md` | Analyze context, generate quality checklist, classify gaps |
| Spec Clarify | `${CLAUDE_PLUGIN_ROOT}/agents/spec-clarify.md` | Dual-mode: classify gaps OR apply user answers |

---

## Pre-Execution: Constitution Check

Before any workflow execution, verify that the project constitution exists:

1. **Check for constitution file** at `.humaninloop/memory/constitution.md`
2. **If NOT found**, display the following and STOP execution:

```
Constitution Required

The HumanInLoop specify workflow requires a project constitution to be configured.

The constitution defines project principles that guide specification quality validation.

To set up your constitution, run:
/humaninloop-constitution:setup

This will walk you through defining your project's core principles.

Then retry /humaninloop-specs:specify
```

3. **If found**: Continue to Resume Detection

---

## Pre-Execution: Resume Detection

Before starting, check if a workflow is already in progress:

1. **Search for existing index.md files** in `specs/` with `loop_status != completed`
2. **If found with matching feature**:
   ```
   AskUserQuestion(
     questions: [{
       question: "Found interrupted workflow for '{feature_id}'. Resume or start fresh?",
       header: "Resume?",
       options: [
         {label: "Resume from iteration {N}", description: "Continue where you left off"},
         {label: "Start fresh", description: "Delete existing and start over"}
       ],
       multiSelect: false
     }]
   )
   ```
3. **If resume**: Read index.md state and jump to appropriate phase
4. **If fresh start**: Delete existing feature directory and proceed

---

## Phase A: Initial Specification

### A1: Scaffold

**Spawn the Scaffold Agent** using the Task tool:

```
Task(
  subagent_type: "humaninloop-specs:scaffold-agent",
  description: "Scaffold feature branch",
  prompt: "Execute scaffold for feature: $ARGUMENTS"
)
```

**Extract from result**:
- `feature_id`: e.g., "005-user-auth"
- `spec_path`: e.g., "specs/005-user-auth/spec.md"
- `index_path`: e.g., "specs/005-user-auth/.workflow/index.md"
- `specify_context_path`: e.g., "specs/005-user-auth/.workflow/specify-context.md"
- `feature_dir`: e.g., "specs/005-user-auth/"

**If scaffold fails**: Report error and stop.

---

### A2: Write Specification

**Spawn the Spec Writer Agent**:

```
Task(
  subagent_type: "humaninloop-specs:spec-writer-agent",
  description: "Write spec content",
  prompt: [Include feature_id, spec_path, index_path, specify_context_path, description]
)
```

**Extract from result**:
- `user_story_count`
- `requirement_count`
- `initial_clarifications`: Any spec-writing clarifications (Q-S#)
- `index_synced`: Confirmation index.md was updated

---

### A3: Initial Validation (Checklist)

**Spawn Checklist Agent** (combines context analysis and checklist generation):

```
Task(
  subagent_type: "humaninloop-specs:checklist-agent",
  description: "Analyze and generate checklist",
  prompt: [Include feature_id, index_path]
)
```

**Extract from result**:
- `gaps`: Object with critical, important, minor arrays
- `gap_summary`: Counts of each priority
- `checklist_file`: Path to generated checklist
- `signals`: Extracted domain keywords and focus areas

---

### A4: Classify Gaps

**If gaps.critical.length + gaps.important.length > 0**:

**Spawn Spec Clarify Agent** in `classify_gaps` mode:

```
Task(
  subagent_type: "humaninloop-specs:spec-clarify",
  description: "Classify and group gaps",
  prompt: [Execute with mode="classify_gaps", gaps from checklist-agent output]
)
```

**Extract from result**:
- `clarifications`: Array of grouped clarification questions
- `clarification_count`: Number of clarifications (max 3)
- `grouping_summary`: How gaps were grouped

**Then proceed to Phase B.**

**If no Critical/Important gaps**: Skip to Phase C (completion).

---

## Phase B: Priority Loop

```
iteration = 1
max_iterations = 10
stale_threshold = 3

WHILE (has_unresolved_gaps() AND iteration <= max_iterations):

  # B1: Present clarifications to user
  # B2: Process user answers
  # B3: Re-validate spec
  # B4: Check termination conditions
  # B5: Update state and iterate
```

### B1: Present Clarifications

Use `AskUserQuestion` to present all clarifications at once:

```
AskUserQuestion(
  questions: clarifications.map(c => ({
    question: c.question,
    header: c.id,  // "C1.1", "C1.2", etc.
    options: c.options.map(opt => ({
      label: opt,
      description: ""
    })),
    multiSelect: false
  }))
)
```

---

### B2: Process User Answers

**Spawn Spec Clarify Agent** in `apply_answers` mode:

```
Task(
  subagent_type: "humaninloop-specs:spec-clarify",
  description: "Apply clarifications",
  prompt: [Execute with mode="apply_answers", feature_id, paths, iteration, user_answers JSON]
)
```

**Extract from result**:
- `answers_applied`: Count of answers applied to spec
- `gaps_resolved`: Count of gaps resolved
- `spec_updated`: Boolean
- `remaining_gaps`: Count of remaining unresolved gaps

---

### B3: Re-Validate Spec

**Re-run Checklist Agent** to check if gaps are resolved:

```
Task(
  subagent_type: "humaninloop-specs:checklist-agent",
  description: "Re-validate spec",
  prompt: [Include feature_id, index_path, iteration]
)
```

**If new gaps found**, run Spec Clarify in classify_gaps mode:

```
Task(
  subagent_type: "humaninloop-specs:spec-clarify",
  description: "Classify new gaps",
  prompt: [Execute with mode="classify_gaps", new gaps]
)
```

---

### B4: Check Termination Conditions

**Condition 1: Success (Zero Critical + Important)**
```
if (gaps.critical.length == 0 AND gaps.important.length == 0):
  termination_reason = "success"
  BREAK
```

**Condition 2: Max Iterations**
```
if (iteration >= 10):
  termination_reason = "max_iterations"
  log_remaining_gaps_as_known_issues()
  BREAK
```

**Condition 3: Stale Detection**
```
if (same_gaps_for_3_iterations):
  termination_reason = "stale"
  escalate_to_user("These gaps remain unresolved after 3 attempts:")
  force_user_decision()
  BREAK
```

**Condition 4: No Progress**
```
if (resolved_this_iteration == 0):
  termination_reason = "no_progress"
  AskUserQuestion(
    questions: [{
      question: "No gaps were resolved. How should we proceed?",
      header: "No Progress",
      options: [
        {label: "Try again", description: "Re-attempt with different answers"},
        {label: "Accept current spec", description: "Mark gaps as known issues"},
        {label: "Abort workflow", description: "Cancel and review manually"}
      ]
    }]
  )
```

---

### B5: Update State and Iterate

Update index.md Priority Loop State:
```markdown
| **Loop Status** | validating |
| **Current Iteration** | {iteration} / 10 |
| **Last Activity** | {timestamp} |
| **Stale Count** | {stale_count} / 3 |
```

Update Gap Priority Queue with resolution status.

```
iteration++
CONTINUE LOOP
```

---

## Phase C: Completion

### C1: Log Deferred Minor Gaps

If any Minor gaps were deferred:
```markdown
## Known Minor Gaps (Deferred)

| Gap ID | Description | FR Reference |
|--------|-------------|--------------|
| G-005 | Password strength UI not specified | FR-012 |
```

Update index.md:
- Set `deferred_count` in Priority Loop State
- Add to Gap Resolution History with status `deferred`

---

### C2: Finalize Traceability Matrix

Ensure all Requirements have checklist coverage:
```markdown
### Requirements → Checklist Coverage

| FR ID | CHK IDs | Coverage Status | Notes |
|-------|---------|-----------------|-------|
| FR-001 | CHK001, CHK015 | ✓ Covered | - |
| FR-002 | CHK005 | ✓ Covered | - |
| FR-003 | CHK012 | ✓ Covered | Gap resolved in iteration 2 |
```

---

### C3: Generate Quality Report

```markdown
## Specification Quality Report

**Feature**: {{feature_id}}
**Branch**: `{{branch_name}}`

### Validation Summary
| Metric | Value |
|--------|-------|
| Total Iterations | {{iteration_count}} |
| Termination Reason | {{termination_reason}} |
| Critical Gaps Resolved | {{critical_resolved}} |
| Important Gaps Resolved | {{important_resolved}} |
| Minor Gaps Deferred | {{minor_deferred}} |
| Traceability Coverage | {{coverage_percent}}% |

### Files Created
- Spec: `{{spec_path}}`
- Checklist: `{{feature_dir}}/checklists/requirements.md`
- Index: `{{index_path}}`
- Context: `{{specify_context_path}}`

### Specification Stats
- User Stories: {{user_story_count}}
- Functional Requirements: {{requirement_count}}
- Success Criteria: {{criteria_count}}

### Next Steps
1. Review the spec at `{{spec_path}}`
2. Run `/humaninloop:plan` to create implementation plan
```

---

### C4: Update Final State

Update index.md:
```markdown
## Priority Loop State

| Field | Value |
|-------|-------|
| **Loop Status** | completed |
| **Current Iteration** | {{final_iteration}} / 10 |
| **Last Activity** | {{timestamp}} |
| **Termination Reason** | {{reason}} |
| **Deferred Minor Gaps** | {{deferred_count}} |
```

Update Workflow Status Table:
```markdown
| specify | completed | {{timestamp}} | supervisor | specify-context.md |
```

---

## Error Handling

### Scaffold Failure
```markdown
**Scaffold Failed**

Error: {{error_message}}

Please check:
- Git repository is initialized
- `.humaninloop/` directory exists
- You have write permissions
```

### Agent Failure Mid-Loop
```markdown
**Agent Failure in Iteration {{iteration}}**

Error: {{error_message}}
Failed Agent: {{agent_name}}

The workflow state has been preserved in index.md.
Run `/humaninloop-specs:specify` to resume from iteration {{iteration}}.
```

### Stale Escalation
```markdown
**Stale Gaps Detected**

The following gaps have remained unresolved for 3 iterations:

{{gap_list}}

Options:
1. Provide different answers
2. Accept gaps as known limitations
3. Manually edit spec.md
```

---

## State Recovery

The workflow supports resume from any point:

1. **Read index.md** from specs directories
2. **Check Priority Loop State**:
   - `not_started`: Begin Phase A
   - `scaffolding`: Resume A1
   - `spec_writing`: Resume A2
   - `validating`: Resume A3/A4 or B3
   - `clarifying`: Resume B1/B2
   - `completed`: Report already done
   - `terminated`: Report termination reason
3. **Read Gap Priority Queue** to restore gap state
4. **Read Gap Resolution History** to determine progress

---

## Knowledge Sharing Protocol

All agents share state via the **Unified Index Architecture**:

1. **Unified Index File** (`index.md`):
   - Feature Metadata & Document Availability
   - Workflow Status Table
   - Priority Loop State
   - Specification Progress
   - Extracted Signals & Focus Areas
   - Checklist Configuration
   - Gap Priority Queue
   - Traceability Matrix
   - Unified Pending Questions
   - Gap Resolution History
   - Unified Decisions Log
   - Agent Handoff Notes
   - Feature Readiness

2. **Prompt Injection**: Pass extracted data between agents

3. **Filesystem**: Agents read/write spec.md, checklists, index.md

---

## Important Notes

- Do NOT modify git config
- Do NOT push to remote
- Do NOT skip validation phases
- Maximum 10 Priority Loop iterations
- Maximum 3 clarifications per iteration
- Always use Task tool for agents
- Handle AskUserQuestion responses before spawning next agent
- Log all gap resolutions in Gap Resolution History
