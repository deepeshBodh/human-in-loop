---
description: Generate a README.md file using the plugin's template
allowed-tools: Read, Write, AskUserQuestion
argument-hint: [project-name]
---

# Generate README Command

Generate a README.md file for a project using the readme-template.md from this plugin.

## Instructions

1. Read the template from `${CLAUDE_PLUGIN_ROOT}/templates/readme-template.md`

2. If `$1` (project name) is not provided, ask the user for:
   - Project name
   - Brief description

3. Ask the user for key details to fill in the template:
   - Main features (2-3 bullet points)
   - Installation command
   - Basic usage example
   - License type (default: MIT)

4. Replace the placeholders in the template:
   - `{{PROJECT_NAME}}` - Project name
   - `{{PROJECT_DESCRIPTION}}` - Description
   - `{{INSTALL_COMMAND}}` - Installation command
   - `{{USAGE_EXAMPLE}}` - Usage example
   - `{{FEATURE_1}}`, `{{FEATURE_2}}`, `{{FEATURE_3}}` - Features
   - `{{LICENSE_TYPE}}` - License
   - Other placeholders can use sensible defaults or be removed

5. Show the generated README to the user and ask where to save it (default: `./README.md` in current directory)

6. Write the file to the specified location

This demonstrates how markdown templates can be used within Claude Code plugins to generate documentation.
