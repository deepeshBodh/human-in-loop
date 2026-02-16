---
description: Execute the multi-agent technical specification workflow with three agents and validation loops
---

# Three-Agent Technical Specification Workflow

You are the **Supervisor** orchestrating a three-agent technical specification workflow. You own the loop, manage state via files, and route based on agent outputs.

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
    ├── Technical Analyst → Writes requirements.md, constraints.md, nfrs.md, integrations.md, data-sensitivity.md
    ├── Principal Architect → Reviews feasibility, validates constraints and NFR measurability
    └── Devil's Advocate → Reviews completeness, finds gaps, checks consistency
```

**Communication Pattern**: Context + Artifacts + Separate Reports

```
specs/{feature-id}/
├── spec.md                          # Input (from specify workflow)
├── technical/                       # Techspec output
│   ├── requirements.md              # Business FR → Technical TR mapping
│   ├── constraints.md               # Tech constraints & migration needs
│   ├── nfrs.md                      # Non-functional requirements
│   ├── integrations.md              # System boundaries & external deps
│   └── data-sensitivity.md          # Data classification & security
└── .workflow/
    ├── context.md                   # Context + instructions (specify)
    ├── techspec-context.md          # Context + instructions (techspec)
    ├── techanalyst-report.md        # Technical Analyst output
    ├── architect-report.md          # Principal Architect feasibility report
    └── advocate-report.md           # Devil's Advocate completeness report
```

---

## Agents Used

| Agent | File | Purpose |
|-------|------|---------|
| Technical Analyst | `${CLAUDE_PLUGIN_ROOT}/agents/technical-analyst.md` | Translate business FR into technical requirements |
| Principal Architect | `${CLAUDE_PLUGIN_ROOT}/agents/principal-architect.md` | Review feasibility, validate constraints and NFR measurability |
| Devil's Advocate | `${CLAUDE_PLUGIN_ROOT}/agents/devils-advocate.md` | Review completeness, find gaps, check consistency |

---

## Pre-Execution: Constitution Check

Before any workflow execution, verify that the project constitution exists:

1. **Check for constitution file** at `.humaninloop/memory/constitution.md`
2. **If NOT found**, display the following and STOP execution:

```
Constitution Required

The HumanInLoop techspec workflow requires a project constitution to be configured.

The constitution defines project principles that guide technical specification quality validation.

To set up your constitution, run:
/humaninloop:setup

This will walk you through defining your project's core principles.

