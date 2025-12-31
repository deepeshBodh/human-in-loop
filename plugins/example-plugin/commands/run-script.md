---
description: Run the sample shell script with various commands
allowed-tools: Bash, Read
argument-hint: [command] [args...]
---

# Run Script Command

Execute the sample.sh shell script from this plugin to demonstrate shell script integration.

## Available Script Commands

- `greet [name]` - Display a greeting message
- `info` - Show plugin information
- `list-files` - List plugin files
- `help` - Show script help

## Instructions

1. The script is located at `${CLAUDE_PLUGIN_ROOT}/scripts/sample.sh`
2. Run it using the Bash tool with the command/args provided by the user

If `$1` is provided, use it as the script command. Additional arguments (`$2`, `$3`, etc.) should be passed along.

**Examples:**
- `/example-plugin:run-script greet Alice` runs `sample.sh greet Alice`
- `/example-plugin:run-script info` runs `sample.sh info`
- `/example-plugin:run-script` (no args) runs `sample.sh help`

Execute the script and display its output to the user.
