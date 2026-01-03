# HumanInLoop Claude Code Plugin Marketplace

Official Claude Code plugin marketplace for [HumanInLoop](https://humaninloop.dev).

## Quick Start

### Add the Marketplace

```bash
/plugin marketplace add deepeshBodh/human-in-loop
```

### Install Plugins

```bash
# Install humaninloop plugin
/plugin install humaninloop

# Set up your project constitution (first-time setup)
/humaninloop:setup
```

### Browse Installed Plugins

```bash
/plugin
```

## Available Plugins

| Plugin | Description | Commands |
|--------|-------------|----------|
| [humaninloop](./plugins/humaninloop) | Specification-driven development workflow: setup → specify → plan → tasks → implement | `/humaninloop:setup`, `/humaninloop:specify`, `/humaninloop:plan`, `/humaninloop:tasks`, `/humaninloop:audit`, `/humaninloop:implement` |

### humaninloop

Multi-agent specification-driven development workflow with integrated quality validation and project constitution management.

**Agents:** 5 specialized agents for spec writing, validation, planning, and task generation
**Commands:** `/humaninloop:setup`, `/humaninloop:specify`, `/humaninloop:plan`, `/humaninloop:tasks`, `/humaninloop:audit`, `/humaninloop:implement`
**Skills:** 13 model-invoked skills for authoring, analysis, patterns, and validation

#### Skills (13 total)

See [plugin README](./plugins/humaninloop/README.md) for the full list. Key skills include:

| Category | Skills |
|----------|--------|
| Authoring | `authoring-requirements`, `authoring-user-stories`, `authoring-constitution` |
| Analysis | `analysis-codebase`, `analysis-iterative`, `analysis-specifications` |
| Patterns | `patterns-api-contracts`, `patterns-entity-modeling`, `patterns-technical-decisions`, `patterns-vertical-tdd` |
| Validation | `validation-plan-artifacts`, `validation-task-artifacts` |
| Utilities | `syncing-claude-md` |

## Contributing

Want to add your plugin to the marketplace? See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## Documentation

- [Claude Code Plugin Documentation](./docs/claude-plugin-documentation.md) - Complete technical reference for building plugins
- [Changelog](./CHANGELOG.md) - Release history
- [Roadmap](./ROADMAP.md) - Vision and planned features
- [Architecture Decisions](./docs/decisions/) - ADRs explaining key technical choices
- [Release Philosophy](./RELEASES.md) - Versioning strategy and release guidelines

## Repository Structure

```
human-in-loop/
├── .claude-plugin/
│   └── marketplace.json           # Marketplace manifest
├── plugins/
│   ├── humaninloop/               # Main workflow plugin
│   │   ├── agents/                # 5 specialized workflow agents
│   │   ├── commands/              # setup, specify, plan, tasks, audit, implement
│   │   ├── skills/                # 13 model-invoked skills
│   │   ├── scripts/               # Shell utilities
│   │   └── templates/             # Workflow templates
├── specs/                         # Feature specifications
│   ├── completed/                 # Shipped features
│   ├── in-progress/               # Currently implementing
│   └── planned/                   # Future features
├── docs/
│   ├── decisions/                 # Architecture Decision Records
│   └── claude-plugin-documentation.md
├── CHANGELOG.md                   # Release history
├── ROADMAP.md                     # Vision and planned features
├── RELEASES.md                    # Release philosophy
├── CONTRIBUTING.md
└── LICENSE
```

## License

MIT - See [LICENSE](./LICENSE)
