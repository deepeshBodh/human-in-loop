# Evolution Roadmap

> Generated: 2026-02-18T19:10:00Z
> Based on: codebase-analysis.md (2026-02-18), constitution.md v2.0.0
> Status: active

---

## Overview

Gap analysis of the HumanInLoop Plugin Marketplace codebase against constitution v2.0.0 reveals 7 gaps. The codebase is in strong shape -- 6 of 10 core principles are fully satisfied, with the remaining gaps concentrated in CI/CD automation (which blocks enforcement of multiple quality gates) and documentation synchronization. No architectural gaps exist; the emergent ceiling principles (V-X) accurately codify existing practice.

The critical finding: **CI is the single largest blocker.** Without GitHub Actions, 7 of 9 quality gates exist only on paper. GAP-001 (CI workflow) is the foundation that enables GAP-003 (secret scanning) and GAP-004 (coverage ratchet). Addressing GAP-001 alone converts the project from "manual compliance" to "automated enforcement."

**Total Gaps**: 7
- P1 (Critical): 2
- P2 (Important): 2
- P3 (Nice-to-have): 3

---

## Gap Summary

| ID | Title | Priority | Category | Principle | Depends On | Effort |
|----|-------|----------|----------|-----------|------------|--------|
| GAP-001 | Create GitHub Actions CI workflow | P1 | Testing/CI | II, Quality Gates | None | Medium |
| GAP-002 | Sync CLAUDE.md with constitution v2.0.0 | P1 | Governance | CLAUDE.md Sync | None | Small |
| GAP-003 | Add secret scanning to CI | P2 | Security | I | GAP-001 | Small |
| GAP-004 | Establish coverage ratchet baseline | P2 | Testing | II | GAP-001 | Small |
| GAP-005 | Migrate legacy plugin validators | P3 | Testing | II, V | None | Large |
| GAP-006 | Create specs/ directory structure | P3 | Governance | N/A (CLAUDE.md ref) | GAP-002 | Small |
| GAP-007 | Add CODEOWNERS file | P3 | Governance | Governance | None | Small |

---

## Dependency Graph

```
[CI Foundation] -- Must be addressed first, enables automated enforcement
    GAP-001: Create GitHub Actions CI workflow
         |
         +-- GAP-003: Add secret scanning to CI
         |
         +-- GAP-004: Establish coverage ratchet baseline

[Documentation Sync] -- Can proceed in parallel with CI
    GAP-002: Sync CLAUDE.md with constitution v2.0.0
         |
         +-- GAP-006: Create specs/ directory structure

[Independent Tracks] -- No dependencies, address when convenient
    GAP-005: Migrate legacy plugin validators
    GAP-007: Add CODEOWNERS file
```

**Critical path**: GAP-001 -> GAP-003 + GAP-004 (CI foundation enables automated enforcement)

**Parallel track**: GAP-002 -> GAP-006 (documentation sync, independent of CI)

**Independent**: GAP-005 and GAP-007 can be addressed at any time

---

## Gap Cards

### GAP-001: Create GitHub Actions CI workflow

| Aspect | Value |
|--------|-------|
| Priority | P1 |
| Category | Testing/CI |
| Principle Violated | II (Testing Discipline), Quality Gates table (7 of 9 gates require CI) |
| Blocks | GAP-003 (secret scanning), GAP-004 (coverage ratchet) |
| Enables | Automated enforcement of 7 of 9 quality gates |
| Depends On | None |
| Effort | Medium |

**Current state**: No `.github/workflows/` directory exists. All testing is manual (`cd humaninloop_brain && uv run pytest`). Constitution v2.0.0 mandates CI as a P1 requirement. The Quality Gates table lists 7 gates requiring CI automation: Python Tests, Test Coverage, Coverage Ratchet, Python Syntax, Shell Syntax, JSON Schema, and Secret Scanning. None are currently enforced automatically. This gap was inherited from constitution v1.0.0 (where it was GAP-002) and elevated to P1 per user decision on 2026-02-18.

**Target state**: GitHub Actions workflow runs on every push to main and every PR. At minimum:
- `cd humaninloop_brain && uv run pytest --cov --cov-fail-under=90` (blocking)
- `bash -n plugins/humaninloop/scripts/*.sh` (blocking)
- `cd humaninloop_brain && uv run python -m py_compile src/humaninloop_brain/**/*.py` (blocking)
- Coverage report posted on PRs

