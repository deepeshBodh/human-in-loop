# SECTION-TEMPLATES.md

Reference file for CLAUDE.md section templates and sync rule definitions.

## Purpose

This file provides detailed templates for each CLAUDE.md section and explains how sync rules transform constitution content into agent instructions.

---

## Sync Rule Definitions

### MUST list all with enforcement

Principles appear in CLAUDE.md as a summarized list including enforcement keywords:

**Constitution (detailed)**:
```markdown
### I. Test-First Development (NON-NEGOTIABLE)

All production code MUST be written following test-driven development...

**Enforcement**:
- CI MUST verify test-before-implementation order
- Coverage MUST meet 80% minimum

**Testability**:
- Pass: All tests pass, coverage ≥80%
- Fail: Tests missing or coverage below threshold

**Rationale**: Tests written after implementation...
```

**CLAUDE.md (summarized)**:
```markdown
## Principles

1. **Test-First Development** (NON-NEGOTIABLE): TDD mandatory. CI enforces test-before-implementation. Coverage ≥80%.
2. **Code Quality**: Zero lint warnings. Functions ≤40 lines. Cyclomatic complexity ≤10.
3. ...
```

### MUST match exactly

Tables are copied directly with no summarization:

**Constitution**:
```markdown
## Technology Stack

| Category | Choice | Rationale |
|----------|--------|-----------|
| Language | Python 3.12 | Type hints, performance |
| Framework | FastAPI | Async-first, Pydantic |
```

**CLAUDE.md**:
```markdown
## Technical Stack

| Category | Choice | Rationale |
|----------|--------|-----------|
| Language | Python 3.12 | Type hints, performance |
| Framework | FastAPI | Async-first, Pydantic |
```

---

## CLAUDE.md Structure Template

CLAUDE.md should follow this structure for proper sync:

```markdown
# CLAUDE.md

This file provides guidance to Claude Code when working with this codebase.

## Project Overview

[Brief project description]

## Principles

[Synchronized from Constitution Core Principles]

1. **[Principle I Name]**: [Summary with enforcement]
2. **[Principle II Name]**: [Summary with enforcement]
...

## Technical Stack

[Synchronized from Constitution Technology Stack - exact match]

| Category | Choice | Rationale |
|----------|--------|-----------|
| ... | ... | ... |

## Quality Gates

[Synchronized from Constitution Quality Gates - exact match]

| Gate | Requirement | Measurement | Enforcement |
|------|-------------|-------------|-------------|
| ... | ... | ... | ... |

## Development Workflow

[Synchronized from Constitution Governance]

### Branch Strategy
[From governance or conventions]

### Commit Conventions
[Conventional commits or project standard]

### Code Review Requirements
[From governance]

## Project Structure

[Synchronized if present in constitution]

```
project/
├── src/
│   ├── domain/
│   └── ...
```

---

**Version**: X.Y.Z (synced with constitution)
**Last Synced**: YYYY-MM-DD
```

---

## Section-Specific Guidance

### Project Overview

- Keep brief (2-4 sentences)
- Focus on what the project does, not implementation details
- Should match constitution's project description if present

### Principles Section

- Number each principle
- Include enforcement keywords (MUST, NON-NEGOTIABLE, etc.)
- Preserve metrics and thresholds
- Format: `**Name** (modifier): Summary with enforcement`

### Technical Stack Section

- Copy table exactly from constitution
- Include all columns (Category, Choice, Rationale)
- Do not summarize or omit entries

### Quality Gates Section

- Copy table exactly from constitution
- Preserve all thresholds and metrics
- Include enforcement column

### Development Workflow Section

- Extract from Governance section in constitution
- Include branch strategy, commit conventions, review requirements
- May be reformatted for clarity but rules must match

### Project Structure Section

- Include only if constitution defines project structure
- Use tree format for clarity
- Keep aligned with actual project layout

---

## Version Footer

Always include version tracking at the bottom of CLAUDE.md:

```markdown
---

**Version**: X.Y.Z (synced with constitution)
**Last Synced**: YYYY-MM-DD
```

This enables:
- Quick version comparison with constitution
- Audit trail for sync operations
- CI/CD validation of alignment
