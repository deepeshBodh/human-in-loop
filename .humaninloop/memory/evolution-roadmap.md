# Evolution Roadmap

> Generated: 2026-01-13T21:00:00Z
> Based on: codebase-analysis.md, constitution.md v1.0.0
> Status: active

---

## Overview

Gap analysis between current HumanInLoop Plugin Marketplace state and constitution v1.0.0 requirements. Primary gaps are in testing infrastructure (absent) and CI/CD automation (absent). Error handling patterns are strong; security posture is appropriate for repository type.

**Total Gaps**: 6
- P1 (Critical): 2
- P2 (Important): 3
- P3 (Nice-to-have): 1

---

## Gap Summary

| ID | Title | Priority | Category | Depends On | Effort |
|----|-------|----------|----------|------------|--------|
| GAP-001 | Configure pytest testing infrastructure | P1 | Testing | None | Medium |
| GAP-002 | Add GitHub Actions CI workflow | P1 | Testing | GAP-001 | Medium |
| GAP-003 | Add validator test coverage | P2 | Testing | GAP-001 | Large |
| GAP-004 | Add structured logging for scripts | P2 | Observability | None | Small |
| GAP-005 | Standardize SKILL.md frontmatter | P2 | Architecture | None | Small |
| GAP-006 | Resolve version mismatch | P3 | Governance | None | Small |

---

## Dependency Graph

```
[Testing Foundation Track]
    GAP-001: Configure pytest testing infrastructure
         |
         +-- GAP-002: Add GitHub Actions CI workflow
         |
         +-- GAP-003: Add validator test coverage

[Parallel Tracks - No Dependencies]
    GAP-004: Add structured logging for scripts
    GAP-005: Standardize SKILL.md frontmatter
    GAP-006: Resolve version mismatch
```

---

## Gap Cards

### GAP-001: Configure pytest testing infrastructure

| Aspect | Value |
|--------|-------|
| Priority | P1 |
| Category | Testing |
| Blocks | Constitution Principle II enforcement |
| Enables | GAP-002 (CI), GAP-003 (test coverage) |
| Depends On | None |
| Effort | Medium |

**Current state**: No test framework configured. No `pytest.ini`, `pyproject.toml` [tool.pytest] section, or `conftest.py` files exist. No test files matching `test_*.py` pattern found in repository. (From codebase-analysis.md: Testing Assessment - "Test framework configured: absent")

**Target state**: Constitution Principle II requires pytest framework with coverage measurement. Quality Gates table specifies `pytest plugins/ --cov --cov-fail-under=60` as blocking gate.

**Suggested approach**:
1. Create `pyproject.toml` with pytest and coverage configuration
2. Add `conftest.py` with shared fixtures for validator testing
3. Create initial test file structure mirroring `skills/*/scripts/` layout
4. Configure coverage paths to focus on Python validator files
5. Document test patterns in `CONTRIBUTING.md`

**Related files**:
- `plugins/humaninloop/skills/validation-task-artifacts/scripts/validate-requirements.py`
- `plugins/humaninloop/skills/validation-task-artifacts/scripts/validate-user-stories.py`
- `plugins/humaninloop/skills/patterns-api-contracts/scripts/validate-openapi.py`
- `plugins/humaninloop/skills/patterns-entity-modeling/scripts/validate-model.py`
- `plugins/humaninloop/skills/validation-plan-artifacts/scripts/validate-research.py`

---

### GAP-002: Add GitHub Actions CI workflow

| Aspect | Value |
|--------|-------|
| Priority | P1 |
| Category | Testing |
| Blocks | Constitution Quality Gates automated enforcement |
| Enables | Automated PR validation, blocking merge on failures |
| Depends On | GAP-001 |
| Effort | Medium |

**Current state**: No `.github/workflows/` directory exists. No CI/CD configuration detected. All Quality Gates in constitution list enforcement as "CI automated (when configured)". (From codebase-analysis.md: Testing Assessment - "CI runs tests: absent")

**Target state**: Constitution Quality Gates require automated enforcement for validator syntax, tests, coverage, and JSON schema validation. CI MUST block merge when coverage falls below 60%.

**Suggested approach**:
1. Create `.github/workflows/ci.yml` with Python setup
2. Add jobs for: syntax check (`python -m py_compile`), shell lint (`bash -n`), pytest, coverage reporting
3. Configure coverage threshold as blocking (60%) with warning annotation at 80%
4. Add JSON output validation step using `jq`
5. Configure workflow triggers for pull_request and push to main

**Related files**:
- `.github/workflows/ci.yml` (to create)
- `pyproject.toml` (from GAP-001)

---

### GAP-003: Add validator test coverage

| Aspect | Value |
|--------|-------|
| Priority | P2 |
| Category | Testing |
| Blocks | Full compliance with Principle II |
| Enables | Safe refactoring, regression detection |
| Depends On | GAP-001 |
| Effort | Large |

**Current state**: Five Python validators exist with no test coverage. Validators use consistent JSON+exit code pattern suitable for testing. (From codebase-analysis.md: "Missing tests - No test files or test framework configured for Python validators - high severity")

**Target state**: Constitution Principle II specifies coverage >= 60% blocking threshold, >= 80% warning threshold. Each validator must have corresponding `test_*.py` file.

