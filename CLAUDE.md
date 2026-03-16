# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains the HumanInLoop (HIL) project -- a deterministic DAG infrastructure for Claude Code plugin workflows, built around the `humaninloop_brain` Python package and a Claude Code plugin marketplace.

**Governed codebase**: `humaninloop_brain/` -- Python package providing deterministic DAG infrastructure for workflow execution. The plugin marketplace (agents, commands, skills, templates in `plugins/`) is the consumption layer.

## Constitution

This project is governed by a constitution at `.humaninloop/memory/constitution.md` (v3.0.0). All development MUST comply with its principles.

## Development Guidelines

These guidelines derive from the project constitution. RFC 2119 keywords (MUST, SHOULD, MAY) define requirement levels. See the constitution for full details.

### General

- Use `gh` CLI for all GitHub-related tasks (viewing repos, issues, PRs, etc.)
- Deterministic logic (graph operations, structural validation) MUST live in `humaninloop_brain`, not in agent prompts
- The `hil-dag` CLI MUST be the sole write gate for StrategyGraph JSON -- agents MUST NOT write JSON directly

### Key Principles

| # | Principle | Summary |
|---|-----------|---------|
| I | **Security** | No secrets in repo; input validation required; Pydantic model validators enforce constraints; secret scanning MUST be in CI (GAP-003) |
| II | **Testing** | pytest required; `humaninloop_brain` >= 90% coverage (blocking CI gate); 381+ tests |
| III | **Error Handling** | Structured JSON output with `checks`/`summary` fields; exit codes 0/1/2; `FrozenEntryError`; `ValidationViolation` |
| IV | **Observability** | JSON to stdout, parseable by `jq`; StrategyGraph JSON as primary workflow observability artifact |
| V | **Structured Output** | All 7 `hil-dag` CLI subcommands follow `checks`/`summary` JSON schema |
| VI | **ADR Discipline** | Architectural decisions documented in `docs/decisions/` (8 ADRs) |
| VII | **Skill Structure** | `SKILL.md` required; progressive disclosure with bundled reference files; kebab-case with category prefix |
| VIII | **Conventional Commits** | `type(scope): description` format; pre-commit hook + CI enforcement |
| IX | **Deterministic Infrastructure** | Two tiers: Tier 1 (strict graph-algorithmic) + Tier 2 (heuristic-deterministic); all in `humaninloop_brain`; agents consume via CLI |
| X | **Pydantic Entity Modeling** | Frozen models; type-status validation via `TYPE_STATUS_MAP`; derived field enforcement; 11 enums, 14 models, 7 modules |
| XI | **Layer Dependency** | Strict unidirectional imports: entities -> graph -> validators -> passes -> cli; no upward imports |
| XII | **Catalog-Driven Assembly** | JSON catalogs with capability-based resolution; system invariants (INV-001 through INV-005); `carry_forward` gates |

### Commit Conventions