**Suggested approach**:
1. Create `.github/workflows/ci.yml` with a single job targeting `humaninloop_brain`
2. Use `actions/setup-python@v5` with Python 3.12 and install uv via `astral-sh/setup-uv@v4`
3. Run `uv sync` in `humaninloop_brain/` directory
4. Run pytest with coverage gate: `uv run pytest --cov --cov-fail-under=90 --tb=short`
5. Add shell syntax check step: `bash -n` on all `.sh` files in `plugins/humaninloop/scripts/`
6. Add Python compile check: `uv run python -m py_compile` on all `.py` files in `humaninloop_brain/src/`
7. Trigger on push to `main` and all pull requests
8. Once stable, extend with GAP-003 (secret scanning) and GAP-004 (coverage ratchet)

**Related files**:
- `humaninloop_brain/pyproject.toml` (test configuration, dependencies)
- `humaninloop_brain/tests/` (190 tests across 5 suites)
- `plugins/humaninloop/scripts/*.sh` (shell scripts to syntax-check)

---

### GAP-002: Sync CLAUDE.md with constitution v2.0.0

| Aspect | Value |
|--------|-------|
| Priority | P1 |
| Category | Governance |
| Principle Violated | CLAUDE.md Synchronization section of constitution |
| Blocks | GAP-006 (specs/ directory -- need to decide whether to keep reference during sync) |
| Enables | AI agents operating with current governance rules |
| Depends On | None |
| Effort | Small |

**Current state**: CLAUDE.md references constitution v1.0.0 with multiple stale values:

| Section | Current (Stale) | Required (v2.0.0) |
|---------|----------------|-------------------|
| Constitution version | v1.0.0 | v2.0.0 |
| Principles count | 7 principles | 10 principles (add VIII, IX, X) |
| Coverage thresholds | >= 60% blocking, >= 80% target | >= 90% blocking (humaninloop_brain) |
| Skill structure | "SKILL.md under 200 lines" | "Progressive disclosure, no hard limit" |
| Validator Pattern | "Docstring header, validate_file() entry" | "Structured JSON output with checks/summary" |
| Quality Gates commands | `pytest plugins/ --tb=short` | `cd humaninloop_brain && uv run pytest --cov --cov-fail-under=90` |
| Two-codebase distinction | Absent | MUST distinguish humaninloop_brain from legacy validators |
| specs/ directory | Referenced, does not exist | Decide: create or remove reference |

**Target state**: CLAUDE.md synchronized with constitution v2.0.0:
- Version reference updated to v2.0.0
- Key Principles table lists all 10 principles with enforcement keywords
- Quality Gates table matches constitution exactly (9 gates with actual commands)
- Two-codebase distinction present
- Coverage thresholds: 90% blocking for humaninloop_brain
- Skill structure: progressive disclosure guidance
- specs/ reference resolved (created or removed)

**Suggested approach**:
1. Update constitution version reference from v1.0.0 to v2.0.0
2. Rewrite Key Principles table to cover all 10 principles with enforcement keywords
3. Replace Quality Gates table with constitution v2.0.0 version
4. Add two-codebase distinction in Development Guidelines
5. Update commit conventions to include `brain` and `dag` as valid scopes
6. Resolve specs/ reference (see GAP-006)
7. Commit message: `docs: sync CLAUDE.md with constitution v2.0.0`

**Related files**:
- `CLAUDE.md` (file to update)
- `.humaninloop/memory/constitution.md` (authoritative source, v2.0.0)

---

### GAP-003: Add secret scanning to CI

| Aspect | Value |
|--------|-------|
| Priority | P2 |
| Category | Security |
| Principle Violated | I (Security by Default) -- "CI MUST run secret scanning on every push (when CI is configured -- see GAP-003)" |
| Blocks | Nothing |
| Enables | Automated detection of accidentally committed secrets |
| Depends On | GAP-001 (CI workflow must exist first) |
| Effort | Small |

**Current state**: No CI workflow exists. No `git secrets`, `trufflehog`, or GitHub secret scanning is configured. Constitution Principle I mandates: "CI MUST run secret scanning on every push." The Quality Gates table lists "Secret Scanning" with command `git secrets --scan` and enforcement "CI automated (GAP-003)." The codebase currently relies on `.gitignore` patterns and manual code review for secret prevention.

