# Constitution Context Template

This template provides the **structure** for the constitution setup context artifact. The supervisor populates and modifies this at runtime.

---

```markdown
---
type: constitution-setup
mode: [create|amend]
iteration: 1
created: [ISO date]
---

# Constitution Setup Request

## User Input

[User's request or "Set up project governance" if none provided]

## Project Context

<!-- Supervisor populates from detection -->

| Aspect | Value |
|--------|-------|
| Project Name | |
| Tech Stack | |
| CLAUDE.md Exists | |

## Context Files

<!-- Supervisor lists files the agent should read -->

## Existing Constitution

<!-- If mode is amend, supervisor includes current constitution content -->
<!-- If mode is create, supervisor writes "None - creating new constitution" -->

## Supervisor Instructions

<!--
Supervisor writes iteration-specific instructions here.
This section is FULLY OWNED by the supervisor - content changes between iterations.

The supervisor uses this section to:
- Direct the agent on what to produce
- Specify output location and format
- Provide iteration-specific guidance

Examples:

First pass:
  "Create a constitution for this project.
   Write to: .humaninloop/memory/constitution.md
   Report questions in ## Clarifications Needed section."

Refinement pass:
  "User answered your questions (see Clarification Log below).
   Finalize the constitution incorporating their answers.
   Write to: .humaninloop/memory/constitution.md"
-->

## Clarification Log

<!--
Supervisor appends rounds here to maintain conversation history.
Agent reads this to understand prior context and user decisions.

Format:

### Round N - Agent Questions
[Questions from agent's previous output]

### Round N - User Answers
[User's responses, added by supervisor before re-invoking agent]
-->
```

---

## Usage Notes

1. **Supervisor owns this artifact** - creates, modifies, and deletes it
2. **Agent reads only** - treats context as source of truth for context and instructions
3. **Flexible structure** - supervisor can add custom sections as needed
4. **Iteration tracking** - `iteration` in frontmatter helps track conversation rounds
5. **Delete after completion** - context is ephemeral, removed when workflow finishes
