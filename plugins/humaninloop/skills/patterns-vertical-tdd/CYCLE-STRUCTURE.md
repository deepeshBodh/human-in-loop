# Cycle Structure Reference

This reference file provides detailed cycle formatting, task structure, and examples.

## Cycle Anatomy

```markdown
### Cycle N: [Descriptive title of the vertical slice]

> Stories: US-X, US-Y (comma-separated story IDs this cycle covers)
> Dependencies: C1, C2 (cycles that must complete first, or "None")
> Type: Foundation | Feature [P] (Foundation = sequential, Feature [P] = parallel-eligible)

- [ ] **TN.1**: Write failing test for [behavior] in [test file path]
- [ ] **TN.2**: Implement [component] to pass test in [source file path]
- [ ] **TN.3**: Refactor and verify tests pass
- [ ] **TN.4**: Demo [behavior], verify acceptance criteria

**Checkpoint**: [Observable outcome when cycle is complete]
```

## Task ID Format

Tasks use hierarchical IDs: `T{cycle}.{sequence}`

| Cycle | Task IDs |
|-------|----------|
| Cycle 1 | T1.1, T1.2, T1.3, T1.4 |
| Cycle 2 | T2.1, T2.2, T2.3, T2.4 |
| Cycle 3 | T3.1, T3.2, T3.3, T3.4 |

If a cycle needs more than 4 tasks:
- T1.5, T1.6, etc. for additional implementation
- Keep test task first, demo task last

## File Path Conventions

Every task MUST include a specific file path.

### Test Files
```
tests/e2e/test_[feature].py
tests/integration/test_[feature].py
tests/unit/test_[module].py
tests/contract/test_[endpoint].py
```

### Source Files
```
src/models/[entity].py
src/services/[service].py
src/api/[endpoint].py
src/[feature]/[component].py
```

### Adjust for Project Structure

| Project Type | Source | Tests |
|--------------|--------|-------|
| Single app | `src/` | `tests/` |
| Backend/Frontend | `backend/src/`, `frontend/src/` | `backend/tests/`, `frontend/tests/` |
| Monorepo | `packages/[pkg]/src/` | `packages/[pkg]/tests/` |

## Foundation Cycle Examples

### Example: Core Entity

```markdown
### Cycle 1: Task entity and basic creation

> Stories: US-1
> Dependencies: None
> Type: Foundation

- [ ] **T1.1**: Write failing E2E test for task creation in tests/e2e/test_task_creation.py
- [ ] **T1.2**: Create Task model with title, status fields in src/models/task.py
- [ ] **T1.3**: Implement TaskService.create() in src/services/task_service.py
- [ ] **T1.4**: Create POST /api/tasks endpoint in src/api/tasks.py
- [ ] **T1.5**: Refactor and verify tests pass
- [ ] **T1.6**: Demo task creation, verify acceptance criteria

**Checkpoint**: Can create a task via API and retrieve it
```

### Example: Authentication

```markdown
### Cycle 2: User authentication framework

> Stories: (infrastructure)
> Dependencies: C1
> Type: Foundation

- [ ] **T2.1**: Write failing test for user login in tests/e2e/test_auth.py
- [ ] **T2.2**: Create User model with password hash in src/models/user.py
- [ ] **T2.3**: Implement AuthService with login/logout in src/services/auth_service.py
- [ ] **T2.4**: Create POST /api/auth/login endpoint in src/api/auth.py
- [ ] **T2.5**: Add JWT middleware in src/middleware/auth.py
- [ ] **T2.6**: Refactor and verify tests pass
- [ ] **T2.7**: Demo login flow, verify token generation

**Checkpoint**: Can log in and receive valid auth token
```

## Feature Cycle Examples

### Example: Simple Feature

```markdown
### Cycle 4: [P] Task completion

> Stories: US-2
> Dependencies: C1
> Type: Feature [P]

- [ ] **T4.1**: Write failing test for marking task complete in tests/e2e/test_task_completion.py
- [ ] **T4.2**: [EXTEND] Add completed_at field to Task model in src/models/task.py
- [ ] **T4.3**: Implement TaskService.complete() in src/services/task_service.py
- [ ] **T4.4**: Create PATCH /api/tasks/{id}/complete endpoint in src/api/tasks.py
- [ ] **T4.5**: Refactor and verify tests pass
- [ ] **T4.6**: Demo task completion, verify acceptance criteria

**Checkpoint**: Can mark a task as complete and see completion timestamp
```

### Example: Feature with Multiple Stories

