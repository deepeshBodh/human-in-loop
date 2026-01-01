---
description: Execute the multi-agent implementation planning workflow with specialized agents and validation loops
handoffs:
  - label: Create Tasks
    agent: humaninloop:tasks
    prompt: Generate tasks from the plan
    send: true
  - label: Run Checklist
    agent: humaninloop:checklist
    prompt: Create a checklist for implementation review
---

# Multi-Agent Planning Workflow

You are the **Plan Supervisor** orchestrating a multi-agent workflow that creates implementation plans from feature specifications. The workflow uses specialized agents for research, domain modeling, and API contracts, with validation after each phase.

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
│                    MULTI-AGENT PLANNING WORKFLOW                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PHASE A0: Discovery Gate (Brownfield Support)                       │
│  ├── Check if discovery needed (brownfield vs greenfield)            │
│  ├── Run codebase-discovery agent (if needed)                        │
│  ├── Handle collision risks (escalate high-risk to user)            │
│  └── Initialize codebase context in plan-context.md                  │
│                                                                      │
│  PHASE A1: Entry Gate                                                │
│  ├── Check specify workflow completion                               │
│  ├── Initialize plan state in index.md                              │
│  └── Copy plan-context template                                      │
│                                                                      │
│  PHASE B: Agent Loop (C-lite)                                        │
│  ├── B0: Research Phase (max 3 iterations)                          │
│  │   ├── Spawn plan-research agent                                  │
│  │   ├── Spawn plan-validator (research-checks)                     │
│  │   └── Loop if gaps, escalate if stale                            │
│  │                                                                   │
│  ├── B1: Domain Model Phase (max 3 iterations)                      │
│  │   ├── Spawn plan-domain-model agent                              │
│  │   ├── Spawn plan-validator (model-checks)                        │
│  │   └── Loop if gaps, escalate if stale                            │
│  │                                                                   │
│  ├── B2: Contract Phase (max 3 iterations)                          │
│  │   ├── Spawn plan-contract agent                                  │
│  │   ├── Spawn plan-validator (contract-checks)                     │
│  │   └── Loop if gaps, escalate if stale                            │
│  │                                                                   │
│  └── B3: Final Validation                                            │
│      ├── Spawn plan-validator (final-checks)                        │
│      └── Loop back to affected phase if cross-artifact gaps         │
│                                                                      │
│  PHASE C: Completion                                                 │
│  ├── Generate plan.md summary                                        │
│  ├── Finalize traceability matrix                                   │
│  └── Report quality metrics                                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Agents Used

| Agent | Type | Purpose | Model |
|-------|------|---------|-------|
| codebase-discovery | Specialized | Analyze existing codebase, detect collisions (Phase A0) | Sonnet |
| plan-research | Specialized | Resolve unknowns, document decisions | Sonnet |
| plan-domain-model | Specialized | Extract entities, relationships, validation | Opus |
| plan-contract | Specialized | Map endpoints, schemas, quickstart | Opus |
| plan-validator | Modular | Validate artifacts against check modules | Sonnet |

---

## Pre-Execution: Resume Detection

Before starting, check if a planning workflow is already in progress:

1. **Identify the feature directory**:
   - If `$ARGUMENTS` specifies a feature ID: use that
   - Otherwise: Run `${CLAUDE_PLUGIN_ROOT}/scripts/setup-plan.sh --json` to detect current branch and feature paths

2. **Check for existing plan state** in `specs/{feature_id}/.workflow/index.md`:
   - Look for `Plan Phase State` section
   - Check if `Phase` != `completed` and != `not_started`

3. **Check for discovery state** in index.md `Codebase Discovery Summary`:
   - If `Discovery Status` == `not_run`: Discovery not started
   - If `Discovery Status` == `partial`: Discovery interrupted
   - If `Discovery Status` == `completed` or `skipped_greenfield`: Discovery done