**Suggested approach**:
1. Create test files for each validator:
   - `test_validate_requirements.py`
   - `test_validate_user_stories.py`
   - `test_validate_openapi.py`
   - `test_validate_model.py`
   - `test_validate_research.py`
2. Test categories per validator:
   - Happy path: valid input produces `{"summary": {"failed": 0}}`
   - Invalid input: produces expected failure structure
   - Edge cases: empty files, missing fields, malformed content
   - Error handling: nonexistent files exit with code 1
3. Use pytest fixtures for sample input files
4. Target 80% coverage for initial implementation

**Related files**:
- `plugins/humaninloop/skills/validation-task-artifacts/scripts/` (5 validators)
- `plugins/humaninloop/skills/patterns-api-contracts/scripts/`
- `plugins/humaninloop/skills/patterns-entity-modeling/scripts/`
- `plugins/humaninloop/skills/validation-plan-artifacts/scripts/`

---

### GAP-004: Add structured logging for scripts

| Aspect | Value |
|--------|-------|
| Priority | P2 |
| Category | Observability |
| Blocks | None (current JSON output is acceptable) |
| Enables | Better debugging, operational insights |
| Depends On | None |
| Effort | Small |

**Current state**: No logging framework configured. Python validators output only JSON results. Shell scripts write to stdout/stderr without structured format. (From codebase-analysis.md: Observability Assessment - "Structured logging: absent")

**Target state**: Constitution Principle IV focuses on machine-parseable output (satisfied by JSON). Structured logging would enhance debugging but is not a MUST requirement for current scope.

**Suggested approach**:
1. Add Python `logging` module configuration to validators (optional enhancement)
2. Configure logging to stderr only (stdout reserved for JSON output)
3. Use structured format: `[LEVEL] [validator_name] message`
4. Log key checkpoints: file load, check start/complete, summary
5. Keep logging disabled by default, enable via CLI flag or env var

**Note**: This gap is marked as acceptable for current scope in constitution. Implementation is optional improvement.

**Related files**:
- `plugins/humaninloop/skills/*/scripts/*.py`

---

### GAP-005: Standardize SKILL.md frontmatter

| Aspect | Value |
|--------|-------|
| Priority | P2 |
| Category | Architecture |
| Blocks | None (skills functional without frontmatter) |
| Enables | Consistent skill discovery, documentation generation |
| Depends On | None |
| Effort | Small |

**Current state**: Some skills lack YAML frontmatter (name, description fields). Inconsistency noted in codebase analysis. (From codebase-analysis.md: Inconsistencies - "SKILL.md frontmatter - Some skills lack frontmatter (name, description) - medium severity")

**Target state**: Constitution Principle VII requires SKILL.md entry point file. While frontmatter is not explicitly mandated, consistency aligns with established patterns.

**Suggested approach**:
1. Audit all 16 skills for frontmatter presence
2. Add minimal frontmatter to skills lacking it:
   ```yaml
   ---
   name: [skill-name]
   description: [one-line description]
   ---
   ```
3. Document frontmatter requirement in skill creation checklist

**Related files**:
- `plugins/humaninloop/skills/*/SKILL.md` (16 files to audit)

---

### GAP-006: Resolve version mismatch

| Aspect | Value |
|--------|-------|
| Priority | P3 |
| Category | Governance |
| Blocks | None |
| Enables | Clean release process |
| Depends On | None |
| Effort | Small |

**Current state**: Version mismatch detected between `marketplace.json` (0.7.7) and `plugin.json` (0.7.8). (From codebase-analysis.md: Inconsistencies - "Version mismatch - marketplace.json shows 0.7.7 but plugin.json shows 0.7.8 - low severity")

**Target state**: Version numbers should be consistent across manifest files, or version management process should be documented.

**Suggested approach**:
1. Verify which version is correct (likely 0.7.8 based on recent commits)
2. Update `marketplace.json` to match `plugin.json`
3. Document version sync process in `RELEASES.md`

**Related files**:
- `.claude-plugin/marketplace.json`
- `plugins/humaninloop/.claude-plugin/plugin.json`

---

## Recommended Implementation Order

### Phase 1: Testing Foundation (P1)
1. **GAP-001**: Configure pytest - prerequisite for everything
2. **GAP-002**: Add CI workflow - enables enforcement

### Phase 2: Quality Improvements (P2)
3. **GAP-003**: Add test coverage - largest effort, highest value
4. **GAP-005**: Standardize frontmatter - quick win, parallel track

### Phase 3: Optional Enhancements (P2/P3)
5. **GAP-004**: Structured logging - optional, not blocking
6. **GAP-006**: Version mismatch - trivial fix

---

## Maintenance Protocol

When addressing gaps during `/plan`, `/tasks`, `/implement` phases:

1. **Note in commits**: Include `Addressed: GAP-XXX` in commit body
2. **Update this roadmap**: Mark gaps as `[ADDRESSED]` with date
3. **Verify constitution compliance**: Confirm the gap resolution meets principle requirements
4. **Suggest new gaps**: If discovering issues not in roadmap, document as "Suggested gap: [description]"

### Gap Status Updates

Use this format when addressing gaps:

```markdown
### GAP-XXX: [Title] [ADDRESSED: YYYY-MM-DD]
...
**Resolution**: [Brief description of how gap was addressed]
**Commit**: [commit hash or PR link]
```

---

**Roadmap Version**: 1.0.0 | **Created**: 2026-01-13 | **Last Updated**: 2026-01-13
