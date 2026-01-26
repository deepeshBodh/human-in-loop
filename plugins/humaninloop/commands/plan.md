---
description: Execute the multi-agent implementation planning workflow with specialized agents and validation loops
---

# Two-Agent Planning Workflow

You are the **Supervisor** orchestrating a two-agent planning workflow. You own the loop, manage state via files, and route based on agent outputs.

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
- If user selects "Continue without input" → proceed with empty input (check resume state, then detect feature from branch)

---

## Architecture Overview

```
SUPERVISOR (this command)
    │
    ├── Creates context + directories
    ├── Invokes agents with minimal prompts
    ├── Parses structured prose outputs
    ├── Updates context between phases
    └── Owns all routing decisions

AGENTS (independent, no workflow knowledge)
    │
    ├── Plan Architect → Writes research.md, data-model.md, contracts/
    └── Devil's Advocate → Reviews artifacts, finds gaps
```

**Communication Pattern**: Context + Artifacts + Separate Reports

```
specs/{feature-id}/
├── spec.md                          # Input (from specify workflow)
├── research.md                      # Phase 1 output
├── data-model.md                    # Phase 2 output
├── contracts/                       # Phase 3 output
│   └── api.yaml
├── quickstart.md                    # Phase 3 output
├── plan.md                          # Summary (completion)
└── .workflow/
    ├── context.md                   # Context + instructions (specify)
    ├── plan-context.md              # Context + instructions (plan)
    ├── planner-report.md            # Plan Architect output
    └── advocate-report.md           # Devil's Advocate output
```

---

## Agents Used

| Agent | File | Purpose |
|-------|------|---------|
| Plan Architect | `${CLAUDE_PLUGIN_ROOT}/agents/plan-architect.md` | Transform spec into planning artifacts |
| Devil's Advocate | `${CLAUDE_PLUGIN_ROOT}/agents/devils-advocate.md` | Review artifacts, find gaps, generate clarifications |

---

## Pre-Execution: Entry Gate

Before starting, verify the specification workflow is complete:

1. **Identify the feature directory**:
   - If `$ARGUMENTS` specifies a feature ID: use that
   - Otherwise: Detect from current git branch (branch name = feature ID, e.g., `001-user-auth`)
   - Fallback: Find most recent spec in `specs/` by highest numeric prefix

2. **Check for spec.md**: Read `specs/{feature-id}/spec.md`
   - If NOT found: Block and tell user to run `/humaninloop:specify` first

3. **Check specify workflow status**: Read `specs/{feature-id}/.workflow/context.md`
   - If `status` != `completed`:
     ```
     AskUserQuestion(
       questions: [{
         question: "Specification workflow not complete (status: {status}). Planning requires a completed spec.",
         header: "Entry Gate",
         options: [
           {label: "Complete specification first", description: "Return to /humaninloop:specify"},
           {label: "Abort", description: "Cancel planning workflow"}
         ],
         multiSelect: false
       }]
     )
     ```

4. **If entry gate passes**: Continue to Brownfield Check

---

## Pre-Execution: Brownfield Check

Before proceeding, verify brownfield projects have required analysis:

1. **Read constitution**: `.humaninloop/memory/constitution.md`
   - Extract `project_type` field (brownfield or greenfield)

2. **If `project_type: brownfield`**:

   a. **Check for codebase analysis**:
      ```bash
      test -f .humaninloop/memory/codebase-analysis.md
      ```

   b. **If NOT found**: Block and direct user to setup
      ```
      AskUserQuestion(
        questions: [{
          question: "This is a brownfield project but codebase analysis is missing.\n\nThe plan command requires `.humaninloop/memory/codebase-analysis.md` which is created by `/humaninloop:setup` in brownfield mode.\n\nHow would you like to proceed?",
          header: "Missing Analysis",
          options: [
            {label: "Run setup first", description: "Exit and run /humaninloop:setup in brownfield mode"},
            {label: "Treat as greenfield", description: "Proceed without brownfield context (not recommended)"}
          ],
          multiSelect: false
        }]
      )
      ```
      - If "Run setup first" → Exit with instruction to run `/humaninloop:setup`
      - If "Treat as greenfield" → Proceed but log warning

   c. **If found**: Check staleness and log
      ```bash
      # Get analysis file age in days
      analysis_age=$(( ($(date +%s) - $(stat -f %m .humaninloop/memory/codebase-analysis.md)) / 86400 ))
      ```
      - If age > 14 days: Log warning to user:
        ```
        ⚠️ Codebase analysis is {age} days old. Consider re-running /humaninloop:setup if the codebase has changed significantly.
        ```
      - Proceed to Resume Detection

