# State Analyst / DAG Assembler Merge Analysis Synthesis

## Problem Statement

The State Analyst and DAG Assembler agents have tight coupling — the State Analyst produces recommendations with capability tags that the DAG Assembler mechanically resolves — and both parse the same files (DAG JSON, catalog, artifact paths). Investigation revealed the DAG Assembler adds zero intelligence: tag resolution is a set intersection, edge inference is contract-driven rules, prompt construction is templates. The real question shifted from "should we merge two agents" to "should the State Analyst absorb the Assembler's mechanical MCP tool calls."

## Context & Constraints

- **Flat subagent hierarchy**: Claude Code subagents cannot spawn other subagents. Both agents are called by the Supervisor (main thread). Merging doesn't change the hierarchy — it reduces distinct agents from 2 to 1.
- **MCP tools do the real work**: Graph mutations, validation, edge inference, and invariant checking all live in `humaninloop_brain` via `hil-dag` MCP tools. The Assembler agent is a thin caller of these tools.
- **7 nodes per catalog, ~24 unique capability tags**: Within a single workflow, capability tag resolution is deterministic 1:1. No ambiguous resolutions exist.
- **Strategy skills encode heuristics explicitly**: Recommendation ranking logic is in `strategy-core`, `strategy-specification`, and `strategy-implementation` — not emergent from opus reasoning.

## Key Decisions

| Decision | Choice | Confidence | Rationale |
|----------|--------|------------|-----------|
| Merge direction | Absorb DAG Assembler into State Analyst (not a new combined agent) | Confident | State Analyst already reads the same files; Assembler adds no intelligence beyond MCP tool calls |
| Model | opus for the absorbed agent | Confident | No compromise on reasoning quality; cost increase accepted |
| Agent name | Keep "State Analyst" | Confident | Name is established across agents and documentation; no churn |
| Action combining | Combined actions in single calls (brief+assemble, parse+record+freeze) | Confident | Reduces Supervisor round-trips from 6 to 2 per node execution |
| Recommendation selection | Auto-select top recommendation with visible override | Confident | Strategy skills encode ranking heuristics; Supervisor sees alternatives and rationale but only intervenes on exceptions |

## Decision Trail

### Auto-select vs Supervisor-picks recommendations

- **Options considered**: (A) Supervisor always picks from ranked list, (B) State Analyst auto-selects top recommendation, Supervisor overrides if needed, (C) Fully autonomous — no visibility into alternatives
- **Recommendation was**: B — auto-select with visible override
- **Chosen**: B
- **Key reasoning**: Strategy skills already encode ranking heuristics. If ranking is consistently wrong, fix the skills — don't add a mandatory review step. The override escape valve preserves control without adding friction to the happy path.

## Risks

- **Prompt bloat**: Combined agent prompt will be ~800+ lines. May need pruning of duplicated sections (artifact path conventions appear in both agents today) to keep it manageable.
- **Debugging isolation lost**: With two agents, a bad recommendation vs a bad assembly was immediately attributable. Single agent loses that signal. Mitigation: structured logging in the MCP tool calls still attributes graph mutations vs reasoning errors.

## Open Questions

- What is the new action vocabulary for the absorbed State Analyst? Current actions are `briefing` and `parse-and-recommend` (State Analyst) plus `assemble-and-prepare`, `freeze-pass`, and `update-status` (DAG Assembler). These need to be re-designed as combined actions.
- How much of the DAG Assembler's NL Prompt Construction Patterns section can be simplified when it lives alongside the recommendation logic?
- Should the Supervisor skill prompts be updated simultaneously, or can the State Analyst agent be updated independently?

## Recommended Next Steps

1. **Design the new action vocabulary**: Define 2-3 combined actions (e.g., `brief-and-assemble`, `parse-and-advance`) with input/output contracts that replace the current 5 separate actions across both agents.
2. **Deduplicate the prompt**: Merge both agent prompts, eliminate the duplicated Artifact Path Convention table, Tool Usage sections, and Error Protocol sections. Target under 600 lines.
3. **Update MCP tool permissions**: The State Analyst currently only uses `record`. Add `assemble`, `freeze`, `status`, `validate`, `sort`, `catalog_validate` to its `mcpServers` access.
4. **Update Supervisor workflow skills**: Revise `strategy-core`, `strategy-specification`, and `strategy-implementation` to reflect the 2-call happy path (brief+assemble → domain agent → parse+record+freeze) instead of the current 6-step orchestration.
5. **Delete the DAG Assembler agent**: Remove `plugins/humaninloop/agents/dag-assembler.md` and its registration in the plugin manifest after the State Analyst absorbs all functionality.
