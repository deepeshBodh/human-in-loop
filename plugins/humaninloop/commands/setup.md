---
description: Create or update the project constitution using the Principal Architect agent.
---

## User Input

```text
$ARGUMENTS
```

## Workflow

This supervisor follows a decoupled architecture: create context → invoke agent → iterate if needed → finalize.

### Phase 1: Initialize

1. **Ensure directory exists**
   ```bash
   mkdir -p .humaninloop/memory
   ```

2. **Generate context filename with timestamp**
   ```bash
   CONTEXT_FILE=".humaninloop/memory/constitution-context-$(date +%Y%m%d-%H%M%S).md"
   ```

3. **Check for existing constitution**
   ```bash
   cat .humaninloop/memory/constitution.md 2>/dev/null
   ```
   - If exists: `mode: amend`, capture content
   - If not: `mode: create`

4. **Detect project context**
   - Check `package.json`, `pyproject.toml`, `pubspec.yaml`, `go.mod`, `Cargo.toml`, etc.
   - Extract project name and tech stack
   - Check if `CLAUDE.md` exists

5. **Create context artifact**

   Write to `$CONTEXT_FILE` (e.g., `.humaninloop/memory/constitution-context-20260103-154500.md`):

   ```markdown
   ---
   type: constitution-setup
   mode: [create|amend]
   iteration: 1
   created: [ISO date]
   ---

   # Constitution Setup Request

   ## User Input

   [User's request or "Set up project governance"]

   ## Project Context

   | Aspect | Value |
   |--------|-------|
   | Project Name | [detected] |
   | Tech Stack | [detected] |
   | CLAUDE.md Exists | [Yes/No] |

   ## Context Files

   - [List detected config files]
   - [CLAUDE.md if exists]

   ## Existing Constitution

   [If amending: full content]
   [If creating: "None - creating new constitution"]

   ## Supervisor Instructions

   Create a constitution for this project.

   Write to: `.humaninloop/memory/constitution.md`

   If CLAUDE.md exists, sync relevant sections using your syncing-claude-md skill.

   Report back with structured prose:
   - `## What I Created` - Constitution version, principle count, key governance areas
   - `## CLAUDE.md Sync Status` - What was synced (or "N/A" if no CLAUDE.md)
   - `## Clarifications Needed` - Questions requiring user input (if any)
   - `## Assumptions Made` - Decisions made when requirements were ambiguous

   ## Clarification Log

   [Empty on first iteration]
   ```

### Phase 2: Invoke Agent

Invoke with minimal prompt pointing to context (use the generated `$CONTEXT_FILE` path):

```
Task(
  subagent_type: "humaninloop:principal-architect",
  prompt: "
    Work on the constitution setup.

    Read the context at: $CONTEXT_FILE

    The context file contains all context, instructions, and where to write output.
  ",
  description: "Create project constitution"
)
```

### Phase 3: Parse & Route

Parse agent's structured prose output:

**If `## Clarifications Needed` has questions:**
1. Present questions to user
2. Collect answers
3. Append to `$CONTEXT_FILE`'s `## Clarification Log`:
   ```markdown
   ### Round N - Agent Questions
   [Questions from agent output]

   ### Round N - User Answers
   [User's responses]
   ```
4. Update `$CONTEXT_FILE`'s `## Supervisor Instructions`:
   ```markdown
   User answered your questions (see Clarification Log).
   Finalize the constitution incorporating their answers.

   Write to: `.humaninloop/memory/constitution.md`
   [Same output format instructions]
   ```
5. Increment `iteration` in `$CONTEXT_FILE` frontmatter
6. **Loop back to Phase 2**

**If no clarifications (or max iterations reached):**
- Proceed to Phase 4

### Phase 4: Finalize

1. **Report to user**
   - Summarize what was created (from `## What I Created`)
   - Note any assumptions made (from `## Assumptions Made`)
   - Report CLAUDE.md sync status (from `## CLAUDE.md Sync Status`)

2. **Suggest commit**
   - If new: `docs: create constitution v1.0.0`
   - If amended: `docs: update constitution to v[X.Y.Z]`

---

## Supervisor Behaviors

- **Owns the loop**: Decides when to iterate vs. finalize
- **Modifies context**: Updates `$CONTEXT_FILE` instructions and appends to clarification log between iterations
- **Presents clarifications**: Chooses how to display agent questions to user
- **Injects context**: Can add sections to `$CONTEXT_FILE` if needed mid-loop
- **Max iterations**: Consider limiting to 3 rounds to prevent infinite loops
