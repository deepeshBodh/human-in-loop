# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains the HumanInLoop (HIL) Claude Code Plugin Marketplace - a platform for discovering, sharing, and managing Claude Code plugins for the company HumanInLoop (humaninloop.dev).

## Related Repositories

- **human-in-loop-experiments** (`deepeshBodh/human-in-loop-experiments`): Experimental repository where plugin adaptations are developed and tested before being imported into this marketplace. This is the staging ground for new features and migrations.

## Reference Artefacts (docs/speckit-artefacts/)

The `docs/speckit-artefacts/` folder contains a snapshot of the original **speckit** toolkit - the inspiration for the humaninloop plugins.

### Important Context

1. **Speckit is inspiration, not specification**: The humaninloop plugins are a **fundamental rearchitecture**, not a direct migration or port of speckit. They are loosely similar but architecturally different.

2. **No behavioral parity expected**: NEVER assume humaninloop plugins should behave the same as speckit. The plugins may work differently by design. Only expect matching behavior if the user explicitly confirms this expectation.

3. **Read-only reference**: These artefacts are imported snapshots for reference only. All active development happens in `plugins/`. Do not modify files in `docs/speckit-artefacts/`.

4. **Development workflow**:
   - **speckit** (original inspiration)
   - → **human-in-loop-experiments** (experimental adaptation)
   - → **human-in-loop-marketplace** (clean production version)

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

## Development Guidelines

- Use `gh` CLI for all GitHub-related tasks (viewing repos, issues, PRs, etc.)

## Development Workflow

### Commit Conventions

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat(plugin): description` - New features
- `fix(plugin): description` - Bug fixes
- `docs: description` - Documentation changes
- `refactor(plugin): description` - Code restructuring
- `chore: description` - Maintenance tasks

Examples:
```
feat(humaninloop): add /tasks command
fix(constitution): correct handoff agent reference
docs: add ADR for multi-agent architecture
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

### Releases

See [RELEASES.md](RELEASES.md) for release process. Update [CHANGELOG.md](CHANGELOG.md) with each release.

## Documentation

- **[docs/claude-plugin-documentation.md](docs/claude-plugin-documentation.md)**: Primary reference for Claude Code plugin development. Contains comprehensive technical details on plugin architecture, commands, skills, hooks, MCP integrations, and more.
- **[docs/agent-skills-documentation.md](docs/agent-skills-documentation.md)**: Complete technical reference for Agent Skills. Covers SKILL.md schema, progressive disclosure, triggering mechanism, description optimization, bundled resources, and the agentskills.io ecosystem.
- **[RELEASES.md](RELEASES.md)**: Release philosophy and versioning strategy for the marketplace.
- **[CHANGELOG.md](CHANGELOG.md)**: Curated history of all releases.
- **[ROADMAP.md](ROADMAP.md)**: Vision and planned features.
- **[docs/decisions/](docs/decisions/)**: Architecture Decision Records (ADRs) explaining key technical choices.
- **[specs/](specs/)**: Feature specifications (completed, in-progress, planned).

## Marketplace Structure

```
human-in-loop-marketplace/
├── .claude-plugin/
│   └── marketplace.json           # Marketplace manifest
├── plugins/
│   ├── humaninloop/               # Main workflow plugin (specify → plan → tasks → implement)
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── agents/                # Multi-agent workflow agents
│   │   ├── commands/              # /humaninloop:specify, /humaninloop:plan, etc.
│   │   ├── skills/                # Auto-invoked agent skills
│   │   ├── check-modules/         # Validation check modules
│   │   ├── scripts/               # Shell utilities
│   │   └── templates/             # Workflow templates
│   └── humaninloop-constitution/  # Constitution setup plugin
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── agents/                # Principal architect agent
│       ├── commands/              # /humaninloop-constitution:setup
│       ├── skills/                # Constitution authoring skills
│       └── templates/
├── specs/
│   ├── completed/                 # Shipped feature specs
│   ├── in-progress/               # Currently implementing
│   └── planned/                   # Future features (living roadmap)
├── docs/
│   ├── decisions/                 # Architecture Decision Records
│   ├── internal/                  # Internal strategy docs (not for external use)
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
| `humaninloop` | Specification-driven development workflow | `/humaninloop:specify`, `/humaninloop:plan`, `/humaninloop:tasks`, `/humaninloop:analyze`, `/humaninloop:checklist`, `/humaninloop:implement` | `authoring-requirements`, `authoring-user-stories`, `iterative-analysis` |
| `humaninloop-constitution` | Project constitution setup with enforceable governance | `/humaninloop-constitution:setup` | `authoring-constitution`, `analyzing-project-context`, `syncing-claude-md` |
| `humaninloop-experiments` | Experimental sandbox for new agent patterns | `/humaninloop-experiments:specify` | `authoring-requirements`, `authoring-user-stories`, `reviewing-specifications` |

## Common Commands

```bash
# Add this marketplace to Claude Code
/plugin marketplace add deepeshBodh/human-in-loop-marketplace

# Install constitution plugin first (required by humaninloop)
/plugin install humaninloop-constitution
/humaninloop-constitution:setup

# Install main workflow plugin
/plugin install humaninloop

# View installed plugins
/plugin
```

## Adding New Plugins

1. Copy `plugins/humaninloop-constitution/` as a template for simpler plugins
2. Update plugin.json, commands, and README with your plugin's info
3. Add entry to `.claude-plugin/marketplace.json`
4. Submit PR
