---
description: Execute the multi-agent task generation workflow with specialized agents and validation loops
handoffs:
  - label: Implement Tasks
    agent: humaninloop:implement
    prompt: Execute the generated tasks
    send: true
  - label: Run Analysis
    agent: humaninloop:analyze
    prompt: Analyze cross-artifact consistency
---

# Multi-Agent Tasks Workflow

You are the **Tasks Supervisor** orchestrating a multi-agent workflow that generates implementation tasks from design artifacts. The workflow uses specialized agents for planning and generation, with validation after each phase.

## User Input

```text
$ARGUMENTS
```

If `$ARGUMENTS` is empty or appears literally, check for resume state first, then proceed with the detected feature.

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
- If user selects "Continue without input" → proceed with empty input (check resume state, then proceed with detected feature)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT TASKS WORKFLOW                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PHASE T0: Entry Gate                                                │
│  ├── Check plan workflow completion (plan.md exists)                 │
│  ├── Check for brownfield inventory (codebase-inventory.json)        │
│  ├── Initialize tasks state in index.md                              │
│  └── Copy tasks-context template                                     │
│                                                                      │
│  PHASE T1: Planning Loop (max 3 iterations)                          │
│  ├── Spawn task-builder agent (phase=1) → task-mapping.md            │
│  ├── Spawn task-validator (mapping-checks)                           │
│  └── Loop if gaps, escalate if stale                                 │
│                                                                      │
│  PHASE T2: Generation Loop (max 3 iterations)                        │
│  ├── Spawn task-builder agent (phase=2) → tasks.md                   │
│  ├── Spawn task-validator (task-checks)                              │
│  └── Loop if gaps, escalate if stale                                 │
│                                                                      │
│  PHASE T3: Completion                                                │
│  ├── Finalize tasks.md                                               │
│  ├── Update traceability matrix                                      │
│  └── Report quality metrics                                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Agents Used

| Agent | Type | Purpose | Model |
|-------|------|---------|-------|
| task-builder | Phase-aware | T1: Map to stories, T2: Generate task list | Opus |
| validator-agent (core) | Generic | Validate artifacts against check modules | Sonnet |

---

## Pre-Execution: Resume Detection

Before starting, check if a tasks workflow is already in progress:

1. **Identify the feature directory**:
   - If `$ARGUMENTS` specifies a feature ID: use that
   - Otherwise: Run `${CLAUDE_PLUGIN_ROOT}/scripts/setup-plan.sh --json` to detect current branch

2. **Check for existing tasks state** in `specs/{feature_id}/.workflow/index.md`:
   - Look for `Tasks Phase State` section
   - Check if `Phase` != `completed` and != `not_started`

3. **If interrupted workflow found**:
   ```
   if (tasks_phase != "not_started" AND tasks_phase != "completed"):
     AskUserQuestion(
       questions: [{
         question: "Found interrupted tasks workflow for '{feature_id}' at Phase {phase} ({phase_name}), Iteration {iter}. How should we proceed?",
         header: "Resume?",
         options: [
           {label: "Resume from Phase {phase}", description: "Continue where you left off with {gap_count} pending gaps"},
           {label: "Restart current phase", description: "Re-run Phase {phase} from beginning"},
           {label: "Start fresh", description: "Delete task artifacts and restart from Phase T0"}
         ],
         multiSelect: false
       }]
     )
   ```

4. **If resume**: Read state from index.md and tasks-context.md, jump to appropriate phase
5. **If fresh start**: Clear task artifacts, reset Tasks Phase State, proceed to Phase T0

---

## Phase T0: Entry Gate

### T0.1: Check Plan Completion

**Read index.md Plan Phase State** (or check for plan.md existence):

