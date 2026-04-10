# Contributing to HumanInLoop

Thank you for your interest in contributing to HumanInLoop!

## Project Structure

HumanInLoop has two packages:

- **`humaninloop/`** — CLI tool (`uvx humaninloop init`). Contains scaffolded content (agents, skills, commands, templates) and CLI commands.
- **`humaninloop_brain/`** — DAG engine. Deterministic graph infrastructure with Pydantic models, NetworkX operations, and MCP server.

## Adding Agents, Skills, Commands, or Templates

Content lives in `humaninloop/src/humaninloop/scaffolds/`:

```
scaffolds/
├── agents/          # Agent .md definitions
├── skills/          # Skill directories (SKILL.md + references/)
├── commands/        # Slash command .md files
├── templates/       # Workflow templates
├── catalogs/        # DAG node catalogs
└── scripts/         # Shell utilities
```

### Guidelines

- Agents: Follow [AGENT-GUIDELINES.md](./docs/AGENT-GUIDELINES.md)
- Skills: Follow [SKILL-GUIDELINES.md](./docs/SKILL-GUIDELINES.md)
- Test your changes: run `uvx humaninloop init` in a scratch directory to verify

## Contributing to humaninloop_brain

The DAG engine has strict architectural constraints:

- **Layer dependency rule**: entities -> graph -> validators -> passes -> mcp -> cli (no upward imports)
- **Test coverage**: >= 90% required (CI gate)
- **All tests must pass**: `cd humaninloop_brain && uv run pytest --tb=short`

## Feature Contributions

1. **Open an issue** describing the proposed feature
2. **Discuss** the approach before implementing
3. **Create a spec** using `/humaninloop:specify` if the feature is significant
4. **Submit PR** referencing the issue and spec

## Bug Fixes

1. **Open an issue** describing the bug (unless trivial)
2. **Submit PR** with fix, referencing the issue
3. **Include test case** if applicable

## Commit Conventions

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description
```

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `chore` | Maintenance tasks |
| `test` | Adding or updating tests |
| `ci` | CI/CD changes |

### Scope

Use the affected area as scope:
- `feat(humaninloop): add new skill for X`
- `fix(brain): correct topological sort edge case`
- `docs: update README`

## Documentation

- [docs/decisions/](./docs/decisions/) - Architecture Decision Records
- [docs/analysis-cli-distribution-model.md](./docs/analysis-cli-distribution-model.md) - CLI distribution architecture
- [CHANGELOG.md](./CHANGELOG.md) - Release history
- [ROADMAP.md](./ROADMAP.md) - Planned features

## Questions?

Open an issue if you have questions about contributing.
