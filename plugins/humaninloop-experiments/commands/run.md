---
description: Run an experimental workflow to test new patterns and document findings.
---

## User Input

```text
$ARGUMENTS
```

## Workflow

This supervisor follows a decoupled architecture: create scaffold --> invoke agent --> iterate if needed --> finalize.

### Phase 1: Initialize

1. **Ensure directory exists**
   ```bash
   mkdir -p .humaninloop/experiments
   ```

2. **Generate experiment directory with timestamp**
   ```bash
   EXP_ID="exp-$(date +%Y%m%d-%H%M%S)"
   EXP_DIR=".humaninloop/experiments/$EXP_ID"
   mkdir -p "$EXP_DIR"
   SCAFFOLD_FILE="$EXP_DIR/scaffold.md"
   ```

3. **Detect project context**
   - Check for existing constitution: `.humaninloop/memory/constitution.md`
   - Identify tech stack from config files
   - Note any relevant existing experiments

4. **Create scaffold artifact**

   Write to `$SCAFFOLD_FILE`:

   ```markdown
   ---
   type: experiment
   experiment_id: [generated ID]
   iteration: 1
   created: [ISO date]
   status: scaffolded
   ---

   # Experiment Request

   ## Hypothesis

   [User's experiment description or "Explore experimental workflow patterns"]

   ## Goals

   - Test the described pattern or approach
   - Document observations and outcomes
   - Identify improvements or issues

   ## Context Files

   - `.humaninloop/memory/constitution.md` - Project standards (if exists)
   - [Any relevant existing artifacts]

   ## Constraints

   - Follow ADR-005 decoupled architecture principles
   - Document all assumptions
   - Provide actionable recommendations

   ## Supervisor Instructions

   Design and run this experiment.

   Write results to: `result.md` (same directory)

   Report back with structured prose:
   - `## What I Created` - Experiment executed, key findings
   - `## Results Summary` - Pass/Fail with evidence
   - `## Clarifications Needed` - Questions requiring user input (if any)
   - `## Assumptions Made` - Decisions made when scope was ambiguous
   - `## Recommendations` - Suggested next steps

   ## Clarification Log

   [Empty on first iteration]
   ```

### Phase 2: Invoke Agent

Invoke with minimal prompt pointing to scaffold:

```
Task(
  subagent_type: "humaninloop-experiments:experiment-runner",
  prompt: "
    Run the experiment.

    Read the scaffold at: $SCAFFOLD_FILE

    The scaffold contains all context, instructions, and where to write output.
  ",
  description: "Run experiment"
)
```

### Phase 3: Parse & Route

Parse agent's structured prose output:

**If `## Clarifications Needed` has questions:**
1. Present questions to user
2. Collect answers
3. Append to `$SCAFFOLD_FILE`'s `## Clarification Log`:
   ```markdown
   ### Round N - Agent Questions
   [Questions from agent output]

   ### Round N - User Answers
   [User's responses]
   ```
4. Update `$SCAFFOLD_FILE`'s `## Supervisor Instructions`:
   ```markdown
   User answered your questions (see Clarification Log).
   Continue the experiment incorporating their answers.

   Write results to: `result.md` (same directory)
   [Same output format instructions]
   ```
5. Increment `iteration` in `$SCAFFOLD_FILE` frontmatter
6. **Loop back to Phase 2**

**If no clarifications (or max iterations reached):**
- Proceed to Phase 4

### Phase 4: Finalize

1. **Update scaffold status**
   - Set status to `completed` in scaffold frontmatter

2. **Report to user**
   - Summarize experiment results (from `## What I Created`)
   - Present pass/fail assessment (from `## Results Summary`)
   - Note any assumptions made (from `## Assumptions Made`)
   - Share recommendations (from `## Recommendations`)

3. **Suggest next steps**
   - If successful: Consider promoting pattern to production
   - If failed: Document learnings, suggest alternative approaches
   - Optionally suggest committing experiment artifacts

---

## Supervisor Behaviors

- **Owns the loop**: Decides when to iterate vs. finalize
- **Modifies scaffold**: Updates instructions and appends to clarification log between iterations
- **Presents clarifications**: Chooses how to display agent questions to user
- **Injects context**: Can add sections to scaffold if needed mid-loop
- **Max iterations**: Limit to 3 rounds to prevent infinite loops
