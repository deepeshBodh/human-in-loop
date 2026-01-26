---
description: Execute the multi-agent task generation workflow with specialized agents and validation loops
---

# Two-Agent Tasks Workflow

You are the **Supervisor** orchestrating a two-agent tasks workflow. You own the loop, manage state via files, and route based on agent outputs.

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
    ├── Task Architect → Writes task-mapping.md, tasks.md
    └── Devil's Advocate → Reviews artifacts, finds gaps
```

**Communication Pattern**: Context + Artifacts + Separate Reports

```
specs/{feature-id}/
├── spec.md                          # Input (from specify workflow)
├── plan.md                          # Input (from plan workflow)
├── research.md                      # Input (from plan workflow)
├── data-model.md                    # Input (from plan workflow)
├── contracts/                       # Input (from plan workflow)
│   └── api.yaml
├── task-mapping.md                  # Mapping phase output
├── tasks.md                         # Tasks phase output
└── .workflow/
    ├── context.md                   # Context (specify workflow)
    ├── plan-context.md              # Context (plan workflow)
    ├── tasks-context.md             # Context (this workflow)
    ├── planner-report.md            # Task Architect output
    └── advocate-report.md           # Devil's Advocate output
```

---

## Agents Used

| Agent | File | Purpose |
|-------|------|---------|
| Task Architect | `${CLAUDE_PLUGIN_ROOT}/agents/task-architect.md` | Transform plan artifacts into task mappings and task lists |
| Devil's Advocate | `${CLAUDE_PLUGIN_ROOT}/agents/devils-advocate.md` | Review artifacts, find gaps, generate clarifications |

---

## Pre-Execution: Entry Gate

Before starting, verify the plan workflow is complete:

1. **Identify the feature directory**:
   - If `$ARGUMENTS` specifies a feature ID: use that
   - Otherwise: Detect from current git branch (branch name = feature ID, e.g., `001-user-auth`)
   - Fallback: Find most recent spec in `specs/` by highest numeric prefix

2. **Check for plan.md**: Read `specs/{feature-id}/plan.md`
   - If NOT found: Block and tell user to run `/humaninloop:plan` first

3. **Check plan workflow status**: Read `specs/{feature-id}/.workflow/plan-context.md`
   - If `status` != `completed`:
     ```
     AskUserQuestion(
       questions: [{
         question: "Plan workflow not complete (status: {status}). Tasks workflow requires a completed plan.",
         header: "Entry Gate",
         options: [
           {label: "Complete plan first", description: "Return to /humaninloop:plan"},
           {label: "Abort", description: "Cancel tasks workflow"}
         ],
         multiSelect: false
       }]
     )
     ```

4. **If entry gate passes**: Continue to Resume Detection

---

## Pre-Execution: Resume Detection

Before starting, check for interrupted tasks workflows:

1. **Check for existing tasks-context.md**:
   ```bash
   test -f specs/{feature-id}/.workflow/tasks-context.md
   ```

2. **If found**: Read frontmatter, check `status` and `phase` fields

3. **If status is not completed**:
   ```
   AskUserQuestion(
     questions: [{
       question: "Found interrupted tasks workflow for '{feature_id}' (phase: {phase}, status: {status}). Resume or start fresh?",
       header: "Resume?",
       options: [
         {label: "Resume", description: "Continue from {phase} phase"},
         {label: "Start fresh", description: "Delete task artifacts and restart"}
       ],
       multiSelect: false
     }]
   )
   ```

4. **If resume**: Read context, jump to appropriate phase based on status
5. **If fresh**: Delete task artifacts (task-mapping.md, tasks.md) and proceed

---

## Phase 1: Initialize

### 1.1 Create Tasks Context

Use the template at `${CLAUDE_PLUGIN_ROOT}/templates/tasks-context-template.md`.

Write to `specs/{feature-id}/.workflow/tasks-context.md` with these values:

| Placeholder | Value |
|-------------|-------|
| `{{phase}}` | `mapping` |
| `{{status}}` | `awaiting-architect` |
| `{{iteration}}` | `1` |
| `{{feature_id}}` | Feature ID |
| `{{created}}` | ISO date |
| `{{updated}}` | ISO date |
| `{{plan_status}}` | `present` |
| `{{constitution_path}}` | Path to constitution |
| `{{constitution_principles}}` | Extracted key principles |
| `{{spec_path}}` | `specs/{feature-id}/spec.md` |
| `{{spec_status}}` | `present` |
| `{{plan_path}}` | `specs/{feature-id}/plan.md` |
| `{{research_path}}` | `specs/{feature-id}/research.md` |
| `{{research_status}}` | Status (present/missing) |
| `{{datamodel_path}}` | `specs/{feature-id}/data-model.md` |
| `{{datamodel_status}}` | Status (present/missing) |
| `{{contracts_path}}` | `specs/{feature-id}/contracts/` |
| `{{contracts_status}}` | Status (present/missing) |
| `{{mapping_path}}` | `specs/{feature-id}/task-mapping.md` |
| `{{mapping_status}}` | `pending` |
| `{{tasks_path}}` | `specs/{feature-id}/tasks.md` |
| `{{tasks_status}}` | `pending` |
| `{{architect_report_path}}` | `specs/{feature-id}/.workflow/planner-report.md` |
| `{{advocate_report_path}}` | `specs/{feature-id}/.workflow/advocate-report.md` |
| `{{supervisor_instructions}}` | See Phase 2 for initial instructions |
| `{{clarification_log}}` | Empty on first iteration |

---

## Phase 2: Mapping

### 2.1 Set Supervisor Instructions for Architect

Update `{{supervisor_instructions}}` in tasks-context.md:

```markdown
**Phase**: Mapping

