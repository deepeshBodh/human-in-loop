# Anti-Patterns to Avoid

Common mistakes when writing constitutions and how to fix them.

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Vague principle** | "Code should be maintainable" | Define specific metrics (complexity, length) |
| **Missing enforcement** | Principle has no verification method | Add CI check, code review rule, or audit |
| **Untestable rule** | "Architecture should be clean" | Define layer rules with import constraints |
| **Cargo-cult rule** | Rule copied without understanding | Add rationale explaining the "why" |
| **Over-engineering** | 50 principles for a 3-person team | Start with 5-7 core principles |
| **No escape hatch** | No exception process | Define exception registry |
| **Placeholder syndrome** | `[COMMAND]` instead of actual tool | Use detected tools or industry defaults |
| **Generic thresholds** | "Coverage MUST be measured" | Specify numeric values: "≥80% warning, ≥60% blocking" |
| **Missing secret management** | "Secrets from env" only | Specify secret managers, scanning tools, .gitignore rules |

## Detailed Examples

### Vague Principle

**Bad:**
```markdown
### Code Quality
Code should be maintainable and readable.
```

**Good:**
```markdown
### Code Quality
- Functions MUST NOT exceed 40 lines
- Cyclomatic complexity MUST be ≤10
- Files MUST NOT exceed 400 lines

**Enforcement**: Linter configured with rules, CI blocks on violation
**Testability**: Pass: All metrics within limits; Fail: Any violation
**Rationale**: Smaller units are easier to test, understand, and modify
```

### Missing Enforcement

**Bad:**
```markdown
### Security
All inputs must be validated.
```

**Good:**
```markdown
### Security
All inputs MUST be validated before processing.

**Enforcement**:
- Input validation library configured (e.g., Pydantic, Zod)
- CI runs schema validation tests
- Code review checklist item: "All endpoints validate input"
```

### Placeholder Syndrome

**Bad:**
```markdown
## Quality Gates
| Gate | Command |
|------|---------|
| Linting | `[LINTER_COMMAND]` |
| Tests | `[TEST_COMMAND]` |
```

**Good:**
```markdown
## Quality Gates
| Gate | Command |
|------|---------|
| Linting | `ruff check .` |
| Tests | `pytest --cov --cov-fail-under=80` |
```

### Generic Thresholds

**Bad:**
```markdown
Test coverage MUST be maintained at an appropriate level.
```

**Good:**
```markdown
Test coverage MUST be:
- ≥80% for new code (warning threshold)
- ≥60% overall (blocking threshold)
- Non-decreasing (ratchet rule)
```