4. **If interrupted workflow found**:
   ```
   // If interrupted at discovery
   if (discovery_status == "partial"):
     AskUserQuestion(
       questions: [{
         question: "Found interrupted codebase discovery for '{feature_id}'. How should we proceed?",
         header: "Resume?",
         options: [
           {label: "Re-run discovery", description: "Start fresh discovery scan"},
           {label: "Skip discovery", description: "Proceed as greenfield (no codebase context)"},
           {label: "Abort", description: "Cancel planning workflow"}
         ],
         multiSelect: false
       }]
     )

   // If interrupted at planning phases
   else if (phase >= 0 AND phase < completed):
     AskUserQuestion(
       questions: [{
         question: "Found interrupted planning workflow for '{feature_id}' at Phase {N} ({phase_name}), Iteration {iter}. How should we proceed?",
         header: "Resume?",
         options: [
           {label: "Resume from Phase {N}", description: "Continue where you left off with {gap_count} pending gaps"},
           {label: "Restart current phase", description: "Re-run Phase {N} from beginning"},
           {label: "Start fresh", description: "Delete plan artifacts and restart from Phase A0"}
         ],
         multiSelect: false
       }]
     )
   ```

5. **If resume**: Read state from index.md and plan-context.md, jump to appropriate phase
6. **If fresh start**: Clear plan artifacts, reset Plan Phase State, proceed to Phase A0

---

## Phase A0: Discovery Gate (Brownfield Support)

> Phase A0 runs before the Entry Gate to analyze existing codebases and provide context for planning agents.
> This phase is skipped for greenfield projects (no existing code).

### A0.1: Check Discovery Need

Determine if the project is brownfield (existing code) or greenfield (new project):

```
FUNCTION check_brownfield_indicators():
  indicators = []

  // Check for source directories
  if (exists("src/") OR exists("app/") OR exists("lib/")):
    indicators.push("source_directory")

  // Check for package files
  if (exists("package.json") OR exists("requirements.txt") OR exists("go.mod")):
    indicators.push("package_manager")

  // Check for model/entity files
  model_files = Glob("**/*model*.{ts,py,go,java}")
  entity_files = Glob("**/*entity*.{ts,py,go,java}")
  if (model_files.length > 0 OR entity_files.length > 0):
    indicators.push("model_files")

  // Check for existing specs (indicates previous features)
  if (Glob("specs/*/spec.md").length > 1):
    indicators.push("existing_features")

  return {
    is_brownfield: indicators.length >= 2,
    indicators: indicators
  }
```

**Decision logic**:
```
result = check_brownfield_indicators()

if (!result.is_brownfield):
  // Greenfield - skip discovery
  → Update index.md Discovery Status = "skipped_greenfield"
  → Proceed directly to Phase A1

if (result.is_brownfield):
  // Brownfield - check if discovery already done
  if (discovery_status == "completed"):
    → Verify codebase-inventory.json exists and is valid
    → Proceed to A0.4 (inject context)
  else:
    → Proceed to A0.2 (run discovery)
```

### A0.2: Run Codebase Discovery

Spawn the codebase-discovery agent to analyze the existing codebase:

```
Task(
  subagent_type: "codebase-discovery",
  description: "Discover existing codebase",
  prompt: JSON.stringify({
    feature_id: "{feature_id}",
    spec_path: "specs/{feature_id}/spec.md",
    constitution_path: ".humaninloop/memory/constitution.md",
    claude_md_path: "CLAUDE.md",
    index_path: "specs/{feature_id}/.workflow/index.md",
    plan_context_path: "specs/{feature_id}/.workflow/plan-context.md",
    bounds: {
      max_files: 50,
      max_depth: 4,
      timeout_sec: 180
    },
    brownfield_overrides: brownfield_overrides_from_constitution
  })
)
```

**Extract from result**:
- `inventory_path`: Path to codebase-inventory.json
- `summary`: Discovery statistics
- `collision_risks[]`: Detected collision risks
- `greenfield`: Boolean (true if no substantial code found)

**Handle result**:
```
if (result.greenfield):
  → Update index.md Discovery Status = "skipped_greenfield"
  → Proceed to Phase A1

if (result.status == "partial" OR result.status == "timeout"):
  → Log warning in index.md
  → Proceed with partial results

if (result.status == "failed"):
  → AskUserQuestion: "Discovery failed. Skip and proceed as greenfield?"
```

### A0.3: Handle Collision Risks

Process collision risks detected by discovery:

