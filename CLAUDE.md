# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains the HumanInLoop (HIL) Claude Code Plugin Marketplace - a platform for discovering, sharing, and managing Claude Code plugins for the company HumanInLoop (humaninloop.dev).

## Reference Artefacts (docs/speckit-artefacts/)

The `docs/speckit-artefacts/` folder contains a snapshot of the original **speckit** toolkit - the inspiration for the humaninloop plugins.

### Important Context

1. **Speckit is inspiration, not specification**: The humaninloop plugins are a **fundamental rearchitecture**, not a direct migration or port of speckit. They are loosely similar but architecturally different.

2. **No behavioral parity expected**: NEVER assume humaninloop plugins should behave the same as speckit. The plugins may work differently by design. Only expect matching behavior if the user explicitly confirms this expectation.

3. **Read-only reference**: These artefacts are imported snapshots for reference only. All active development happens in `plugins/`. Do not modify files in `docs/speckit-artefacts/`.

4. **Development workflow**:
   - **speckit** (original inspiration)
   - → **human-in-loop-experiments** (experimental adaptation)
   - → **humaninloop** (clean production version)

5. **Need-based migration**: Migration from speckit concepts is ongoing and selective - only what serves humaninloop's needs is adopted and restructured for the multi-agent plugin architecture.

### Artefacts Structure

```
docs/speckit-artefacts/
├── .claude/                    # Original speckit agent files
│   ├── speckit.specify.md
│   ├── speckit.plan.md
│   └── ...
└── .specify/                   # Original speckit resources
    ├── memory/
    ├── scripts/
    └── templates/
```

## Constitution

This project is governed by a constitution at `.humaninloop/memory/constitution.md` (v1.0.0). All development MUST comply with its principles.

## Development Guidelines

These guidelines derive from the project constitution. RFC 2119 keywords (MUST, SHOULD, MAY) define requirement levels.

### General

- Use `gh` CLI for all GitHub-related tasks (viewing repos, issues, PRs, etc.)

### Security (Constitution Principle I)

- Secrets MUST NOT be committed to the repository
- `.gitignore` MUST exclude sensitive patterns (*.env, *.pem, credentials, secrets)
- Input validation MUST be present in all Python validators before processing user-provided file paths
- Shell scripts MUST validate arguments before processing

### Testing (Constitution Principle II)

- All Python validation scripts MUST have automated tests with pytest
- Test files MUST follow `test_*.py` naming convention
- Coverage MUST NOT fall below 60% (blocking threshold)
- Coverage SHOULD be >= 80% (warning threshold)
- New validators MUST include tests in the same PR

### Error Handling (Constitution Principle III)

- Python validators MUST return structured JSON output with `checks`, `summary`, and `issues` fields
- Python validators MUST exit with code 0 on success, code 1 on validation failure or error
- Shell scripts MUST use `set -e` or explicit error checking
- Error messages MUST include file path, line number (when applicable), and check name

### Observability (Constitution Principle IV)

- Python validators MUST output JSON to stdout (not stderr)
- Validation results MUST include check name, pass/fail status, and issue list
- Output MUST be parseable by `jq`

### Validator Script Pattern (Constitution Principle V)

- Validators MUST have a docstring header with description, checks list, usage, and output format
- Validators MUST define a `validate_file(file_path: str) -> dict` entry function
- Validators MUST use `if __name__ == '__main__':` pattern for CLI invocation
- Reference implementation: `plugins/humaninloop/skills/authoring-requirements/scripts/validate-requirements.py`

### ADR Discipline (Constitution Principle VI)

- Architectural decisions MUST be documented in `docs/decisions/`
- ADRs MUST follow Context/Decision/Rationale/Consequences format
- ADR numbers MUST be sequential (001, 002, 003...)

### Skill Structure (Constitution Principle VII)

- Skills MUST have a `SKILL.md` entry point file under 200 lines
- Skill directories MUST use kebab-case naming with category prefix (`authoring-*`, `validation-*`, `patterns-*`, `analysis-*`)
- Skills with validation logic MUST include scripts in a `scripts/` subdirectory

## Development Workflow

### Commit Conventions (Constitution Principle VIII)

