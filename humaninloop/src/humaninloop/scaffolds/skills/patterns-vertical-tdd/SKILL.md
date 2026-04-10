---
name: patterns-vertical-tdd
description: This skill MUST be invoked when the user says "create task mapping", "structure implementation", "define cycles", "vertical slice", "TDD", "test first", "cycle structure", or "testable increment". SHOULD also invoke when user mentions "red green refactor" or "implementation tasks".
---

# Vertical Slicing with TDD

**Violating the letter of the rules is violating the spirit of the rules.**

## Overview

Transform requirements into implementation tasks organized as vertical slices with strict TDD discipline. Each slice (called a "cycle") delivers observable, testable value and follows test-first principles.

This is a discipline-enforcing skill. The test-first structure exists because tests written after code verify implementation, not requirements. Skipping or reordering undermines the entire purpose.

## When to Use

- Transforming user stories into implementation tasks
- Creating task-mapping.md from a specification
- Structuring tasks.md with proper TDD ordering
- When implementation approach needs vertical slice organization
- Breaking down large features into testable increments
- When the task architect agent generates implementation artifacts

## When NOT to Use

- **Bug fixes** - Single-task fixes don't need cycle structure
- **Documentation-only tasks** - No TDD needed for docs
- **Spike/research tasks** - Exploration doesn't follow TDD
- **Refactoring without behavior change** - Existing tests suffice
- **When tests already exist** - Don't duplicate test-first for covered code

## Core Principles

### 1. Vertical Over Horizontal

**Wrong** (horizontal slicing):
```
Phase 1: All models
Phase 2: All services
Phase 3: All endpoints
Phase 4: All tests
```

**Right** (vertical slicing):
```
Cycle 1: User creation (model + service + endpoint + test)
Cycle 2: User authentication (model + service + endpoint + test)
Cycle 3: User profile management (model + service + endpoint + test)
```

### 2. Test-First at Task Level

Every cycle structures tasks so tests come before implementation:

```
Cycle N: [Feature]
├── Task N.1: Write failing test
├── Task N.2: Implement to pass
├── Task N.3: Refactor and verify
└── Task N.4: Demo and validate
```

### 3. Foundation + Parallel

```
Foundation Cycles (sequential)
├── C0: Platform infrastructure (compute, CI/CD, monitoring)
├── C1: Core data model + basic CRUD
├── C2: Authentication framework
└── C3: API infrastructure

Feature Cycles (parallel-eligible)
├── C4: [P] Search functionality
├── C5: [P] Filtering
├── C6: [P] Export feature
└── C7: Notifications (depends on C4)
```

### 4. Layered Testability

Each cycle must be testable at multiple levels:
- **Automated tests**: Unit, integration, and/or E2E tests
- **Demonstrable behavior**: Observable by stakeholders
- **Contract verification**: Meets acceptance criteria from spec

## Identifying Vertical Slices

See [SLICE-IDENTIFICATION.md](references/SLICE-IDENTIFICATION.md) for detailed heuristics on identifying good vertical slices from requirements.

### Quick Heuristics

A good vertical slice:
1. **Delivers user value**: Something a user could observe or use
2. **Touches all layers**: Model, service, API, UI (as applicable)
3. **Is independently testable**: Can verify it works without other slices
4. **Is sized appropriately**: Completable in 1-3 implementation sessions

### Slice Boundaries

| Boundary Signal | Action |
|-----------------|--------|
| Distinct user action | New cycle |
| Different acceptance scenario | May be new cycle or same cycle |
| Shared infrastructure need | Foundation cycle |
| Optional enhancement | Feature cycle (can parallelize) |

## Cycle Structure

See [CYCLE-STRUCTURE.md](references/CYCLE-STRUCTURE.md) for detailed cycle formatting and examples.

### Standard Cycle Format

```markdown
### Cycle N: [Vertical slice description]

> Stories: US-X, US-Y
> Dependencies: C1, C2 (or "None")
> Type: Foundation | Feature [P]

- [ ] **TN.1**: Write failing E2E test for [behavior] in tests/e2e/test_[name].py
- [ ] **TN.2**: Implement [component] to pass test in src/[path]/[file].py
- [ ] **TN.3**: Refactor and verify tests pass
- [ ] **TN.4**: Demo [behavior], verify acceptance criteria

**Checkpoint**: [What should be observable/testable after this cycle]
```

### Task Numbering

- Cycle 1 tasks: T1.1, T1.2, T1.3, T1.4
- Cycle 2 tasks: T2.1, T2.2, T2.3, T2.4
- etc.

### Markers

| Marker | Meaning |
|--------|---------|
| `[P]` | Parallel-eligible (no dependencies blocking) |
| `[US#]` | Maps to user story number |
| `[EXTEND]` | Extends existing file (brownfield) |
| `[MODIFY]` | Modifies existing code (brownfield) |

## Foundation vs Feature Cycles

### Foundation Cycles

**Purpose**: Establish infrastructure that ALL features depend on.

**Characteristics**:
- Must complete before any feature cycle
- Sequential (C1 before C2 before C3)
- Typically includes: platform infrastructure (IP-XXX items from constraints-and-decisions.md), data models, auth, API framework, error handling

