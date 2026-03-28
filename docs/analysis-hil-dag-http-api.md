# hil-dag HTTP API Layer — Analysis Synthesis

## Problem Statement

The `hil-dag` MCP server works well for Claude Code agent workflows over stdio, but two problems exist: (1) every MCP tool call triggers a permission prompt, causing approval fatigue during workflow execution, and (2) there's no way for a web UI to consume DAG data — needed for a planned kanban board and DAG graph visualizer.

## Context & Constraints

- **0-to-1 mindset**: MVP scope only — get something rendering, iterate from there
- **Read-only web UI first**: Claude Code agents remain the sole writers; web UI is a consumer
- **Existing transport-agnostic layer**: `operations.py` (573 lines, 7 `op_*()` functions) already separates business logic from transport
- **DAG JSON as data store**: No database — the JSON files in `specs/<feature>/.workflow/dags/` are the source of truth

## Key Decisions

| Decision | Choice | Confidence | Rationale |
|----------|--------|------------|-----------|
| Architecture | Layered: shared `operations.py` with MCP + HTTP wrappers | Confident | Reuses existing transport-agnostic logic; avoids forcing web UI to speak MCP protocol |
| HTTP framework | FastAPI | Confident | Already Python; auto-generated OpenAPI docs; slots next to existing `server.py` |
| Web UI interaction model | Read-only first | Confident | Keeps write authority with Claude Code agents; avoids concurrent access complexity |
| Data persistence | DAG JSON files on disk (no database) | Confident | No sync problem; JSON files are the source of truth; add persistence later only if needed |
| MVP API surface | Two endpoints: `GET /dags` and `GET /dags/{feature}/{dag_name}` | Confident | Minimum viable for kanban + graph rendering |
| Live updates | Skip for v1 (polling acceptable) | Confident | WebSocket adds complexity; polling is fine for local read-only dashboard |
| Frontend technology | Deferred | Deferred | API-first approach — any frontend can consume; decide later |
| Auth | Skip for v1 | Confident | Local-only server; no external exposure |
| Permission fatigue fix | Allowlist 7 MCP tools in Claude Code settings | Confident | Immediate fix, independent of API work |

## Decision Trail

### MCP-over-HTTP vs Layered approach
- **Options considered**: (A) File-watching web server, (B) Upgrade hil-dag to HTTP MCP transport with web UI as MCP client, (C) Separate FastAPI server reading same files
- **User leaned toward**: B (HTTP MCP server — single server appeal)
- **Chosen**: Hybrid of B and C — layered approach with shared operations layer
- **Key reasoning**: MCP protocol is designed for AI agent tool invocations, not frontend data fetching. A web UI needs REST endpoints shaped for rendering (lists, filtering, projections), not `tool_call("assemble", {...})`. The operations layer is the real shared asset — wrap it twice, each wrapper shaped for its consumer.

## Open Questions

- How does the API discover active DAGs? (Filesystem scan of `specs/*/` vs a registry file)
- Will the API run as a standalone process or be embedded in a larger dev tooling server?
- When read-only becomes limiting, what write operations does the web UI need first?

## Recommended Next Steps

1. **Fix permission fatigue now**: Add the 7 `mcp__hil-dag__*` tools to the Claude Code settings allowlist — immediate quality-of-life improvement, zero architecture work
2. **Create `api.py` alongside `server.py`**: FastAPI app with two endpoints (`GET /dags`, `GET /dags/{feature}/{dag_name}`) that reads DAG JSON from disk using the existing operations layer
3. **Add `hil-api` script entry point**: In `pyproject.toml`, add `hil-api = "humaninloop_brain.mcp.api:main"` so it launches with `uvicorn`
4. **Validate with a throwaway frontend**: Use the auto-generated Swagger UI at `/docs` to verify the API returns what a kanban board and graph renderer would need — before writing any frontend code
