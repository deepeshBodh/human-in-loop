---
description: Execute the multi-agent implementation planning workflow with specialized agents and validation loops
---

# Unified Planning Workflow

You are the **Supervisor** orchestrating a unified planning workflow across two phases (Analysis → Design). You own the loop, manage state via files, and route based on agent outputs.

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
    ├── Technical Analyst → Phase 1: requirements.md, constraints-and-decisions.md, nfrs.md
    │                     → Phase 2: data-model.md, contracts/api.yaml, quickstart.md
    ├── Principal Architect → Feasibility intersection review (Phase 1 only)
    └── Devil's Advocate → Completeness review (both phases)
```

**Communication Pattern**: Context + Artifacts + Separate Reports

```
specs/{feature-id}/
├── spec.md                          # Input (from specify workflow)
├── requirements.md                  # Phase 1 output
├── constraints-and-decisions.md     # Phase 1 output
├── nfrs.md                          # Phase 1 output
├── data-model.md                    # Phase 2 output (includes sensitivity)
├── contracts/                       # Phase 2 output
│   └── api.yaml                     # (includes integration boundaries)
├── quickstart.md                    # Phase 2 output
├── plan.md                          # Summary (completion)
└── .workflow/
    ├── context.md                   # Context + instructions (specify)
    ├── plan-context.md              # Context + instructions (plan)
    ├── techanalyst-report.md        # Technical Analyst output
    ├── architect-report.md          # Principal Architect feasibility report
    └── advocate-report.md           # Devil's Advocate completeness report
```

---

## Agents Used

| Agent | File | Purpose |
|-------|------|---------|
| Technical Analyst | `${CLAUDE_PLUGIN_ROOT}/agents/technical-analyst.md` | Produce analysis and design artifacts |
| Principal Architect | `${CLAUDE_PLUGIN_ROOT}/agents/principal-architect.md` | Review cross-artifact feasibility (Phase 1 only) |
| Devil's Advocate | `${CLAUDE_PLUGIN_ROOT}/agents/devils-advocate.md` | Review completeness, find gaps, check consistency |

---

## Pre-Execution: Constitution Check

Before any workflow execution, verify that the project constitution exists:

1. **Check for constitution file** at `.humaninloop/memory/constitution.md`
2. **If NOT found**, display the following and STOP execution:

```
Constitution Required

The HumanInLoop plan workflow requires a project constitution to be configured.

The constitution defines project principles that guide planning quality validation.

To set up your constitution, run:
/humaninloop:setup

This will walk you through defining your project's core principles.

Then retry /humaninloop:plan
```

3. **If found**: Continue to Entry Gate

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

4. **If resume**: Read context, jump to appropriate phase based on status (see State Recovery)
5. **If fresh**: Delete plan artifacts and proceed

---

## Phase 1: Initialize

### 1.1 Create Plan Context

Use the template at `${CLAUDE_PLUGIN_ROOT}/templates/plan-context-template.md`.

Write to `specs/{feature-id}/.workflow/plan-context.md` with these values:

| Placeholder | Value |
|-------------|-------|
| `{{phase}}` | `analysis` |
| `{{status}}` | `awaiting-analyst` |
| `{{iteration}}` | `1` |
| `{{feature_id}}` | Feature ID |
| `{{created}}` | ISO date |
| `{{updated}}` | ISO date |
| `{{analysis_status}}` | `pending` |
| `{{design_status}}` | `pending` |
| `{{spec_status}}` | `present` |
| `{{spec_path}}` | `specs/{feature-id}/spec.md` |
| `{{requirements_path}}` | `specs/{feature-id}/requirements.md` |
| `{{requirements_status}}` | `pending` |
| `{{constraints_decisions_path}}` | `specs/{feature-id}/constraints-and-decisions.md` |
| `{{constraints_decisions_status}}` | `pending` |
| `{{nfrs_path}}` | `specs/{feature-id}/nfrs.md` |
| `{{nfrs_status}}` | `pending` |
| `{{datamodel_path}}` | `specs/{feature-id}/data-model.md` |
| `{{datamodel_status}}` | `pending` |
| `{{contracts_path}}` | `specs/{feature-id}/contracts/` |
| `{{contracts_status}}` | `pending` |
| `{{quickstart_path}}` | `specs/{feature-id}/quickstart.md` |
| `{{quickstart_status}}` | `pending` |
| `{{analyst_report_path}}` | `specs/{feature-id}/.workflow/techanalyst-report.md` |
| `{{architect_report_path}}` | `specs/{feature-id}/.workflow/architect-report.md` |
| `{{advocate_report_path}}` | `specs/{feature-id}/.workflow/advocate-report.md` |
| `{{constitution_path}}` | Path to constitution |
| `{{constitution_principles}}` | Extracted key principles |
| `{{project_type}}` | `brownfield` or `greenfield` (from constitution) |
| `{{codebase_analysis_path}}` | `.humaninloop/memory/codebase-analysis.md` (if brownfield) |
| `{{codebase_analysis_age}}` | Age in days (if brownfield) |
| `{{codebase_context}}` | Empty (filled by analyst if brownfield) |
| `{{supervisor_instructions}}` | See Phase 2 for initial instructions |
| `{{clarification_log}}` | Empty on first iteration |

---

## Phase 2: Analysis

### 2.1 Set Supervisor Instructions for Technical Analyst

Update `{{supervisor_instructions}}` in plan-context.md:

```markdown
**Phase**: Analysis

