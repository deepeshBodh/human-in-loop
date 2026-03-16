# Evolution Roadmap

> Generated: 2026-03-05T19:35:00Z
> Based on: codebase-analysis.md, constitution.md (v3.0.0)
> Status: active

---

## Overview

The HumanInLoop project has strong foundational governance: 97% test coverage, zero layer violations, structured JSON output, frozen Pydantic models, and conventional commit enforcement. Six gaps exist between current codebase state and constitution requirements. Two are P1 (security), two are P2 (tooling and enforcement), and two are P3 (observability and governance hygiene).

**Total Gaps**: 6
- P1 (Critical): 2
- P2 (Important): 2
- P3 (Nice-to-have): 2

---

## Gap Summary

| ID | Title | Priority | Category | Depends On | Effort |
|----|-------|----------|----------|------------|--------|
| GAP-001 | Configure secret scanning in CI | P1 | Security | None | Small |
| GAP-002 | Configure static type checker | P2 | Tooling | None | Medium |
| GAP-003 | Add structured logging for internal diagnostics | P3 | Observability | None | Medium |
| GAP-004 | Automate layer dependency enforcement in CI | P2 | Architecture | None | Small |
| GAP-005 | Create CODEOWNERS file | P3 | Governance | None | Small |
| GAP-006 | Create exception registry file | P3 | Governance | None | Small |

---

## Dependency Graph

```
[Independent -- No Dependencies]

GAP-001: Configure secret scanning in CI          (P1, Small)
GAP-002: Configure static type checker            (P2, Medium)
GAP-003: Add structured logging                   (P3, Medium)
GAP-004: Automate layer dependency in CI          (P2, Small)
GAP-005: Create CODEOWNERS file                   (P3, Small)
GAP-006: Create exception registry file           (P3, Small)
```

All gaps are independent. None block or depend on others. This means they can be addressed in parallel or in any order, though priority ordering (P1 first, then P2, then P3) is recommended.

---

## Gap Cards

---

### GAP-001: Configure secret scanning in CI

| Aspect | Value |
|--------|-------|
| Priority | P1 |
| Category | Security |
| Blocks | Full compliance with Principle I (Security by Default); Quality Gate "Secret Scanning" |
| Enables | Automated detection of accidental credential commits before merge |
| Depends On | None |
| Effort | Small |