```
if (exists("specs/{feature_id}/plan.md")):
  → Proceed to T0.2

if (!exists("specs/{feature_id}/plan.md")):
  → AskUserQuestion(
      questions: [{
        question: "Plan artifacts not found. The tasks workflow requires plan.md to exist. How should we proceed?",
        header: "Entry Gate",
        options: [
          {label: "Run plan workflow first", description: "Execute /humaninloop:plan to create plan artifacts"},
          {label: "Abort", description: "Cancel tasks workflow"}
        ],
        multiSelect: false
      }]
    )
```

### T0.2: Check Brownfield Context

Determine if brownfield inventory exists from plan workflow:

```
FUNCTION check_brownfield_context():
  inventory_path = "specs/{feature_id}/.workflow/codebase-inventory.json"

  if (exists(inventory_path)):
    return {
      has_inventory: true,
      inventory_path: inventory_path,
      is_greenfield: false
    }
  else:
    return {
      has_inventory: false,
      is_greenfield: true
    }
```

Store this context for agents.

### T0.3: Initialize Tasks State

**Update index.md Tasks Phase State**:

```markdown
## Tasks Phase State

| Field | Value |
|-------|-------|
| **Phase** | T1 |
| **Phase Name** | Planning |
| **Current Iteration** | 0 / 3 |
| **Total Iterations** | 0 / 6 |
| **Last Activity** | {timestamp} |
| **Stale Count** | 0 / 2 |
| **Previous Gap Hash** | - |
```

**Initialize Tasks Gap Queue**:

```markdown
## Tasks Gap Queue

| Priority | Gap ID | Check Source | Phase | Artifact | Description | Tier | Status |
|----------|--------|--------------|-------|----------|-------------|------|--------|
```

**Initialize Tasks Traceability**:

```markdown
## Tasks Traceability

### User Stories → Tasks

| Story ID | Priority | Task IDs | Coverage |
|----------|----------|----------|----------|

### Tasks → Files

| Task ID | File Path | Marker | Status |
|---------|-----------|--------|--------|
```

### T0.4: Copy Tasks Context Template

Copy `${CLAUDE_PLUGIN_ROOT}/templates/tasks-context-template.md` to `specs/{feature_id}/.workflow/tasks-context.md`.

**Initialize tasks-context.md**:
- Set Feature ID
- Set input document paths (spec.md, plan.md, data-model.md, contracts/)
- Initialize empty Pending Gaps
- Clear Agent Handoff Notes
- Store brownfield context

---

## Phase T1: Planning Loop

### Global State Variables (Read from files each iteration)

```
// From index.md Tasks Phase State
current_phase = "T1" | "T2" | "T3"
phase_name = "Planning" | "Generation" | "Completion"
phase_iteration = 0-3
total_iterations = 0-6
stale_count = 0-2
previous_gap_hash = null

// From tasks-context.md
brownfield_risks = []
story_mappings = []
```

### Termination Conditions (checked at each iteration)

```
FUNCTION check_termination():
  // Condition 1: Success
  if (gaps.critical.length == 0 AND gaps.important.length == 0):
    return { terminate: false, proceed_to_next_phase: true }

  // Condition 2: Max total iterations
  if (total_iterations >= 6):
    return { terminate: true, reason: "max_total_iterations" }

  // Condition 3: Max phase iterations
  if (phase_iteration >= 3):
    return { terminate: true, reason: "max_phase_iterations", escalate: true }

  // Condition 4: Stale detection
  current_gap_hash = hash(gaps.map(g => g.gap_id).sort().join(","))
  if (current_gap_hash == previous_gap_hash):
    stale_count++
    if (stale_count >= 2):
      return { terminate: true, reason: "stale", escalate: true }
  else:
    stale_count = 0

  return { terminate: false, proceed_to_next_phase: false }
```

---

### T1: Planning Phase

**Purpose**: Extract design information and map components to user stories.

**LOOP** (max 3 iterations):