```markdown
### Cycle 5: [P] Task filtering

> Stories: US-4, US-6
> Dependencies: C1
> Type: Feature [P]

- [ ] **T5.1**: Write failing tests for status and priority filters in tests/e2e/test_task_filtering.py
- [ ] **T5.2**: Implement TaskService.list() with filter params in src/services/task_service.py
- [ ] **T5.3**: Update GET /api/tasks with query params in src/api/tasks.py
- [ ] **T5.4**: Refactor and verify tests pass
- [ ] **T5.5**: Demo filtering by status and priority, verify acceptance criteria

**Checkpoint**: Can filter task list by status and priority via API
```

## Brownfield Markers

When working with existing code, apply markers:

| Marker | When to Use | Example |
|--------|-------------|---------|
| `[EXTEND]` | Adding to existing file | Adding a field to existing model |
| `[MODIFY]` | Changing existing code | Updating existing service method |
| (none) | New file | Creating new endpoint file |

### Example with Brownfield

```markdown
### Cycle 6: [P] Task priority

> Stories: US-3
> Dependencies: C1
> Type: Feature [P]

- [ ] **T6.1**: Write failing test for priority assignment in tests/e2e/test_task_priority.py
- [ ] **T6.2**: [EXTEND] Add priority field to Task model in src/models/task.py
- [ ] **T6.3**: [MODIFY] Update TaskService.create() to accept priority in src/services/task_service.py
- [ ] **T6.4**: [MODIFY] Update POST /api/tasks to accept priority in src/api/tasks.py
- [ ] **T6.5**: Refactor and verify tests pass
- [ ] **T6.6**: Demo priority assignment, verify acceptance criteria

**Checkpoint**: Can create tasks with priority and update existing task priority
```

## Checkpoint Guidelines

Checkpoints should be:

1. **Observable**: Something you can see or demonstrate
2. **Testable**: Automated tests should verify this
3. **Concrete**: Specific behavior, not abstract quality
4. **Human-Verifiable**: A human MUST see the behavior in a real environment, not just in test output

### Good Checkpoints (Human-Verifiable)

- "Human launched app and created task via UI, task appears in list"
- "Human called POST /api/tasks via curl, received 201 response with task ID"
- "Human ran CLI export command, CSV file created with correct data"
- "Human created file in watched directory, event appeared in console output"

### Bad Checkpoints (Test-Only)

- "Task model is complete" (not observable)
- "Code is clean" (subjective)
- "Service layer works" (too vague)
- "Ready for integration" (not testable)
- "All unit tests pass" (automated only, not human-verified)
- "PathValidator correctly rejects symlinks" (tested via mocks, not real files)
- "State updates reactively" (vague, likely tested via mocks)

---

## Human Verification Task Requirements

The final task of each cycle (typically TN.4) is the **Human Verification** task. This is NOT just another automated test—it is the gate that ensures the cycle delivers real, working functionality.

### What Human Verification MUST Include

1. **Real Infrastructure**: Use real file systems, real databases, real APIs—NOT mocks
2. **Tangible Output**: Something a human can see, click, or receive (UI, file, response)
3. **Explicit Steps**: Concrete commands or actions the human performs
4. **Observable Outcome**: What the human should see when it works
5. **Sign-off Gate**: Cycle does not complete until human confirms behavior

### Human Verification Task Format

```markdown
- [ ] **TN.4**: **HUMAN VERIFICATION** - [Brief description of what to verify]
  - Setup: [Any prerequisites or test data to create]
  - Action: [Specific command or UI action to perform]
  - Verify: [What the human should observe]
  - Cleanup: [Optional cleanup steps]
  - **Human confirms**: [Checkbox or explicit sign-off]
```

### Good Human Verification Tasks

```markdown
- [ ] **T2.12**: **HUMAN VERIFICATION** - File watcher detects real file changes
  - Setup: Create test directory `mkdir /tmp/watcher-test`
  - Action: Run `dart run bin/watcher.dart /tmp/watcher-test`
  - Action: In another terminal, `touch /tmp/watcher-test/session.jsonl`
  - Verify: Console outputs "FileWatchEvent: created /tmp/watcher-test/session.jsonl"
  - Action: `rm /tmp/watcher-test/session.jsonl`
  - Verify: Console outputs "FileWatchEvent: deleted ..."
  - **Human confirms**: Events appear in real time ✓
```