**Current state**: No secret scanning tool is configured in CI. The `.github/workflows/ci.yml` file has no `gitleaks` or `git-secrets` step. CLAUDE.md documents this as "GAP-003" (using the project's own numbering). The `.gitignore` correctly excludes `.env` files, but there is no automated scanning for secrets that might be committed in source code.

**Target state**: CI MUST run `gitleaks detect --source .` on every push and pull request. The step MUST block merge on any finding. This is required by Principle I (Security by Default) and listed as a Quality Gate in the constitution.

**Suggested approach**:
1. Add a `gitleaks` job to `.github/workflows/ci.yml`:
   ```yaml
   secret-scan:
     name: Secret Scanning
     runs-on: ubuntu-latest
     steps:
       - uses: actions/checkout@v4
         with:
           fetch-depth: 0
       - uses: gitleaks/gitleaks-action@v2
         env:
           GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
   ```
2. Optionally add a `.gitleaks.toml` config file to tune rules and allowlists.
3. Run `gitleaks detect --source .` locally to verify zero findings before enabling CI gate.

**Related files**:
- `.github/workflows/ci.yml`
- `.gitignore` (already excludes `.env`)

---

### GAP-002: Configure static type checker

| Aspect | Value |
|--------|-------|
| Priority | P2 |
| Category | Tooling |
| Blocks | Full compliance with Quality Gate "Static Type Check" |
| Enables | Type safety enforcement for the heavily type-hinted codebase; catches type errors before runtime |
| Depends On | None |
| Effort | Medium |

**Current state**: The `humaninloop_brain` package uses extensive type hints throughout all 17 source modules (2,394 lines). Pydantic v2 models enforce runtime type validation. However, no static type checker (mypy, pyright, or pytype) is configured. No `[tool.mypy]` or `[tool.pyright]` section exists in `pyproject.toml`. The CI workflow has no type checking step.

**Target state**: A static type checker MUST be configured and integrated into CI. Constitution Quality Gates table lists "Static Type Check" with requirement "Zero type errors" enforced by `mypy` or `pyright`. The checker MUST pass with zero errors on the `humaninloop_brain` source tree.

**Suggested approach**:
1. Add `mypy` (or `pyright`) to dev dependencies in `humaninloop_brain/pyproject.toml`.
2. Add `[tool.mypy]` configuration section:
   ```toml
   [tool.mypy]
   python_version = "3.12"
   strict = true
   plugins = ["pydantic.mypy"]
   ```
3. Run `uv run mypy src/humaninloop_brain/` to identify and fix any type errors.
4. Add a CI step after tests:
   ```yaml
   - name: Type checking
     run: uv run mypy src/humaninloop_brain/
   ```
5. Effort is Medium because strict mode may reveal type issues requiring annotation fixes across all 17 modules.

**Related files**:
- `humaninloop_brain/pyproject.toml`
- `.github/workflows/ci.yml`
- All files in `humaninloop_brain/src/humaninloop_brain/` (17 modules)

---

### GAP-003: Add structured logging for internal diagnostics

| Aspect | Value |
|--------|-------|
| Priority | P3 |
| Category | Observability |
| Blocks | Full compliance with Principle IV (Observability Requirements) |
| Enables | Internal library diagnostics for debugging graph operations, pass execution, and catalog resolution without corrupting structured JSON output on stdout |
| Depends On | None |
| Effort | Medium |

**Current state**: No logging library is imported anywhere in `humaninloop_brain/src/`. No `import logging`, `import structlog`, or equivalent exists. CLI output is structured JSON to stdout, and error output goes to stderr via `json.dumps()`. The StrategyGraph JSON serves as the primary observability artifact, but there are no internal diagnostic logs for debugging library operations (e.g., edge inference decisions, catalog resolution steps, pass lifecycle transitions).

**Target state**: Python's `logging` module or `structlog` SHOULD be added for internal library diagnostics. Per Principle IV, log output MUST go to stderr to avoid corrupting structured JSON on stdout. Log levels SHOULD follow standard conventions (DEBUG for internal tracing, INFO for operation summaries, WARNING for recoverable issues, ERROR for failures).

**Suggested approach**:
1. Add `structlog` to dev/optional dependencies (or use stdlib `logging` for zero new dependencies).
2. Configure a stderr handler in `cli/main.py` that initializes logging before command dispatch:
   ```python
   import logging
   logging.basicConfig(
       level=logging.WARNING,
       format="%(levelname)s %(name)s: %(message)s",
       stream=sys.stderr,
   )
   ```
3. Add `logger = logging.getLogger(__name__)` to key modules:
   - `passes/lifecycle.py` (pass transitions, node status updates)
   - `graph/inference.py` (edge inference decisions)
   - `validators/structural.py` (validation check results)
   - `cli/main.py` (command dispatch, file I/O)
4. Use DEBUG level for internal tracing to avoid noise in normal operation.
5. Verify no log output appears on stdout by running CLI tests and checking JSON parseability.

**Related files**:
- `humaninloop_brain/src/humaninloop_brain/cli/main.py`
- `humaninloop_brain/src/humaninloop_brain/passes/lifecycle.py`
- `humaninloop_brain/src/humaninloop_brain/graph/inference.py`
- `humaninloop_brain/src/humaninloop_brain/validators/structural.py`
- `humaninloop_brain/pyproject.toml`

---

### GAP-004: Automate layer dependency enforcement in CI

| Aspect | Value |
|--------|-------|
| Priority | P2 |
| Category | Architecture |
| Blocks | Full automated enforcement of Principle XI (Layer Dependency Rule) |
| Enables | Automated detection of upward imports that violate the 5-layer architecture; prevents regressions without relying solely on code review |
| Depends On | None |
| Effort | Small |

**Current state**: The layer dependency rule is perfectly followed -- zero upward imports exist (verified in codebase analysis and confirmed by grep during this roadmap creation). However, enforcement relies entirely on code review. The constitution Principle XI notes that import analysis "SHOULD be automated in CI (GAP-002 candidate)" but no CI step exists. The `.github/workflows/ci.yml` has syntax checks and tests but no import direction verification.

**Target state**: CI MUST include an automated check that verifies no module imports from a layer above it. This prevents accidental layer violations from being merged even if code review misses them.

**Suggested approach**:
1. Add a shell-based CI step that checks for upward imports:
   ```yaml
   - name: Layer dependency check
     run: |
       VIOLATIONS=0

       # entities must not import from graph, validators, passes, cli
       if grep -r "from humaninloop_brain\.\(graph\|validators\|passes\|cli\)" \
           src/humaninloop_brain/entities/ 2>/dev/null; then
         echo "::error::entities layer imports from upper layer"
         VIOLATIONS=1
       fi

       # graph must not import from validators, passes, cli
       if grep -r "from humaninloop_brain\.\(validators\|passes\|cli\)" \
           src/humaninloop_brain/graph/ 2>/dev/null; then
         echo "::error::graph layer imports from upper layer"
         VIOLATIONS=1
       fi

       # validators must not import from passes, cli
       if grep -r "from humaninloop_brain\.\(passes\|cli\)" \
           src/humaninloop_brain/validators/ 2>/dev/null; then
         echo "::error::validators layer imports from upper layer"
         VIOLATIONS=1
       fi

       # passes must not import from validators, cli
       if grep -r "from humaninloop_brain\.\(validators\|cli\)" \
           src/humaninloop_brain/passes/ 2>/dev/null; then
         echo "::error::passes layer imports from upper layer"
         VIOLATIONS=1
       fi

       if [ "$VIOLATIONS" -eq 1 ]; then
         exit 1
       fi

       echo "All imports respect layer direction."
   ```
2. Alternatively, use `import-linter` Python package for more sophisticated import graph analysis.
3. This is Small effort because the check is a simple grep pattern that can be added as a CI step in minutes.

**Related files**:
- `.github/workflows/ci.yml`
- `humaninloop_brain/src/humaninloop_brain/entities/`
- `humaninloop_brain/src/humaninloop_brain/graph/`
- `humaninloop_brain/src/humaninloop_brain/validators/`
- `humaninloop_brain/src/humaninloop_brain/passes/`
- `humaninloop_brain/src/humaninloop_brain/cli/`

---

### GAP-005: Create CODEOWNERS file

| Aspect | Value |
|--------|-------|
| Priority | P3 |
| Category | Governance |
| Blocks | Nothing critical; improves review routing |
| Enables | Automatic reviewer assignment for PRs touching governed code areas; prevents PRs from merging without domain-appropriate review |
| Depends On | None |
| Effort | Small |

**Current state**: No `CODEOWNERS` file exists at repository root, `.github/`, or `docs/`. The codebase analysis notes this under Governance Artifacts as "Not present." While code review is required by multiple constitution principles, there is no automated mechanism to ensure the right people review changes to specific areas.

**Target state**: A `CODEOWNERS` file SHOULD exist to route reviews for the governed codebase (`humaninloop_brain/`) and constitution files (`.humaninloop/memory/constitution.md`, `CLAUDE.md`) to appropriate reviewers.

**Suggested approach**:
1. Create `.github/CODEOWNERS` with ownership rules:
   ```
   # Governed codebase
   /humaninloop_brain/ @project-maintainers

   # Constitution and governance
   /.humaninloop/ @project-maintainers
   /CLAUDE.md @project-maintainers

   # CI configuration
   /.github/workflows/ @project-maintainers

   # Plugin marketplace
   /plugins/ @project-maintainers
   ```
2. Configure GitHub branch protection to require CODEOWNERS approval.
3. Adjust team handles to match actual GitHub team or user names.

**Related files**:
- `.github/CODEOWNERS` (to be created)

---

### GAP-006: Create exception registry file

| Aspect | Value |
|--------|-------|
| Priority | P3 |
| Category | Governance |
| Blocks | Nothing critical; required by constitution Governance section |
| Enables | Formal tracking of approved exceptions to constitution principles with expiry and review dates |
| Depends On | None |
| Effort | Small |

**Current state**: The constitution Governance section (Exception Registry) requires that "Approved exceptions to constitution principles MUST be recorded in `docs/constitution-exceptions.md`." This file does not exist. There are currently no known exceptions, but the file should exist as infrastructure for when exceptions are needed.

**Target state**: `docs/constitution-exceptions.md` MUST exist with the header template and empty table, ready for use when exceptions are approved.

**Suggested approach**:
1. Create `docs/constitution-exceptions.md`:
   ```markdown
   # Constitution Exception Registry

   Approved exceptions to constitution principles are recorded here per the
   Governance section of `.humaninloop/memory/constitution.md` (v3.0.0).

   ## Active Exceptions

   | Exception ID | Principle | Scope | Justification | Approved By | Date | Expiry | Tracking Issue |
   |-------------|-----------|-------|---------------|-------------|------|--------|----------------|
   | (none) | -- | -- | -- | -- | -- | -- | -- |

   ## Expired/Resolved Exceptions

   | Exception ID | Principle | Resolution | Date Resolved |
   |-------------|-----------|------------|---------------|
   | (none) | -- | -- | -- |
   ```
2. This is a documentation file with no code changes.

**Related files**:
- `docs/constitution-exceptions.md` (to be created)
- `.humaninloop/memory/constitution.md` (references this file)

---

## Recommended Execution Order

Although all gaps are independent, the following order respects priority and maximizes value per unit effort:

1. **GAP-001** (P1, Small) -- Secret scanning. Highest priority, lowest effort. Addresses a security gap that is a constitutional MUST violation.
2. **GAP-004** (P2, Small) -- Layer dependency CI check. Quick win that automates enforcement of the project's architectural backbone.
3. **GAP-002** (P2, Medium) -- Static type checker. Higher effort but unlocks type safety for a heavily annotated codebase.
4. **GAP-006** (P3, Small) -- Exception registry. Trivial file creation that satisfies governance requirements.
5. **GAP-005** (P3, Small) -- CODEOWNERS. Trivial file creation that improves review routing.
6. **GAP-003** (P3, Medium) -- Structured logging. Lowest priority, moderate effort. Useful for debugging but the CLI tool nature reduces urgency.

---

## Maintenance Protocol

When addressing gaps:

1. **Note in commits**: Include `Addressed: GAP-XXX` in commit body.
2. **Update this roadmap**: Mark the gap as addressed with the commit SHA and date.
3. **Update constitution**: Remove gap references from Evolution Notes and Quality Gates tables.
4. **Suggest new gaps**: If implementation reveals additional issues, document them as suggested gaps for review.

When all gaps are addressed:
- Update the roadmap status from `active` to `completed`.
- Update the constitution Evolution Notes to reflect full compliance.
- Consider removing gap references from Quality Gates table.