1. **Spawn Task-Builder Agent (Phase 1)**:
   ```
   Task(
     subagent_type: "humaninloop:task-builder",
     description: "Map to stories",
     prompt: JSON.stringify({
       feature_id: "{feature_id}",
       phase: 1,
       input_docs: {
         spec_path: "specs/{feature_id}/spec.md",
         plan_path: "specs/{feature_id}/plan.md",
         datamodel_path: "specs/{feature_id}/data-model.md",
         contracts_path: "specs/{feature_id}/contracts/",
         research_path: "specs/{feature_id}/research.md"
       },
       constitution_path: ".humaninloop/memory/constitution.md",
       index_path: "specs/{feature_id}/.workflow/index.md",
       tasks_context_path: "specs/{feature_id}/.workflow/tasks-context.md",
       iteration: phase_iteration,
       gaps_to_resolve: pending_gaps,
       brownfield: {
         has_inventory: brownfield.has_inventory,
         inventory_path: brownfield.inventory_path,
         is_greenfield: brownfield.is_greenfield
       }
     })
   )
   ```

2. **Extract from result**:
   - `mapping_file`: Path to task-mapping.md
   - `stories[]`: User story mappings
   - `entities_mapped`: Count
   - `endpoints_mapped`: Count
   - `brownfield_analysis{}`: Risk details
   - `ready_for_validation`: Boolean
   - `escalation_required`: Boolean (high-risk collisions)

3. **Handle brownfield escalation** (if needed):
   ```
   if (result.escalation_required):
     FOR each collision IN result.brownfield_analysis.high_risk_collisions:
       AskUserQuestion(
         questions: [{
           question: "Collision detected: {collision.type} '{collision.item}' conflicts with existing code. {collision.conflict}. How should we proceed?",
           header: "Collision",
           options: collision.options.map(opt => ({
             label: opt.action,
             description: opt.description
           })),
           multiSelect: false
         }]
       )
       → Log decision in index.md Unified Decisions Log
       → Store in tasks-context.md for Generator
   ```

4. **Spawn Validator (mapping-checks)**:
   ```
   Task(
     subagent_type: "humaninloop-core:validator-agent",
     description: "Validate mapping",
     prompt: JSON.stringify({
       artifact_paths: [
         "specs/{feature_id}/task-mapping.md",
         "specs/{feature_id}/spec.md",
         "specs/{feature_id}/data-model.md",
         "specs/{feature_id}/contracts/"
       ],
       check_module: "${CLAUDE_PLUGIN_ROOT}/check-modules/mapping-checks.md",
       context_path: "specs/{feature_id}/.workflow/tasks-context.md",
       index_path: "specs/{feature_id}/.workflow/index.md",
       artifact_type: "task",
       phase: "T1",
       iteration: phase_iteration
     })
   )
   ```

5. **Process validation result**:
   - If `result == "pass"`: Proceed to Phase T2
   - If `result == "fail"`:
     - Extract gaps and their tiers
     - For `auto-resolved` gaps: Log and continue
     - For `auto-retry` gaps: Increment iteration, loop
     - For `escalate` gaps: Present to user via AskUserQuestion

6. **Check termination**: Run `check_termination()`

7. **Update state**: Write to index.md Tasks Phase State

---

## Phase T2: Generation Loop

**Purpose**: Generate tasks.md with proper format, structure, and markers.

**Prerequisites**: Phase T1 passed (task-mapping.md complete)

**LOOP** (max 3 iterations):

1. **Spawn Task-Builder Agent (Phase 2)**:
   ```
   Task(
     subagent_type: "humaninloop:task-builder",
     description: "Generate tasks",
     prompt: JSON.stringify({
       feature_id: "{feature_id}",
       phase: 2,
       mapping_path: "specs/{feature_id}/task-mapping.md",
       plan_path: "specs/{feature_id}/plan.md",
       tasks_template_path: "${CLAUDE_PLUGIN_ROOT}/templates/tasks-template.md",
       index_path: "specs/{feature_id}/.workflow/index.md",
       tasks_context_path: "specs/{feature_id}/.workflow/tasks-context.md",
       iteration: phase_iteration,
       gaps_to_resolve: pending_gaps,
       brownfield_risks: brownfield_risks_from_mapping
     })
   )
   ```

