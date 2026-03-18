# Synthesis: Convert humaninloop_brain to MCP Server

**Date**: 2026-03-17
**Participants**: User, Claude
**Depth**: 9 questions, focused exploration

---

## Problem Statement

The current `hil-dag` CLI + 7 shell scripts interface between agents (state analyst, dag assembler) and `humaninloop_brain` creates friction:

- Shell script boilerplate (PATH resolution, `uv run` fallback, argument parsing) across 7 scripts
- CLI stdout JSON parsing is fragile compared to structured MCP tool responses
- The architecture is local-only today but should not preclude remote use later

## Key Decisions

### 1. MCP server replaces CLI entirely
**Confidence**: Confident

`hil-dag` becomes an MCP server binary — no CLI subcommands, no `serve` flag. The binary *is* the MCP server. It speaks MCP over stdio.

Previous: `hil-dag` was a CLI with 7 subcommands (`assemble`, `validate`, `status`, `record`, `freeze`, `sort`, `catalog-validate`).

### 2. Stateless — JSON file remains source of truth
**Confidence**: Confident

Each MCP tool call reads the StrategyGraph JSON, performs one operation, writes it back. No in-memory state across calls. Stateful server is a long-term goal, not in scope.

### 3. 1:1 tool mapping from CLI subcommands
**Confidence**: Confident

Seven MCP tools, matching the current CLI surface:

| CLI Subcommand | MCP Tool |
|---------------|----------|
| `assemble` | `assemble` |
| `validate` | `validate` |
| `status` | `status` |
| `record` | `record` |
| `freeze` | `freeze` |
| `sort` | `sort` |
| `catalog-validate` | `catalog_validate` |

No reshaping or combining of tools in the initial migration. Optimization (e.g., merging `status` and `record`) can be explored after migration.

### 4. Code lives inside `humaninloop_brain/`
**Confidence**: Confident

Add an `mcp/` module alongside the existing `cli/` module. Same package, same `pyproject.toml`, same `uv tool install`. The MCP server imports the same internal functions.

### 5. Shell scripts and dag-operations skill are deleted
**Confidence**: Confident

The 7 dag-operations shell scripts, the dag-operations SKILL.md, and the shell-based prerequisite check all go away. Agents call MCP tools directly.

### 6. stdio transport, user configures in settings.json
**Confidence**: Confident

Claude Code spawns the MCP server process. User configuration:

```json
{
  "mcpServers": {
    "hil-dag": {
      "command": "hil-dag"
    }
  }
}
```

Install remains: `uv tool install "humaninloop-brain @ git+https://github.com/deepeshBodh/human-in-loop.git#subdirectory=humaninloop_brain"`

### 7. Prerequisite check verifies MCP server is reachable
**Confidence**: Confident

Replace `command -v hil-dag` / `uv run` PATH checks with an MCP reachability check. The user must install and configure the MCP server locally — the check confirms it's available before workflows start.

### 8. Agents pass explicit full paths
**Confidence**: Confident

The MCP server does not resolve paths internally. Agents pass full `dag-path`, `catalog-path`, etc. as tool parameters. Path derivation (feature directory, branch conventions) stays in the orchestration layer (plugin scripts/agents), not the DAG engine.

**Why**: Keeps the server decoupled from plugin directory structure and workflow conventions. The server is a pure DAG engine.

## What Gets Deleted

- `plugins/humaninloop/skills/dag-operations/` (SKILL.md + 7 scripts)
- `plugins/humaninloop/scripts/check-prerequisites.sh` `--require-hil-dag` PATH check logic
- `humaninloop_brain/src/humaninloop_brain/cli/` (replaced by `mcp/`)
- `hil-dag` CLI entry point (replaced by MCP server entry point, same binary name)

## What Gets Added

- `humaninloop_brain/src/humaninloop_brain/mcp/` — MCP server module with 7 tools
- MCP server entry point in `pyproject.toml` (reusing `hil-dag` binary name)
- Updated agent prompts (dag-assembler, state-analyst) referencing MCP tools instead of shell scripts
- MCP reachability check replacing PATH-based prerequisite check
- Updated install/setup docs showing MCP server configuration

## What Stays the Same

- `humaninloop_brain/src/humaninloop_brain/entities/` — unchanged
- `humaninloop_brain/src/humaninloop_brain/graph/` — unchanged
- `humaninloop_brain/src/humaninloop_brain/validators/` — unchanged
- `humaninloop_brain/src/humaninloop_brain/passes/` — unchanged
- StrategyGraph JSON file format — unchanged
- Node catalogs — unchanged
- Layer dependency rule — unchanged
- All 381+ existing tests — unchanged (test the internals, not the transport)

## Architecture

```
Before:
  Agent → shell script → hil-dag CLI → humaninloop_brain internals → JSON file

After:
  Agent → MCP tool call → hil-dag MCP server → humaninloop_brain internals → JSON file
```

## Risks

- **Test coverage for MCP layer**: The existing 381+ tests cover internals. New tests needed for MCP tool parameter validation and response formatting.
- **MCP SDK dependency**: Adds a new dependency (`mcp` Python SDK) to `humaninloop_brain`. Need to evaluate maturity and compatibility.
- **Agent prompt updates**: dag-assembler and state-analyst prompts reference shell scripts today. Must be updated to reference MCP tools — risk of missed references.

## Next Steps

1. Spec this feature using `/humaninloop:specify`
2. Plan the migration with `/humaninloop:plan`
3. Generate tasks with `/humaninloop:tasks`
4. Implement incrementally — MCP server first, then agent migration, then cleanup