Translate the business specification into technical requirements, constraints, decisions, and non-functional requirements.

**Read**:
- Spec: `specs/{feature-id}/spec.md`
- Constitution: `.humaninloop/memory/constitution.md`

**Write**:
- Technical Requirements: `specs/{feature-id}/requirements.md`
- Constraints and Decisions: `specs/{feature-id}/constraints-and-decisions.md`
- Non-Functional Requirements: `specs/{feature-id}/nfrs.md`
- Report: `specs/{feature-id}/.workflow/techanalyst-report.md`

**Use Skills**:
- `authoring-technical-requirements`
- `patterns-technical-decisions`

**Brownfield Context** (if `project_type: brownfield`):
- Read existing analysis from `.humaninloop/memory/codebase-analysis.md`
- Do NOT invoke `analysis-codebase` skill—use the cached results from setup

**Report format**: Follow `${CLAUDE_PLUGIN_ROOT}/templates/techanalyst-report-template.md`
```

### 2.2 Update Context Status

Update plan-context.md frontmatter:
```yaml
phase: analysis
status: awaiting-analyst
updated: {ISO date}
```

### 2.3 Invoke Technical Analyst

```
Task(
  subagent_type: "humaninloop:technical-analyst",
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/plan-context.md",
  description: "Create analysis artifacts"
)
```

### 2.4 Verify Output

Confirm the agent created:
- `specs/{feature-id}/requirements.md`
- `specs/{feature-id}/constraints-and-decisions.md`
- `specs/{feature-id}/nfrs.md`
- `specs/{feature-id}/.workflow/techanalyst-report.md`

If missing, report error and stop.

### 2.5 Principal Architect Feasibility Review

Update context for architect:

```markdown
**Phase**: Analysis Feasibility Review

Review the analysis artifacts for cross-artifact contradictions and feasibility.

**Read**:
- Spec: `specs/{feature-id}/spec.md`
- Technical Requirements: `specs/{feature-id}/requirements.md`
- Constraints and Decisions: `specs/{feature-id}/constraints-and-decisions.md`
- Non-Functional Requirements: `specs/{feature-id}/nfrs.md`
- Analyst report: `specs/{feature-id}/.workflow/techanalyst-report.md`

**Write**:
- Report: `specs/{feature-id}/.workflow/architect-report.md`

**Focus Areas** (cross-artifact contradictions ONLY):
- Constraint-decision conflicts: Do technology decisions contradict hard constraints?
- NFR-constraint impossibilities: Do NFR targets conflict with constraints or chosen technologies?
- Requirement-constraint contradictions: Do any TRs assume capabilities not available under stated constraints?
- Decision-decision conflicts: Do any technology choices contradict each other?