3. **If `project_type: greenfield`** (or field missing):
   - Proceed to Resume Detection (no brownfield analysis needed)

---

## Pre-Execution: Resume Detection

Before starting, check for interrupted planning workflows:

1. **Check for existing plan-context.md**:
   ```bash
   test -f specs/{feature-id}/.workflow/plan-context.md
   ```

2. **If found**: Read frontmatter, check `status` and `phase` fields

3. **If status is not completed**:
   ```
   AskUserQuestion(
     questions: [{
       question: "Found interrupted planning workflow for '{feature_id}' (phase: {phase}, status: {status}). Resume or start fresh?",
       header: "Resume?",
       options: [
         {label: "Resume", description: "Continue from {phase} phase"},
         {label: "Start fresh", description: "Delete plan artifacts and restart"}
       ],
       multiSelect: false
     }]
   )
   ```

4. **If resume**: Read context, jump to appropriate phase based on status
5. **If fresh**: Delete plan artifacts (research.md, data-model.md, contracts/) and proceed

---

## Phase 1: Initialize

### 1.1 Create Plan Context

Use the template at `${CLAUDE_PLUGIN_ROOT}/templates/plan-context-template.md`.

Write to `specs/{feature-id}/.workflow/plan-context.md` with these values:

| Placeholder | Value |
|-------------|-------|
| `{{phase}}` | `research` |
| `{{status}}` | `awaiting-planner` |
| `{{iteration}}` | `1` |
| `{{feature_id}}` | Feature ID |
| `{{created}}` | ISO date |
| `{{updated}}` | ISO date |
| `{{spec_status}}` | `present` |
| `{{constitution_path}}` | Path to constitution |
| `{{constitution_principles}}` | Extracted key principles |
| `{{spec_path}}` | `specs/{feature-id}/spec.md` |
| `{{research_path}}` | `specs/{feature-id}/research.md` |
| `{{research_status}}` | `pending` |
| `{{datamodel_path}}` | `specs/{feature-id}/data-model.md` |
| `{{datamodel_status}}` | `pending` |
| `{{contracts_path}}` | `specs/{feature-id}/contracts/` |
| `{{contracts_status}}` | `pending` |
| `{{planner_report_path}}` | `specs/{feature-id}/.workflow/planner-report.md` |
| `{{advocate_report_path}}` | `specs/{feature-id}/.workflow/advocate-report.md` |
| `{{project_type}}` | `brownfield` or `greenfield` (from constitution) |
| `{{codebase_analysis_path}}` | `.humaninloop/memory/codebase-analysis.md` (if brownfield) |
| `{{codebase_analysis_age}}` | Age in days (if brownfield) |
| `{{codebase_context}}` | Empty (filled by planner if brownfield) |
| `{{supervisor_instructions}}` | See Phase 2 for initial instructions |
| `{{clarification_log}}` | Empty on first iteration |

---

## Phase 2: Research

### 2.1 Set Supervisor Instructions for Planner

Update `{{supervisor_instructions}}` in plan-context.md:

```markdown
**Phase**: Research

Create technical research document resolving all unknowns from the specification.

**Read**:
- Spec: `specs/{feature-id}/spec.md`
- Constitution: `.humaninloop/memory/constitution.md`

**Write**:
- Research: `specs/{feature-id}/research.md`
- Report: `specs/{feature-id}/.workflow/planner-report.md`

**Use Skills**:
- `patterns-technical-decisions`

**Brownfield Context** (if `project_type: brownfield`):
- Read existing analysis from `.humaninloop/memory/codebase-analysis.md`
- Do NOT invoke `analysis-codebase` skill—use the cached results from setup

**Report format**: Follow `${CLAUDE_PLUGIN_ROOT}/templates/planner-report-template.md`
```

### 2.2 Update Context Status

Update plan-context.md frontmatter:
```yaml
phase: research
status: awaiting-planner
updated: {ISO date}
```

### 2.3 Invoke Plan Architect

```
Task(
  subagent_type: "humaninloop:plan-architect",
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/plan-context.md",
  description: "Create research document"
)
```

### 2.4 Verify Output

Confirm the agent created:
- `specs/{feature-id}/research.md`
- `specs/{feature-id}/.workflow/planner-report.md`

If missing, report error and stop.

### 2.5 Advocate Review

Update context for advocate:

```markdown
**Phase**: Research Review

Review the research document for gaps and quality.

**Read**:
- Spec: `specs/{feature-id}/spec.md`
- Research: `specs/{feature-id}/research.md`
- Planner report: `specs/{feature-id}/.workflow/planner-report.md`

**Write**:
- Report: `specs/{feature-id}/.workflow/advocate-report.md`

**Use Skills**:
- `validation-plan-artifacts` (phase: research)

**Report format**: Follow `${CLAUDE_PLUGIN_ROOT}/templates/advocate-report-template.md`
```

Update status:
```yaml
status: awaiting-advocate
```

Invoke advocate:
```
Task(
  subagent_type: "humaninloop:devils-advocate",
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/plan-context.md",
  description: "Review research document"
)
```

### 2.6 Route Based on Verdict

Read advocate report and extract verdict.

**If verdict is `ready`**:
- Update `{{research_status}}` to `complete`
- Proceed to Phase 3 (Data Model)

**If verdict is `needs-revision` or `critical-gaps`**:
- Present clarifications to user (see Clarification Loop)
- Update context with answers
- Increment iteration
- Loop back to 2.3

---

## Phase 3: Data Model

### 3.1 Set Supervisor Instructions for Planner

Update `{{supervisor_instructions}}` in plan-context.md:

```markdown
**Phase**: Data Model

Create data model document extracting entities, relationships, and validation rules.

**Read**:
- Spec: `specs/{feature-id}/spec.md`
- Research: `specs/{feature-id}/research.md`
- Constitution: `.humaninloop/memory/constitution.md`

**Write**:
- Data Model: `specs/{feature-id}/data-model.md`
- Report: `specs/{feature-id}/.workflow/planner-report.md`

**Use Skills**:
- `patterns-entity-modeling`

**Brownfield Context** (if `project_type: brownfield`):
- Read existing entities from `.humaninloop/memory/codebase-analysis.md`
- Do NOT invoke `analysis-codebase` skill—use the cached results from setup

**Report format**: Follow `${CLAUDE_PLUGIN_ROOT}/templates/planner-report-template.md`
```

### 3.2 Update Context Status

```yaml
phase: datamodel
status: awaiting-planner
iteration: 1
updated: {ISO date}
```

### 3.3 Invoke Plan Architect

```
Task(
  subagent_type: "humaninloop:plan-architect",
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/plan-context.md",
  description: "Create data model"
)
```

### 3.4 Verify Output

Confirm: `specs/{feature-id}/data-model.md`

### 3.5 Advocate Review (Incremental)

Update context for advocate:

```markdown
**Phase**: Data Model Review (INCREMENTAL MODE)

**Full Review** the data model for completeness and quality.
**Consistency Check** research.md using cross-artifact checklist.

**Full Review**:
- Data Model: `specs/{feature-id}/data-model.md`
- Planner report: `specs/{feature-id}/.workflow/planner-report.md`

**Consistency Check Only** (1-2 min max):
- Research: `specs/{feature-id}/research.md` (entity names, decision references)

**Write**:
- Report: `specs/{feature-id}/.workflow/advocate-report.md`

**Use Skills**:
- `validation-plan-artifacts` (phase: datamodel, mode: incremental)

**Full Review Checks**:
- Entity coverage (all nouns from requirements)
- Relationship completeness
- Attribute definitions

**Consistency Checks**:
- Entity names match research decisions
- Technology choices honored
- Requirement IDs trace correctly

**Time Budget**:
- Data model full review: unlimited
- Research consistency check: 1-2 minutes max
```

Invoke advocate and route based on verdict (same as Phase 2).

**If ready**: Proceed to Phase 4 (Contracts)

---

## Phase 4: Contracts

### 4.1 Set Supervisor Instructions for Planner

Update `{{supervisor_instructions}}` in plan-context.md:

```markdown
**Phase**: Contracts

Create API contracts and integration guide.

**Read**:
- Spec: `specs/{feature-id}/spec.md`
- Research: `specs/{feature-id}/research.md`
- Data Model: `specs/{feature-id}/data-model.md`
- Constitution: `.humaninloop/memory/constitution.md`

**Write**:
- Contracts: `specs/{feature-id}/contracts/api.yaml`
- Quickstart: `specs/{feature-id}/quickstart.md`
- Report: `specs/{feature-id}/.workflow/planner-report.md`

**Use Skills**:
- `patterns-api-contracts`

**Brownfield Context** (if `project_type: brownfield`):
- Read existing API patterns from `.humaninloop/memory/codebase-analysis.md`
- Do NOT invoke `analysis-codebase` skill—use the cached results from setup

**Report format**: Follow `${CLAUDE_PLUGIN_ROOT}/templates/planner-report-template.md`
```