```markdown
- [ ] **T4.16**: **HUMAN VERIFICATION** - Sessions appear in UI from real files
  - Setup: Build app with `flutter build macos`
  - Setup: Create test session file in Claude sessions directory
  - Action: Launch the built application
  - Verify: Session appears in list within 1 second
  - Verify: Session shows correct project path with ~ alias
  - Action: Delete the session file
  - Verify: Session disappears from list within 1 second
  - **Human confirms**: Full session lifecycle works ✓
```

### Bad Human Verification Tasks

```markdown
# BAD: Just re-running automated tests
- [ ] **T2.12**: Demo: Verify file watching infrastructure is functional
  - Checkpoint: PathValidator correctly rejects symlinks outside scope

# BAD: Vague with no concrete steps
- [ ] **T4.16**: Demo: Verify full user story functionality
  - Checkpoint: All 5 acceptance scenarios pass

# BAD: Relies on mocked infrastructure
- [ ] **T3.12**: Demo: Verify state management is functional
  - Checkpoint: State updates reactively from file events
```

### Why This Matters

Mocked tests verify that code does what the tests say. Human verification ensures the system does what the user needs. Without human verification:

- All tests can pass while the feature doesn't work
- Integration issues between real components go undetected
- The "vertical slice" isn't actually vertical—it stops at the mock boundary

---

## Testable Verification Tasks (TEST:VERIFY)

When human verification can be automated via CLI with measurable outcomes, use the `**TEST:VERIFY**` format instead of plain `**HUMAN VERIFICATION**`.

### TEST:VERIFY Format

```markdown
- [ ] **TN.X**: **TEST:VERIFY** - {Description}
  - **Setup**: {Prerequisites} (optional)
  - **Action**: {Command} (can have multiple)
  - **Assert**: {Expected outcome} (can have multiple)
  - **Capture**: {console, screenshot, logs} (optional)
  - **Human-Review**: {What human should evaluate}
```

### Field Definitions

| Field | Required | Purpose |
|-------|----------|---------|
| `**Setup**:` | No | Prerequisites to establish before testing |
| `**Action**:` | Yes | Commands to execute (can repeat) |
| `**Assert**:` | Yes | Conditions to verify (can repeat) |
| `**Capture**:` | No | Evidence types to collect |
| `**Human-Review**:` | No | What human should specifically evaluate |

### Action Modifiers

| Modifier | Example | Behavior |
|----------|---------|----------|
| `(background)` | `npm start (background)` | Run async, track PID |
| `(timeout Ns)` | `curl ... (timeout 10s)` | Override 60s default |
| `(in {path})` | `make build (in ./backend)` | Execute in directory |

### Assert Patterns

| Pattern | Verification |
|---------|--------------|
| `Console contains "{text}"` | Substring match in output |
| `Console contains "{text}" (within Ns)` | Timed match |
| `File exists: {path}` | Check file system |
| `Response status: {code}` | HTTP status check |

### Example: File Watcher Verification

**Before** (HUMAN VERIFICATION):
```markdown
- [ ] **T2.12**: **HUMAN VERIFICATION** - File watcher detects real file changes
  - Setup: Create test directory `mkdir /tmp/watcher-test`
  - Action: Run `dart run bin/watcher.dart /tmp/watcher-test`
  - Action: In another terminal, `touch /tmp/watcher-test/session.jsonl`
  - Verify: Console outputs "FileWatchEvent: created ..."
  - **Human confirms**: Events appear in real time ✓
```

**After** (TEST:VERIFY):
```markdown
- [ ] **T2.12**: **TEST:VERIFY** - File watcher detects real file changes
  - **Setup**: `mkdir /tmp/watcher-test`
  - **Action**: `dart run bin/watcher.dart /tmp/watcher-test` (background)
  - **Action**: `sleep 1 && touch /tmp/watcher-test/test.jsonl`
  - **Assert**: Console contains "FileWatchEvent: created"
  - **Capture**: console
  - **Human-Review**: Events appear within 1 second
```

### Example: API Server Verification

```markdown
- [ ] **T4.8**: **TEST:VERIFY** - API server responds to health check
  - **Setup**: Ensure database is running
  - **Action**: `npm start` (background) (timeout 30s)
  - **Action**: `sleep 2 && curl -s localhost:3000/health`
  - **Assert**: Response status: 200
  - **Assert**: Console contains "Server listening on port 3000"
  - **Capture**: console
  - **Human-Review**: Server starts without errors
```

### When to Use Each Format

| Use TEST:VERIFY | Use HUMAN VERIFICATION |
|-----------------|------------------------|
| CLI commands with output | GUI/UI interaction required |
| API calls checkable via curl | Visual design verification |
| File operations | Subjective user experience |
| Process startup with logs | Multi-step UI workflows |
| Any bash-executable action | Non-CLI-accessible behavior |