```
FOR each collision IN collision_risks:
  if (collision.risk_level == "high"):
    // Escalate to user
    AskUserQuestion(
      questions: [{
        question: "Collision detected: {collision.type} '{collision.spec_item}' conflicts with existing '{collision.existing_item}'. How should we proceed?",
        header: "Collision",
        options: collision.resolution_options.map(opt => ({
          label: opt.action,
          description: opt.description
        })),
        multiSelect: false
      }]
    )
    → Log decision in index.md Collision Resolutions
    → Store in plan-context.md for downstream agents

  else if (collision.risk_level == "medium"):
    // Auto-apply recommended action
    → Log in index.md: "Auto-resolved: {collision.recommended_action}"
    → Store in plan-context.md

  else: // low risk
    → Log in index.md for awareness
```

### A0.4: Initialize Codebase Context

Inject filtered discovery results into plan-context.md for downstream agents:

**Read codebase-inventory.json and populate plan-context.md sections**:

```
// For Research Agent (Phase B0)
plan_context.codebase_context.for_research = {
  tech_stack: inventory.project_info.languages + inventory.project_info.frameworks,
  dependencies: inventory.dependencies,
  architecture_pattern: inventory.project_info.architecture_pattern
}

// For Domain Model Agent (Phase B1)
plan_context.codebase_context.for_domain_model = {
  existing_entities: inventory.entities.map(e => ({
    name: e.name,
    file_path: e.file_path,
    fields: e.fields,
    collision_risk: find_collision_for(e.name)
  })),
  vocabulary: inventory.domain_vocabulary
}

// For Contract Agent (Phase B2)
plan_context.codebase_context.for_contracts = {
  existing_endpoints: inventory.endpoints,
  api_patterns: inventory.conventions.api_patterns
}
```

**Update index.md Codebase Discovery Summary**:

```markdown
## Codebase Discovery Summary

| Field | Value |
|-------|-------|
| **Discovery Status** | completed |
| **Inventory Path** | `specs/{feature_id}/.workflow/codebase-inventory.json` |
| **Last Run** | {timestamp} |
| **Greenfield** | false |

### Existing Codebase Stats

| Metric | Count |
|--------|-------|
| Files Scanned | {files_scanned} |
| Entities Found | {entities_count} |
| Endpoints Found | {endpoints_count} |
| Collision Risks | {collision_count} |

### Detected Tech Stack

{tech_stack_list}
```

### A0.5: Proceed to Entry Gate

Discovery complete. Proceed to Phase A1 (Entry Gate).

---

## Phase A1: Entry Gate

### A1.1: Check Specify Completion

**Read index.md Priority Loop State**:

```
if (specify.loop_status == "completed"):
  → Proceed to A1.2

if (specify.loop_status != "completed"):
  → AskUserQuestion(
      questions: [{
        question: "Specification workflow not complete (status: {status}). How should we proceed?",
        header: "Entry Gate",
        options: [
          {label: "Proceed anyway (Recommended)", description: "Plan with current spec, may have gaps"},
          {label: "Complete specification first", description: "Return to /humaninloop-specs:specify"},
          {label: "Abort", description: "Cancel planning workflow"}
        ],
        multiSelect: false
      }]
    )
```

### A1.2: Initialize Plan State

**Update index.md Plan Phase State**:

```markdown
## Plan Phase State

| Field | Value |
|-------|-------|
| **Phase** | 0 |
| **Phase Name** | Research |
| **Current Iteration** | 0 / 3 |
| **Total Iterations** | 0 / 10 |
| **Last Activity** | {timestamp} |
| **Stale Count** | 0 / 2 |
```

**Initialize Plan Gap Queue**:

```markdown
## Plan Gap Queue

| Priority | Gap ID | Check Source | Phase | Artifact | Description | Tier | Status |
|----------|--------|--------------|-------|----------|-------------|------|--------|
```

**Initialize Plan Traceability**:

```markdown
## Plan Traceability

### Requirements → Entities

| FR ID | Entities | Coverage |
|-------|----------|----------|

### Entities → Endpoints

| Entity | Endpoints | Coverage |
|--------|-----------|----------|

### Full Traceability Chain

| FR ID | Entity | Endpoint | Coverage |
|-------|--------|----------|----------|
```

### A1.3: Copy Plan Context Template

