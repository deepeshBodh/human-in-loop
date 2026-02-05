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
- [ ] **TN.4**: **TEST:** - [What to verify with real infrastructure]
  - **Setup**: [Prerequisites]
  - **Action**: [Command or instruction]
  - **Assert**: [Expected outcome]
  - **Capture**: [console, screenshot, logs]

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
4. **Verifiable**: Can be verified with real infrastructure (not just mocks)

### Good Checkpoints

- "Task created via API, console shows 201 response"
- "File watcher detects new file, console outputs event"
- "CLI export command creates CSV with correct data"
- "Server starts and responds to health check"

### Bad Checkpoints

- "Task model is complete" (not observable)
- "Code is clean" (subjective)
- "Service layer works" (too vague)
- "Ready for integration" (not testable)
- "All unit tests pass" (automated only, needs real verification)
- "PathValidator correctly rejects symlinks" (tested via mocks, not real files)
- "State updates reactively" (vague, likely tested via mocks)

---

## Verification Task Requirements

The final task of each cycle (typically TN.4) is the **Verification** task. This is NOT just another automated test—it is the gate that ensures the cycle delivers real, working functionality.

### What Verification MUST Include

1. **Real Infrastructure**: Use real file systems, real databases, real APIs—NOT mocks
2. **Tangible Output**: Something observable (console output, file, response, UI state)
3. **Explicit Steps**: Concrete commands or actions to perform
4. **Observable Outcome**: What should be observed when it works

### Unified TEST: Format

Use the `**TEST:**` marker for all verification tasks:

```markdown
- [ ] **TN.X**: **TEST:** - {Description}
  - **Setup**: {Prerequisites} (optional)
  - **Action**: {Command or instruction}
  - **Assert**: {Expected outcome}
  - **Capture**: {console, screenshot, logs} (optional)
```

The testing-agent **classifies tasks at runtime** and decides whether to auto-approve or present a human checkpoint:

| Classification | Criteria | Execution |
|----------------|----------|-----------|
| **CLI** | Backtick commands + measurable asserts | May auto-approve if 100% pass |
| **GUI** | UI actions, screenshot captures | Human checkpoint |
| **SUBJECTIVE** | Qualitative terms (looks, feels) | Human checkpoint |

**You do NOT need to decide** whether a task needs human verification—the testing-agent handles this.

### Field Definitions

| Field | Required | Purpose |
|-------|----------|---------|
| `**Setup**:` | No | Prerequisites to establish before testing |
| `**Action**:` | Yes | Commands or instructions to execute |
| `**Assert**:` | Yes | Conditions to verify (outcomes) |
| `**Capture**:` | No | Evidence types to collect |

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

### Examples

**CLI verification** (may auto-approve):
```markdown
- [ ] **T2.12**: **TEST:** - File watcher detects real file changes
  - **Setup**: `mkdir /tmp/watcher-test`
  - **Action**: `dart run bin/watcher.dart /tmp/watcher-test` (background)
  - **Action**: `sleep 1 && touch /tmp/watcher-test/test.jsonl`
  - **Assert**: Console contains "FileWatchEvent: created"
  - **Capture**: console
```

**API verification** (may auto-approve):
```markdown
- [ ] **T4.8**: **TEST:** - API server responds to health check
  - **Setup**: Ensure database is running
  - **Action**: `npm start` (background) (timeout 30s)
  - **Action**: `sleep 2 && curl -s localhost:3000/health`
  - **Assert**: Response status: 200
  - **Assert**: Console contains "Server listening on port 3000"
  - **Capture**: console
```

**GUI verification** (human checkpoint):
```markdown
- [ ] **T4.16**: **TEST:** - Sessions appear in UI from real files
  - **Setup**: Build app with `flutter build macos`
  - **Setup**: Create test session file in Claude sessions directory
  - **Action**: Launch the built application
  - **Assert**: Session appears in list within 1 second
  - **Assert**: Session shows correct project path with ~ alias
  - **Capture**: screenshot
```

**Subjective verification** (human checkpoint):
```markdown
- [ ] **T5.10**: **TEST:** - Dashboard layout is well-organized
  - **Action**: Open dashboard at localhost:3000/dashboard
  - **Assert**: Layout feels balanced and spacing looks consistent
  - **Capture**: screenshot
```

### Bad Verification Tasks

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

Mocked tests verify that code does what the tests say. Real verification ensures the system does what the user needs. Without verification:

- All tests can pass while the feature doesn't work
- Integration issues between real components go undetected
- The "vertical slice" isn't actually vertical—it stops at the mock boundary

### Legacy Format Support

For backward compatibility, the testing-agent accepts these legacy markers (internally mapped to TEST:):
- `**TEST:VERIFY**`
- `**TEST:CONTRACT**`
- `**HUMAN VERIFICATION**` (maps Setup/Action/Verify fields)

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
- [ ] **T1.6**: **TEST:** - CRUD operations work via API
  - **Action**: `curl -X POST localhost:3000/api/tasks -d '{"title":"Test"}'`
  - **Assert**: Response status: 201
  - **Assert**: Console contains "task_id"
  - **Capture**: console

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
- [ ] **T2.7**: **TEST:** - Login returns valid token
  - **Action**: `curl -X POST localhost:3000/api/auth/login -d '{"email":"test@example.com","password":"test"}'`
  - **Assert**: Response status: 200
  - **Assert**: Console contains "token"
  - **Capture**: console

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
- [ ] **T3.6**: **TEST:** - Task completion updates timestamp
  - **Setup**: Create task via POST /api/tasks
  - **Action**: `curl -X PATCH localhost:3000/api/tasks/1/complete`
  - **Assert**: Response status: 200
  - **Assert**: Console contains "completed_at"
  - **Capture**: console

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
- [ ] **T4.6**: **TEST:** - Priority assignment works
  - **Action**: `curl -X POST localhost:3000/api/tasks -d '{"title":"Urgent","priority":"high"}'`
  - **Assert**: Response status: 201
  - **Assert**: Console contains "priority":"high"
  - **Capture**: console

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
- [ ] **T5.5**: **TEST:** - Filtering returns correct results
  - **Setup**: Create tasks with different statuses
  - **Action**: `curl "localhost:3000/api/tasks?status=pending"`
  - **Assert**: Response status: 200
  - **Assert**: Console contains only pending tasks
  - **Capture**: console

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
- [ ] **T6.5**: **TEST:** - CSV export creates valid file
  - **Setup**: Create several tasks
  - **Action**: `curl localhost:3000/api/export/csv -o /tmp/tasks.csv`
  - **Assert**: File exists: /tmp/tasks.csv
  - **Assert**: Console contains "Content-Type: text/csv"
  - **Capture**: console

**Checkpoint**: Can export task list to valid CSV file
```
