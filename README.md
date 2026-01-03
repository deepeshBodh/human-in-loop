# HumanInLoop Claude Code Plugin Marketplace

Official Claude Code plugin marketplace for [HumanInLoop](https://humaninloop.dev).

## Quick Start

### Add the Marketplace

```bash
/plugin marketplace add deepeshBodh/human-in-loop-marketplace
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
| [humaninloop-experiments](./plugins/humaninloop-experiments) | Experimental sandbox for new agent patterns | `/humaninloop-experiments:specify` |

### humaninloop

Multi-agent specification-driven development workflow with integrated quality validation and project constitution management.

**Agents:** 11 specialized agents for constitution setup, spec writing, validation, planning, and task generation
**Commands:** `/humaninloop:setup`, `/humaninloop:specify`, `/humaninloop:plan`, `/humaninloop:tasks`, `/humaninloop:audit`, `/humaninloop:implement`
**Skills:** 7 model-invoked skills for authoring and analysis

#### Skills

| Skill | Trigger Phrases | Description |
|-------|-----------------|-------------|
| `iterative-analysis` | "brainstorm", "deep analysis", "let's think through" | Progressive questioning with 2-3 options per question and synthesis |
| `authoring-requirements` | "functional requirements", "FR-", "RFC 2119", "MUST SHOULD MAY" | Write FR-XXX format requirements with validation |
| `authoring-user-stories` | "user story", "Given When Then", "P1", "P2", "P3" | Write prioritized user stories with acceptance scenarios |
| `authoring-constitution` | "constitution", "principles", "governance" | Write enforceable project constitution with three-part principles |
| `analyzing-project-context` | "project context", "tech stack detection" | Infer project characteristics from codebase |
| `syncing-claude-md` | "sync CLAUDE.md", "constitution sync" | Synchronize CLAUDE.md with constitution sections |

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
human-in-loop-marketplace/
├── .claude-plugin/
│   └── marketplace.json           # Marketplace manifest
├── plugins/
│   ├── humaninloop/               # Main workflow plugin
│   │   ├── agents/                # 11 multi-agent workflow agents
│   │   ├── commands/              # setup, specify, plan, tasks, analyze, checklist, implement
│   │   ├── skills/                # 7 model-invoked authoring skills
│   │   ├── check-modules/         # Validation check modules
│   │   ├── scripts/               # Shell utilities
│   │   └── templates/             # Workflow templates
│   └── humaninloop-experiments/   # Experimental sandbox plugin
│       ├── agents/
│       ├── commands/
│       └── skills/
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
