# Task Parsing

Rules for extracting task information from `tasks.md`. The Staff Engineer uses these rules to identify which tasks belong to the current cycle, what files to create or modify, and how to handle brownfield markers.

## Task Pattern

```markdown
- [ ] **T{N}.{X}**: Description with `file/path.ts` reference
  - Sub-bullet with additional details
  - Another sub-bullet
```

### Pattern Components

| Component | Format | Example |
|-----------|--------|---------|
| Checkbox | `- [ ]` (pending) or `- [x]` (complete) | `- [ ]` |
| Task ID | `**T{cycle}.{task}**:` | `**T3.2**:` |
| Description | Free text after the colon | `Implement user route handler` |
| File path | Backtick-wrapped path in description | `` `src/routes/user.ts` `` |
| Markers | `[EXTEND]` or `[MODIFY]` in description | `[EXTEND] existing model` |

## Cycle Identification

Tasks belong to a cycle based on their task ID prefix:
- `T1.*` = Cycle 1
- `T2.*` = Cycle 2
- `T{N}.*` = Cycle N

The current cycle is the first cycle with any unchecked tasks (`- [ ]`).

## File Path Extraction

File paths appear in backticks within the task description. A single task may reference multiple files:

```markdown
- [ ] **T2.3**: Create `src/models/user.ts` and test file `src/models/user.test.ts`
```

Extract all backtick-wrapped paths. Use them to determine:
- Which files to create (if path does not exist)
- Which files to read first (if `[EXTEND]` or `[MODIFY]`)

## Brownfield Markers

| Marker | Meaning | Action |
|--------|---------|--------|
| `[EXTEND]` | Add new code to existing file following existing patterns | Read file first. Add code. Do not change existing code. |
| `[MODIFY]` | Change existing behavior in the file | Read file first. Change only what the task specifies. |
| No marker | Create new file or greenfield implementation | Create file at specified path. |

### Marker Position

Markers appear in the task description, typically before the verb:

```markdown
- [ ] **T3.4**: [EXTEND] `src/models/user.ts` with lastLogin field
- [ ] **T4.2**: [MODIFY] `src/middleware/auth.ts` to check token expiry
```

## Multi-Line Tasks

Tasks with sub-bullets contain additional implementation details:

```markdown
- [ ] **T2.1**: Write failing tests for User model `src/models/user.test.ts`
  - Test user creation with valid data
  - Test validation rejects missing email
  - Test unique constraint on username
```

Sub-bullets are implementation guidance, not separate tasks. The parent task ID (`T2.1`) is the unit of completion — mark the parent `[x]` when all sub-bullets are addressed.

## Checkpoint Pattern

Each cycle ends with a checkpoint statement (not a task):

```markdown
**Checkpoint**: All user CRUD tests pass, lint clean, API routes registered
```

Checkpoints define the done criteria for the cycle. They are not marked with checkboxes.

## Quality Gates Pattern

Quality gates appear in a dedicated section, not as cycle tasks:

```markdown
## Quality Gates
- `pnpm lint` passes with zero errors
- `pnpm build` completes successfully
- `pnpm test` all tests pass
```

Quality gates are verified by the testing-agent, not the Staff Engineer.