**Target state**: CI pipeline includes a secret scanning step that blocks merge on findings.

**Suggested approach**:
1. After GAP-001 is resolved, add a new step to the CI workflow
2. Evaluate tool options:
   - `git-secrets` (AWS open source): lightweight, pattern-based, easy to configure
   - `trufflehog` (Truffle Security): broader pattern matching, entropy detection
   - GitHub native secret scanning: requires GitHub Advanced Security (availability depends on plan)
3. Start with `git-secrets` for simplicity:
   ```yaml
   - name: Secret scanning
     run: |
       git secrets --install
       git secrets --scan
   ```
4. Configure custom patterns for any project-specific secret formats if needed
5. Block merge on any findings (exit code 1 from `git secrets --scan`)

**Related files**:
- `.github/workflows/ci.yml` (to be created in GAP-001)
- `.gitignore` (existing secret exclusion patterns: `.env`, `.env.local`, `*.pem`)

---

### GAP-004: Establish coverage ratchet baseline

| Aspect | Value |
|--------|-------|
| Priority | P2 |
| Category | Testing |
| Principle Violated | II (Testing Discipline) -- "Coverage baseline MUST NOT decrease (ratchet rule)" |
| Blocks | Nothing |
| Enables | Prevents coverage regression over time; enforces that new code maintains test quality |
| Depends On | GAP-001 (CI workflow must exist to enforce ratchet) |
| Effort | Small |

**Current state**: humaninloop_brain has 98% coverage (190 tests, 609 statements, 13 misses). Constitution v2.0.0 mandates a ratchet rule: "Coverage baseline MUST NOT decrease." The Quality Gates table specifies "Compare against stored baseline" but no storage or comparison mechanism exists. The 90% threshold is the hard floor, but the ratchet should prevent regression from the current 98% baseline.

**Target state**: Coverage baseline stored in a version-controlled file. Each CI run compares current coverage against the stored baseline. Coverage decrease fails the build. Baseline is updated (manually or automatically) when coverage increases.

**Suggested approach**:
1. After GAP-001 is resolved, add a coverage ratchet mechanism
2. Create `humaninloop_brain/.coverage-baseline` containing the number `98`
3. Add a CI step that:
   - Runs pytest with `--cov` and captures the coverage percentage
   - Compares the result against the value in `.coverage-baseline`
   - Fails if current coverage < stored baseline
4. Document the process: to update the baseline, submit a PR changing `.coverage-baseline`
5. Alternative: use a GitHub Action like `codecov/codecov-action` with ratchet support

**Related files**:
- `humaninloop_brain/pyproject.toml` (coverage configuration in `[tool.coverage.run]` and `[tool.coverage.report]`)
- `.github/workflows/ci.yml` (to be created in GAP-001)
- `humaninloop_brain/.coverage-baseline` (to be created)

---

### GAP-005: Migrate legacy plugin validators

| Aspect | Value |
|--------|-------|
| Priority | P3 |
| Category | Testing |
| Principle Violated | II (Testing Discipline) -- "Legacy validators are marked for deprecation" and "New validation logic MUST be built in humaninloop_brain" |
| Blocks | Nothing (validators MAY remain untested during deprecation period) |
| Enables | Single well-tested codebase; elimination of untested code; consistent validation API |
| Depends On | None (can proceed independently at any time) |
| Effort | Large |

**Current state**: 5 standalone Python validator scripts exist in `plugins/humaninloop/skills/*/scripts/`:

| Validator | Location | Tests |
|-----------|----------|-------|
| `validate-requirements.py` | `authoring-requirements/scripts/` | None |
| `validate-user-stories.py` | `authoring-user-stories/scripts/` | None |
| `validate-openapi.py` | `patterns-api-contracts/scripts/` | None |
| `validate-model.py` | `patterns-entity-modeling/scripts/` | None |
| `check-artifacts.py` | `validation-plan-artifacts/scripts/` | None |

Constitution v2.0.0 explicitly marks these as deprecated: "During the deprecation period, legacy validators MAY remain untested. New validation logic MUST be built in humaninloop_brain." This was the original GAP-001 in constitution v1.0.0 (then called "Configure pytest testing infrastructure") and has been unaddressed since 2026-01-13. Per user decision on 2026-02-18, the approach changed from "test the validators" to "deprecate and migrate."

