# Contributing to HumanInLoop Marketplace

Thank you for your interest in contributing a plugin to the HumanInLoop marketplace!

## Submitting a Plugin

### 1. Create Your Plugin

Copy an existing plugin as a starting point:

```bash
# For simpler plugins (commands only)
cp -r plugins/humaninloop-experiments plugins/your-plugin-name

# For complex multi-agent plugins
cp -r plugins/humaninloop plugins/your-plugin-name
```

Then update the values in your copied plugin.

### 2. Required Files

Your plugin must include:

```
your-plugin-name/
├── .claude-plugin/
│   └── plugin.json      # REQUIRED: Plugin manifest
├── commands/            # Slash commands (optional)
│   └── *.md
├── agents/              # Subagents (optional)
│   └── *.md
├── check-modules/       # Validation check modules (optional)
│   └── *.md
├── scripts/             # Shell scripts (optional)
│   └── *.sh
├── templates/           # Workflow templates (optional)
│   └── *.md
├── skills/              # Agent skills (optional)
│   └── skill-name/
│       └── SKILL.md
├── hooks/               # Hooks (optional)
│   └── hooks.json
├── README.md            # REQUIRED: Plugin documentation
└── LICENSE              # RECOMMENDED: License file
```

### 3. Plugin Manifest (`plugin.json`)

```json
{
  "name": "your-plugin-name",
  "version": "1.0.0",
  "description": "Brief description of what your plugin does",
  "author": {
    "name": "Your Name",
    "url": "https://yoursite.com"
  },
  "license": "MIT",
  "keywords": ["relevant", "keywords"],
  "commands": "./commands/",
  "agents": "./agents/",
  "checkModules": "./check-modules/"
}
```

Note: Only include `commands`, `agents`, and `checkModules` fields if your plugin uses them.

### 4. Submit a Pull Request

1. Fork this repository
2. Add your plugin to the `plugins/` directory
3. Add an entry to `.claude-plugin/marketplace.json`:

```json
{
  "name": "your-plugin-name",
  "description": "Brief description",
  "source": "./plugins/your-plugin-name",
  "category": "category-name",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}
```

4. Submit a pull request

## Plugin Guidelines

### Naming

- Use kebab-case: `my-plugin-name`
- Be descriptive but concise
- Avoid generic names like `utils` or `helpers`

### Categories

Use one of these categories:
- `workflow` - Multi-step development workflows
- `development` - Dev tools, linting, formatting
- `productivity` - Workflow automation
- `documentation` - Doc generation, READMEs
- `testing` - Test runners, coverage
- `deployment` - CI/CD, deployment helpers
- `configuration` - Project setup and configuration
- `examples` - Example/demo plugins

### Quality Checklist

- [ ] Plugin has a clear, single purpose
- [ ] README explains what the plugin does and how to use it
- [ ] All commands have descriptions in frontmatter
- [ ] No hardcoded paths (use `${CLAUDE_PLUGIN_ROOT}`)
- [ ] Scripts are executable (`chmod +x`)
- [ ] License file included

## Commit Conventions

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `chore` | Maintenance tasks |

### Scope

Use the plugin name as scope when applicable:
- `feat(humaninloop): add /tasks command`
- `fix(constitution): correct agent reference`
- `docs: update README`

## Contributing to Core Plugins

For contributions to the `humaninloop` or `humaninloop-experiments` plugins:

### Feature Contributions

1. **Open an issue** describing the proposed feature
2. **Discuss** the approach before implementing
3. **Create a spec** using `/humaninloop:specify` if the feature is significant
4. **Submit PR** referencing the issue and spec

### Bug Fixes

1. **Open an issue** describing the bug (unless trivial)
2. **Submit PR** with fix, referencing the issue
3. **Include test case** if applicable

## Documentation

- [docs/claude-plugin-documentation.md](./docs/claude-plugin-documentation.md) - Claude Code plugin technical reference
- [docs/decisions/](./docs/decisions/) - Architecture Decision Records
- [CHANGELOG.md](./CHANGELOG.md) - Release history
- [ROADMAP.md](./ROADMAP.md) - Planned features

## Questions?

Open an issue if you have questions about contributing.