All commits MUST follow [Conventional Commits](https://www.conventionalcommits.org/) with scope.

**Format**: `type(scope): description`

**Valid types**:
- `feat` - New features
- `fix` - Bug fixes
- `docs` - Documentation changes
- `refactor` - Code restructuring
- `chore` - Maintenance tasks
- `test` - Adding or modifying tests
- `ci` - CI/CD configuration changes

**Rules**:
- Scope MUST identify affected plugin or area (e.g., `humaninloop`, `constitution`, `spec`)
- Description MUST be imperative mood, lowercase, no period
- Breaking changes MUST include `BREAKING CHANGE:` footer or `!` after type

**Examples**:
```
feat(humaninloop): add /tasks command
fix(constitution): correct handoff agent reference
docs: add ADR for multi-agent architecture
test(validators): add unit tests for validate-requirements
ci: add GitHub Actions workflow for pytest
feat(humaninloop)!: change skill loading mechanism
```

### Feature Development

New features follow spec-driven development (dogfooding our own tools):

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

User feedback is tracked using a structured methodology in `docs/internal/feedback/`:

1. **Collect** raw feedback from users
2. **Anonymize** using first+last letter convention (e.g., "John" → "Jn")
3. **Categorize** by type (`bug`, `enhancement`, `feature-request`, `performance`) and phase
4. **Prioritize** using Pain × Effort matrix → P1/P2/P3
5. **Document** in `round-N.md` following `_template.md`
6. **Create GitHub issue** as tracking issue with checklist

See `docs/internal/feedback/methodology.md` for full process details.

### Releases

See [RELEASES.md](RELEASES.md) for release process. Update [CHANGELOG.md](CHANGELOG.md) with each release.

### Constitution Amendment

When amending `.humaninloop/memory/constitution.md`:

1. Propose change via PR to constitution file
2. Document rationale for change in PR description
3. Update version per semantic versioning (MAJOR: principle removal, MINOR: new principle, PATCH: clarification)
4. Update this CLAUDE.md to reflect changes
5. Include both files in the same commit
6. PR description MUST note "Constitution sync: CLAUDE.md updated"

## Quality Gates

| Gate | Requirement | Command | Enforcement |
|------|-------------|---------|-------------|
| Validator Syntax | Valid Python | `python -m py_compile <file>` | CI (when configured) |
| Shell Script Syntax | Valid Bash | `bash -n <file>` | CI (when configured) |
| Validator Tests | All pass | `pytest plugins/ --tb=short` | CI (when configured) |
| Validator Coverage | >= 60% | `pytest --cov --cov-fail-under=60` | CI (blocking) |
| Validator Coverage | >= 80% | `pytest --cov` | CI (warning) |
| JSON Schema | Valid output | `python <validator> <input> \| jq .` | CI (when configured) |
| Commit Format | Conventional | Pattern match | Code review |
| ADR Presence | Required for arch changes | Manual review | Code review |

## Documentation

- **[.humaninloop/memory/constitution.md](.humaninloop/memory/constitution.md)**: Project constitution (v1.0.0) - governance principles, quality gates, and enforcement mechanisms.
- **[docs/claude-plugin-documentation.md](docs/claude-plugin-documentation.md)**: Primary reference for Claude Code plugin development. Contains comprehensive technical details on plugin architecture, commands, skills, hooks, MCP integrations, and more.
- **[docs/agent-skills-documentation.md](docs/agent-skills-documentation.md)**: Complete technical reference for Agent Skills. Covers SKILL.md schema, progressive disclosure, triggering mechanism, description optimization, bundled resources, and the agentskills.io ecosystem.
- **[RELEASES.md](RELEASES.md)**: Release philosophy and versioning strategy for the marketplace.
- **[CHANGELOG.md](CHANGELOG.md)**: Curated history of all releases.
- **[ROADMAP.md](ROADMAP.md)**: Vision and planned features.
- **[docs/decisions/](docs/decisions/)**: Architecture Decision Records (ADRs) explaining key technical choices.
- **[docs/internal/feedback/](docs/internal/feedback/)**: Feedback triage methodology and round-by-round tracking.
- **[specs/](specs/)**: Feature specifications (completed, in-progress, planned).

## Marketplace Structure

```
human-in-loop/
├── .claude-plugin/
│   └── marketplace.json           # Marketplace manifest
├── plugins/
│   ├── humaninloop/               # Main workflow plugin (setup → specify → plan → tasks → implement)
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── agents/                # Multi-agent workflow agents
│   │   ├── commands/              # /humaninloop:setup, /humaninloop:specify, etc.
│   │   ├── skills/                # Auto-invoked agent skills
│   │   ├── check-modules/         # Validation check modules
│   │   ├── scripts/               # Shell utilities
│   │   └── templates/             # Workflow templates
├── specs/
│   ├── completed/                 # Shipped feature specs
│   ├── in-progress/               # Currently implementing
│   └── planned/                   # Future features (living roadmap)
├── docs/
│   ├── decisions/                 # Architecture Decision Records
│   ├── internal/                  # Internal docs (not for external use)
│   │   ├── feedback/              # Feedback triage (methodology, rounds)
│   │   └── strategy.md
│   ├── agent-skills-documentation.md
│   ├── claude-plugin-documentation.md
│   └── speckit-artefacts/         # READ-ONLY reference (original speckit)
├── README.md
├── CHANGELOG.md                   # Release history
├── ROADMAP.md                     # Vision and planned features
├── RELEASES.md                    # Release philosophy and versioning
├── CONTRIBUTING.md
└── LICENSE
```

## Available Plugins

| Plugin | Description | Commands | Skills |
|--------|-------------|----------|--------|
| `humaninloop` | Specification-driven development workflow | `/humaninloop:setup`, `/humaninloop:specify`, `/humaninloop:plan`, `/humaninloop:tasks`, `/humaninloop:audit`, `/humaninloop:implement` | `authoring-requirements`, `authoring-user-stories`, `authoring-constitution`, `brownfield-constitution`, `validation-constitution`, `analysis-codebase`, `syncing-claude-md`, `analysis-iterative` |

## Common Commands

```bash
# Add this marketplace to Claude Code
/plugin marketplace add deepeshBodh/human-in-loop

# Install humaninloop plugin
/plugin install humaninloop

# Set up project constitution (first-time setup)
/humaninloop:setup

# View installed plugins
/plugin
```

## Adding New Plugins

1. Create a new plugin directory under `plugins/`
2. Add a `.claude-plugin/plugin.json` manifest
3. Add commands, agents, and skills as needed
4. Add entry to `.claude-plugin/marketplace.json`
5. Submit PR
