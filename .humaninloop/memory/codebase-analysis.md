# Codebase Analysis

> Generated: 2026-01-13T20:50:00Z
> Mode: setup-brownfield
> Status: draft

---

## Part 1: Inventory (Factual)

### Project Identity

| Aspect | Value | Source |
|--------|-------|--------|
| Name | human-in-loop (HumanInLoop Plugin Marketplace) | CLAUDE.md, README.md |
| Primary Language | Markdown, Shell (bash), Python 3.x | File inspection |
| Framework | Claude Code Plugin Architecture | plugin.json |
| Package Manager | N/A (documentation/plugin repository) | File inspection |
| Entry Points | Commands in `plugins/humaninloop/commands/` | plugin.json |

### Directory Structure

```
human-in-loop/
├── .claude-plugin/           # Marketplace manifest
├── plugins/
│   └── humaninloop/          # Main workflow plugin
│       ├── .claude-plugin/   # Plugin manifest (plugin.json)
│       ├── agents/           # Multi-agent definitions (5 files)
│       ├── commands/         # Slash commands (6 files)
│       ├── scripts/          # Shell utilities (4 files)
│       ├── skills/           # Agent skills (16 directories)
│       └── templates/        # Workflow templates (16 files)
├── docs/
│   ├── decisions/            # Architecture Decision Records (5 ADRs)
│   ├── internal/             # Internal documentation
│   └── speckit-artefacts/    # READ-ONLY reference (original speckit)
├── specs/
│   ├── completed/            # Shipped feature specs
│   ├── in-progress/          # Currently implementing
│   └── planned/              # Future features
├── CLAUDE.md                 # Agent instructions
├── CONTRIBUTING.md           # Contribution guidelines
├── CHANGELOG.md              # Release history
├── RELEASES.md               # Release philosophy
└── ROADMAP.md                # Vision and planned features
```

### Detected Patterns

#### Architecture Pattern

| Pattern | Evidence |
|---------|----------|
| Multi-Agent Architecture | `plugins/humaninloop/agents/` with 5 specialized agents; ADR-001 documents this decision |
| Skill-Augmented Agents | `plugins/humaninloop/skills/` with 16 skill directories; ADR-004 documents this approach |
| Feature-based Organization | Skills organized by concern: `authoring-*`, `validation-*`, `patterns-*`, `analysis-*` |

#### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Files (commands) | kebab-case.md | `setup.md`, `plan.md`, `specify.md` |
| Files (skills) | SCREAMING-KEBAB-CASE.md | `SKILL.md`, `RFC-2119-KEYWORDS.md` |
| Files (agents) | kebab-case.md | `principal-architect.md`, `devils-advocate.md` |
| Files (templates) | kebab-case-template.md | `constitution-template.md`, `spec-template.md` |
| Files (Python) | snake_case with validate- prefix | `validate-requirements.py`, `validate-openapi.py` |
| Files (Shell) | kebab-case.sh | `create-new-feature.sh`, `common.sh` |
| Directories (skills) | kebab-case | `authoring-constitution`, `patterns-api-contracts` |
| Variables (Shell) | SCREAMING_SNAKE_CASE | `REPO_ROOT`, `FEATURE_DIR`, `CURRENT_BRANCH` |
| Functions (Shell) | snake_case | `get_repo_root()`, `check_feature_branch()` |
| Functions (Python) | snake_case | `validate_file()`, `check_format()` |
| Classes (Python) | N/A (functional style) | No class definitions found |

#### Error Handling Pattern

| Pattern | Evidence |
|---------|----------|
| JSON output with exit codes | All Python validators return JSON with `summary.failed` count and exit 1 on failure |
| Structured error objects | `{"check": "name", "passed": bool, "issues": []}` pattern in validators |
| Early exit with error message | Shell scripts use `exit 1` with stderr messages |

#### Test Pattern

| Aspect | Value |
|--------|-------|
| Framework | None configured |
| Location | N/A |
| Naming | N/A |
| Coverage Config | N/A |

### Domain Entities

