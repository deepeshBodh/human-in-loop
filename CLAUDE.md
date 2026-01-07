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

## Documentation

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
