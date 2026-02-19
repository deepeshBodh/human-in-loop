# Evolution Roadmap

> Generated: 2026-02-19T04:10:00Z
> Based on: codebase-analysis.md (2026-02-19), constitution.md v3.0.0
> Status: active

---

## Overview

Gap analysis of the HumanInLoop codebase against constitution v3.0.0 (12 principles) reveals 5 gaps. The project is in strong shape -- 10 of 12 core principles are fully compliant, all quality gates except secret scanning are automated, and the CLAUDE.md is synchronized with the constitution. The remaining gaps are concentrated in security automation (secret scanning, carried forward from v2), enforcement test automation for layer discipline, and documentation hygiene.

The critical finding: **Secret scanning (GAP-003) remains the only Essential Floor gap.** All other gaps are governance improvements (CODEOWNERS, documentation accuracy) or enforcement strengthening (layer dependency test). No architectural or testing gaps exist.

**Total Gaps**: 5
- P1 (Critical): 0
- P2 (Important): 2
- P3 (Nice-to-have): 3

---

## Gap Summary

| ID | Title | Priority | Category | Principle | Depends On | Effort |
|----|-------|----------|----------|-----------|------------|--------|
| GAP-003 | Add secret scanning to CI | P2 | Security | I | None | Small |
| GAP-008 | Add layer dependency enforcement test | P2 | Testing/Architecture | XI | None | Small |
| GAP-009 | Resolve specs/ directory reference in CLAUDE.md | P3 | Governance | CLAUDE.md Sync | None | Small |
| GAP-010 | Update constitution skill counts (25/9 to 27/10) | P3 | Constitution Accuracy | VII | None | Small |
| GAP-011 | Add CODEOWNERS file | P3 | Governance | Governance | None | Small |

---

## Dependency Graph

```
[Independent Tracks] -- All gaps can be addressed in parallel; no blocking dependencies

    GAP-003: Add secret scanning to CI (P2, Security)
    GAP-008: Add layer dependency enforcement test (P2, Testing)

    GAP-009: Resolve specs/ directory reference (P3, Governance)
    GAP-010: Update constitution skill counts (P3, Accuracy)
    GAP-011: Add CODEOWNERS file (P3, Governance)
```

**Critical path**: None -- all gaps are independent. GAP-003 and GAP-008 are the highest priority and can be addressed in parallel.

**No blocking relationships exist.** This is a significant improvement from the v2 roadmap where GAP-001 (CI) blocked GAP-003 and GAP-004. With CI now resolved, all remaining gaps are independently addressable.

---

## Gap Cards

### GAP-003: Add secret scanning to CI [CARRIED FORWARD]

| Aspect | Value |
|--------|-------|
| Priority | P2 |
| Category | Security |
| Principle Violated | I (Security by Default) -- "CI MUST run secret scanning on every push (GAP-003: not yet configured)" |
| Blocks | Nothing |
| Enables | Automated detection of accidentally committed secrets; full compliance with Principle I |
| Depends On | None (CI workflow exists at `.github/workflows/ci.yml`) |
| Effort | Small |

**Current state**: CI workflow exists and runs tests, coverage, syntax checks, and commit linting. Secret scanning is not configured. Constitution Principle I explicitly annotates this as "GAP-003: not yet configured" in two locations (the principle body and the enforcement section). The Quality Gates table lists "Secret Scanning" with enforcement "GAP-003: not yet configured." The codebase currently relies on `.gitignore` patterns (`.env`, `.env.local`, `.env.*.local`, `*.pem`, `credentials`, `secrets`) and manual code review for secret prevention.

This gap was first identified in constitution v1.0.0, carried through v2.0.0, and remains in v3.0.0. CI now exists (GAP-001 resolved), removing the previous blocker.

**Target state**: CI pipeline includes a secret scanning step that blocks merge on findings. The Quality Gates table and Principle I annotations are updated to remove "GAP-003" markers.

**Suggested approach**:
1. Add a new step to `.github/workflows/ci.yml` in the `test` job
2. Use `trufflesecurity/trufflehog@v3` GitHub Action (broader pattern matching than `git-secrets`, no installation step needed):
   ```yaml
   - name: Secret scanning
     uses: trufflesecurity/trufflehog@v3
     with:
       extra_args: --only-verified
   ```
3. Alternative: `git-secrets` (requires installation step but is lighter weight):
   ```yaml
   - name: Secret scanning
     run: |
       git clone https://github.com/awslabs/git-secrets.git /tmp/git-secrets
       cd /tmp/git-secrets && make install
       cd $GITHUB_WORKSPACE
       git secrets --install
       git secrets --register-aws
       git secrets --scan
   ```