**Out of Scope** (handled by Devil's Advocate):
- Individual artifact completeness
- Whether alternatives were properly considered
- Whether NFRs are individually measurable
- Formatting or style issues

**Report format**: Follow `${CLAUDE_PLUGIN_ROOT}/templates/architect-report-template.md`
```

Update status:
```yaml
status: awaiting-architect
```

Invoke architect:
```
Task(
  subagent_type: "humaninloop:principal-architect",
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/plan-context.md",
  description: "Review analysis feasibility"
)
```

### 2.6 Route Based on Architect Verdict

Read architect report and extract verdict.

**If verdict is `feasible`**:
- Proceed to 2.7 (Devil's Advocate review)

**If verdict is `infeasible` or `needs-revision`**:
- Enter Feasibility Rejection Loop (see below)
- After user decision and analyst revision → re-submit to architect (back to 2.5)

### 2.7 Devil's Advocate Completeness Review

Update context for advocate:

```markdown
**Phase**: Analysis Completeness Review

Review the analysis artifacts for completeness and gaps.

**Read**:
- Spec: `specs/{feature-id}/spec.md`
- Technical Requirements: `specs/{feature-id}/requirements.md`
- Constraints and Decisions: `specs/{feature-id}/constraints-and-decisions.md`
- Non-Functional Requirements: `specs/{feature-id}/nfrs.md`
- Analyst report: `specs/{feature-id}/.workflow/techanalyst-report.md`

**Write**:
- Report: `specs/{feature-id}/.workflow/advocate-report.md`

**Use Skills**:
- `validation-plan-artifacts` (phase: P1)

**Focus Areas**:
- FR coverage: Is every functional requirement from spec.md mapped to at least one TR?
- Orphan TRs: Are there technical requirements with no business source?
- Testable criteria: Does every TR have measurable acceptance criteria?
- Sourced constraints: Is every constraint traceable to a real limitation (not a preference)?
- Decision quality: Were 2+ alternatives considered for each decision? Does each have rationale?
- Constraint-decision cross-refs: Does each decision reference the constraints that shaped it?
- NFR measurability: Does every NFR have a specific, measurable target and measurement method?
- NFR sources: Do NFR sources trace to valid TRs or business requirements?

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
  description: "Review analysis completeness"
)
```

### 2.8 Route Based on Advocate Verdict

Read advocate report and extract verdict.

**If verdict is `ready`**:
- Update `analysis_status` to `complete`
- Update `requirements_status`, `constraints_decisions_status`, `nfrs_status` to `complete`
- Proceed to Phase 3 (Design)

**If verdict is `needs-revision` or `critical-gaps`**:
- Enter Clarification Loop (see below)
- After user answers and analyst revision → route back:
  - **Skip architect re-review** UNLESS structural changes occurred:
    - New constraints added or existing constraints changed
    - Requirement scope expanded significantly
    - NFR targets modified
  - If only clarifications were addressed (adding detail, fixing traceability) → go directly to 2.7
  - If structural changes occurred → go back to 2.5

---

## Phase 3: Design

### 3.1 Set Supervisor Instructions for Technical Analyst

Update `{{supervisor_instructions}}` in plan-context.md:

```markdown
**Phase**: Design

Create data model, API contracts, and integration guide based on the analysis artifacts.

**Read**:
- Spec: `specs/{feature-id}/spec.md`
- Technical Requirements: `specs/{feature-id}/requirements.md`
- Constraints and Decisions: `specs/{feature-id}/constraints-and-decisions.md`
- Non-Functional Requirements: `specs/{feature-id}/nfrs.md`
- Constitution: `.humaninloop/memory/constitution.md`

**Write**:
- Data Model: `specs/{feature-id}/data-model.md`
- API Contracts: `specs/{feature-id}/contracts/api.yaml`
- Integration Guide: `specs/{feature-id}/quickstart.md`
- Report: `specs/{feature-id}/.workflow/techanalyst-report.md`

**Use Skills**:
- `patterns-entity-modeling`
- `patterns-api-contracts`

**Brownfield Context** (if `project_type: brownfield`):
- Read existing analysis from `.humaninloop/memory/codebase-analysis.md`
- Do NOT invoke `analysis-codebase` skill—use the cached results from setup