**Target state**: Validation logic migrated to `humaninloop_brain` as new CLI subcommands or Python API functions. Legacy scripts either removed or replaced with thin wrappers calling the new implementation. All validation logic covered by humaninloop_brain's 90% coverage threshold.

**Suggested approach**:
1. Audit each validator to catalog its validation rules and JSON output schema
2. Design new `humaninloop_brain` modules to absorb this logic (likely in `validators/` layer)
3. Implement one validator at a time, starting with the simplest
4. Add tests in humaninloop_brain test suite for each migrated validator
5. Update skill script references to call the new implementation
6. Migration order (simplest to most complex):
   - `check-artifacts.py` (artifact existence checks)
   - `validate-model.py` (entity model validation)
   - `validate-requirements.py` (requirements structure validation)
   - `validate-user-stories.py` (user story format validation)
   - `validate-openapi.py` (OpenAPI spec validation -- most complex)
7. Each migrated validator is a separate PR with tests

**Related files**:
- `plugins/humaninloop/skills/authoring-requirements/scripts/validate-requirements.py`
- `plugins/humaninloop/skills/authoring-user-stories/scripts/validate-user-stories.py`
- `plugins/humaninloop/skills/patterns-api-contracts/scripts/validate-openapi.py`
- `plugins/humaninloop/skills/patterns-entity-modeling/scripts/validate-model.py`
- `plugins/humaninloop/skills/validation-plan-artifacts/scripts/check-artifacts.py`
- `humaninloop_brain/src/humaninloop_brain/validators/` (target location for migrated logic)

---

### GAP-006: Create specs/ directory structure

| Aspect | Value |
|--------|-------|
| Priority | P3 |
| Category | Governance |
| Principle Violated | N/A (CLAUDE.md references nonexistent directory, not a constitution violation) |
| Blocks | Nothing |
| Enables | Spec-driven development workflow described in CLAUDE.md |
| Depends On | GAP-002 (decide during CLAUDE.md sync whether to keep or remove the reference) |
| Effort | Small |

**Current state**: CLAUDE.md Development Workflow section references `specs/in-progress/` and `specs/completed/` directories. The Documentation section links to `specs/` as "Feature specifications (completed, in-progress, planned)." These directories do not exist. No specs have ever been created in this structure. The `/humaninloop:specify` command exists and presumably generates specs, suggesting the workflow was intended but never executed.

**Target state**: Either:
- (A) Create `specs/in-progress/`, `specs/completed/`, and `specs/planned/` directories with `.gitkeep` and a brief `README.md` explaining the spec workflow, OR
- (B) Remove specs/ references from CLAUDE.md if spec-driven development is not the active workflow

**Suggested approach**:
1. During GAP-002 (CLAUDE.md sync), decide whether the specs/ workflow is still desired
2. If YES (recommended -- the `/humaninloop:specify` command exists):
   - Create `specs/in-progress/.gitkeep`, `specs/completed/.gitkeep`, `specs/planned/.gitkeep`
   - Create `specs/README.md` with brief explanation of the spec workflow
3. If NO: remove references from CLAUDE.md Development Workflow and Documentation sections
4. Commit with the GAP-002 CLAUDE.md sync or as a follow-up

**Related files**:
- `CLAUDE.md` (references specs/)
- `plugins/humaninloop/commands/specify.md` (the command that generates specs)

---

### GAP-007: Add CODEOWNERS file

| Aspect | Value |
|--------|-------|
| Priority | P3 |
| Category | Governance |
| Principle Violated | Governance section -- constitution acknowledges absence: "In absence of CODEOWNERS file, project maintainers have approval authority" |
| Blocks | Nothing |
| Enables | Automated review assignment on GitHub PRs; explicit ownership of governance artifacts |
| Depends On | None |
| Effort | Small |

**Current state**: No CODEOWNERS file exists at root, `.github/CODEOWNERS`, or `docs/CODEOWNERS`. The constitution's Governance section notes: "In absence of CODEOWNERS file, project maintainers have approval authority. Maintainers are identified by repository admin access." This is functional but informal -- there is no automated review assignment and no explicit ownership boundaries.