| Entity | File | Purpose | Relationships |
|--------|------|---------|---------------|
| Constitution | templates/constitution-template.md | Project governance document | Has Principles, Technology Stack, Quality Gates |
| Principle | skills/authoring-constitution/SKILL.md | Enforceable governance rule | Part of Constitution; has Enforcement, Testability, Rationale |
| Skill | skills/*/SKILL.md | Agent capability definition | Used by Agents; has bundled resources |
| Agent | agents/*.md | Specialized workflow participant | Uses Skills; produces Artifacts |
| Command | commands/*.md | User-invokable workflow entry | Orchestrates Agents |
| Spec | templates/spec-template.md | Feature specification | Has User Stories, Requirements, Success Criteria |
| Gap Card | skills/authoring-roadmap/SKILL.md | Brownfield improvement item | Part of Evolution Roadmap; has Priority, Dependencies |

### External Dependencies

| Service | Access Pattern | Config Location |
|---------|---------------|-----------------|
| GitHub | `gh` CLI commands | CLAUDE.md (referenced) |
| Claude Code Plugin System | Plugin manifest, commands, skills | `.claude-plugin/` directories |

---

## Part 2: Assessment (Judgment)

### Strengths to Preserve

1. **Well-documented architecture decisions**: 5 ADRs in `docs/decisions/` with clear Context/Decision/Rationale/Consequences structure. This practice enables future maintainers to understand why choices were made.

2. **Consistent Python validator pattern**: All 5 Python scripts follow identical structure: docstring header, JSON output, structured checks with `passed`/`issues` fields, proper exit codes. This pattern is production-ready and easy to extend.

3. **Comprehensive skill organization**: 16 skills organized by function (`authoring-*`, `validation-*`, `patterns-*`, `analysis-*`) with consistent SKILL.md entry points and bundled resources. Clear separation of concerns.

4. **RFC 2119 keyword discipline**: Constitution authoring explicitly requires MUST/SHOULD/MAY keywords with enforcement mechanisms. This prevents vague governance.

5. **Multi-agent handoff protocol**: Agents communicate through file artifacts (context files, reports). Clear contracts documented in templates. Enables independent agent evolution.

6. **Conventional Commits adopted**: CLAUDE.md and CONTRIBUTING.md enforce `type(scope): description` format. CHANGELOG follows Keep a Changelog format.

### Inconsistencies Found

| Area | Finding | Severity | Location |
|------|---------|----------|----------|
| Python file naming | Uses kebab-case (`validate-requirements.py`) instead of Python-standard snake_case | low | `skills/*/scripts/` |
| Missing tests | No test files or test framework configured for Python validators | high | Repository root |
| Shell script permissions | Inconsistent permissions (some `rwxr-xr-x`, some `rwx--x--x`) | low | `plugins/humaninloop/scripts/` |
| SKILL.md frontmatter | Some skills lack frontmatter (name, description) | medium | Skills like `authoring-roadmap` |
| Version mismatch | marketplace.json shows 0.7.7 but plugin.json shows 0.7.8 | low | `.claude-plugin/marketplace.json` |

### Essential Floor Status

| Category | Status | Evidence |
|----------|--------|----------|
| Security | partial | No secrets handling needed (documentation repo); no auth required |
| Testing | absent | No test framework, no test files, no coverage configuration |
| Error Handling | present | Consistent JSON+exit code pattern in Python validators; Shell scripts use early exit |
| Observability | partial | No logging framework; relies on stdout/stderr; no structured logging |

#### Security Assessment Details

- **Auth at boundaries**: N/A - This is a documentation/plugin repository, not an application with API boundaries
- **Secrets from env**: present - No secrets required; .gitignore excludes sensitive patterns (*.env, *.pem, credentials)
- **Input validation**: present - Python validators validate file content; Shell scripts validate arguments

#### Testing Assessment Details

- **Test framework configured**: absent - No pytest.ini, jest.config, or similar configuration files
- **Test files present**: absent - No files matching `*test*.py`, `test_*.py`, or `*_test.py`
- **CI runs tests**: absent - No `.github/workflows/` directory; no CI/CD configuration

#### Error Handling Assessment Details

- **Explicit error types**: partial - Python uses generic `ValueError`, `FileNotFoundError`; no custom error classes
- **Context preservation**: present - Error messages include file paths, line numbers, check names
- **Appropriate status codes**: present - Validators exit with 0 on success, 1 on failure

#### Observability Assessment Details

- **Structured logging**: absent - No logging library (no `logging`, `structlog`, `loguru` imports)
- **Correlation IDs**: N/A - Not applicable for batch-style validation scripts
- **No PII in logs**: present - Scripts output validation results only, no user data

### Recommended Constitution Focus

Based on this analysis, the constitution should:

1. **Establish testing discipline (P1)**: The Python validators are critical for workflow quality but have no tests. Constitution MUST require tests for all Python scripts with measurable coverage threshold.

2. **Codify validation script pattern (P2)**: Document the successful JSON+exit code pattern as a principle. New validators MUST follow this pattern.

3. **Define skill structure requirements (P2)**: Require SKILL.md frontmatter (name, description) for all skills. Define bundled resource conventions.

4. **Address naming inconsistencies (P3)**: Either adopt Python snake_case for script files or document kebab-case as deliberate choice with rationale.

5. **Preserve ADR discipline (P2)**: Require ADRs for architectural decisions. Define when an ADR is needed vs. a simple commit.

---

## Appendix: Detection Method

| Aspect | Method Used |
|--------|-------------|
| Tech Stack | Manual inspection (no package manager files) |
| Architecture | Directory pattern matching + ADR review |
| Entities | Template and skill file analysis |
| Conventions | File sampling across all directories |
| Essential Floor | Manual code review of scripts and patterns |