### Benefits of TEST:VERIFY

1. **Automated execution**: Testing agent runs commands
2. **Evidence capture**: Console output saved automatically
3. **Structured assertions**: Pass/fail clearly defined
4. **Checkpoint presentation**: Human sees evidence summary
5. **Retry support**: Can re-run with adjustments

The human still approves—but the execution and evidence collection are automated

## Complete Example: Task Management Feature

```markdown
# Implementation Tasks: task-management

## Foundation Cycles

### Cycle 1: Task entity and basic CRUD

> Stories: US-1
> Dependencies: None
> Type: Foundation

- [ ] **T1.1**: Write failing E2E tests for task CRUD in tests/e2e/test_task_crud.py
- [ ] **T1.2**: Create Task model in src/models/task.py
- [ ] **T1.3**: Implement TaskService in src/services/task_service.py
- [ ] **T1.4**: Create task API endpoints in src/api/tasks.py
- [ ] **T1.5**: Refactor and verify tests pass
- [ ] **T1.6**: Demo CRUD operations, verify acceptance criteria

**Checkpoint**: Can create, read, update, delete tasks via API

---

### Cycle 2: User authentication

> Stories: (infrastructure)
> Dependencies: C1
> Type: Foundation

- [ ] **T2.1**: Write failing test for auth flow in tests/e2e/test_auth.py
- [ ] **T2.2**: Create User model in src/models/user.py
- [ ] **T2.3**: Implement AuthService in src/services/auth_service.py
- [ ] **T2.4**: Create auth endpoints in src/api/auth.py
- [ ] **T2.5**: Add auth middleware in src/middleware/auth.py
- [ ] **T2.6**: Refactor and verify tests pass
- [ ] **T2.7**: Demo login/logout, verify token handling

**Checkpoint**: Can authenticate and access protected endpoints

---

## Feature Cycles

### Cycle 3: [P] Task completion

> Stories: US-2
> Dependencies: C1, C2
> Type: Feature [P]

- [ ] **T3.1**: Write failing test for task completion in tests/e2e/test_completion.py
- [ ] **T3.2**: [EXTEND] Add completion fields to Task in src/models/task.py
- [ ] **T3.3**: [EXTEND] Add complete() to TaskService in src/services/task_service.py
- [ ] **T3.4**: Add completion endpoint in src/api/tasks.py
- [ ] **T3.5**: Refactor and verify tests pass
- [ ] **T3.6**: Demo task completion, verify acceptance criteria

**Checkpoint**: Can mark tasks complete with timestamp

---

### Cycle 4: [P] Task priority

> Stories: US-3
> Dependencies: C1, C2
> Type: Feature [P]

- [ ] **T4.1**: Write failing test for priority in tests/e2e/test_priority.py
- [ ] **T4.2**: [EXTEND] Add priority field to Task in src/models/task.py
- [ ] **T4.3**: [MODIFY] Update TaskService for priority in src/services/task_service.py
- [ ] **T4.4**: [MODIFY] Update task endpoints for priority in src/api/tasks.py
- [ ] **T4.5**: Refactor and verify tests pass
- [ ] **T4.6**: Demo priority assignment, verify acceptance criteria

**Checkpoint**: Can assign and update task priority

---

### Cycle 5: [P] Task filtering

> Stories: US-4
> Dependencies: C1, C2
> Type: Feature [P]

- [ ] **T5.1**: Write failing tests for filters in tests/e2e/test_filtering.py
- [ ] **T5.2**: [EXTEND] Add filter methods to TaskService in src/services/task_service.py
- [ ] **T5.3**: [MODIFY] Update list endpoint with query params in src/api/tasks.py
- [ ] **T5.4**: Refactor and verify tests pass
- [ ] **T5.5**: Demo filtering, verify acceptance criteria

**Checkpoint**: Can filter tasks by status and priority

---

### Cycle 6: [P] CSV export

> Stories: US-5
> Dependencies: C1, C2
> Type: Feature [P]

- [ ] **T6.1**: Write failing test for export in tests/e2e/test_export.py
- [ ] **T6.2**: Create ExportService in src/services/export_service.py
- [ ] **T6.3**: Add export endpoint in src/api/export.py
- [ ] **T6.4**: Refactor and verify tests pass
- [ ] **T6.5**: Demo CSV export, verify file format

**Checkpoint**: Can export task list to valid CSV file
```
