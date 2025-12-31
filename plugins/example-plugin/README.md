# Example Plugin

A comprehensive example plugin demonstrating Claude Code plugin capabilities including commands, shell scripts, and markdown templates.

## Installation

```bash
# First, add the HumanInLoop marketplace (if not already added)
/plugin marketplace add deepeshBodh/human-in-loop-marketplace

# Install this plugin
/plugin install example-plugin
```

## Commands

### `/example-plugin:hello [name]`

Displays a greeting message. Optionally include a name to personalize the greeting.

**Examples:**
- `/example-plugin:hello` - Generic greeting
- `/example-plugin:hello World` - Greets "World"

### `/example-plugin:run-script [command] [args...]`

Executes the sample shell script to demonstrate script integration.

**Available commands:**
- `greet [name]` - Display a greeting
- `info` - Show plugin information
- `list-files` - List plugin files
- `help` - Show script help

**Examples:**
- `/example-plugin:run-script greet Alice` - Greets Alice
- `/example-plugin:run-script info` - Shows plugin info

### `/example-plugin:generate-readme [project-name]`

Generates a README.md file using the plugin's template. Interactively collects project details and fills in the template placeholders.

**Examples:**
- `/example-plugin:generate-readme my-project` - Generate README for "my-project"
- `/example-plugin:generate-readme` - Prompts for project name

## Plugin Structure

```
example-plugin/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── commands/
│   ├── hello.md              # Basic greeting command
│   ├── run-script.md         # Script execution command
│   └── generate-readme.md    # Template-based README generator
├── scripts/
│   └── sample.sh             # Example shell script
├── templates/
│   └── readme-template.md    # README template with placeholders
├── README.md                 # This file
└── LICENSE                   # MIT license
```

## Artifacts

### Shell Script (`scripts/sample.sh`)

Demonstrates:
- Proper shebang and bash best practices
- Command-line argument parsing
- Colored terminal output
- `${CLAUDE_PLUGIN_ROOT}` environment variable usage

### Markdown Template (`templates/readme-template.md`)

Demonstrates:
- Placeholder pattern (`{{PLACEHOLDER_NAME}}`)
- Common README sections
- Template-based documentation generation

## Using as a Template

Copy this plugin to create your own:

1. Copy the entire `example-plugin/` directory
2. Rename to your plugin name
3. Update `plugin.json` with your plugin's details
4. Modify or add commands in `commands/`
5. Add your scripts to `scripts/`
6. Add your templates to `templates/`
7. Update this README

## License

MIT