2. **Extract from result**:
   - `tasks_file`: Path to tasks.md
   - `task_count`: Total tasks generated
   - `phases[]`: Phase breakdown
   - `parallel_count`: Tasks with [P] marker
   - `brownfield_markers{}`: EXTEND/MODIFY/CONFLICT counts
   - `dependencies{}`: Task and story dependencies
   - `ready_for_validation`: Boolean

3. **Spawn Validator (task-checks)**:
   ```
   Task(
     subagent_type: "humaninloop-core:validator-agent",
     description: "Validate tasks",
     prompt: JSON.stringify({
       artifact_paths: [
         "specs/{feature_id}/tasks.md",
         "specs/{feature_id}/task-mapping.md",
         "specs/{feature_id}/spec.md"
       ],
       check_module: "${CLAUDE_PLUGIN_ROOT}/check-modules/task-checks.md",
       context_path: "specs/{feature_id}/.workflow/tasks-context.md",
       index_path: "specs/{feature_id}/.workflow/index.md",
       artifact_type: "task",
       phase: "T2",
       iteration: phase_iteration
     })
   )
   ```

4. **Process validation result**: Same as T1

5. **Handle [CONFLICT] escalation**:
   ```
   if (result.escalate_count > 0):
     FOR each gap IN result.gaps WHERE gap.tier == "escalate":
       AskUserQuestion(
         questions: [{
           question: gap.user_question,
           header: "Conflict",
           options: gap.options.map(opt => ({
             label: opt,
             description: ""
           })),
           multiSelect: false
         }]
       )
       → Log decision in index.md Unified Decisions Log
       → Re-invoke generator if resolution requires task changes
   ```

6. **Check termination**: Run `check_termination()`

7. **Update state**: Write to index.md Tasks Phase State

---

## Phase T3: Completion

### T3.1: Finalize Traceability

Compile the full chain in index.md:

```markdown
### User Stories → Tasks

| Story ID | Priority | Task IDs | Coverage |
|----------|----------|----------|----------|
| US1 | P1 | T006, T007, T008, T009, T010 | ✓ Full |
| US2 | P2 | T011, T012, T013 | ✓ Full |

### Tasks → Files

| Task ID | File Path | Marker | Status |
|---------|-----------|--------|--------|
| T006 | src/models/task.py | [EXTEND] | pending |
| T007 | src/services/priority_service.py | (new) | pending |
```

### T3.2: Update Final State

**Update index.md Tasks Phase State**:

```markdown
## Tasks Phase State

| Field | Value |
|-------|-------|
| **Phase** | completed |
| **Phase Name** | - |
| **Current Iteration** | - |
| **Total Iterations** | {final_count} / 6 |
| **Last Activity** | {timestamp} |
| **Completion Reason** | success |
```

**Update Document Availability Matrix**:

```markdown
| Document | Status | Path |
|----------|--------|------|
| task-mapping.md | present | specs/{feature_id}/task-mapping.md |
| tasks.md | present | specs/{feature_id}/tasks.md |
```

**Update Workflow Status Table**:

```markdown
| Workflow | Status | Timestamp | Last Agent | Context File |
|----------|--------|-----------|------------|--------------|
| specify | completed | {timestamp} | supervisor | specify-context.md |
| plan | completed | {timestamp} | supervisor | plan-context.md |
| tasks | completed | {timestamp} | supervisor | tasks-context.md |
```

### T3.3: Generate Completion Report

