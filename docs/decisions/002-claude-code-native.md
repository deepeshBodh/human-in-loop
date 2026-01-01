# ADR-002: Claude Code Native Integration

**Status:** Accepted
**Date:** 2026-01-01

## Context

Specification-driven development tools can be built as:
1. Standalone CLIs that work with any AI coding assistant
2. Native integrations for a specific tool
3. Hybrid approaches with adapters for multiple tools

We need to decide the integration strategy for humaninloop plugins.

## Decision

Build **Claude Code native plugins** using the official plugin system (slash commands, agents, hooks, MCP).

We do not build:
- Standalone CLI tools
- Generic integrations for other AI assistants
- Abstraction layers to support multiple tools

## Rationale

### Benefits of Claude Code native

1. **Deep integration** - Access to Claude Code's full plugin API: commands, agents, check modules, hooks, templates. No impedance mismatch.

2. **Natural workflow** - Users stay in Claude Code. No context switching to external tools, no copy-paste between systems.

3. **Leverages Claude capabilities** - Agents can use Claude's reasoning, code understanding, and multi-turn conversation directly.

4. **Simpler maintenance** - One integration to maintain, not N adapters for N tools.

5. **First-class experience** - Native integrations can provide better UX than generic abstractions.

### Alternatives considered

**Tool-agnostic CLI:** Build a standalone `hil` CLI that works with any AI assistant.
- Rejected because: Creates friction (switching contexts), loses access to Claude Code's agent system, requires maintaining external tooling.

**Multi-tool adapters:** Build core logic with adapters for Claude Code, Cursor, Copilot, etc.
- Rejected because: Lowest common denominator problem—features limited to what all tools support. Maintenance burden multiplies with each tool. Better to excel at one integration than be mediocre at many.

**MCP-only approach:** Use only Model Context Protocol, avoiding Claude Code plugin API.
- Partially adopted: MCP is used where appropriate (e.g., external services), but slash commands and agents provide better UX for core workflows.

## Consequences

- **Positive:** Best possible Claude Code experience, simpler codebase, faster iteration
- **Negative:** Users of other AI tools cannot use these plugins directly
- **Neutral:** Clear positioning as a Claude Code solution

## Related

- [Claude Code Plugin Documentation](../claude-plugin-documentation.md)
