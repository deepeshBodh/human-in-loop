---
name: brownfield-integration
description: This skill MUST be invoked when encountering tasks with `[EXTEND]` or `[MODIFY]` markers against existing codebases. SHOULD also invoke when implementing tasks that reference existing files, follow existing patterns, or integrate with established interfaces.
---

# Brownfield Integration

## Overview

Guidance for implementing tasks that touch existing code. When a task says `[EXTEND]`, add new code following existing patterns. When a task says `[MODIFY]`, change specific behavior as described. In both cases, read the existing code first and respect what is already there.

**The existing code is not wrong until proven otherwise.** It has consumers, tests, and patterns that evolved for reasons you may not immediately see.

## When to Use

- Tasks marked with `[EXTEND]` — adding new functionality to existing files
- Tasks marked with `[MODIFY]` — changing existing behavior in files
- Any task that references files already on disk
- When following patterns established by previous cycles

## When NOT to Use

- Greenfield tasks creating entirely new files
- Tasks with no reference to existing code
- Refactoring work (which should not happen during cycle execution)

## Core Process

### EXTEND vs. MODIFY Semantics

| Marker | Meaning | Scope | Interface Impact |
|--------|---------|-------|-----------------|
| `[EXTEND]` | Add new code alongside existing code | New functions, new methods, new exports | MUST NOT change existing function signatures, exports, or type contracts |
| `[MODIFY]` | Change existing behavior | Specified sections only | MAY change function internals; MUST NOT change signatures unless task explicitly says so |

**Never MODIFY when the task says EXTEND.** If you believe the existing code cannot support the extension, flag it in the cycle report — do not silently rewrite.

### Read-Before-Write Checklist

Before writing any code in an existing file, complete all five steps:

1. **Read the full file** — not just the section you plan to change. Understand the complete context.
2. **Identify naming conventions** — variable naming (camelCase, snake_case), file naming, function naming patterns. Follow them exactly.
3. **Identify error handling patterns** — how does existing code handle errors? Try-catch, Result types, error callbacks? Match the pattern.
4. **Identify import style** — relative vs. absolute imports, named vs. default exports, import ordering. Follow the same style.
5. **Identify test patterns** — if the file has tests, how are they structured? Match describe/it nesting, assertion style, fixture patterns.

### Interface Preservation

When extending existing code:

- Do NOT change function signatures (parameter order, types, return types)
- Do NOT change export surfaces (what is exported, export names)
- Do NOT rename existing variables, functions, or classes
- Do NOT change the file's public API unless the task explicitly says `[MODIFY]`
- DO add new exports alongside existing ones
- DO follow the file's established patterns for new code

### Conflict Detection

Before adding new code, check for:

- **Name collisions** — search the file for the function/class/variable name you plan to add
- **Import collisions** — verify your new imports don't shadow existing ones
- **Test file alignment** — if adding to `user.ts`, check that `user.test.ts` exists and follow its patterns
- **Circular dependencies** — verify your new imports don't create circular reference chains

### When to Flag

Flag in the cycle report (do NOT silently resolve) when:

- Existing code contradicts the task description
- The file's patterns are inconsistent (multiple conflicting conventions)
- The task says `[EXTEND]` but the existing interface cannot support the addition without modification
- Existing tests would break from the addition (interface leak)
- The file has no tests but the task expects test-first development

## Common Mistakes

### Mistake: Not Reading the Full File

**What goes wrong:** You add code that duplicates existing functionality, uses different naming conventions, or conflicts with code you didn't see.

**Fix:** Always read the entire file before making any changes. Skim is not sufficient for brownfield work.

### Mistake: Silently Rewriting When Asked to Extend

**What goes wrong:** Existing consumers break because the interface changed. Tests fail for unrelated code. The cycle report doesn't explain why unrelated files were modified.

**Fix:** EXTEND means extend. If you cannot extend, flag it. Never silently rewrite.

### Mistake: Ignoring Existing Error Handling

**What goes wrong:** Your new code throws raw exceptions while the rest of the file uses Result types. Or your code returns null while existing code throws. Inconsistency confuses consumers.

**Fix:** Step 3 of the Read-Before-Write Checklist. Match the existing error handling pattern exactly.

### Mistake: Adding "Better" Patterns

**What goes wrong:** You introduce a "better" pattern alongside the existing one. Now the file has two patterns. The next developer doesn't know which to follow. Consistency is more valuable than local improvement.

**Fix:** Follow existing patterns, even if you'd prefer different ones. Note the improvement opportunity in the cycle report.

## Red Flags — STOP and Reconsider

- "This existing code is messy, I'll clean it up" — Not your scope. Note it, don't fix it.
- "I'll use a better pattern here" — Consistency beats local optimization. Follow what exists.
- "The existing tests don't cover this" — That's a pre-existing gap, not your problem to fix now.
- "I need to refactor this to make my change work" — Flag it in the cycle report. Don't silently refactor.
- "This interface doesn't make sense" — It made sense to someone. Read more context before judging.