Copy `${CLAUDE_PLUGIN_ROOT}/templates/plan-context-template.md` to `specs/{feature_id}/.workflow/plan-context.md`.

**Initialize plan-context.md**:
- Set Feature ID
- Set Spec Path
- Initialize empty Entity Registry
- Initialize empty Endpoint Registry
- Clear Agent Handoff Notes

---

## Phase B: Agent Loop

### Global State Variables (Read from files each iteration)

```
// From index.md Plan Phase State
current_phase = 0-3
phase_name = "Research" | "Domain Model" | "Contracts" | "Final Validation"
phase_iteration = 0-3
total_iterations = 0-10
stale_count = 0-2
previous_gap_hash = null

// From plan-context.md
entity_registry = {}
endpoint_registry = []
technical_decisions = []
```

### Termination Conditions (checked at each iteration)

```
FUNCTION check_termination():
  // Condition 1: Success
  if (gaps.critical.length == 0 AND gaps.important.length == 0):
    return { terminate: false, proceed_to_next_phase: true }

  // Condition 2: Max total iterations
  if (total_iterations >= 10):
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

### B0: Research Phase

**Purpose**: Resolve all technical unknowns from the spec.

**LOOP** (max 3 iterations):

1. **Spawn Research Agent**:
   ```
   Task(
     subagent_type: "plan-research",
     description: "Research unknowns",
     prompt: JSON.stringify({
       feature_id: "{feature_id}",
       spec_path: "specs/{feature_id}/spec.md",
       constitution_path: ".humaninloop/memory/constitution.md",
       index_path: "specs/{feature_id}/.workflow/index.md",
       plan_context_path: "specs/{feature_id}/.workflow/plan-context.md",
       phase: 0,
       iteration: phase_iteration,
       gaps_to_resolve: pending_gaps  // from previous validation, if any
     })
   )
   ```

2. **Extract from result**:
   - `research_file`: Path to research.md
   - `resolved_unknowns[]`: Decisions made
   - `unresolved_count`: Any remaining unknowns
   - `ready_for_validation`: Boolean

3. **Spawn Validator (research-checks)**:
   ```
   Task(
     subagent_type: "plan-validator",
     description: "Validate research",
     prompt: JSON.stringify({
       feature_id: "{feature_id}",
       phase: 0,
       check_module: "${CLAUDE_PLUGIN_ROOT}/check-modules/research-checks.md",
       artifacts: {
         spec_path: "specs/{feature_id}/spec.md",
         research_path: "specs/{feature_id}/research.md"
       },
       constitution_path: ".humaninloop/memory/constitution.md",
       index_path: "specs/{feature_id}/.workflow/index.md",
       plan_context_path: "specs/{feature_id}/.workflow/plan-context.md",
       iteration: phase_iteration
     })
   )
   ```

4. **Process validation result**:
   - If `result == "pass"`: Proceed to Phase B1
   - If `result == "fail"`:
     - Extract gaps and their tiers
     - For `auto-resolved` gaps: Log and continue
     - For `auto-retry` gaps: Increment iteration, loop
     - For `escalate` gaps: Present to user via AskUserQuestion

5. **Check termination**: Run `check_termination()`

6. **Update state**: Write to index.md Plan Phase State

---

### B1: Domain Model Phase

**Purpose**: Extract entities, relationships, and validation rules.

**Prerequisites**: Phase B0 passed (research.md complete)

**LOOP** (max 3 iterations):

1. **Spawn Domain Model Agent**:
   ```
   Task(
     subagent_type: "plan-domain-model",
     description: "Create data model",
     prompt: JSON.stringify({
       feature_id: "{feature_id}",
       spec_path: "specs/{feature_id}/spec.md",
       research_path: "specs/{feature_id}/research.md",
       constitution_path: ".humaninloop/memory/constitution.md",
       index_path: "specs/{feature_id}/.workflow/index.md",
       plan_context_path: "specs/{feature_id}/.workflow/plan-context.md",
       phase: 1,
       iteration: phase_iteration,
       gaps_to_resolve: pending_gaps
     })
   )
   ```

2. **Extract from result**:
   - `datamodel_file`: Path to data-model.md
   - `entity_registry{}`: Entity definitions
   - `entity_count`: Number of entities
   - `relationship_count`: Number of relationships
   - `traceability{}`: FR → Entity mapping

3. **Store entity_registry** in plan-context.md for Contract Agent

4. **Spawn Validator (model-checks)**:
   ```
   Task(
     subagent_type: "plan-validator",
     description: "Validate data model",
     prompt: JSON.stringify({
       feature_id: "{feature_id}",
       phase: 1,
       check_module: "${CLAUDE_PLUGIN_ROOT}/check-modules/model-checks.md",
       artifacts: {
         spec_path: "specs/{feature_id}/spec.md",
         research_path: "specs/{feature_id}/research.md",
         datamodel_path: "specs/{feature_id}/data-model.md"
       },
       constitution_path: ".humaninloop/memory/constitution.md",
       index_path: "specs/{feature_id}/.workflow/index.md",
       plan_context_path: "specs/{feature_id}/.workflow/plan-context.md",
       iteration: phase_iteration
     })
   )
   ```

5. **Process validation result**: Same as B0

6. **Update Plan Traceability**: Populate Requirements → Entities section

---

### B2: Contract Phase

**Purpose**: Design API endpoints, schemas, and integration guide.

**Prerequisites**: Phase B1 passed (data-model.md complete)

**LOOP** (max 3 iterations):

1. **Spawn Contract Agent**:
   ```
   Task(
     subagent_type: "plan-contract",
     description: "Create API contracts",
     prompt: JSON.stringify({
       feature_id: "{feature_id}",
       spec_path: "specs/{feature_id}/spec.md",
       datamodel_path: "specs/{feature_id}/data-model.md",
       research_path: "specs/{feature_id}/research.md",
       constitution_path: ".humaninloop/memory/constitution.md",
       index_path: "specs/{feature_id}/.workflow/index.md",
       plan_context_path: "specs/{feature_id}/.workflow/plan-context.md",
       entity_registry: entity_registry,  // from plan-context.md
       phase: 2,
       iteration: phase_iteration,
       gaps_to_resolve: pending_gaps
     })
   )
   ```

2. **Extract from result**:
   - `contract_files[]`: Paths to OpenAPI specs
   - `quickstart_file`: Path to quickstart.md
   - `endpoint_registry[]`: Endpoint definitions
   - `schema_count`: Number of schemas
   - `traceability{}`: FR → Endpoint mapping

3. **Store endpoint_registry** in plan-context.md

4. **Spawn Validator (contract-checks)**:
   ```
   Task(
     subagent_type: "plan-validator",
     description: "Validate contracts",
     prompt: JSON.stringify({
       feature_id: "{feature_id}",
       phase: 2,
       check_module: "${CLAUDE_PLUGIN_ROOT}/check-modules/contract-checks.md",
       artifacts: {
         spec_path: "specs/{feature_id}/spec.md",
         research_path: "specs/{feature_id}/research.md",
         datamodel_path: "specs/{feature_id}/data-model.md",
         contracts_path: "specs/{feature_id}/contracts/",
         quickstart_path: "specs/{feature_id}/quickstart.md"
       },
       constitution_path: ".humaninloop/memory/constitution.md",
       index_path: "specs/{feature_id}/.workflow/index.md",
       plan_context_path: "specs/{feature_id}/.workflow/plan-context.md",
       iteration: phase_iteration
     })
   )
   ```

5. **Process validation result**: Same as B0/B1

6. **Update Plan Traceability**: Populate Entities → Endpoints section

---

### B3: Final Validation

**Purpose**: Cross-artifact consistency and full constitution sweep.

**Prerequisites**: All artifacts generated

1. **Spawn Validator (final-checks)**:
   ```
   Task(
     subagent_type: "plan-validator",
     description: "Final validation",
     prompt: JSON.stringify({
       feature_id: "{feature_id}",
       phase: 3,
       check_module: "${CLAUDE_PLUGIN_ROOT}/check-modules/final-checks.md",
       artifacts: {
         spec_path: "specs/{feature_id}/spec.md",
         research_path: "specs/{feature_id}/research.md",
         datamodel_path: "specs/{feature_id}/data-model.md",
         contracts_path: "specs/{feature_id}/contracts/",
         quickstart_path: "specs/{feature_id}/quickstart.md"
       },
       constitution_path: ".humaninloop/memory/constitution.md",
       index_path: "specs/{feature_id}/.workflow/index.md",
       plan_context_path: "specs/{feature_id}/.workflow/plan-context.md",
       iteration: 1
     })
   )
   ```

2. **Process validation result**:
   - If `result == "pass"`: Proceed to Phase C
   - If `result == "fail"`:
     - Check `loop_back_target` for each gap
     - Loop back to affected phase (B0, B1, or B2)
     - This is how final validation catches cross-artifact issues

3. **Loop-back logic**:
   | Gap Type | Loop Back To |
   |----------|--------------|
   | Research-related | Phase B0 |
   | Entity/model issues | Phase B1 |
   | Contract/endpoint issues | Phase B2 |
   | Constitution issues | Escalate to user |

---

## Phase C: Completion

### C1: Generate plan.md Summary

The Supervisor writes `specs/{feature_id}/plan.md`:

```markdown
# Implementation Plan: {feature_id}