Then retry /humaninloop:techspec
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
         question: "Specification workflow not complete (status: {status}). Technical specification requires a completed spec.",
         header: "Entry Gate",
         options: [
           {label: "Complete specification first", description: "Return to /humaninloop:specify"},
           {label: "Abort", description: "Cancel techspec workflow"}
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
          question: "This is a brownfield project but codebase analysis is missing.\n\nThe techspec command requires `.humaninloop/memory/codebase-analysis.md` which is created by `/humaninloop:setup` in brownfield mode.\n\nHow would you like to proceed?",
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

Before starting, check for interrupted techspec workflows:

1. **Check for existing techspec-context.md**:
   ```bash
   test -f specs/{feature-id}/.workflow/techspec-context.md
   ```

2. **If found**: Read frontmatter, check `status` and `phase` fields

3. **If status is not completed**:
   ```
   AskUserQuestion(
     questions: [{
       question: "Found interrupted techspec workflow for '{feature_id}' (phase: {phase}, status: {status}). Resume or start fresh?",
       header: "Resume?",
       options: [
         {label: "Resume", description: "Continue from {phase} phase"},
         {label: "Start fresh", description: "Delete technical artifacts and restart"}
       ],
       multiSelect: false
     }]
   )
   ```

4. **If resume**: Read context, jump to appropriate phase based on status (see State Recovery)
5. **If fresh**: Delete technical artifacts (`technical/` directory, workflow reports) and proceed

---

## Phase 1: Initialize

### 1.1 Create Directories

```bash
mkdir -p specs/{feature-id}/technical
```

### 1.2 Create Techspec Context

Use the template at `${CLAUDE_PLUGIN_ROOT}/templates/techspec-context-template.md`.

Write to `specs/{feature-id}/.workflow/techspec-context.md` with these values:

| Placeholder | Value |
|-------------|-------|
| `{{phase}}` | `core` |
| `{{status}}` | `awaiting-analyst` |
| `{{iteration}}` | `1` |
| `{{feature_id}}` | Feature ID |
| `{{created}}` | ISO date |
| `{{updated}}` | ISO date |
| `{{core_status}}` | `pending` |
| `{{supplementary_status}}` | `pending` |
| `{{spec_status}}` | `present` |
| `{{spec_path}}` | `specs/{feature-id}/spec.md` |
| `{{constitution_path}}` | Path to constitution |
| `{{constitution_principles}}` | Extracted key principles |
| `{{project_type}}` | `brownfield` or `greenfield` (from constitution) |
| `{{requirements_path}}` | `specs/{feature-id}/technical/requirements.md` |
| `{{requirements_status}}` | `pending` |
| `{{constraints_path}}` | `specs/{feature-id}/technical/constraints.md` |
| `{{constraints_status}}` | `pending` |
| `{{nfrs_path}}` | `specs/{feature-id}/technical/nfrs.md` |
| `{{nfrs_status}}` | `pending` |
| `{{integrations_path}}` | `specs/{feature-id}/technical/integrations.md` |
| `{{integrations_status}}` | `pending` |
| `{{datasensitivity_path}}` | `specs/{feature-id}/technical/data-sensitivity.md` |
| `{{datasensitivity_status}}` | `pending` |
| `{{techanalyst_report_path}}` | `specs/{feature-id}/.workflow/techanalyst-report.md` |
| `{{architect_report_path}}` | `specs/{feature-id}/.workflow/architect-report.md` |
| `{{advocate_report_path}}` | `specs/{feature-id}/.workflow/advocate-report.md` |
| `{{codebase_analysis_path}}` | `.humaninloop/memory/codebase-analysis.md` (if brownfield) |
| `{{codebase_analysis_age}}` | Age in days (if brownfield) |
| `{{codebase_context}}` | Empty (filled by analyst if brownfield) |
| `{{supervisor_instructions}}` | See Phase 2 for initial instructions |
| `{{clarification_log}}` | Empty on first iteration |

---

## Phase 2: Core Requirements (Pass 1)

### 2.1 Set Supervisor Instructions for Technical Analyst

Update `{{supervisor_instructions}}` in techspec-context.md:

```markdown
**Phase**: Core Requirements

Translate the business specification into technical requirements and constraints.

**Read**:
- Spec: `specs/{feature-id}/spec.md`
- Constitution: `.humaninloop/memory/constitution.md`

**Write**:
- Technical Requirements: `specs/{feature-id}/technical/requirements.md`
- Technical Constraints: `specs/{feature-id}/technical/constraints.md`
- Report: `specs/{feature-id}/.workflow/techanalyst-report.md`

**Use Skills**:
- `authoring-technical-requirements`

**Brownfield Context** (if `project_type: brownfield`):
- Read existing analysis from `.humaninloop/memory/codebase-analysis.md`
- Do NOT invoke `analysis-codebase` skill—use the cached results from setup

**Report format**: Follow `${CLAUDE_PLUGIN_ROOT}/templates/techanalyst-report-template.md`
```

### 2.2 Update Context Status

Update techspec-context.md frontmatter:
```yaml
phase: core
status: awaiting-analyst
updated: {ISO date}
```

### 2.3 Invoke Technical Analyst

```
Task(
  subagent_type: "humaninloop:technical-analyst",
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/techspec-context.md",
  description: "Create technical requirements"
)
```

### 2.4 Verify Output

Confirm the agent created:
- `specs/{feature-id}/technical/requirements.md`
- `specs/{feature-id}/technical/constraints.md`
- `specs/{feature-id}/.workflow/techanalyst-report.md`

If missing, report error and stop.

### 2.5 Principal Architect Feasibility Review

Update context for architect:

```markdown
**Phase**: Core Requirements Feasibility Review

Review the technical requirements and constraints for feasibility.

**Read**:
- Spec: `specs/{feature-id}/spec.md`
- Technical Requirements: `specs/{feature-id}/technical/requirements.md`
- Technical Constraints: `specs/{feature-id}/technical/constraints.md`
- TechAnalyst report: `specs/{feature-id}/.workflow/techanalyst-report.md`

**Write**:
- Report: `specs/{feature-id}/.workflow/architect-report.md`

**Focus Areas**:
- Constraint validity: Are constraints real technical limitations or disguised preferences?
- Acceptance criteria achievability: Can each criterion actually be tested?
- Requirement-constraint contradictions: Do any requirements conflict with constraints?

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
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/techspec-context.md",
  description: "Review core feasibility"
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
**Phase**: Core Requirements Completeness Review

Review the technical requirements and constraints for completeness and gaps.

**Read**:
- Spec: `specs/{feature-id}/spec.md`
- Technical Requirements: `specs/{feature-id}/technical/requirements.md`
- Technical Constraints: `specs/{feature-id}/technical/constraints.md`
- TechAnalyst report: `specs/{feature-id}/.workflow/techanalyst-report.md`

**Write**:
- Report: `specs/{feature-id}/.workflow/advocate-report.md`

**Use Skills**:
- `validation-plan-artifacts` (phase: T0)

**Focus Areas**:
- FR coverage: Is every functional requirement from spec.md mapped to at least one TR?
- Orphan TRs: Are there technical requirements with no business source?
- Testable criteria: Does every TR have measurable acceptance criteria?
- Sourced constraints: Is every constraint traceable to a real limitation?

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
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/techspec-context.md",
  description: "Review core completeness"
)
```

### 2.8 Route Based on Advocate Verdict

Read advocate report and extract verdict.

**If verdict is `ready`**:
- Update `core_status` to `complete`
- Update `requirements_status` and `constraints_status` to `complete`
- Proceed to Phase 3 (Supplementary Requirements)

**If verdict is `needs-revision` or `critical-gaps`**:
- Enter Clarification Loop (see below)
- After user answers and analyst revision → route back:
  - **Skip architect re-review** UNLESS structural changes occurred:
    - New constraints added or existing constraints changed
    - Requirement scope expanded significantly
  - If only clarifications were addressed (adding detail, fixing traceability) → go directly to 2.7
  - If structural changes occurred → go back to 2.5

---

## Phase 3: Supplementary Requirements (Pass 2)

### 3.1 Set Supervisor Instructions for Technical Analyst

Update `{{supervisor_instructions}}` in techspec-context.md:

```markdown
**Phase**: Supplementary Requirements

Layer operational concerns on top of the core technical requirements.

**Read**:
- Spec: `specs/{feature-id}/spec.md`
- Technical Requirements: `specs/{feature-id}/technical/requirements.md`
- Technical Constraints: `specs/{feature-id}/technical/constraints.md`
- Constitution: `.humaninloop/memory/constitution.md`

**Write**:
- Non-Functional Requirements: `specs/{feature-id}/technical/nfrs.md`
- System Integrations: `specs/{feature-id}/technical/integrations.md`
- Data Sensitivity: `specs/{feature-id}/technical/data-sensitivity.md`
- Report: `specs/{feature-id}/.workflow/techanalyst-report.md`

**Use Skills**:
- `authoring-technical-requirements`

**Brownfield Context** (if `project_type: brownfield`):
- Read existing analysis from `.humaninloop/memory/codebase-analysis.md`
- Do NOT invoke `analysis-codebase` skill—use the cached results from setup

**Report format**: Follow `${CLAUDE_PLUGIN_ROOT}/templates/techanalyst-report-template.md`
```

### 3.2 Update Context Status

Update techspec-context.md frontmatter:
```yaml
phase: supplementary
status: awaiting-analyst
iteration: 1
updated: {ISO date}
```

### 3.3 Invoke Technical Analyst

```
Task(
  subagent_type: "humaninloop:technical-analyst",
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/techspec-context.md",
  description: "Create supplementary requirements"
)
```

### 3.4 Verify Output

Confirm the agent created:
- `specs/{feature-id}/technical/nfrs.md`
- `specs/{feature-id}/technical/integrations.md`
- `specs/{feature-id}/technical/data-sensitivity.md`
- `specs/{feature-id}/.workflow/techanalyst-report.md`

If missing, report error and stop.

### 3.5 Principal Architect Feasibility Review

Update context for architect:

```markdown
**Phase**: Supplementary Requirements Feasibility Review

Review the supplementary requirements for feasibility.

**Read**:
- Technical Requirements: `specs/{feature-id}/technical/requirements.md`
- Technical Constraints: `specs/{feature-id}/technical/constraints.md`
- Non-Functional Requirements: `specs/{feature-id}/technical/nfrs.md`
- System Integrations: `specs/{feature-id}/technical/integrations.md`
- Data Sensitivity: `specs/{feature-id}/technical/data-sensitivity.md`
- TechAnalyst report: `specs/{feature-id}/.workflow/techanalyst-report.md`

**Write**:
- Report: `specs/{feature-id}/.workflow/architect-report.md`

**Focus Areas**:
- NFR measurability: Can each NFR target actually be measured with the specified method?
- NFR-constraint conflicts: Do any NFR targets contradict existing constraints?
- Integration failure modes: Are fallback strategies realistic and implementable?

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
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/techspec-context.md",
  description: "Review supplementary feasibility"
)
```

### 3.6 Route Based on Architect Verdict

Same logic as Phase 2.6:

**If `feasible`**: Proceed to 3.7

**If `infeasible` or `needs-revision`**: Feasibility Rejection Loop → back to 3.5

### 3.7 Devil's Advocate Completeness Review

Update context for advocate:

```markdown
**Phase**: Supplementary Requirements Completeness Review (INCREMENTAL MODE)

**Full Review** the supplementary requirements for completeness and quality.
**Consistency Check** core requirements using cross-artifact checklist.

**Full Review**:
- Non-Functional Requirements: `specs/{feature-id}/technical/nfrs.md`
- System Integrations: `specs/{feature-id}/technical/integrations.md`
- Data Sensitivity: `specs/{feature-id}/technical/data-sensitivity.md`
- TechAnalyst report: `specs/{feature-id}/.workflow/techanalyst-report.md`

**Consistency Check Only** (2-3 min max):
- Technical Requirements: `specs/{feature-id}/technical/requirements.md`
- Technical Constraints: `specs/{feature-id}/technical/constraints.md`

**Write**:
- Report: `specs/{feature-id}/.workflow/advocate-report.md`

**Use Skills**:
- `validation-plan-artifacts` (phase: T1, mode: incremental)

**Full Review Checks**:
- NFR coverage: Are all quality attributes addressed?
- Integration completeness: Are all external systems catalogued with failure modes?
- Data classification: Is all PII/sensitive data identified?

**Consistency Checks**:
- NFR sources trace to valid TRs
- Integration points align with constraints
- Data sensitivity aligns with requirements

**Time Budget**:
- Supplementary full review: unlimited
- Core consistency check: 2-3 minutes max

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
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/techspec-context.md",
  description: "Review supplementary completeness"
)
```

### 3.8 Route Based on Advocate Verdict

Read advocate report and extract verdict.

**If verdict is `ready`**:
- Update `supplementary_status` to `complete`
- Update `nfrs_status`, `integrations_status`, `datasensitivity_status` to `complete`
- Proceed to Phase 4 (Completion)

**If verdict is `needs-revision` or `critical-gaps`**:
- Enter Clarification Loop
- After user answers and analyst revision → route back:
  - **Skip architect re-review** UNLESS structural changes occurred:
    - NFR targets modified
    - Integration boundaries changed
    - New constraints implied by supplementary analysis
  - If only clarifications → go directly to 3.7
  - If structural changes → go back to 3.5

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
   ### Phase: {phase} - Feasibility Iteration {N}

   #### Architect Concerns
   {List from architect report}

   #### User Decisions
   | Issue | Decision | User Direction |
   |-------|----------|----------------|
   | {issue} | {accept/relax/keep/custom} | {user's specific direction} |
   ```

3. **Update supervisor instructions for revision**:
   ```markdown
   **Phase**: {phase} (Feasibility Revision)

   Revise the technical artifacts based on user decisions about feasibility concerns.

   **Read**:
   - Current artifacts: `specs/{feature-id}/technical/`
   - Architect concerns and user decisions: See `## Clarification Log` below
   - Spec: `specs/{feature-id}/spec.md`

   **Write**:
   - Updated artifacts: `specs/{feature-id}/technical/`
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

   Revise the technical artifacts based on user feedback.

   **Read**:
   - Current artifacts: `specs/{feature-id}/technical/`
   - Gaps and user answers: See `## Clarification Log` below
   - Spec: `specs/{feature-id}/spec.md`

   **Write**:
   - Updated artifacts: `specs/{feature-id}/technical/`
   - Report: `specs/{feature-id}/.workflow/techanalyst-report.md`

   **Report format**: Follow `${CLAUDE_PLUGIN_ROOT}/templates/techanalyst-report-template.md`
   ```

4. **Increment iteration** in context frontmatter

5. **Loop back to Technical Analyst invocation**

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

### 4.1 Update Final Status

Update techspec-context.md frontmatter:
```yaml
phase: completed
status: completed
core_status: complete
supplementary_status: complete
updated: {ISO date}
```

Update all artifact statuses:
```yaml
requirements_status: complete
constraints_status: complete
nfrs_status: complete
integrations_status: complete
datasensitivity_status: complete
```

### 4.2 Generate Completion Report

Output to user:

```markdown
## Technical Specification Complete

**Feature**: {feature_id}

### Summary
- Technical Requirements: {count from requirements.md}
- Constraints: {count from constraints.md}
- Non-Functional Requirements: {count from nfrs.md}
- Integration Points: {count from integrations.md}
- Data Classifications: {count from data-sensitivity.md}

### Artifacts Generated
- `specs/{feature-id}/technical/requirements.md` - FR → TR mapping
- `specs/{feature-id}/technical/constraints.md` - Technical boundaries
- `specs/{feature-id}/technical/nfrs.md` - Performance & quality targets
- `specs/{feature-id}/technical/integrations.md` - System boundaries
- `specs/{feature-id}/technical/data-sensitivity.md` - Data classification

### Known Limitations
{Any minor gaps deferred, if applicable}

### Next Steps
1. Review the technical specification in `specs/{feature-id}/technical/`
2. Run `/humaninloop:plan` to create implementation plan
```

---

## Error Handling

### Agent Failure

```markdown
**Agent Failed**

Error: {error_message}
Agent: {agent_name}
Phase: {phase}

The workflow state has been saved. Run `/humaninloop:techspec` to resume from {phase} phase.
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
| `core` | `awaiting-analyst` | Phase 2.3 (invoke analyst) |
| `core` | `awaiting-architect` | Phase 2.5 (invoke architect) |
| `core` | `awaiting-advocate` | Phase 2.7 (invoke advocate) |
| `core` | `awaiting-user` | Clarification loop or Feasibility rejection loop |
| `supplementary` | `awaiting-analyst` | Phase 3.3 (invoke analyst) |
| `supplementary` | `awaiting-architect` | Phase 3.5 (invoke architect) |
| `supplementary` | `awaiting-advocate` | Phase 3.7 (invoke advocate) |
| `supplementary` | `awaiting-user` | Clarification loop or Feasibility rejection loop |
| `completed` | `completed` | Report already done |

---

## Important Notes

- Do NOT modify git config or push to remote
- Use judgment for iteration limits (no hard caps)
- Always use Task tool to invoke agents
- Agents have NO workflow knowledge—all context via context file
- Supervisor owns ALL routing and state decisions
- Architect reviews feasibility first—prevents wasting time reviewing completeness of infeasible requirements
- After advocate-driven revisions, skip architect re-review unless structural changes occurred (new constraints, changed requirement scope, modified NFR targets, changed integration boundaries)
- Technical Analyst does NOT make technology choices—that remains plan-architect's responsibility