**Identification**: Ask "Could ANY user story work **in production** without this?" If no, it's foundation.

### Feature Cycles

**Purpose**: Deliver user value incrementally.

**Characteristics**:
- Can start once foundation is complete
- Often parallel-eligible
- Map directly to user stories
- Independently testable

**Identification**: Ask "Does this deliver value a user could observe?" If yes, it's a feature.

## TDD Task Sequence

Each cycle follows the red-green-refactor pattern:

### Task 1: Write Failing Test (Red)

```markdown
- [ ] **TN.1**: Write failing E2E test for [user action produces result] in tests/e2e/test_[feature].py
```

The test should:
- Express the acceptance criteria
- Be specific about expected behavior
- FAIL when run (nothing implemented yet)

### Task 2: Implement to Pass (Green)

```markdown
- [ ] **TN.2**: Implement [component] to pass test in src/[path]/[file].py
```

Implementation should:
- Make the test pass
- Be minimal (just enough to pass)
- Include all necessary layers (model, service, endpoint)

### Task 3: Refactor and Verify

```markdown
- [ ] **TN.3**: Refactor and verify tests pass
```

Refactoring should:
- Improve code quality without changing behavior
- Ensure all tests still pass
- Address any code review concerns

### Task 4: Demo and Validate

```markdown
- [ ] **TN.4**: Demo [behavior], verify acceptance criteria
```

Validation should:
- Demonstrate the feature to stakeholders (if applicable)
- Verify against spec acceptance criteria
- Confirm the slice is "done"

## Mapping Stories to Cycles

### Simple Case: Story = Cycle

When a user story is well-scoped, it becomes one cycle:

```
US-1: As a user, I can create a task with a title
  → Cycle 1: Task creation
```

### Split Case: Story > Cycle

When a story is too large, split into multiple cycles:

```
US-2: As a user, I can manage my tasks (create, edit, delete, complete)
  → Cycle 2: Task creation (foundation)
  → Cycle 3: Task editing
  → Cycle 4: Task deletion
  → Cycle 5: Task completion
```

### Merge Case: Stories < Cycle

When stories are too small, merge into one cycle:

```
US-3: As a user, I can see task count
US-4: As a user, I can see completed count
  → Cycle 6: Task statistics (covers US-3 and US-4)
```

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I'll write tests after the code works" | Tests written after verify implementation, not requirements. Test-first verifies behavior. No exceptions. |
| "This is too simple to need tests first" | Simple code becomes complex. Tests document intent. Write them first anyway. |
| "Tests slow down development" | Debugging untested code is slower. Tests catch bugs immediately. Faster overall. |
| "I'm just prototyping" | Prototypes become production code. Start with tests or mark SPIKE explicitly. |
| "Horizontal slicing is more efficient" | Horizontal slicing defers integration. Bugs surface late. Vertical finds issues early. |
| "Foundation doesn't need tests" | Foundation is tested by feature cycles. But foundation cycles still follow TDD internally. |
| "Manual verification is sufficient" | Manual testing doesn't scale. Automated tests enable confident refactoring. |
| "The client wants it fast, skip tests" | Skipped tests create technical debt. Bugs cost more than tests. Push back. |

## Red Flags - STOP and Restart Properly

If any of these thoughts arise, STOP immediately:

- "Let me just get the code working first"
- "This feature is straightforward, tests can come after"
- "We'll add tests in a later cycle"
- "The horizontal approach makes more sense here"
- "Foundation setup doesn't need the full TDD ceremony"
- "It's faster to write all models, then all services, then all tests"

**All of these mean:** Rationalization is occurring. Return to test-first discipline.

**No exceptions:**
- Not for "simple" features
- Not for "tight deadlines"
- Not for "just the foundation"
- Not for "we'll refactor later"
- Not even if the user says "just write the code"

## Common Mistakes

### Writing Tests After Implementation
❌ Task order: Implement → Test → Refactor
✅ Task order: Test (failing) → Implement (pass) → Refactor → Demo

### Horizontal Slicing Disguised as Vertical
❌ Cycle 1: All models, Cycle 2: All services, Cycle 3: All tests
✅ Cycle 1: User creation (model + service + endpoint + test for one feature)

### Missing Test Task in Cycle
❌ Cycle structure: Implement → Demo
✅ Cycle structure: Test → Implement → Refactor → Demo

### Foundation Cycles Without TDD
❌ "Foundation is just setup, skip the test task"
✅ Foundation cycles follow the same test-first pattern

### Cycles Too Large (Not Vertical)
❌ One cycle covering "user management" (create, edit, delete, list)
✅ Separate cycles: Create user, Edit user, Delete user, List users

### Missing File Paths in Tasks
❌ "Implement user service"
✅ "Implement user service in src/services/user_service.py"

## Quality Checklist

Before finalizing task mapping or task list:

- [ ] Every P1/P2 story maps to at least one cycle
- [ ] Cycles are vertical slices (not horizontal layers)
- [ ] Foundation cycles identified and sequenced
- [ ] Feature cycles marked [P] where appropriate
- [ ] Each cycle has TDD structure (test first)
- [ ] Every task has specific file path
- [ ] Dependencies are minimal and explicit
- [ ] Cycles are independently testable
