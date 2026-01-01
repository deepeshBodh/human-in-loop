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

## Documentation

- **[docs/claude-plugin-documentation.md](docs/claude-plugin-documentation.md)**: Primary reference for Claude Code plugin development. Contains comprehensive technical details on plugin architecture, commands, skills, hooks, MCP integrations, and more.
- **[RELEASES.md](RELEASES.md)**: Release philosophy and versioning strategy for the marketplace.

## Marketplace Structure

```
human-in-loop-marketplace/
├── .claude-plugin/
│   └── marketplace.json           # Marketplace manifest
├── plugins/
│   ├── humaninloop/               # Main workflow plugin (specify → plan)
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── agents/                # Multi-agent workflow agents
│   │   ├── commands/              # /humaninloop:specify, /humaninloop:plan
│   │   ├── check-modules/         # Validation check modules
│   │   ├── scripts/               # Shell utilities
│   │   └── templates/             # Workflow templates
│   └── humaninloop-constitution/  # Constitution setup plugin
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── commands/              # /humaninloop-constitution:setup
│       └── templates/
├── docs/
│   ├── claude-plugin-documentation.md
│   └── speckit-artefacts/         # READ-ONLY reference (original speckit)
├── README.md
├── RELEASES.md                    # Release philosophy and versioning
├── CONTRIBUTING.md
└── LICENSE
```

## Available Plugins

| Plugin | Description | Commands |
|--------|-------------|----------|
| `humaninloop` | Specification-driven development workflow | `/humaninloop:specify`, `/humaninloop:plan`, `/humaninloop:tasks`, `/humaninloop:analyze`, `/humaninloop:checklist`, `/humaninloop:implement` |
| `humaninloop-constitution` | Project constitution setup | `/humaninloop-constitution:setup` |

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