4. After CI passes with scanning enabled, update constitution Principle I to remove "GAP-003: not yet configured" annotations
5. Update Quality Gates table: change Secret Scanning enforcement from "GAP-003: not yet configured" to "CI automated"
6. Update CLAUDE.md Quality Gates and Key Principles tables to match

**Related files**:
- `.github/workflows/ci.yml` (add scanning step)
- `.humaninloop/memory/constitution.md` (remove GAP-003 annotations in Principle I and Quality Gates)
- `CLAUDE.md` (update Quality Gates table and Principle I summary)
- `.gitignore` (existing exclusion patterns -- complementary, not replaced)

---

### GAP-008: Add layer dependency enforcement test

| Aspect | Value |
|--------|-------|
| Priority | P2 |
| Category | Testing/Architecture |
| Principle Violated | XI (Layer Dependency Discipline) -- "Tests SHOULD include an import-order check that scans `from humaninloop_brain.` imports in each module" |
| Blocks | Nothing |
| Enables | Automated regression detection for layer violations; CI-enforced architecture |
| Depends On | None |
| Effort | Small |

**Current state**: The layer dependency hierarchy (entities -> graph -> validators -> passes -> cli) is perfectly clean -- grep scans confirm zero violations. However, this compliance is enforced only by code review. Constitution Principle XI states: "Tests SHOULD include an import-order check that scans `from humaninloop_brain.` imports in each module." No such test exists in the test suite. The `SHOULD` keyword means this is recommended with valid exceptions, but there is no documented exception for skipping it.

**Target state**: A pytest test in `humaninloop_brain/tests/` that scans all Python source files in each layer and verifies no imports violate the hierarchy. This test runs as part of the standard test suite and CI pipeline.

**Suggested approach**:
1. Create `humaninloop_brain/tests/test_architecture/__init__.py` and `humaninloop_brain/tests/test_architecture/test_layer_imports.py`
2. Define the allowed import mapping:
   ```python
   LAYER_RULES = {
       "entities": [],  # no internal imports allowed
       "graph": ["entities"],
       "validators": ["entities", "graph"],
       "passes": ["entities", "graph"],
       "cli": ["entities", "graph", "validators", "passes"],
   }
   ```
3. For each layer directory, scan all `.py` files for `from humaninloop_brain.<layer>` or `import humaninloop_brain.<layer>` patterns
4. Assert that only allowed layers are imported
5. Test should produce clear failure messages identifying the violating file, line, and import
6. Add to the existing test suite -- it will run automatically in CI

**Related files**:
- `humaninloop_brain/tests/` (create new test file)
- `humaninloop_brain/src/humaninloop_brain/entities/` (layer to verify)
- `humaninloop_brain/src/humaninloop_brain/graph/` (layer to verify)
- `humaninloop_brain/src/humaninloop_brain/validators/` (layer to verify)
- `humaninloop_brain/src/humaninloop_brain/passes/` (layer to verify)
- `humaninloop_brain/src/humaninloop_brain/cli/` (layer to verify)

---

### GAP-009: Resolve specs/ directory reference in CLAUDE.md

| Aspect | Value |
|--------|-------|
| Priority | P3 |
| Category | Governance |
| Principle Violated | CLAUDE.md Synchronization -- CLAUDE.md references nonexistent `specs/` directory structure |
| Blocks | Nothing |
| Enables | Documentation accuracy; prevents developer confusion when following CLAUDE.md workflow |
| Depends On | None |
| Effort | Small |

**Current state**: CLAUDE.md Development Workflow section (lines 108-114) references `specs/in-progress/` and `specs/completed/` directories as part of the feature development workflow. The `specs/` directory does not exist in the repository. No specs have been created using this workflow. The `/humaninloop:specify` command exists in the plugin and presumably generates specs, suggesting the workflow was intended but never executed. This gap was carried forward from the v2 roadmap (was GAP-006).

**Target state**: Either:
- (A) Create `specs/in-progress/`, `specs/completed/`, and `specs/planned/` directories with `.gitkeep` files, OR
- (B) Remove `specs/` references from CLAUDE.md Development Workflow section

**Suggested approach**:
1. Decision: determine whether spec-driven development is the active workflow
2. If YES (recommended -- the `/humaninloop:specify` command exists):
   - Create `specs/in-progress/.gitkeep`, `specs/completed/.gitkeep`, `specs/planned/.gitkeep`
   - Optionally create `specs/README.md` explaining the spec workflow