> Summary document for the planning workflow.
> Generated by Plan Supervisor.

---

## Overview

{2-3 sentence summary extracted from spec.md}

---

## Key Decisions

| Decision | Choice | See |
|----------|--------|-----|
{For each decision in plan-context.md Technical Decisions}

---

## Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Research | specs/{feature_id}/research.md | ✓ Complete |
| Data Model | specs/{feature_id}/data-model.md | ✓ Complete |
| API Contracts | specs/{feature_id}/contracts/ | ✓ Complete |
| Quickstart | specs/{feature_id}/quickstart.md | ✓ Complete |

---

## Constitution Alignment

{Summary from plan-context.md Constitution Check Results}

---

## Quality Metrics

| Metric | Value |
|--------|-------|
| Total Iterations | {total_iterations} |
| Gaps Resolved | {resolved_count} |
| Gaps Deferred (Minor) | {deferred_count} |

---

## Full Traceability

{Copy from index.md Plan Traceability - Full Traceability Chain}

---

## Next Steps

Run `/humaninloop:tasks` to generate implementation tasks from this plan.
```

### C2: Finalize Traceability Matrix

Compile the full chain in index.md:

```markdown
### Full Traceability Chain

| FR ID | Entity | Endpoint | Coverage |
|-------|--------|----------|----------|
| FR-001 | User | POST /auth/login | ✓ Full |
| FR-002 | User, Session | POST /auth/login, GET /auth/session | ✓ Full |
| FR-003 | Session | DELETE /auth/logout | ✓ Full |
```

### C3: Update Final State

**Update index.md Plan Phase State**:

```markdown
## Plan Phase State