Create task mapping document from plan artifacts.

**Read**:
- Spec: `specs/{feature-id}/spec.md`
- Plan: `specs/{feature-id}/plan.md`
- Research: `specs/{feature-id}/research.md`
- Data Model: `specs/{feature-id}/data-model.md`
- Contracts: `specs/{feature-id}/contracts/`
- Constitution: `.humaninloop/memory/constitution.md`

**Write**:
- Mapping: `specs/{feature-id}/task-mapping.md`
- Report: `specs/{feature-id}/.workflow/planner-report.md`

**Use Skills**:
- `patterns-vertical-tdd` (identify vertical slices)

**Report format**: Follow planner report template
```

### 2.2 Update Context Status

Update tasks-context.md frontmatter:
```yaml
phase: mapping
status: awaiting-architect
updated: {ISO date}
```

### 2.3 Invoke Task Architect

```
Task(
  subagent_type: "humaninloop:task-architect",
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/tasks-context.md",
  description: "Create task mapping"
)
```

### 2.4 Verify Output

Confirm the agent created:
- `specs/{feature-id}/task-mapping.md`
- `specs/{feature-id}/.workflow/planner-report.md`

If missing, report error and stop.

### 2.5 Advocate Review

Update context for advocate:

```markdown
**Phase**: Mapping Review

Review the task mapping for gaps and quality.

**Read**:
- Spec: `specs/{feature-id}/spec.md`
- Plan: `specs/{feature-id}/plan.md`
- Task Mapping: `specs/{feature-id}/task-mapping.md`
- Architect report: `specs/{feature-id}/.workflow/planner-report.md`

**Write**:
- Report: `specs/{feature-id}/.workflow/advocate-report.md`

**Use Skills**:
- `validation-task-artifacts` (phase: mapping)

**Report format**: Follow advocate report template
```

Update status:
```yaml
status: awaiting-advocate
```

Invoke advocate:
```
Task(
  subagent_type: "humaninloop:devils-advocate",
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/tasks-context.md",
  description: "Review task mapping"
)
```

### 2.6 Route Based on Verdict

Read advocate report and extract verdict.

**If verdict is `ready`**:
- Update `{{mapping_status}}` to `complete`
- Proceed to Phase 3 (Tasks)

**If verdict is `needs-revision` or `critical-gaps`**:
- Present clarifications to user (see Clarification Loop)
- Update context with answers
- Increment iteration
- Loop back to 2.3

---

## Phase 3: Tasks

### 3.1 Set Supervisor Instructions for Architect

Update `{{supervisor_instructions}}` in tasks-context.md:

```markdown
**Phase**: Tasks

