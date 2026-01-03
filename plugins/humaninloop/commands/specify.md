---
description: Create feature specification using decoupled two-agent architecture (Requirements Analyst + Devil's Advocate)
---

# Decoupled Specify Workflow

You are the **Supervisor** orchestrating a two-agent specification workflow. You own the loop, manage state via files, and route based on agent outputs.

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

## Pre-Execution: Constitution Check

Before any workflow execution, verify that the project constitution exists:

1. **Check for constitution file** at `.humaninloop/memory/constitution.md`
2. **If NOT found**, display the following and STOP execution:

```
Constitution Required

The HumanInLoop specify workflow requires a project constitution to be configured.

The constitution defines project principles that guide specification quality validation.

To set up your constitution, run:
/humaninloop:setup

This will walk you through defining your project's core principles.

Then retry /humaninloop:specify
```

3. **If found**: Continue to Resume Detection

---

## Architecture Overview

```
SUPERVISOR (this command)
    │
    ├── Creates scaffold + directories
    ├── Invokes agents with minimal prompts
    ├── Parses structured prose outputs
    ├── Updates scaffold between iterations
    └── Owns all routing decisions

AGENTS (independent, no workflow knowledge)
    │
    ├── Requirements Analyst → Writes spec.md
    └── Devil's Advocate → Reviews spec.md, finds gaps
```

**Communication Pattern**: Scaffold + Spec File + Separate Reports

```
specs/{feature-id}/
├── spec.md                          # The deliverable
└── .workflow/
    ├── scaffold.md                  # Context + instructions
    ├── analyst-report.md            # Requirements Analyst output
    └── advocate-report.md           # Devil's Advocate output
```

---

## Agents Used

| Agent | File | Purpose |
|-------|------|---------|
| Requirements Analyst | `${CLAUDE_PLUGIN_ROOT}/agents/requirements-analyst.md` | Transform feature request into spec |
| Devil's Advocate | `${CLAUDE_PLUGIN_ROOT}/agents/devils-advocate.md` | Review spec, find gaps, generate clarifications |

---

## Pre-Execution: Resume Detection

Before starting, check for interrupted workflows:

1. **Search for existing scaffolds** with `status` not `completed`:
   ```bash
   find specs -name "scaffold.md" -path "*/.workflow/*" 2>/dev/null
   ```

2. **If found**: Read scaffold frontmatter, check `status` field

3. **If status is not completed**:
   ```
   AskUserQuestion(
     questions: [{
       question: "Found interrupted workflow for '{feature_id}' (status: {status}). Resume or start fresh?",
       header: "Resume?",
       options: [
         {label: "Resume", description: "Continue from where you left off"},
         {label: "Start fresh", description: "Delete existing and start over"}
       ],
       multiSelect: false
     }]
   )
   ```

4. **If resume**: Read scaffold, jump to appropriate phase based on status
5. **If fresh**: Delete existing feature directory and proceed

---

## Phase 1: Initialize

### 1.1 Generate Feature ID

Create a feature ID from the user input:
- Slugify the description (lowercase, hyphens, max 40 chars)
- Prefix with sequence number if specs directory has existing features
- Example: `001-user-authentication`

### 1.2 Create Directory Structure

```bash
mkdir -p specs/{feature-id}/.workflow
```

### 1.3 Create Scaffold

Use the template at `${CLAUDE_PLUGIN_ROOT}/templates/scaffold-template.md`.

Write to `specs/{feature-id}/.workflow/scaffold.md` with these values:

| Placeholder | Value |
|-------------|-------|
| `{{status}}` | `awaiting-analyst` |
| `{{iteration}}` | `1` |
| `{{feature_id}}` | Generated feature ID |
| `{{created}}` | ISO date |
| `{{updated}}` | ISO date |
| `{{user_input}}` | Original user input from $ARGUMENTS |
| `{{project_name}}` | Detected from package.json, etc. |
| `{{tech_stack}}` | Detected |
| `{{constitution_path}}` | Path if exists, or "not configured" |
| `{{constitution_principles}}` | Extracted key principles, or "No constitution configured. Use general best practices." |
| `{{spec_path}}` | `specs/{feature-id}/spec.md` |
| `{{scaffold_path}}` | `specs/{feature-id}/.workflow/scaffold.md` |
| `{{analyst_report_path}}` | `specs/{feature-id}/.workflow/analyst-report.md` |
| `{{advocate_report_path}}` | `specs/{feature-id}/.workflow/advocate-report.md` |
| `{{supervisor_instructions}}` | See Phase 2 for initial analyst instructions |
| `{{clarification_log}}` | Empty on first iteration |

### 1.4 Create Spec File

Use the template at `${CLAUDE_PLUGIN_ROOT}/templates/spec-template.md`.

Write to `specs/{feature-id}/spec.md` with initial values:

| Placeholder | Value |
|-------------|-------|
| `{{feature_title}}` | Derived from user input |
| `{{feature_id}}` | Generated feature ID |
| `{{created}}` | ISO date |
| `{{status}}` | `draft` |
| All other sections | Empty (to be filled by analyst) |

---

## Phase 2: Requirements Analyst

### 2.1 Set Supervisor Instructions for Analyst

Update `{{supervisor_instructions}}` in scaffold:

```markdown
Create a feature specification based on the user input above.

**Read**:
- Spec template: `${CLAUDE_PLUGIN_ROOT}/templates/spec-template.md`

**Write**:
- Spec: `specs/{feature-id}/spec.md`
- Report: `specs/{feature-id}/.workflow/analyst-report.md`

**Report format**: Follow `${CLAUDE_PLUGIN_ROOT}/templates/analyst-report-template.md`
```

### 2.2 Update Scaffold Status

Update scaffold frontmatter:
```yaml
status: awaiting-analyst
updated: {ISO date}
```

### 2.3 Invoke Agent

```
Task(
  subagent_type: "humaninloop:requirements-analyst",
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/scaffold.md",
  description: "Write feature specification"
)
```

### 2.4 Verify Output

Confirm the agent created:
- `specs/{feature-id}/spec.md` (updated with content)
- `specs/{feature-id}/.workflow/analyst-report.md`

If missing, report error and stop.

---

## Phase 3: Devil's Advocate

### 3.1 Set Supervisor Instructions for Advocate

Update `{{supervisor_instructions}}` in scaffold:

```markdown
Review the specification and find gaps.

**Read**:
- Spec: `specs/{feature-id}/spec.md`
- Analyst report: `specs/{feature-id}/.workflow/analyst-report.md`

**Write**:
- Report: `specs/{feature-id}/.workflow/advocate-report.md`

**Report format**: Follow `${CLAUDE_PLUGIN_ROOT}/templates/advocate-report-template.md`
```

### 3.2 Update Scaffold Status

Update scaffold frontmatter:
```yaml
status: awaiting-advocate
updated: {ISO date}
```

### 3.3 Invoke Agent

```
Task(
  subagent_type: "humaninloop:devils-advocate",
  prompt: "Read your instructions from: specs/{feature-id}/.workflow/scaffold.md",
  description: "Review spec for gaps"
)
```

### 3.4 Parse Advocate Report

Read `specs/{feature-id}/.workflow/advocate-report.md` and extract:
- `verdict`: ready | needs-clarification | major-gaps
- `gaps`: List of gaps with severity
- `clarifications`: List of questions

---

## Phase 4: Route Based on Verdict

### If Verdict is `ready`

1. Update scaffold status to `completed`
2. Generate completion report (see Phase 5)
3. Exit workflow

### If Verdict is `needs-clarification` or `major-gaps`

1. **Present clarifications to user** using AskUserQuestion:
   ```
   AskUserQuestion(
     questions: clarifications.map(c => ({
       question: c.question,
       header: c.gap_id,
       options: c.options || [
         {label: "Yes", description: ""},
         {label: "No", description: ""},
         {label: "Not sure", description: "Needs more discussion"}
       ],
       multiSelect: false
     }))
   )
   ```

2. **Update scaffold with user answers**:
   Append to `## Clarification Log`:
   ```markdown
   ### Iteration {N}

   #### Gaps Identified
   {List from advocate report}

   #### User Answers
   | Gap ID | Question | Answer |
   |--------|----------|--------|
   | G1 | {question} | {user's answer} |
   | G2 | {question} | {user's answer} |
   ```

3. **Update supervisor instructions for next analyst pass**:
   ```markdown
   Revise the specification based on user feedback.

   **Read**:
   - Current spec: `specs/{feature-id}/spec.md`
   - Gaps and user answers: See `## Clarification Log` below
   - Spec template: `${CLAUDE_PLUGIN_ROOT}/templates/spec-template.md`

   **Write**:
   - Updated spec: `specs/{feature-id}/spec.md`
   - Report: `specs/{feature-id}/.workflow/analyst-report.md`

   **Report format**: Follow `${CLAUDE_PLUGIN_ROOT}/templates/analyst-report-template.md`
   ```

4. **Increment iteration** in scaffold frontmatter

5. **Loop back to Phase 2**

---

## Supervisor Judgment: When to Exit Early

Use your judgment to recommend exiting if:

- **Iteration count exceeds 5**: Recommend accepting current spec or manual review
- **User answers aren't resolving gaps**: Ask how to proceed
- **Only minor gaps remain**: Offer to finalize with known limitations
- **User seems satisfied**: Offer to complete even with open gaps

Always give the user the choice—never force-terminate without consent:

```
AskUserQuestion(
  questions: [{
    question: "We've iterated {N} times. {Context}. How should we proceed?",
    header: "Next Step",
    options: [
      {label: "Continue refining", description: "Another round of clarification"},
      {label: "Accept current spec", description: "Finalize with known gaps as limitations"},
      {label: "Stop and review manually", description: "Exit workflow, review spec yourself"}
    ],
    multiSelect: false
  }]
)
```

---

## Phase 5: Completion

### 5.1 Update Final Status

Update scaffold frontmatter:
```yaml
status: completed
updated: {ISO date}
```

### 5.2 Generate Completion Report

Output to user:

```markdown
## Specification Complete

**Feature**: {feature_id}
**Iterations**: {count}

### Files Created
- Spec: `specs/{feature-id}/spec.md`
- Workflow: `specs/{feature-id}/.workflow/`

### Summary
{From analyst report: user story count, requirement count}

### Known Limitations
{Any minor gaps deferred, if applicable}

### Next Steps
1. Review the spec at `specs/{feature-id}/spec.md`
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

The workflow state has been saved. Run `/humaninloop:specify` to resume.
```

### Missing Files

If expected output files are missing after agent invocation:
1. Log the issue
2. Ask user: Retry agent, or abort?

---

## State Recovery

Resume logic based on `status` field:

| Status | Resume Point |
|--------|--------------|
| `awaiting-analyst` | Phase 2 (invoke analyst) |
| `awaiting-advocate` | Phase 3 (invoke advocate) |
| `awaiting-user` | Phase 4 (present clarifications) |
| `completed` | Report already done |

---

## Important Notes

- Do NOT modify git config or push to remote
- Maximum practical iterations: ~5 (use judgment, not hard limit)
- Always use Task tool to invoke agents
- Agents have NO workflow knowledge—all context via scaffold
- Supervisor owns ALL routing and state decisions