| Field | Value |
|-------|-------|
| **Phase** | completed |
| **Phase Name** | - |
| **Current Iteration** | - |
| **Total Iterations** | {final_count} / 10 |
| **Last Activity** | {timestamp} |
| **Completion Reason** | success |
```

**Update Document Availability Matrix**:

```markdown
| Document | Status | Path |
|----------|--------|------|
| spec.md | present | specs/{feature_id}/spec.md |
| research.md | present | specs/{feature_id}/research.md |
| data-model.md | present | specs/{feature_id}/data-model.md |
| contracts/ | present | specs/{feature_id}/contracts/ |
| quickstart.md | present | specs/{feature_id}/quickstart.md |
| plan.md | present | specs/{feature_id}/plan.md |
```

**Update Workflow Status Table**:

```markdown
| Workflow | Status | Timestamp | Last Agent | Context File |
|----------|--------|-----------|------------|--------------|
| specify | completed | {timestamp} | supervisor | specify-context.md |
| plan | completed | {timestamp} | supervisor | plan-context.md |
```

### C4: Generate Completion Report

```markdown
## Planning Workflow Complete

**Feature**: {feature_id}
**Branch**: `{branch_name}`

### Summary
- Research decisions: {decision_count}
- Entities modeled: {entity_count}
- API endpoints: {endpoint_count}
- Total iterations: {total_iterations}

### Artifacts Generated
- `specs/{feature_id}/plan.md` - Summary document
- `specs/{feature_id}/research.md` - Technical decisions
- `specs/{feature_id}/data-model.md` - Entity definitions
- `specs/{feature_id}/contracts/api.yaml` - OpenAPI specification
- `specs/{feature_id}/quickstart.md` - Integration guide