**Report format**: Follow `${CLAUDE_PLUGIN_ROOT}/templates/techanalyst-report-template.md`
```

### 3.2 Update Context Status

```yaml
phase: design
status: awaiting-analyst
iteration: 1
updated: {ISO date}
```

### 3.3 Invoke Technical Analyst

```
Task(
  subagent_type: "humaninloop:technical-analyst",
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/plan-context.md",
  description: "Create design artifacts"
)
```

### 3.4 Verify Output

Confirm the agent created:
- `specs/{feature-id}/data-model.md`
- `specs/{feature-id}/contracts/api.yaml`
- `specs/{feature-id}/quickstart.md`

If missing, report error and stop.

### 3.5 Devil's Advocate Review (Incremental)

Update context for advocate:

```markdown
**Phase**: Design Review (INCREMENTAL MODE)

**Full Review** the design artifacts for completeness and quality.
**Consistency Check** analysis artifacts using cross-artifact checklist.

**Full Review**:
- Data Model: `specs/{feature-id}/data-model.md`
- API Contracts: `specs/{feature-id}/contracts/api.yaml`
- Integration Guide: `specs/{feature-id}/quickstart.md`
- Analyst report: `specs/{feature-id}/.workflow/techanalyst-report.md`

**Consistency Check Only** (2-3 min max):
- Requirements: `specs/{feature-id}/requirements.md`
- Constraints and Decisions: `specs/{feature-id}/constraints-and-decisions.md`
- NFRs: `specs/{feature-id}/nfrs.md`

**Write**:
- Report: `specs/{feature-id}/.workflow/advocate-report.md`

**Use Skills**:
- `validation-plan-artifacts` (phase: P2, mode: incremental)

**Full Review Checks**:
- Entity coverage (all nouns from requirements modeled)
- Attribute completeness and relationship definitions
- Data sensitivity annotations (PII classified, Confidential+ attributes have full handling requirements)
- Endpoint coverage (all user actions mapped)
- Schema-model consistency (schemas match data model entities)
- Error handling completeness
- Integration boundaries (x-integration documentation for external system endpoints)
- Integration guide usability

**Consistency Checks**:
- Entity names match requirement references
- Technology choices from decisions honored in design
- Requirement IDs trace correctly
- Sensitivity-contract alignment: API responses respect data classification (no Restricted data in responses)
- Integration-contract alignment: Contract integration boundaries match systems implied by requirements
- NFR-design feasibility: Can the design as specified meet the NFR targets?