3. If NO: remove lines 108-114 from CLAUDE.md or replace with the actual development workflow
4. Commit: `docs(claude): resolve specs/ directory reference (GAP-009)`

**Related files**:
- `CLAUDE.md` (contains the stale reference, lines 108-114)
- `plugins/humaninloop/commands/specify.md` (the command that generates specs)

---

### GAP-010: Update constitution skill counts (25/9 to 27/10)

| Aspect | Value |
|--------|-------|
| Priority | P3 |
| Category | Constitution Accuracy |
| Principle Violated | VII (Skill Structure Requirements) -- count discrepancy, not a structural violation |
| Blocks | Nothing |
| Enables | Accurate constitution; prevents confusion about expected skill inventory |
| Depends On | None |
| Effort | Small |

**Current state**: Constitution Principle VII states "9 categories, 25 skills" with category listing: `analysis-*` (4), `authoring-*` (6), `brownfield-*` (1), `dag-*` (1), `patterns-*` (6), `syncing-*` (1), `testing-*` (1), `using-*` (2), `validation-*` (3). Actual count is 27 skills in 10 categories. The missing category is `strategy-*` (2 skills: `strategy-core`, `strategy-specification`). The `authoring-*` category also has a possible count discrepancy -- actual is 6 (`authoring-constitution`, `authoring-design-system`, `authoring-requirements`, `authoring-roadmap`, `authoring-technical-requirements`, `authoring-user-stories`) which matches.

Actual inventory:
- `analysis-*` (4): codebase, iterative, screenshot, specifications
- `authoring-*` (6): constitution, design-system, requirements, roadmap, technical-requirements, user-stories
- `brownfield-*` (1): constitution
- `dag-*` (1): operations
- `patterns-*` (6): api-contracts, entity-modeling, flow-mapping, interface-design, technical-decisions, vertical-tdd
- `strategy-*` (2): core, specification
- `syncing-*` (1): claude-md
- `testing-*` (1): end-user
- `using-*` (2): git-worktrees, github-issues
- `validation-*` (3): constitution, plan-artifacts, task-artifacts

**Target state**: Constitution Principle VII updated to "10 categories, 27 skills" with `strategy-*` (2) added to the category listing.

**Suggested approach**:
1. Update constitution Principle VII: "9 categories, 25 skills" to "10 categories, 27 skills"
2. Add `strategy-*` (2) to the category listing
3. This is a PATCH version change (count correction, no principle change)
4. Sync CLAUDE.md if it references skill counts
5. Commit: `docs(constitution): update skill counts to 27/10 (GAP-010)`

**Related files**:
- `.humaninloop/memory/constitution.md` (Principle VII, line ~277)
- `CLAUDE.md` (if skill counts are referenced)

---

### GAP-011: Add CODEOWNERS file

| Aspect | Value |
|--------|-------|
| Priority | P3 |
| Category | Governance |
| Principle Violated | Governance section -- constitution acknowledges absence: "In absence of CODEOWNERS file, project maintainers have approval authority" |
| Blocks | Nothing |
| Enables | Automated review assignment on GitHub PRs; explicit ownership of governance artifacts |
| Depends On | None |
| Effort | Small |

**Current state**: No CODEOWNERS file exists. The constitution's Governance section notes the absence and provides a fallback: "Maintainers are identified by repository admin access." This is functional but informal -- there is no automated review assignment and no explicit ownership boundaries for constitution, infrastructure, or plugin changes. This gap was carried forward from the v2 roadmap (was GAP-007).

**Target state**: `.github/CODEOWNERS` file defining ownership for key areas, ensuring constitution and governance changes receive appropriate review.

**Suggested approach**:
1. Create `.github/CODEOWNERS`:
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
4. Update constitution Governance section to remove the "In absence of CODEOWNERS" note
5. Commit: `chore(governance): add CODEOWNERS file (GAP-011)`

**Related files**:
- `.github/CODEOWNERS` (to be created)
- `.humaninloop/memory/constitution.md` (Governance section)

---

## Resolved Gaps (from v2 roadmap)

| ID | Title | Resolution | Date |
|----|-------|------------|------|
| GAP-001 | Create GitHub Actions CI workflow | Resolved -- `.github/workflows/ci.yml` runs tests, coverage floor (90%), ratchet (98% baseline), Python syntax, shell syntax, commit lint | 2026-02-18 |
| GAP-002 | Sync CLAUDE.md with constitution | Resolved -- CLAUDE.md synchronized with constitution v3.0.0 | 2026-02-19 |
| GAP-004 | Establish coverage ratchet baseline | Superseded -- Constitution v3.0.0 removed ratchet concept; 90% blocking floor is the sole coverage gate. CI still has ratchet step (operational detail, not constitutional requirement) | 2026-02-19 |
| GAP-005 | Migrate legacy plugin validators | Out of scope -- Constitution v3.0.0 removed plugin validators from governance scope. `humaninloop_brain` is the sole governed codebase | 2026-02-19 |
| GAP-006 | Create specs/ directory structure | Renumbered to GAP-009 and carried forward | 2026-02-19 |
| GAP-007 | Add CODEOWNERS file | Renumbered to GAP-011 and carried forward | 2026-02-19 |