**Target state**: `.github/CODEOWNERS` file defining ownership for key areas, ensuring constitution and governance changes receive appropriate review.

**Suggested approach**:
1. Create `.github/CODEOWNERS` with ownership mappings:
   ```
   # Constitution and governance
   .humaninloop/          @deepeshBodh
   CLAUDE.md              @deepeshBodh

   # Python infrastructure
   humaninloop_brain/     @deepeshBodh

   # Plugin code
   plugins/               @deepeshBodh

   # Architecture decisions
   docs/decisions/        @deepeshBodh
   ```
2. Adjust usernames/teams as appropriate for the repository's contributors
3. Start with a single catch-all owner and refine as the team grows
4. Ensures PRs touching governance artifacts get proper review

**Related files**:
- `.github/CODEOWNERS` (to be created)

---

## Compliance Summary by Principle

| Principle | Status | Gaps |
|-----------|--------|------|
| I. Security by Default | Partial | GAP-003 (secret scanning requires CI) |
| II. Testing Discipline | Partial | GAP-001 (CI), GAP-004 (ratchet), GAP-005 (migration) |
| III. Error Handling Standards | **Compliant** | -- |
| IV. Observability Requirements | **Compliant** | -- |
| V. Structured Output Pattern | **Compliant** | -- |
| VI. ADR Discipline | **Compliant** | -- |
| VII. Skill Structure Requirements | **Compliant** | -- |
| VIII. Conventional Commits | **Compliant** | -- |
| IX. Deterministic Infrastructure | **Compliant** | -- |
| X. Pydantic Entity Modeling | **Compliant** | -- |
| Quality Gates (automated) | Non-compliant | GAP-001 (CI enables all automated gates) |
| CLAUDE.md Synchronization | Non-compliant | GAP-002 (stale sync, 8 drift points) |
| Governance artifacts | Partial | GAP-006 (specs/), GAP-007 (CODEOWNERS) |

---

## Recommended Implementation Order

### Phase 1: Immediate (P1) -- Address before new feature work

| Order | Gap | Effort | Rationale |
|-------|-----|--------|-----------|
| 1 | GAP-001: CI workflow | Medium | Foundation for all automated enforcement |
| 2 | GAP-002: CLAUDE.md sync | Small | Agents operating on stale instructions |

These two gaps can be addressed in parallel since they have no dependencies on each other.

### Phase 2: Next iteration (P2) -- Address after CI is running

| Order | Gap | Effort | Rationale |
|-------|-----|--------|-----------|
| 3 | GAP-003: Secret scanning | Small | Extends CI with security gate |
| 4 | GAP-004: Coverage ratchet | Small | Extends CI with regression prevention |

Both depend on GAP-001 and can be addressed in parallel.

### Phase 3: When convenient (P3) -- No urgency

| Order | Gap | Effort | Rationale |
|-------|-----|--------|-----------|
| 5 | GAP-007: CODEOWNERS | Small | Quick governance improvement |
| 6 | GAP-006: specs/ directory | Small | Depends on GAP-002 decision |
| 7 | GAP-005: Validator migration | Large | Long-term, incremental migration |

---

## Maintenance Protocol

### When addressing a gap

1. Reference the gap ID in commit messages: `fix(ci): create GitHub Actions workflow (GAP-001)`
2. Update this roadmap when a gap is resolved: change gap card header to include `[RESOLVED: YYYY-MM-DD]`
3. Add resolution details to the gap card:
   ```markdown
   **Resolution**: [Brief description of how gap was addressed]
   **PR/Commit**: [Link or hash]
   ```
4. If work reveals new gaps, add them with the next sequential ID (GAP-008, GAP-009, etc.)

### When reviewing this roadmap

- Review after each major release or quarterly, whichever comes first
- Move resolved gaps to a "Resolved Gaps" section at the bottom
- Re-prioritize remaining gaps based on current project needs
- Verify no new constitution requirements exist without corresponding gap analysis

### Gap lifecycle

```
Identified -> In Progress -> Resolved
                  |
                  +-> Deferred (with justification and review date)
```

---

**Roadmap Version**: 2.0.0 | **Created**: 2026-02-18 | **Constitution**: v2.0.0 | **Previous Version**: 1.0.0 (2026-01-13)