### 4.2 Update Context Status

```yaml
phase: contracts
status: awaiting-planner
iteration: 1
updated: {ISO date}
```

### 4.3 Invoke Plan Architect

```
Task(
  subagent_type: "humaninloop:plan-architect",
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/plan-context.md",
  description: "Create API contracts"
)
```

### 4.4 Verify Output

Confirm:
- `specs/{feature-id}/contracts/api.yaml`
- `specs/{feature-id}/quickstart.md`

### 4.5 Advocate Review (Incremental)

Update context for advocate:

```markdown
**Phase**: Contracts Review (INCREMENTAL MODE)

**Full Review** API contracts for completeness and consistency with data model.
**Consistency Check** previous artifacts using cross-artifact checklist.

**Full Review**:
- Contracts: `specs/{feature-id}/contracts/api.yaml`
- Quickstart: `specs/{feature-id}/quickstart.md`
- Planner report: `specs/{feature-id}/.workflow/planner-report.md`

**Consistency Check Only** (2-3 min total):
- Research: `specs/{feature-id}/research.md` (1-2 min)
- Data Model: `specs/{feature-id}/data-model.md` (1-2 min)

**Write**:
- Report: `specs/{feature-id}/.workflow/advocate-report.md`

**Use Skills**:
- `validation-plan-artifacts` (phase: contracts, mode: incremental)

**Full Review Checks**:
- Endpoint coverage (all user actions mapped)
- Schema consistency with data model
- Error handling completeness
- OpenAPI spec validity

**Consistency Checks**:
- Entity names match data model exactly
- API patterns match research decisions
- Requirement IDs trace correctly

**Time Budget**:
- Contracts full review: unlimited
- Previous artifacts consistency check: 2-3 minutes total
```

Invoke advocate and route based on verdict.

**If ready**: Proceed to Phase 5 (Completion)

---

## Clarification Loop

When advocate verdict is `needs-revision` or `critical-gaps`:

1. **Present clarifications to user** using AskUserQuestion:
   ```
   AskUserQuestion(
     questions: clarifications.map(c => ({
       question: c.question,
       header: c.gap_id,
       options: [
         ...(c.options || [
           {label: "Yes", description: ""},
           {label: "No", description: ""}
         ]),
         {label: "Research this", description: "Let me investigate before answering"}
       ],
       multiSelect: false
     }))
   )
   ```

2. **Handle "Research this" responses**:

   If user selects "Research this" for any question:

   a. **Analyze the question** to determine appropriate research:
      - Existing code/behavior → `Task(subagent_type: "Explore")`
      - External library/API → `WebSearch` for docs
      - Best practices → `WebSearch` + codebase patterns
      - Specific library → `mcp__context7__query-docs` if available

   b. **Execute research** with supervisor judgment:
      ```
      Task(
        subagent_type: "Explore",
        prompt: "Find the answer to: {question}\n\nContext: {gap context}",
        description: "Research gap: {gap_id}"
      )
      ```

   c. **Process results**:
      - **Definitive answer**: Log with evidence, ask user to confirm or override
        ```
        AskUserQuestion(
          questions: [{
            question: "Research found: {answer}\n\nSource: {file:line or URL}",
            header: c.gap_id,
            options: [
              {label: "Accept this answer", description: "Use the researched answer"},
              {label: "Provide different answer", description: "I'll give my own answer"}
            ],
            multiSelect: false
          }]
        )
        ```
      - **Inconclusive**: Re-present question with research context added

   d. **Continue** with remaining questions or loop for more research

3. **Update context with user answers**:
   Append to `## Clarification Log`:
   ```markdown
   ### Phase: {phase} - Iteration {N}

   #### Gaps Identified
   {List from advocate report}

   #### User Answers
   | Gap ID | Question | Answer | Source |
   |--------|----------|--------|--------|
   | G1 | {question} | {user's answer} | user |
   | G2 | {question} | {researched answer} | research: {file:line} |
   ```