Create implementation task list from mapping.

**Read**:
- Task Mapping: `specs/{feature-id}/task-mapping.md`
- Spec: `specs/{feature-id}/spec.md`
- Plan: `specs/{feature-id}/plan.md`
- Research: `specs/{feature-id}/research.md`
- Data Model: `specs/{feature-id}/data-model.md`
- Contracts: `specs/{feature-id}/contracts/`
- Constitution: `.humaninloop/memory/constitution.md`

**Write**:
- Tasks: `specs/{feature-id}/tasks.md`
- Report: `specs/{feature-id}/.workflow/planner-report.md`

**Use Skills**:
- `patterns-vertical-tdd` (TDD cycle structure)

**Report format**: Follow planner report template
```

### 3.2 Update Context Status

```yaml
phase: tasks
status: awaiting-architect
iteration: 1
updated: {ISO date}
```

### 3.3 Invoke Task Architect

```
Task(
  subagent_type: "humaninloop:task-architect",
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/tasks-context.md",
  description: "Create implementation tasks"
)
```

### 3.4 Verify Output

Confirm: `specs/{feature-id}/tasks.md`

### 3.5 Advocate Review (Cumulative)

Update context for advocate:

```markdown
**Phase**: Tasks Review

Review the task list for completeness and TDD structure.

**Read**:
- Task Mapping: `specs/{feature-id}/task-mapping.md`
- Tasks: `specs/{feature-id}/tasks.md`
- Spec: `specs/{feature-id}/spec.md`
- Architect report: `specs/{feature-id}/.workflow/planner-report.md`

**Write**:
- Report: `specs/{feature-id}/.workflow/advocate-report.md`

**Use Skills**:
- `validation-task-artifacts` (phase: tasks)

**Check**:
- TDD structure (test-first ordering in each cycle)
- Cycle coverage (all mapped cycles have tasks)
- File path specificity
- Cross-artifact consistency with mapping
```

Invoke advocate and route based on verdict (same as Phase 2).

**If ready**: Proceed to Phase 4 (Completion)

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

5. **Loop back to Architect invocation**

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

Update tasks-context.md frontmatter:
```yaml
phase: completed
status: completed
updated: {ISO date}
```

Update artifact statuses:
```yaml
mapping_status: complete
tasks_status: complete
```

### 4.2 Generate Completion Report

Output to user:

```markdown
## Tasks Workflow Complete

**Feature**: {feature_id}

### Summary
- Cycles mapped: {count from task-mapping.md}
- Tasks generated: {count from tasks.md}
- Foundation cycles: {count}
- Feature cycles: {count}
- Parallel opportunities: {count with [P] marker}

### Artifacts Generated
- `specs/{feature-id}/task-mapping.md` - Story to cycle mapping
- `specs/{feature-id}/tasks.md` - Implementation tasks with TDD structure

### Known Limitations
{Any minor gaps deferred, if applicable}

### Next Steps
1. Review the tasks at `specs/{feature-id}/tasks.md`
2. Run `/humaninloop:implement` to execute the implementation
```

---

## Error Handling

### Agent Failure

```markdown
**Agent Failed**

Error: {error_message}
Agent: {agent_name}
Phase: {phase}

The workflow state has been saved. Run `/humaninloop:tasks` to resume from {phase} phase.
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
| `mapping` | `awaiting-architect` | Phase 2.3 (invoke architect) |
| `mapping` | `awaiting-advocate` | Phase 2.5 (invoke advocate) |
| `mapping` | `awaiting-user` | Clarification loop |
| `tasks` | `awaiting-architect` | Phase 3.3 (invoke architect) |
| `tasks` | `awaiting-advocate` | Phase 3.5 (invoke advocate) |
| `tasks` | `awaiting-user` | Clarification loop |
| `completed` | `completed` | Report already done |

---

## Important Notes

- Do NOT modify git config or push to remote
- Use judgment for iteration limits (no hard caps)
- Always use Task tool to invoke agents
- Agents have NO workflow knowledge—all context via context file
- Supervisor owns ALL routing and state decisions
- Advocate reviews are cumulative (check against mapping when reviewing tasks)
- Brownfield context comes from plan artifacts, not re-analyzed
