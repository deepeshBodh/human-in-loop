# Phase-Specific Review Checklists

This reference file contains detailed review checklists for each task phase. Used by the Devil's Advocate when reviewing task artifacts.

## Phase: Mapping Review

### Checklist Table

| Check | Question | Severity |
|-------|----------|----------|
| Story coverage | Are all P1/P2 stories mapped to cycles? | Critical |
| Cycle identification | Are cycles true vertical slices (not horizontal)? | Critical |
| Foundation separation | Are foundation cycles clearly identified? | Critical |
| Feature parallelization | Are feature cycles marked [P] where appropriate? | Important |
| Dependency accuracy | Are cycle dependencies correct and minimal? | Important |
| Slice sizing | Are cycles appropriately sized (not too big/small)? | Important |
| Traceability | Can we trace from story to cycle? | Important |

### Key Questions

- Are any P1/P2 stories missing from the mapping?
- Are there cycles that are really horizontal slices (all models, then all services)?
- Is the foundation too large? Too small?
- Are there unnecessary dependencies between feature cycles?
- Are any cycles too large (should be split)?
- Are any cycles too small (should be merged)?

### Vertical Slice Validation

For each cycle, ask:
1. Does it deliver observable user value?
2. Does it touch multiple layers (model, service, API)?
3. Can it be tested independently?
4. Is it sized for 1-3 implementation sessions?

If NO to any: the cycle may need restructuring.

---

## Phase: Tasks Review

### Checklist Table

| Check | Question | Severity |
|-------|----------|----------|
| Cycle coverage | Does every cycle from mapping have tasks? | Critical |
| TDD structure | Does each cycle have test-first task ordering? | Critical |
| File paths | Does every task have a specific file path? | Critical |
| Verification task | Does each cycle end with a **TEST:** verification task? | Critical |
| Real infrastructure | Do verification tasks use real infrastructure (not mocks)? | Critical |
| Task IDs | Are task IDs properly formatted (TN.X)? | Important |
| Story labels | Are tasks linked to stories where appropriate? | Important |
| Brownfield markers | Are [EXTEND]/[MODIFY] markers correctly applied? | Important |
| Parallel markers | Are [P] markers correctly applied to feature cycles? | Important |
| Checkpoints | Does each cycle have a human-verifiable checkpoint? | Important |
| Dependencies | Are dependencies between cycles correctly documented? | Important |

### Key Questions

- Are any cycles from the mapping missing from tasks.md?
- Does every cycle start with a test task?
- Are there tasks without file paths (using vague descriptions)?
- Do the task IDs follow the T{cycle}.{seq} format?
- Are feature cycles properly marked as parallel-eligible?
- Do checkpoints describe observable, testable outcomes?
- **Does every cycle end with a `**TEST:**` verification task?**
- **Do verification tasks specify concrete steps with real infrastructure?**
- **Do verification tasks have clear Setup/Action/Assert structure?**

### TDD Structure Validation

For each cycle, verify task ordering:
1. **First task**: Write failing test (TN.1)
2. **Middle tasks**: Implementation (TN.2, TN.3, ...)
3. **Near-last task**: Refactor and verify automated tests pass
4. **Last task**: `**TEST:**` verification with real infrastructure

If this order is violated: Critical issue.

### Verification Task Validation

For each cycle's final task, verify:

1. **Is it using `**TEST:**` format?** If it just says "Demo" or "Verify", it may be vague.
2. **Does it specify real infrastructure?** Look for concrete paths, commands, or UI actions.
3. **Does it have explicit steps?** Setup/Action/Assert format with specific commands.
4. **Does it have observable outcomes?** Clear Assert conditions.
5. **Does it include Capture?** Evidence collection for review (console, screenshot, logs).

**Good Verification Task:**
```markdown
- [ ] **T2.12**: **TEST:** - File watcher detects real files
  - **Setup**: `mkdir /tmp/test-dir`
  - **Action**: `dart run bin/watcher.dart /tmp/test-dir` (background)
  - **Action**: `sleep 1 && touch /tmp/test-dir/test.jsonl`
  - **Assert**: Console contains "FileWatchEvent: created"
  - **Capture**: console
```

**Bad Verification Task (REJECT):**
```markdown
- [ ] **T2.12**: Demo: Verify file watching infrastructure is functional
  - Checkpoint: PathValidator correctly rejects symlinks outside scope
```

Why bad? No concrete steps, no real files created, "checkpoint" describes what tests verify, not observable behavior.

---

## Cross-Artifact Review

### Checklist Table