---

## Compliance Summary by Principle

| Principle | Status | Gaps |
|-----------|--------|------|
| I. Security by Default | Partial | GAP-003 (secret scanning not in CI) |
| II. Testing Discipline | **Compliant** | -- |
| III. Error Handling Standards | **Compliant** | -- |
| IV. Observability Requirements | **Compliant** | -- |
| V. Structured Output Pattern | **Compliant** | -- |
| VI. ADR Discipline | **Compliant** | -- |
| VII. Skill Structure Requirements | **Compliant** (stale count) | GAP-010 (count inaccuracy, not structural) |
| VIII. Conventional Commits | **Compliant** | -- |
| IX. Deterministic Infrastructure | **Compliant** | -- |
| X. Pydantic Entity Modeling | **Compliant** | -- |
| XI. Layer Dependency Discipline | **Compliant** (missing test) | GAP-008 (SHOULD-level enforcement test absent) |
| XII. Catalog-Driven Assembly | **Compliant** | -- |
| Quality Gates (automated) | **Compliant** (except secret scanning) | GAP-003 |
| CLAUDE.md Synchronization | **Compliant** (minor drift) | GAP-009 (specs/ reference) |
| Governance artifacts | Partial | GAP-011 (CODEOWNERS absent) |

---

## Recommended Implementation Order

### Phase 1: Next iteration (P2) -- Address in regular development

| Order | Gap | Effort | Rationale |
|-------|-----|--------|-----------|
| 1 | GAP-003: Secret scanning | Small | Only remaining Essential Floor gap; Principle I compliance |
| 2 | GAP-008: Layer dependency test | Small | Strengthens architectural enforcement; prevents regression |

Both are independent and can be addressed in parallel.

### Phase 2: When convenient (P3) -- No urgency

| Order | Gap | Effort | Rationale |
|-------|-----|--------|-----------|
| 3 | GAP-010: Skill count update | Small | PATCH constitution update |
| 4 | GAP-009: specs/ directory | Small | Documentation hygiene |
| 5 | GAP-011: CODEOWNERS | Small | Governance improvement |

All are independent and can be addressed in any order.

---

## Operational Notes

The following items are NOT constitutional gaps but are worth noting:

1. **Coverage baseline file**: `.coverage-baseline` contains `98` and CI still runs a ratchet step against it. Constitution v3.0.0 removed the ratchet concept. The ratchet CI step is harmless (it raises the bar) but could cause confusion if coverage dips below 98% -- the CI would fail on the ratchet step even though the constitution only requires 90%. Consider either removing the ratchet step from CI or documenting it as an operational choice beyond constitutional requirements.

2. **Skill count drift**: New skills (`strategy-core`, `strategy-specification`) were added without updating the constitution counts. This suggests the constitution amendment process for count updates may need a lighter-weight trigger -- counts are PATCH-level changes that should not require full amendment ceremony.

---

## Maintenance Protocol

### When addressing a gap

1. Reference the gap ID in commit messages: `fix(ci): add secret scanning to CI pipeline (GAP-003)`
2. Update this roadmap when a gap is resolved: move gap card to "Resolved Gaps" table
3. Add resolution details:
   ```markdown
   | GAP-XXX | [Title] | [How resolved] | YYYY-MM-DD |
   ```
4. If work reveals new gaps, add them with the next sequential ID (GAP-012, GAP-013, etc.)
5. Update constitution to remove GAP-XXX annotations if applicable

### When reviewing this roadmap

- Review after each major release or quarterly, whichever comes first
- Verify no new constitution requirements exist without corresponding gap analysis
- Update counts and statistics that may have drifted
- Re-prioritize remaining gaps based on current project needs

### Gap lifecycle

```
Identified -> In Progress -> Resolved
                  |
                  +-> Superseded (with rationale)
                  +-> Out of Scope (with rationale)
```

---

**Roadmap Version**: 3.0.0 | **Created**: 2026-02-19 | **Constitution**: v3.0.0 | **Previous Version**: 2.0.0 (2026-02-18)