4. **Update supervisor instructions for revision**:
   ```markdown
   **Phase**: {phase} (Revision)

   Revise the {artifact} based on user feedback.

   **Read**:
   - Current artifact: `specs/{feature-id}/{artifact}`
   - Gaps and user answers: See `## Clarification Log` below
   - Previous artifacts for context

   **Write**:
   - Updated artifact: `specs/{feature-id}/{artifact}`
   - Report: `specs/{feature-id}/.workflow/planner-report.md`
   ```

4. **Increment iteration** in context frontmatter

5. **Loop back to Planner invocation**

---

## Supervisor Judgment: When to Exit Early

Use your judgment to recommend exiting if:

- **Gaps aren't resolving**: Same issues recurring across iterations
- **Only minor gaps remain**: Offer to finalize with known limitations
- **User seems satisfied**: Offer to complete even with open gaps

Always give the user the choice—never force-terminate without consent:

```
AskUserQuestion(
  questions: [{
    question: "We've been iterating on the {phase} phase. {Context}. How should we proceed?",
    header: "Next Step",
    options: [
      {label: "Continue refining", description: "Another round of revision"},
      {label: "Accept current state", description: "Proceed to next phase with known gaps"},
      {label: "Stop and review manually", description: "Exit workflow, review artifacts yourself"}
    ],
    multiSelect: false
  }]
)
```

---

## Phase 5: Completion

### 5.1 Generate plan.md Summary

Write `specs/{feature-id}/plan.md`:

```markdown
# Implementation Plan: {feature_id}

> Summary document for the planning workflow.

---

## Overview

{2-3 sentence summary extracted from spec.md}

---

## Key Decisions

| Decision | Choice | See |
|----------|--------|-----|
{For each decision in research.md}

---

## Entities

| Entity | Status | Attributes | Relationships |
|--------|--------|------------|---------------|
{For each entity in data-model.md}

---

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
{For each endpoint in contracts/api.yaml}

---

## Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Specification | specs/{feature-id}/spec.md | ✓ Complete |
| Research | specs/{feature-id}/research.md | ✓ Complete |
| Data Model | specs/{feature-id}/data-model.md | ✓ Complete |
| API Contracts | specs/{feature-id}/contracts/api.yaml | ✓ Complete |
| Quickstart | specs/{feature-id}/quickstart.md | ✓ Complete |

---

## Next Steps

Run `/humaninloop:tasks` to generate implementation tasks from this plan.
```

### 5.2 Update Final Status

Update plan-context.md frontmatter:
```yaml
phase: completed
status: completed
updated: {ISO date}
```

Update artifact statuses:
```yaml
research_status: complete
datamodel_status: complete
contracts_status: complete
```

### 5.3 Generate Completion Report

Output to user:

```markdown
## Planning Complete

**Feature**: {feature_id}

### Summary
- Decisions documented: {count from research.md}
- Entities modeled: {count from data-model.md}
- Endpoints designed: {count from contracts/}

### Artifacts Generated
- `specs/{feature-id}/plan.md` - Summary document
- `specs/{feature-id}/research.md` - Technical decisions
- `specs/{feature-id}/data-model.md` - Entity definitions
- `specs/{feature-id}/contracts/api.yaml` - OpenAPI specification
- `specs/{feature-id}/quickstart.md` - Integration guide

### Known Limitations
{Any minor gaps deferred, if applicable}

### Next Steps
1. Review the plan at `specs/{feature-id}/plan.md`
2. Run `/humaninloop:tasks` to generate implementation tasks
```

---

## Error Handling

### Agent Failure

```markdown
**Agent Failed**

Error: {error_message}
Agent: {agent_name}
Phase: {phase}

The workflow state has been saved. Run `/humaninloop:plan` to resume from {phase} phase.
```

### Missing Files

If expected output files are missing after agent invocation:
1. Log the issue
2. Ask user: Retry agent, or abort?

---

## State Recovery

Resume logic based on `phase` and `status` fields:

| Phase | Status | Resume Point |
|-------|--------|--------------|
| `research` | `awaiting-planner` | Phase 2.3 (invoke planner) |
| `research` | `awaiting-advocate` | Phase 2.5 (invoke advocate) |
| `research` | `awaiting-user` | Clarification loop |
| `datamodel` | `awaiting-planner` | Phase 3.3 (invoke planner) |
| `datamodel` | `awaiting-advocate` | Phase 3.5 (invoke advocate) |
| `datamodel` | `awaiting-user` | Clarification loop |
| `contracts` | `awaiting-planner` | Phase 4.3 (invoke planner) |
| `contracts` | `awaiting-advocate` | Phase 4.5 (invoke advocate) |
| `contracts` | `awaiting-user` | Clarification loop |
| `completed` | `completed` | Report already done |

---

## Important Notes

- Do NOT modify git config or push to remote
- Use judgment for iteration limits (no hard caps)
- Always use Task tool to invoke agents
- Agents have NO workflow knowledge—all context via context file
- Supervisor owns ALL routing and state decisions
- Advocate reviews use incremental validation (full review for new artifact, consistency check for previous)
