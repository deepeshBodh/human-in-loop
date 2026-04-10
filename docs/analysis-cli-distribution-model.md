# Analysis: CLI-Based Distribution Model

**Date**: 2026-04-09
**Status**: Decision made
**Scope**: Fundamental shift from plugin-based to CLI-based distribution

## Problem Statement

The current plugin marketplace model constrains humaninloop's evolution. Plugins are limited to what Claude Code's plugin system exposes (commands, agents, skills). Future capabilities — local servers, git hooks, shell configuration, background processes — require a distribution surface with more flexibility. The plugin model also couples distribution tightly to Claude Code's plugin conventions.

## Decision

Replace the plugin marketplace model with a CLI-based distribution model using `uvx humaninloop` as the single entry point.

## Key Decisions

| # | Decision | Confidence |
|---|----------|------------|
| 1 | CLI via `uvx humaninloop init` — one-shot scaffold, no global install required | Confident |
| 2 | Two install scopes: local (`.claude/` in repo) and global (`~/.claude/`) | Confident |
| 3 | `humaninloop` is a new PyPI package (the CLI); `humaninloop-brain` stays a separate library dependency | Confident |
| 4 | Full install — all agents, skills, commands, templates in one shot. No selective/interactive install. | Confident |
| 5 | Explicit `uvx humaninloop update` command for updates, separate from `init` | Confident |
| 6 | Plugin marketplace is fully replaced — CLI is the only distribution path | Confident |
| 7 | `init` auto-wires MCP server config into `.mcp.json` (local) or Claude Code global settings (global) | Confident |
| 8 | MCP server runs via `uvx humaninloop server` — no persistent installation; uv cache handles runtime | Confident |
| 9 | Content bundled as package data inside `humaninloop/scaffolds/` — agents, skills, commands, templates | Confident |

## Architecture

### Package Structure

```
humaninloop/                  # New PyPI package — the CLI
  __init__.py
  cli/
    init.py                   # Scaffold command
    update.py                 # Update command
    server.py                 # MCP server command
  scaffolds/
    agents/                   # Agent .md files
    skills/                   # Skill .md + reference files
    commands/                 # Command scripts
    templates/                # Workflow templates
```

`humaninloop-brain` remains a separate package — the DAG engine. The CLI depends on it.

### User Experience

**First-time setup (local):**
```bash
cd my-project
uvx humaninloop init
```
Scaffolds into `.claude/` and writes `.mcp.json` with server config.

**First-time setup (global):**
```bash
uvx humaninloop init --global
```
Scaffolds into `~/.claude/` and writes MCP config to Claude Code's global settings.

**Updates:**
```bash
uvx humaninloop update          # local
uvx humaninloop update --global # global
```

### MCP Server Wiring

`init` writes the following into `.mcp.json`:

```json
{
  "mcpServers": {
    "hil-dag": {
      "command": "uvx",
      "args": ["humaninloop", "server"]
    }
  }
}
```

Claude Code auto-starts the server on demand. `uvx` handles caching and fetching. Version pinning via `humaninloop==X.Y.Z` in args enables reproducibility; `update` bumps the pin.

### Relationship Between Packages

```
User runs: uvx humaninloop init
                |
                v
        humaninloop (CLI)          <-- PyPI package, user-facing
          - cli/ (init, update, server)
          - scaffolds/ (agents, skills, commands, templates)
          - depends on: humaninloop-brain
                |
                v
        humaninloop-brain          <-- PyPI package, library
          - entities, graph, validators, passes, mcp, cli
          - deterministic DAG infrastructure
```

`humaninloop` is the product. `humaninloop-brain` is the engine.

## Migration Path

1. Create new `humaninloop` Python package with CLI entry point
2. Move agent/skill/command/template content from `plugins/humaninloop/` into `humaninloop/scaffolds/`
3. Implement `init` command — scaffold to `.claude/` or `~/.claude/`, write `.mcp.json`
4. Implement `update` command — detect existing install, update changed files, warn on user modifications
5. Implement `server` command — wrap existing `hil-dag` MCP server
6. Publish `humaninloop` to PyPI
7. Retire `plugins/` directory and marketplace manifests

## What Dies

- `plugins/humaninloop/` directory structure
- `.claude-plugin/plugin.json` manifest
- `.claude-plugin/marketplace.json`
- Plugin marketplace as a distribution concept
- Any Claude Code plugin-specific conventions (plugin resolution, marketplace install flow)

## What Survives

- All agent `.md` files (move to `scaffolds/agents/`)
- All skill `.md` + reference files (move to `scaffolds/skills/`)
- All command scripts (move to `scaffolds/commands/`)
- All templates (move to `scaffolds/templates/`)
- `humaninloop_brain` package — unchanged
- DAG-first architecture — unchanged
- Constitution and governance — unchanged

## Open Questions

- Version pinning strategy: pin exact version in `.mcp.json` args, or let `uvx` resolve latest?
- `update` conflict resolution: what happens when a user has modified a scaffolded file? Warn? Skip? Backup?
- Global install: which Claude Code settings file gets the MCP config — `settings.json` or `settings.local.json`?
- Future subcommands: `hooks`, `doctor`, `status` — scope TBD

## Next Steps

1. Create `humaninloop` package skeleton with `cli/` and `scaffolds/` structure
2. Implement `init` command as first deliverable
3. Migrate content from `plugins/humaninloop/` into `scaffolds/`
4. Publish to PyPI and validate `uvx humaninloop init` end-to-end