All commits MUST follow [Conventional Commits](https://www.conventionalcommits.org/) with scope.

**Format**: `type(scope): description`

**Valid types**: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`

**Rules**:
- Scope MUST identify affected plugin or area (e.g., `humaninloop`, `constitution`, `brain`, `dag`)
- Description MUST be imperative mood, lowercase, no period
- Breaking changes MUST include `!` after type or `BREAKING CHANGE:` footer

**Enforcement**:
- Pre-commit hook (`conventional-pre-commit` v4.0.0) validates on every commit
- CI job (`commit-lint`) validates all PR commits

**Examples**:
```
feat(humaninloop): add /tasks command
fix(brain): correct topological sort edge case
docs: add ADR for DAG-first infrastructure
ci(brain): add GitHub Actions workflow
```

### Layer Dependency Rule

The `humaninloop_brain` package MUST maintain strict unidirectional import dependencies:

```
entities       (no internal imports)
    |
  graph        (imports from: entities)
    |
validators     (imports from: entities, graph)
    |
  passes       (imports from: entities, graph)
    |
   cli         (imports from: entities, graph, validators, passes)
```

No module MUST import from a layer below it in this hierarchy.

## Technology Stack

| Category | Choice | Version |
|----------|--------|---------|
| Infrastructure Language | Python | >= 3.11 |
| Entity Modeling | Pydantic | >= 2.0 |
| Graph Operations | NetworkX | >= 3.0 |
| Package Manager | uv | Latest |
| Build System | hatchling | Latest |
| Shell Scripts | Bash | POSIX-compatible |
| Test Framework | pytest | >= 8.0 |
| Coverage Tool | pytest-cov | >= 5.0 |
| Commit Linting | conventional-pre-commit | v4.0.0 |
| Shell Linting | shellcheck-py | v0.10.0.1 |
| Plugin Architecture | Claude Code Plugin System | N/A |
| Primary Content | Markdown | N/A |
| Version Control | Git | N/A |
| GitHub Integration | `gh` CLI | N/A |

## Development Workflow

### Feature Development

New features follow spec-driven development:

1. **Create GitHub issue** describing the feature
2. **Run `/humaninloop:specify`** -- commit spec to `specs/in-progress/`
3. **Run `/humaninloop:plan`** -- commit plan
4. **Implement** -- PR references issue and spec
5. **On merge** -- move spec to `specs/completed/`

### Bug Fixes

1. **Create GitHub issue** describing the bug
2. **Fix** -- PR references issue
3. **Trivial fixes** -- clear commit message, no issue required

### Feedback Triage

User feedback is tracked in `docs/internal/feedback/` using Pain x Effort prioritization (P1/P2/P3). See `docs/internal/feedback/methodology.md` for the full process.

### Releases

See [RELEASES.md](RELEASES.md) for release process. Update [CHANGELOG.md](CHANGELOG.md) with each release.

### Constitution Amendment

When amending `.humaninloop/memory/constitution.md`:

1. Propose change via PR to constitution file
2. Document rationale in PR description
3. Update version per semantic versioning
4. Update this CLAUDE.md to reflect changes
5. Include both files in the same commit
6. PR description MUST note "Constitution sync: CLAUDE.md updated"

## Quality Gates

| Gate | Scope | Requirement | Command | Enforcement |
|------|-------|-------------|---------|-------------|
| Python Tests | humaninloop_brain | All 381+ tests pass | `cd humaninloop_brain && uv run pytest --tb=short` | CI automated |
| Test Coverage | humaninloop_brain | >= 90% | `cd humaninloop_brain && uv run pytest --cov --cov-fail-under=90` | CI automated, blocking |
| Python Syntax | humaninloop_brain | Valid Python | `find src/humaninloop_brain -name '*.py' -print0 \| xargs -0 uv run python -m py_compile` | CI automated |
| Shell Syntax | Plugin scripts | Valid Bash | `find plugins/humaninloop -name '*.sh' -print0 \| xargs -0 -n1 bash -n` | CI automated |
| JSON Schema | CLI output | Valid structured output | `hil-dag validate <input> \| jq .` | Tests |
| Commit Format | All | Conventional Commits | Pre-commit hook + CI `commit-lint` job | CI automated + pre-commit |
| ADR Presence | Architectural changes | ADR exists | Manual review of `docs/decisions/` | Code review |
| Secret Scanning | All | No secrets in code | `git secrets --scan` | GAP-003: not yet configured |

## Documentation

- **[.humaninloop/memory/constitution.md](.humaninloop/memory/constitution.md)**: Project constitution - governance principles and enforcement (v3.0.0).
- **[docs/claude-plugin-documentation.md](docs/claude-plugin-documentation.md)**: Claude Code plugin development reference.
- **[docs/agent-skills-documentation.md](docs/agent-skills-documentation.md)**: Agent Skills technical reference.
- **[docs/decisions/](docs/decisions/)**: Architecture Decision Records (8 ADRs).
- **[docs/architecture/](docs/architecture/)**: DAG-first architecture synthesis documents.
- **[docs/architecture/v3/](docs/architecture/v3/)**: V3 architecture design documents.
- **[docs/AGENT-GUIDELINES.md](docs/AGENT-GUIDELINES.md)**: Agent creation guidelines — persona design, coupling detection, compliance.
- **[docs/SKILL-GUIDELINES.md](docs/SKILL-GUIDELINES.md)**: Skill creation guidelines — structure, testing, anti-rationalization.

## Adding New Plugins

1. Create plugin directory under `plugins/`
2. Add `.claude-plugin/plugin.json` manifest
3. Add commands, agents, and skills as needed
4. Add entry to `.claude-plugin/marketplace.json`
5. Submit PR

<!-- Constitution sync: v3.0.0 | Last synced: 2026-02-19 -->
