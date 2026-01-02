---
name: brownfield-patterns
description: Patterns for working with existing codebases. Use when integrating new features into established code, understanding legacy systems, or assessing change impact. Essential for any brownfield (vs greenfield) development work.
---

# Brownfield Patterns

## Purpose

Provide systematic approaches for understanding, integrating with, and extending existing codebases. These patterns help navigate the complexity of brownfield development where new work must coexist with established code.

## Core Principles

1. **Understand Before Changing**: Map existing patterns before introducing new ones
2. **Minimize Disruption**: Prefer extension over modification
3. **Respect Existing Conventions**: Adopt the codebase's style, not your preference
4. **Assess Impact**: Trace ripple effects of changes
5. **Document Decisions**: Explain why you did/didn't reuse existing code

## Discovery Pattern

### Phase 1: Identify Existing Assets

For any new feature, search for:

| Asset Type | Questions | Tools |
|------------|-----------|-------|
| **Entities** | Do similar data structures exist? | Grep for types, schemas |
| **Endpoints** | Are there related API patterns? | Grep for routes, controllers |
| **Components** | Are there reusable UI elements? | Glob for component directories |
| **Utilities** | Are there helper functions? | Grep for common operations |
| **Patterns** | What architectural patterns are used? | Read key files, configs |

### Phase 2: Classify Relevance

For each discovered asset:

| Classification | Meaning | Action |
|----------------|---------|--------|
| **[REUSE]** | Directly usable as-is | Reference existing |
| **[EXTEND]** | Usable with additions | Extend, don't copy |
| **[REFERENCE]** | Pattern to follow | Adopt conventions |
| **[COLLISION]** | Conflicts with new work | Resolve explicitly |
| **[IRRELEVANT]** | No relation | Ignore |

### Phase 3: Document Inventory

```markdown
## Brownfield Inventory

### Entities Found
| Entity | Location | Relevance | Notes |
|--------|----------|-----------|-------|
| User | src/models/user.ts | [EXTEND] | Add new fields |

### Patterns Identified
| Pattern | Example | Adopt? |
|---------|---------|--------|
| Repository pattern | src/repos/ | Yes |

### Conventions
- Naming: camelCase for functions, PascalCase for classes
- File structure: feature-based folders
- Error handling: Result<T, Error> pattern
```

## Impact Assessment Pattern

Before making changes:

### 1. Trace Dependencies

```
Changed file → Imports it → Imports that → ... (max 3 levels)
```

### 2. Classify Risk

| Risk Level | Criteria | Approach |
|------------|----------|----------|
| **Low** | Internal change, no public interface change | Proceed |
| **Medium** | Interface change, few dependents | Update dependents |
| **High** | Core component, many dependents | Escalate for review |

### 3. Document Impact

```markdown
### Impact Assessment

**Change**: {description}
**Files Directly Modified**: {count}
**Downstream Dependents**: {count}
**Risk Level**: {low|medium|high}
**Mitigation**: {approach}
```

## Integration Strategies

### Strategy 1: Extension

When existing code is close but not exact:

```
✓ Add new fields to existing entity
✓ Add new methods to existing class
✓ Add new endpoint to existing controller
✗ Don't fork/copy with modifications
```

### Strategy 2: Wrapper

When you can't modify existing code:

```
✓ Create wrapper that adapts interface
✓ Delegate to existing implementation
✓ Add new behavior in wrapper
✗ Don't duplicate logic
```

### Strategy 3: Parallel + Migrate

When existing code must be replaced:

```
1. Build new implementation alongside old
2. Feature flag to switch between
3. Migrate incrementally
4. Remove old after migration complete
```

## Collision Resolution Pattern

When new requirements conflict with existing code:

### 1. Identify the Collision

```markdown
**New Requirement**: {what you need}
**Existing Behavior**: {what exists}
**Conflict**: {why they clash}
```

### 2. Evaluate Options

| Option | Pros | Cons |
|--------|------|------|
| Modify existing | Single source | May break dependents |
| Create parallel | No risk to existing | Duplication |
| Abstract common | Clean long-term | More work now |

### 3. Decide and Document

```markdown
**Decision**: {chosen option}
**Rationale**: {why this choice}
**Trade-offs Accepted**: {what you're giving up}
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Not Invented Here** | Ignoring existing solutions | Always search first |
| **Copy-Paste Modify** | Creates unmaintainable forks | Extend or wrap |
| **Breaking Changes** | Disrupts existing functionality | Assess impact first |
| **Style Clash** | New code looks foreign | Adopt existing conventions |
| **Undocumented Decisions** | No record of why | Document choices |

## When to Use These Patterns

- Starting work in an unfamiliar codebase
- Adding features to established systems
- Integrating with legacy code
- Assessing refactoring scope
- Onboarding to a new project