### Constitution Alignment
{alignment_status}

### Next Steps
1. Review the plan at `specs/{feature_id}/plan.md`
2. Run `/humaninloop:tasks` to generate implementation tasks
```

---

## Error Handling

### Entry Gate Failure

```markdown
**Entry Gate Failed**

The specification workflow is not complete.

Options:
1. Run `/humaninloop-specs:specify` to complete the spec
2. Use `/humaninloop:plan --force` to proceed anyway
```

### Agent Failure

```markdown
**Agent Failure in Phase {N} ({phase_name})**

Error: {error_message}
Failed Agent: {agent_name}
Iteration: {iteration}

The workflow state has been preserved in:
- `specs/{feature_id}/.workflow/index.md`
- `specs/{feature_id}/.workflow/plan-context.md`

Run `/humaninloop:plan` to resume from Phase {N}, Iteration {iteration}.
```

### Constitution Violation

```markdown
**Constitution Violation Detected**

Principle: {principle_name}
Violation: {violation_description}

This requires human decision. Options:
1. Modify the design to comply with the principle
2. Document a justified exception
3. Abort the workflow

The workflow will pause until you decide.
```

### Max Iterations Reached

```markdown
**Maximum Iterations Reached**

The planning workflow has reached the maximum of 10 total iterations.

Remaining gaps ({gap_count}):
{gap_list}

These gaps have been logged as known issues in index.md.
You may:
1. Manually address these gaps
2. Accept them and proceed with `/humaninloop:tasks`
```

---

## State Recovery

The workflow supports resume from any point:

1. **Read index.md** Codebase Discovery Summary:
   - `not_run`: Begin Phase A0 (Discovery Gate)
   - `partial`: Resume A0 or skip to A1
   - `completed` or `skipped_greenfield`: Proceed to A1 or B phases

2. **Read index.md** Plan Phase State:
   - `not_started`: Begin Phase A1
   - `0` (Research): Resume B0
   - `1` (Domain Model): Resume B1
   - `2` (Contracts): Resume B2
   - `3` (Final): Resume B3
   - `completed`: Report already done

3. **Read Plan Gap Queue** to restore pending gaps

4. **Read plan-context.md** for:
   - Codebase Context (if discovery completed - for all agents)
   - Entity Registry (if past Phase B1)
   - Endpoint Registry (if past Phase B2)
   - Technical Decisions (if past Phase B0)
   - Agent Handoff Notes (context from completed phases)
   - Collision Risk Summary and Resolutions

---

## Knowledge Sharing Protocol

All agents share state via the **Hybrid Context Architecture**:

1. **Index File** (`index.md`):
   - Codebase Discovery Summary (from Phase A0)
   - Plan Phase State (phase, iteration, stale count)
   - Plan Gap Queue (gaps with priority, tier, status)
   - Plan Traceability (FR → Entity → Endpoint chain)
   - Unified Decisions Log

2. **Plan Context** (`plan-context.md`):
   - Codebase Context (filtered from inventory, per phase)
   - Collision Risk Summary and Resolutions
   - Technical Decisions (from Research Agent)
   - Entity Registry (from Domain Model Agent)
   - Endpoint Registry (from Contract Agent)
   - Agent Handoff Notes (for continuity)
   - Constitution Check Results (per phase)

3. **Codebase Inventory** (`codebase-inventory.json`):
   - Full discovery output (entities, endpoints, features, vocabulary)
   - Used by Phase A0 to populate plan-context.md
   - Referenced by agents for collision checking

4. **Prompt Injection**: Pass extracted/filtered codebase context to agents

5. **Filesystem**: Agents read/write artifacts (research.md, data-model.md, etc.)

---

## Important Notes

- Do NOT modify git config
- Do NOT push to remote
- Do NOT skip validation phases
- Maximum 3 iterations per phase
- Maximum 10 iterations total
- Maximum 2 stale iterations before escalation
- Always use Task tool for spawning agents
- Handle AskUserQuestion responses before spawning next agent
- Read state from files at every decision point (stateless orchestration)
- Log all decisions and transitions in index.md Unified Decisions Log