| Check | Question | Severity |
|-------|----------|----------|
| Mapping-Tasks alignment | Does every cycle in mapping appear in tasks.md? | Critical |
| Story traceability | Can we trace Story -> Cycle -> Tasks? | Critical |
| Cycle consistency | Do cycle descriptions match between artifacts? | Important |
| Dependency consistency | Do dependencies match between artifacts? | Important |
| Foundation-Feature alignment | Is foundation/feature classification consistent? | Important |

### Cross-Reference Steps

1. **List all cycles from mapping**
2. **Verify each appears in tasks.md**
3. **Check descriptions match**
4. **Verify dependencies match**
5. **Confirm parallel markers match**

### Traceability Matrix Validation

Build and verify this chain:

```
US-1 (P1) -> Cycle 1 -> T1.1, T1.2, T1.3, T1.4
US-2 (P1) -> Cycle 2 -> T2.1, T2.2, T2.3, T2.4
US-3 (P2) -> Cycle 3 -> T3.1, T3.2, T3.3, T3.4
```

If any link is broken: Critical issue.

---

## Common Issues

### Mapping Phase

| Issue | Severity | Fix |
|-------|----------|-----|
| Missing P1 story | Critical | Add cycle for story |
| Horizontal slice | Critical | Restructure as vertical |
| Missing foundation | Critical | Identify shared infrastructure |
| Too many dependencies | Important | Review if truly required |
| Oversized cycle | Important | Split into smaller cycles |
| Undersized cycle | Minor | Consider merging |

### Tasks Phase

| Issue | Severity | Fix |
|-------|----------|-----|
| Missing cycle | Critical | Add tasks for cycle |
| No test task first | Critical | Reorder to test-first |
| Vague file paths | Critical | Specify exact paths |
| Missing verification task | Critical | Add `**TEST:**` task as final task |
| Mock-only verification | Critical | Rewrite with real infrastructure steps |
| Vague demo task | Critical | Add concrete Setup/Action/Assert steps |
| Wrong task ID format | Important | Fix to TN.X format |
| Missing checkpoint | Important | Add verifiable outcome |
| Test-only checkpoint | Important | Rewrite as observable behavior |
| Missing [P] marker | Minor | Add if parallel-eligible |

---

## Example Review Report

```markdown
# Advocate Report: Tasks Review

## Summary

| Metric | Value |
|--------|-------|
| **Phase** | Tasks |
| **Artifact** | specs/042-task-priority/tasks.md |
| **Verdict** | needs-revision |

## Issues Found

### Critical (2)

**Issue T-001**: Cycle 3 missing test-first structure

- **Evidence**: T3.1 is "Create PriorityService", T3.2 is "Write tests"
- **Impact**: Violates TDD discipline, tests may be afterthought
- **Suggested Fix**: Reorder T3.1 to be test, T3.2+ to be implementation

**Issue T-002**: Cycle 2 has mock-only verification task

- **Evidence**: T2.12 says "Demo: Verify file watching infrastructure is functional" with checkpoint "PathValidator correctly rejects symlinks outside scope"
- **Impact**: No real infrastructure tested. All tests could pass while feature doesn't work in production.
- **Suggested Fix**: Rewrite with `**TEST:**` format and real infrastructure:
  ```
  - [ ] **T2.12**: **TEST:** - File watcher detects real files
    - **Setup**: `mkdir /tmp/watcher-test`
    - **Action**: `dart run bin/watcher.dart /tmp/watcher-test` (background)
    - **Action**: `sleep 1 && touch /tmp/watcher-test/test.jsonl`
    - **Assert**: Console contains "FileWatchEvent: created"
    - **Capture**: console
  ```

### Important (2)

**Issue T-003**: Task T4.3 has vague file path

- **Evidence**: "Update relevant service files"
- **Impact**: Unclear which files will be modified
- **Suggested Fix**: Specify exact path: "src/services/task_service.py"

**Issue T-004**: Cycle 5 checkpoint is test-only

- **Evidence**: Checkpoint says "State updates reactively from file events"
- **Impact**: Describes what tests verify, not what human observes
- **Suggested Fix**: Rewrite as: "Human sees session appear in UI within 1 second of creating file"

### Minor (0)

None

## Strengths

- All P1/P2 stories mapped to cycles
- Foundation cycles clearly separated
- Good use of [P] markers for parallel features
- Task IDs follow correct format

## Verdict

**needs-revision**: 2 Critical issues (TDD ordering, mock-only verification) and 2 Important issues.
The mock-only verification is the most severe—without real infrastructure testing, the entire feature could be broken despite all tests passing.
Fixable in one iteration by the Task Architect using the unified `**TEST:**` format.
```