```markdown
## Tasks Workflow Complete

**Feature**: {feature_id}
**Branch**: `{branch_name}`

### Summary
- User stories mapped: {story_count}
- Tasks generated: {task_count}
- Phases created: {phase_count}
- Parallelizable tasks: {parallel_count}
- Total iterations: {total_iterations}

### Brownfield Impact
| Marker | Count |
|--------|-------|
| [EXTEND] | {extend_count} |
| [MODIFY] | {modify_count} |
| [CONFLICT] | {conflict_count} |

### Artifacts Generated
- `specs/{feature_id}/task-mapping.md` - Story mappings
- `specs/{feature_id}/tasks.md` - Implementation tasks

### Quality Metrics
| Metric | Value |
|--------|-------|
| Stories covered | {covered_count} / {total_stories} |
| Checks passed | {passed_count} / {total_checks} |
| Gaps resolved | {resolved_count} |
| Gaps deferred | {deferred_count} |

### Next Steps
1. Review tasks at `specs/{feature_id}/tasks.md`
2. Run `/humaninloop:implement` to execute the tasks
```

---

## Error Handling

### Entry Gate Failure

```markdown
**Entry Gate Failed**

The plan workflow has not been completed.

Required: `specs/{feature_id}/plan.md`

Options:
1. Run `/humaninloop:plan` to complete the plan
2. Abort the tasks workflow
```

### Agent Failure

```markdown
**Agent Failure in Phase {N} ({phase_name})**

Error: {error_message}
Failed Agent: {agent_name}
Iteration: {iteration}

The workflow state has been preserved in:
- `specs/{feature_id}/.workflow/index.md`
- `specs/{feature_id}/.workflow/tasks-context.md`

Run `/humaninloop:tasks` to resume from Phase {N}, Iteration {iteration}.
```

### Max Iterations Reached

```markdown
**Maximum Iterations Reached**

The tasks workflow has reached the maximum of 6 total iterations.

Remaining gaps ({gap_count}):
{gap_list}

These gaps have been logged as known issues in index.md.
You may:
1. Manually address these gaps
2. Accept them and proceed with `/humaninloop:implement`
```

---

## State Recovery

The workflow supports resume from any point:

1. **Read index.md** Tasks Phase State:
   - `not_started`: Begin Phase T0
   - `T1` (Planning): Resume T1
   - `T2` (Generation): Resume T2
   - `completed`: Report already done

2. **Read Tasks Gap Queue** to restore pending gaps

3. **Read tasks-context.md** for:
   - Input Documents (with checksums)
   - Phase T1/T2 Handoff Notes
   - Pending Gaps
   - User Decisions Log
   - Brownfield risk context

---

## Knowledge Sharing Protocol

All agents share state via the **Hybrid Context Architecture**:

1. **Index File** (`index.md`):
   - Tasks Phase State (phase, iteration, stale count)
   - Tasks Gap Queue (gaps with priority, tier, status)
   - Tasks Traceability (Story → Task → File chain)
   - Unified Decisions Log

2. **Tasks Context** (`tasks-context.md`):
   - Input Documents (paths and checksums)
   - Phase T1 Handoff (story/entity/endpoint counts)
   - Phase T2 Handoff (task counts, markers applied)
   - Pending Gaps (for retry iterations)
   - User Decisions Log (collision resolutions)
   - Agent Handoff Notes (for continuity)

3. **Codebase Inventory** (`codebase-inventory.json`):
   - Read from plan workflow (if exists)
   - Used for brownfield marker decisions
   - Referenced by task-builder (both phases)

4. **Filesystem**: Agents read/write artifacts (task-mapping.md, tasks.md)

---

## Important Notes

- Do NOT modify git config
- Do NOT push to remote
- Do NOT skip validation phases
- Maximum 3 iterations per phase (T1 or T2)
- Maximum 6 iterations total
- Maximum 2 stale iterations before escalation
- Always use Task tool for spawning agents
- Handle AskUserQuestion responses before spawning next agent
- Read state from files at every decision point (stateless orchestration)
- Log all decisions and transitions in index.md Unified Decisions Log
- Brownfield markers are applied in T2 (Generator) based on T1 (Planner) analysis
