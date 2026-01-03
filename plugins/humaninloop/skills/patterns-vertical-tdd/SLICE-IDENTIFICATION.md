# Slice Identification Heuristics

This reference file provides detailed guidance on identifying good vertical slices from requirements.

## The Value Stream Test

For each potential slice, ask: "Can a user observe or use this independently?"

| Answer | Action |
|--------|--------|
| Yes, directly | Good slice candidate |
| Yes, but needs other slices first | Check if it's a dependency or can be deferred |
| No, it's infrastructure | Foundation cycle |
| No, it's internal refactoring | Not a slice; attach to a feature cycle |

## Extraction from User Stories

### Step 1: List All User Stories

Extract from spec.md:
```
US-1 (P1): As a user, I can create a task with a title
US-2 (P1): As a user, I can mark a task as complete
US-3 (P2): As a user, I can set task priority
US-4 (P2): As a user, I can filter tasks by status
US-5 (P3): As a user, I can export tasks to CSV
```

### Step 2: Identify Foundation Needs

Ask: "What must exist before ANY of these stories can work?"

Common foundation elements:
- Data model for core entities
- Authentication/authorization
- API routing infrastructure
- Database setup
- Error handling framework

### Step 3: Map Stories to Cycles

| Story | Cycle | Rationale |
|-------|-------|-----------|
| US-1 | C1 (Foundation) | Creates the core Task entity; everything depends on this |
| US-2 | C2 (Feature) | Adds status field and completion logic |
| US-3 | C3 (Feature) | Adds priority field and assignment |
| US-4 | C4 (Feature) | Query/filter logic; independent of US-3 |
| US-5 | C5 (Feature) | Export logic; can parallelize with others |

### Step 4: Identify Parallelization

After foundation:
- C2, C3, C4, C5 can all proceed in parallel
- Mark each with [P]

## Size Calibration

### Too Small

Signs a slice is too small:
- Single function or method
- No testable behavior
- Takes < 30 minutes to implement

**Fix**: Merge with related slices.

### Too Large

Signs a slice is too large:
- Multiple distinct user actions
- Would take > 1 day to implement
- Has internal phases ("first this, then that")

**Fix**: Split into smaller slices.

### Just Right

A well-sized slice:
- One coherent user action
- 1-3 hours to implement
- Clear test scenario
- Obvious when it's "done"

## Dependency Analysis

### Dependency Types

| Type | Description | Handling |
|------|-------------|----------|
| Data | Cycle B needs entity from Cycle A | A is foundation for B |
| API | Cycle B calls endpoint from Cycle A | A is foundation for B |
| UI | Cycle B shows component from Cycle A | A is foundation for B |
| None | Cycles are independent | Both can be [P] |

### Minimizing Dependencies

1. **Extract shared infrastructure to foundation**
   - Don't make feature cycles depend on each other
   - Move shared needs to foundation

2. **Accept some duplication**
   - If extracting creates complexity, duplicate
   - Refactor later in a dedicated cycle

3. **Order by priority when dependencies exist**
   - If C4 depends on C3, and C3 is P2 while C4 is P3, natural order works

## Examples by Domain

### CRUD Feature

```
Foundation:
  C1: Basic entity creation

Features:
  C2: [P] Read/list entities
  C3: [P] Update entity
  C4: [P] Delete entity
```

### Search Feature

```
Foundation:
  C1: Data model with searchable fields
  C2: Search infrastructure

Features:
  C3: [P] Basic text search
  C4: [P] Filter by field
  C5: [P] Sort results
  C6: Pagination (depends on C3-C5)
```

### Authentication Feature

```
Foundation:
  C1: User model and storage
  C2: Password hashing and validation
  C3: Session/token management

Features:
  C4: [P] Login flow
  C5: [P] Logout flow
  C6: [P] Password reset
  C7: OAuth integration (if applicable)
```

## Anti-Patterns

### Horizontal Slicing

**Wrong**:
```
Cycle 1: All database models
Cycle 2: All service classes
Cycle 3: All API endpoints
Cycle 4: All tests
```

**Problem**: Nothing is testable until Cycle 4 completes.

### Big Bang Integration

**Wrong**:
```
Cycle 1: Build entire backend
Cycle 2: Build entire frontend
Cycle 3: Integrate
```

**Problem**: Integration issues discovered too late.

### Premature Generalization

**Wrong**:
```
Cycle 1: Build generic CRUD framework
Cycle 2: Apply to all entities
```

**Problem**: Framework complexity without concrete use case.

## Decision Matrix

When unsure how to slice, use this matrix:

| Question | If Yes | If No |
|----------|--------|-------|
| Is this user-facing? | Feature cycle | May be foundation |
| Does it need other features? | Consider dependency ordering | Can be [P] |
| Is it > 1 day of work? | Split it | Good size |
| Is it < 30 min of work? | Merge it | Good size |
| Can it be tested in isolation? | Good slice | Reconsider boundaries |