**Time Budget**:
- Design full review: unlimited
- Analysis consistency check: 2-3 minutes max

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
  description: "Review design completeness"
)
```

### 3.6 Route Based on Verdict

Read advocate report and extract verdict.

**If verdict is `ready`**:
- Update `design_status` to `complete`
- Update `datamodel_status`, `contracts_status`, `quickstart_status` to `complete`
- Proceed to Phase 4 (Completion)

**If verdict is `needs-revision` or `critical-gaps`**:
- Enter Clarification Loop
- After user answers and analyst revision → loop back to 3.5

---

## Feasibility Rejection Loop

When the Principal Architect verdict is `infeasible` or `needs-revision`:

1. **Present architect's concerns to user** using AskUserQuestion:
   ```
   AskUserQuestion(
     questions: issues.map(issue => ({
       question: "Feasibility concern: {issue.description}\n\nEvidence: {issue.evidence}\n\nImpact on design: {issue.impact}\n\nSuggested resolution: {issue.suggested_resolution}",
       header: issue.id || "Feasibility",
       options: [
         {label: "Accept resolution", description: "Apply the suggested resolution"},
         {label: "Relax requirement", description: "Reduce the target or remove the constraint"},
         {label: "Keep as-is", description: "Proceed despite the concern (architect will re-review)"},
         {label: "Provide direction", description: "I'll give specific guidance"}
       ],
       multiSelect: false
     }))
   )
   ```

2. **Log user decisions** in clarification log:
   ```markdown
   ### Phase: Analysis - Feasibility Iteration {N}

   #### Architect Concerns
   {List from architect report}

   #### User Decisions
   | Issue | Decision | User Direction |
   |-------|----------|----------------|
   | {issue} | {accept/relax/keep/custom} | {user's specific direction} |
   ```

3. **Update supervisor instructions for revision**:
   ```markdown
   **Phase**: Analysis (Feasibility Revision)

   Revise the analysis artifacts based on user decisions about feasibility concerns.

   **Read**:
   - Current artifacts: `specs/{feature-id}/requirements.md`, `specs/{feature-id}/constraints-and-decisions.md`, `specs/{feature-id}/nfrs.md`
   - Architect concerns and user decisions: See `## Clarification Log` below
   - Spec: `specs/{feature-id}/spec.md`

   **Write**:
   - Updated artifacts as needed
   - Report: `specs/{feature-id}/.workflow/techanalyst-report.md`

   **Report format**: Follow `${CLAUDE_PLUGIN_ROOT}/templates/techanalyst-report-template.md`
   ```

4. **Increment iteration** in context frontmatter

5. **Re-invoke Technical Analyst** → then re-submit to Principal Architect

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

   Revise the artifacts based on user feedback.

   **Read**:
   - Current artifacts (see File Paths table in context)
   - Gaps and user answers: See `## Clarification Log` below
   - Spec: `specs/{feature-id}/spec.md`

   **Write**:
   - Updated artifacts as needed
   - Report: `specs/{feature-id}/.workflow/techanalyst-report.md`

   **Report format**: Follow `${CLAUDE_PLUGIN_ROOT}/templates/techanalyst-report-template.md`
   ```

5. **Increment iteration** in context frontmatter

6. **Loop back to Technical Analyst invocation**

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

## Phase 4: Completion

### 4.1 Generate plan.md Summary

Use the template at `${CLAUDE_PLUGIN_ROOT}/templates/plan-template.md`.

Write `specs/{feature-id}/plan.md` by extracting:
- Key decisions from `constraints-and-decisions.md`
- Entity summary from `data-model.md` (including sensitivity)
- Endpoint summary from `contracts/api.yaml` (including integrations)

### 4.2 Update Final Status

Update plan-context.md frontmatter:
```yaml
phase: completed
status: completed
analysis_status: complete
design_status: complete
updated: {ISO date}
```

Update all artifact statuses to `complete`.

### 4.3 Generate Completion Report

Output to user:

```markdown
## Planning Complete

**Feature**: {feature_id}

### Summary
- Technical Requirements: {count from requirements.md}
- Constraints: {count from constraints-and-decisions.md}
- Decisions: {count from constraints-and-decisions.md}
- Non-Functional Requirements: {count from nfrs.md}
- Entities modeled: {count from data-model.md}
- Endpoints designed: {count from contracts/api.yaml}

### Artifacts Generated
- `specs/{feature-id}/requirements.md` - FR → TR mapping
- `specs/{feature-id}/constraints-and-decisions.md` - Hard boundaries and technology choices
- `specs/{feature-id}/nfrs.md` - Performance and quality targets
- `specs/{feature-id}/data-model.md` - Entity definitions with sensitivity annotations
- `specs/{feature-id}/contracts/api.yaml` - OpenAPI specification with integration boundaries
- `specs/{feature-id}/quickstart.md` - Integration guide
- `specs/{feature-id}/plan.md` - Summary document

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
| `analysis` | `awaiting-analyst` | Phase 2.3 (invoke analyst) |
| `analysis` | `awaiting-architect` | Phase 2.5 (invoke architect) |
| `analysis` | `awaiting-advocate` | Phase 2.7 (invoke advocate) |
| `analysis` | `awaiting-user` | Clarification or Feasibility loop |
| `design` | `awaiting-analyst` | Phase 3.3 (invoke analyst) |
| `design` | `awaiting-advocate` | Phase 3.5 (invoke advocate) |
| `design` | `awaiting-user` | Clarification loop |
| `completed` | `completed` | Report already done |

---

## Important Notes

- Do NOT modify git config or push to remote
- Use judgment for iteration limits (no hard caps)
- Always use Task tool to invoke agents
- Agents have NO workflow knowledge—all context via context file
- Supervisor owns ALL routing and state decisions
- Architect reviews feasibility ONCE after Phase 1 only—prevents wasting time reviewing completeness of infeasible requirements
- After advocate-driven revisions in Phase 1, skip architect re-review unless structural changes occurred (new constraints, changed requirement scope, modified NFR targets)
- Phase 2 has NO architect review—Devil's Advocate handles both completeness and cross-artifact consistency via incremental mode
- Advocate reviews in Phase 2 use incremental validation (full review for new design artifacts, consistency check for Phase 1 analysis artifacts)
