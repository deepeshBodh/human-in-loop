# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains the HumanInLoop (HIL) Claude Code Plugin Marketplace - a platform for discovering, sharing, and managing Claude Code plugins for the company HumanInLoop (humaninloop.dev).

## Constitution

This project is governed by a constitution at `.humaninloop/memory/constitution.md` (v1.0.0). All development MUST comply with its principles.

## Development Guidelines

These guidelines derive from the project constitution. RFC 2119 keywords (MUST, SHOULD, MAY) define requirement levels. See the constitution for full details.

### General

- Use `gh` CLI for all GitHub-related tasks (viewing repos, issues, PRs, etc.)

### Key Principles

| Principle | Summary |
|-----------|---------|
| **Security** | No secrets in repo, input validation required |
| **Testing** | pytest required, coverage >= 60% (blocking), >= 80% (target) |
| **Error Handling** | Structured JSON output with `checks`, `summary`, `issues` fields |
| **Observability** | JSON to stdout, parseable by `jq` |
| **Validator Pattern** | Docstring header, `validate_file()` entry, `__main__` CLI pattern |
| **ADR Discipline** | Architectural decisions documented in `docs/decisions/` |
| **Skill Structure** | `SKILL.md` under 200 lines, kebab-case with category prefix |

### Commit Conventions

All commits MUST follow [Conventional Commits](https://www.conventionalcommits.org/) with scope.

**Format**: `type(scope): description`

**Valid types**: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`

**Rules**:
- Scope MUST identify affected plugin or area (e.g., `humaninloop`, `constitution`)
- Description MUST be imperative mood, lowercase, no period
- Breaking changes MUST include `!` after type or `BREAKING CHANGE:` footer

**Examples**:
```
feat(humaninloop): add /tasks command
fix(constitution): correct handoff agent reference
docs: add ADR for multi-agent architecture
```

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

| Gate | Requirement | Command | Enforcement |
|------|-------------|---------|-------------|
| Validator Tests | All pass | `pytest plugins/ --tb=short` | CI |
| Validator Coverage | >= 60% | `pytest --cov --cov-fail-under=60` | CI (blocking) |
| Validator Coverage | >= 80% | `pytest --cov` | CI (warning) |
| Commit Format | Conventional | Pattern match | Code review |
| ADR Presence | Required for arch changes | Manual review | Code review |

## Documentation

- **[.humaninloop/memory/constitution.md](.humaninloop/memory/constitution.md)**: Project constitution - governance principles and enforcement.
- **[docs/claude-plugin-documentation.md](docs/claude-plugin-documentation.md)**: Claude Code plugin development reference.
- **[docs/agent-skills-documentation.md](docs/agent-skills-documentation.md)**: Agent Skills technical reference.
- **[docs/decisions/](docs/decisions/)**: Architecture Decision Records (ADRs).
- **[specs/](specs/)**: Feature specifications (completed, in-progress, planned).

## Adding New Plugins

1. Create plugin directory under `plugins/`
2. Add `.claude-plugin/plugin.json` manifest
3. Add commands, agents, and skills as needed
4. Add entry to `.claude-plugin/marketplace.json`
5. Submit PR
