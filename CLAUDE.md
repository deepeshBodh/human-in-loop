# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains the HumanInLoop (HIL) Claude Code Plugin Marketplace - a platform for discovering, sharing, and managing Claude Code plugins for the company HumanInLoop (humaninloop.dev).

This project contains two distinct codebases:

| Codebase | Location | Nature | Status |
|----------|----------|--------|--------|
| **humaninloop_brain** | `humaninloop_brain/` | Python package (uv-managed, tested, DAG infrastructure) | Active development |
| **Plugin validators** | `plugins/humaninloop/skills/*/scripts/` | Standalone Python scripts (untested) | Deprecated -- migrate to humaninloop_brain |

## Constitution

This project is governed by a constitution at `.humaninloop/memory/constitution.md` (v2.0.0). All development MUST comply with its principles.

## Development Guidelines

These guidelines derive from the project constitution. RFC 2119 keywords (MUST, SHOULD, MAY) define requirement levels. See the constitution for full details.

### General

- Use `gh` CLI for all GitHub-related tasks (viewing repos, issues, PRs, etc.)
- New validation logic MUST be built in `humaninloop_brain`, not as new plugin validators
- Deterministic logic (graph operations, structural validation) MUST live in `humaninloop_brain`, not in agent prompts

### Key Principles

| # | Principle | Summary |
|---|-----------|---------|
| I | **Security** | No secrets in repo, input validation required, Pydantic model validators enforce constraints |
| II | **Testing** | pytest required; humaninloop_brain >= 90% coverage (blocking); legacy validators deprecated |
| III | **Error Handling** | Structured JSON output with `checks`, `summary`, `issues` fields; exit codes 0/1/2; `FrozenPassError`, `ValidationViolation` |
| IV | **Observability** | JSON to stdout, parseable by `jq`; DAG pass JSON as workflow observability artifact |
| V | **Structured Output** | All 12 Python entry points follow `checks`/`summary` JSON schema |
| VI | **ADR Discipline** | Architectural decisions documented in `docs/decisions/` (7 ADRs) |
| VII | **Skill Structure** | `SKILL.md` required, progressive disclosure with bundled reference files, kebab-case with category prefix |
| VIII | **Conventional Commits** | `type(scope): description` format required |
| IX | **Deterministic Infrastructure** | Graph operations, validation, pass lifecycle in `humaninloop_brain`; LLM agents consume via CLI |
| X | **Pydantic Entity Modeling** | Frozen models, type-status validation, enum types for constrained values |

### Commit Conventions

All commits MUST follow [Conventional Commits](https://www.conventionalcommits.org/) with scope.

**Format**: `type(scope): description`

**Valid types**: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`

**Rules**:
- Scope MUST identify affected plugin or area (e.g., `humaninloop`, `constitution`, `brain`, `dag`)
- Description MUST be imperative mood, lowercase, no period
- Breaking changes MUST include `!` after type or `BREAKING CHANGE:` footer

**Examples**:
```
feat(humaninloop): add /tasks command
fix(brain): correct topological sort edge case
docs: add ADR for DAG-first infrastructure
ci(brain): add GitHub Actions workflow
```

## Technology Stack

| Category | Choice | Version |
|----------|--------|---------|
| Primary Content | Markdown | N/A |
| Infrastructure Language | Python | >= 3.11 |
| Entity Modeling | Pydantic | >= 2.0 |
| Graph Operations | NetworkX | >= 3.0 |
| Package Manager | uv | Latest |
| Build System | hatchling | Latest |
| Shell Scripts | Bash | POSIX-compatible |
| Test Framework | pytest | >= 8.0 |
| Coverage Tool | pytest-cov | >= 5.0 |
| Plugin Architecture | Claude Code Plugin System | N/A |
| Version Control | Git | N/A |
| GitHub Integration | `gh` CLI | N/A |

## Development Workflow

### Feature Development

New features follow spec-driven development:

1. **Create GitHub issue** describing the feature
2. **Run `/humaninloop:specify`** → commit spec to `specs/in-progress/`
3. **Run `/humaninloop:plan`** → commit plan
4. **Implement** → PR references issue and spec
5. **On merge** → move spec to `specs/completed/`

### Bug Fixes

1. **Create GitHub issue** describing the bug
2. **Fix** → PR references issue
3. **Trivial fixes** → clear commit message, no issue required

### Feedback Triage

User feedback is tracked in `docs/internal/feedback/` using Pain × Effort prioritization (P1/P2/P3). See `docs/internal/feedback/methodology.md` for the full process.

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
| Python Tests | humaninloop_brain | All 190+ tests pass | `cd humaninloop_brain && uv run pytest --tb=short` | CI automated (GAP-001) |
| Test Coverage | humaninloop_brain | >= 90% | `cd humaninloop_brain && uv run pytest --cov --cov-fail-under=90` | CI automated, blocking (GAP-001) |
| Coverage Ratchet | humaninloop_brain | >= previous baseline (currently 98%) | Compare against stored baseline | CI automated (GAP-001) |
| Python Syntax | humaninloop_brain | Valid Python | `cd humaninloop_brain && uv run python -m py_compile src/humaninloop_brain/**/*.py` | CI automated (GAP-001) |
| Shell Syntax | Plugin scripts | Valid Bash | `bash -n plugins/humaninloop/scripts/*.sh` | CI automated (GAP-001) |
| JSON Schema | CLI output | Valid structured output | `hil-dag validate <input> \| jq .` | Tests |
| Commit Format | All | Conventional Commits | Pattern match | Code review |
| ADR Presence | Architectural changes | ADR exists | Manual review | Code review |
| Secret Scanning | All | No secrets in code | `git secrets --scan` | CI automated (GAP-003) |

## Documentation

- **[.humaninloop/memory/constitution.md](.humaninloop/memory/constitution.md)**: Project constitution - governance principles and enforcement (v2.0.0).
- **[docs/claude-plugin-documentation.md](docs/claude-plugin-documentation.md)**: Claude Code plugin development reference.
- **[docs/agent-skills-documentation.md](docs/agent-skills-documentation.md)**: Agent Skills technical reference.
- **[docs/decisions/](docs/decisions/)**: Architecture Decision Records (7 ADRs).
- **[docs/architecture/](docs/architecture/)**: DAG-first architecture synthesis documents.
- **[specs/](specs/)**: Feature specifications (completed, in-progress, planned).

## Adding New Plugins

1. Create plugin directory under `plugins/`
2. Add `.claude-plugin/plugin.json` manifest
3. Add commands, agents, and skills as needed
4. Add entry to `.claude-plugin/marketplace.json`
5. Submit PR

<!-- Constitution sync: v2.0.0 | Last synced: 2026-02-18 -->
