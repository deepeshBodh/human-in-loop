# DAG Specialist Subagents — Analysis Synthesis

## Problem Statement

The DAG-first execution architecture requires two new specialist subagents — State Briefer and DAG Assembler — that handle graph mechanics while preserving the Supervisor's context for assembly decisions. A critical platform constraint shapes the design: Claude Code subagents cannot spawn other subagents. Only the main conversation thread (the Supervisor) can use the Task tool. This means all agent spawning must be orchestrated by the Supervisor, and the communication architecture must work within a flat (non-nested) agent hierarchy.

## Context & Constraints

- **No nested subagents**: Claude Code enforces single-level agent hierarchy. Subagents cannot spawn other subagents. Only the main thread can use the Task tool. This is a deliberate platform design to prevent infinite recursion and maintain execution clarity.
- **Supervisor context preservation**: The Supervisor's context is its most precious resource. Raw artifacts (spec.md, advocate-report.md, full prose reports) must never enter the Supervisor's context. All heavy content is handled by subagents or on disk.
- **ADR-005 compatibility**: Domain agents are unchanged. They receive natural language prompts, write artifacts to disk, and return prose reports. The DAG architecture wraps around them.
- **File system as communication channel**: Domain agents write reports to disk (existing pattern). The DAG Assembler reads reports from disk. The Supervisor never handles full report content.
- **Supervisor awareness level**: The Supervisor is node-aware (knows node IDs from briefings) but edge-unaware (doesn't know about edge types, graph wiring, invariant mechanics). The DAG Assembler handles all graph structure.

## Key Decisions

| Decision | Choice | Confidence | Rationale |
|----------|--------|------------|-----------|
| DAG Assembler scope | Single agent handling all 5 responsibilities (node addition, edge inference, invariant validation, NL prompt construction, report parsing). Can split later. | Confident | Splitting creates more round-trips. Responsibilities are tightly coupled — you build the node AND construct its prompt in the same step. Start simple, split if earned. |
| Subagent nesting workaround | Supervisor orchestrates all agent spawning. File system is the communication channel between domain agents and DAG Assembler. | Confident | Platform constraint — no alternative. But file-based communication is already the ADR-005 pattern, so it's natural. |
| Supervisor context protection | Domain agents return brief status to Supervisor ("completed successfully"), write full reports to disk. DAG Assembler reads full reports from disk, returns structured summaries. | Confident | Full prose reports never enter Supervisor context. The Supervisor sees only compact structured data at every step. |
| Edge inference | DAG Assembler infers edges from node contracts (consumes/produces matching). Supervisor specifies only node ID + parameters, never edges. | Confident | Keeps graph mechanics out of the Supervisor's concerns. The catalog contracts have enough information to infer edges. The DAG Assembler tells the domain agent where to write (from contract), then reads from the same path. |
| Artifact path resolution | DAG Assembler infers paths from node contracts + feature directory convention. Domain agents don't return paths. | Confident | Single source of truth — the contract. The DAG Assembler tells the agent where to write in the NL prompt, then reads from the same location. No path coordination needed. |
| Error handling | All errors escalate to Supervisor with structured information. DAG Assembler never silently recovers. Three failure modes with defined handlers. | Confident | The Supervisor has the judgment to decide retry/skip/halt. The DAG Assembler has the mechanics to detect and report problems. |
| Agent definition format | Role-defined, not persona-defined. Sections: Role, Actions (with inputs/outputs), Operational Rules, Error Protocol. No persona, values, or identity sections. | Confident | DAG-ops agents need operational precision, not creative judgment. Their definitions are reference documents for consistent mechanical behavior. |

## Decision Trail

### DAG Assembler scope: One agent vs. split

- **Options considered**: Split translation work (NL prompt construction, report parsing) from graph work (node addition, invariant validation). Two agents with different responsibilities.
- **Chosen**: Single agent, split later if needed
- **Key reasoning**: "Lets keep it as 1 for now, can breakup later." Splitting adds round-trips. Build-node and construct-prompt are tightly coupled — you need the contract to do both. Pragmatic start.

### Supervisor awareness: Fully graph-aware vs. node-aware vs. purely strategic

- **Options considered**: (A) Supervisor speaks purely strategic intent ("research the auth gaps"). (B) Supervisor picks node IDs but DAG Assembler handles edges. (C) Supervisor specifies nodes AND edges.
- **Chosen**: Option B — node-aware, edge-unaware
- **Key reasoning**: The State Briefer already presents viable node IDs. The Supervisor naturally reasons about them. But edges are mechanical — inferrable from contracts. Keeping edge types out of the Supervisor saves context and keeps its decisions at the level of "what should happen" not "how it maps to graph structure."

### Report flow: Through Supervisor vs. file-based

- **Original proposal**: Domain agent reports to Supervisor, Supervisor passes to DAG Assembler for parsing.
- **Concern raised**: "If supervisor starts to access source artifacts, it will fill up context window"
- **User asked**: "Is subagent capable of calling another subagent?"
- **Discovery**: No — Claude Code subagents cannot spawn other subagents (platform constraint).
- **Solution**: File-based communication. Domain agents write full reports to disk (existing ADR-005 pattern), return brief status to Supervisor. DAG Assembler reads reports from disk.
- **Key reasoning**: Platform constraint forces flat hierarchy. File system bridges the gap. Full reports never enter Supervisor context. Strengthens the architecture — disk is the communication channel between domain agents and DAG Assembler.

## Complete Per-Node Protocol

```
SUPERVISOR                    STATE BRIEFER         DAG ASSEMBLER         DOMAIN AGENT
    │                              │                     │                     │
    │──── briefing request ───────>│                     │                     │
    │     {workflow, feature_id,   │  reads: history,    │                     │
    │      pass_number, paths}     │  catalog, strategy  │                     │
    │                              │  skills, artifacts  │                     │
    │<─── structured briefing ─────│                     │                     │
    │     (state, viable nodes,    │                     │                     │
    │      gaps, patterns)         │                     │                     │
    │                              │                     │                     │
    │ DECIDES: next node + params  │                     │                     │
    │                              │                     │                     │
    │──── assemble-and-prepare ───────────────────────> │                     │
    │     {next_node, parameters}  │   reads catalog,    │                     │
    │                              │   infers edges,     │                     │
    │                              │   validates,        │                     │
    │                              │   writes DAG JSON,  │                     │
    │                              │   builds NL prompt  │                     │
    │<─── {valid, agent_prompt} ──────────────────────── │                     │
    │                              │                     │                     │
    │──── spawn with NL prompt ──────────────────────────────────────────────>│
    │                              │                     │   writes full       │
    │                              │                     │   report to disk    │
    │<─── brief status ─────────────────────────────────────────────────────│
    │     ("completed, report at                         │   returns only      │
    │      expected path")                               │   brief status      │
    │                              │                     │                     │
    │──── parse-report ───────────────────────────────> │                     │
    │     {node_id}                │   reads report      │                     │
    │                              │   FROM DISK,        │                     │
    │                              │   parses to         │                     │
    │                              │   structured,       │                     │
    │                              │   updates DAG       │                     │
    │                              │   execution trace   │                     │
    │<─── structured summary ─────────────────────────── │                     │
    │                              │                     │                     │
    │ EVALUATES: continue/halt/done│                     │                     │
```

### Call Counts

| Phase | State Briefer | DAG Assembler | Domain Agent | Supervisor Decisions |
|---|---|---|---|---|
| Pass start | 1 | 0 | 0 | 0 |
| Per node | 0 (on-demand) | 2 (assemble + parse) | 1 | 2 (select node + evaluate) |
| Pass end | 0 | 1 (freeze DAG) | 0 | 1 (done/new pass/halt) |

**Typical 3-node pass**: 1 State Briefer + 7 DAG Assembler (6 for nodes + 1 freeze) + 3 domain agents = **11 subagent calls, 7 Supervisor decisions**.

### What Enters Supervisor Context

| Data | In Supervisor Context? | Source |
|---|---|---|
| State Briefer structured briefing | Yes | State Briefer return |
| Node selection + parameters | Yes (Supervisor generates) | Supervisor decision |
| DAG Assembler validation result | Yes | DAG Assembler return |
| NL prompt for domain agent | Yes (brief, passed through) | DAG Assembler return |
| Domain agent full report | **No** | Written to disk |
| Domain agent brief status | Yes (1-2 sentences) | Domain agent return |
| DAG Assembler structured summary | Yes | DAG Assembler return |
| Raw catalog, history, strategy skills | **No** | Read by State Briefer |
| Raw DAG JSON | **No** | Read/written by DAG Assembler |

## State Briefer Specification

### Agent Definition Structure

```markdown
# State Briefer

## Role
Produce decision-ready briefings for the Supervisor by reading and
synthesizing DAG history, node catalog, strategy skills, and current
artifacts. The Supervisor makes assembly decisions from these briefings
alone — the briefing must contain everything needed to decide.

## Input
- Workflow identifier (to select strategy skills)
- Feature ID and pass number (to locate history and artifacts)
- Catalog path (to read node definitions)
- Strategy skill names (to read relevant patterns)
- DAG history path (to read previous pass JSONs)
- Artifacts directory (to check what exists on disk)

## Output
Structured briefing containing:
- state_summary: What happened, where we are
- available_artifacts: What exists on disk with source attribution
- gap_details: Specific gaps with type classification and content
- viable_nodes: Nodes whose contracts are satisfiable, with contracts
- relevant_patterns: Strategy skill patterns applicable to current state
- relevant_anti_patterns: What to avoid in current situation
- pass_context: Pass number, iteration trends, convergence signals

## Operational Rules
- Read strategy skills (core + workflow-specific) fresh each invocation
- Apply progressive summarization to DAG history (recent = full, older = compressed)
- Classify gaps by type (knowledge/preference/scope) from advocate reports
- Filter viable nodes by contract satisfiability against available artifacts
- Include node contracts in viable nodes list (Supervisor needs them for decisions)
- Never recommend — present options and patterns, let Supervisor decide

## Error Protocol
- If catalog file missing → return error with path
- If DAG history corrupted → return partial briefing with warning
- If strategy skill not found → proceed without it, flag in briefing
```

### Request/Response Schema

**Supervisor → State Briefer:**
```json
{
  "request": "briefing",
  "workflow": "specify",
  "feature_id": "001-user-auth",
  "pass_number": 2,
  "catalog_path": "path/to/specify-catalog.json",
  "strategy_skills": ["strategy-core", "strategy-specification"],
  "dag_history_path": "specs/001-user-auth/.workflow/dags/",
  "artifacts_dir": "specs/001-user-auth/"
}
```

**State Briefer → Supervisor:**
```json
{
  "state_summary": "Pass 2. Previous pass assembled: input-enrichment → analyst-review → advocate-review (verdict: needs-revision).",

  "available_artifacts": [
    {"artifact": "spec.md", "source": "analyst-review (pass 1)", "status": "produced"},
    {"artifact": "analyst-report.md", "source": "analyst-review (pass 1)", "status": "produced"},
    {"artifact": "advocate-report.md", "source": "advocate-review (pass 1)", "status": "produced"},
    {"artifact": "enriched-input", "source": "input-enrichment (pass 1)", "status": "produced"},
    {"artifact": "constitution.md", "source": "system", "status": "available"}
  ],

  "gap_details": [
    {"id": "G1", "type": "knowledge", "description": "Unclear what authentication protocols the existing system uses", "severity": "high"},
    {"id": "G2", "type": "knowledge", "description": "Unknown whether LDAP integration is required", "severity": "medium"},
    {"id": "G3", "type": "preference", "description": "Should notifications be opt-in or opt-out by default?", "severity": "low"}
  ],

  "viable_nodes": [
    {
      "id": "targeted-research",
      "type": "task",
      "agent": "exploration",
      "contract": {
        "consumes": ["advocate-report.md"],
        "produces": ["research-findings"]
      },
      "reason": "Can investigate G1 and G2 (knowledge gaps)"
    },
    {
      "id": "human-clarification",
      "type": "decision",
      "contract": {
        "consumes": ["advocate-report.md"],
        "produces": ["clarification-answers"]
      },
      "reason": "Required for G3 (preference gap)"
    },
    {
      "id": "analyst-review",
      "type": "task",
      "agent": "requirements-analyst",
      "contract": {
        "consumes": ["spec.md", "constitution.md", "clarification-answers?", "research-findings?"],
        "produces": ["spec.md", "analyst-report.md"]
      },
      "reason": "Available after gaps resolved"
    }
  ],

  "relevant_patterns": [
    "Knowledge gaps are often resolvable through research without user involvement",
    "Pass 2: skip enrichment, input already established",
    "Inform analyst of specific gaps via informed-by edge"
  ],

  "relevant_anti_patterns": [
    "Don't send preference gaps to research",
    "Don't re-run enrichment after pass 1"
  ],

  "pass_context": "Pass 2 of 5 max. All 3 gaps are new (not recurring from pass 1)."
}
```

## DAG Assembler Specification

### Agent Definition Structure

```markdown
# DAG Assembler

## Role
Build and maintain DAG pass instances. Translate between structured
Supervisor decisions and natural language domain agent communication.
Validate graph integrity against catalog invariants.

## Actions

### assemble-and-prepare
Input: node ID + parameters from Supervisor
Process:
1. Read node contract from catalog
2. Infer edges from contract (match consumes/produces with existing nodes)
3. Add node + edges to current DAG JSON on disk
4. Validate against catalog invariants (acyclicity, endpoint constraints, etc.)
5. Construct NL prompt for domain agent:
   - Include artifact paths (inferred from contract + feature directory)
   - Include Supervisor parameters (focus gaps, context)
   - Follow ADR-005 conventions (point agent at artifacts, minimal instructions)
6. Return to Supervisor: validation result + NL prompt + agent type

Output:
{
  "status": "valid | invalid",
  "violation": "invariant details if invalid",
  "node_added": {"id": "...", "type": "...", "status": "pending"},
  "edges_inferred": 2,
  "agent_prompt": "<constructed NL prompt>",
  "agent_type": "humaninloop:requirements-analyst"
}

### parse-report
Input: node ID from Supervisor
Process:
1. Read node contract from catalog to determine expected artifacts
2. Verify expected artifacts exist on disk
3. Read domain agent report from disk (path from contract + convention)
4. Extract structured summary:
   - Artifacts produced (verified on disk)
   - Key findings / counts
   - Verdict (for gate nodes)
   - Gaps addressed / unresolved
5. Update DAG execution trace on disk
6. Update node status in DAG JSON

Output:
{
  "node_id": "targeted-research",
  "status": "completed",
  "summary": "Found existing system uses OAuth 2.0 with PKCE...",
  "artifacts_produced": ["research-findings.md"],
  "verdict": null,
  "gaps_addressed": ["G1", "G2"],
  "unresolved": []
}

### freeze-pass
Input: pass outcome (completed/halted) + rationale
Process:
1. Set all node statuses to final states
2. Record pass outcome and rationale in DAG metadata
3. Write completed_at timestamp
4. Write final DAG JSON as immutable pass version
5. Return confirmation

Output:
{
  "pass_frozen": true,
  "dag_path": "specs/001/.workflow/dags/pass-002.json",
  "outcome": "completed",
  "nodes_executed": 3,
  "edges_total": 4
}

## Operational Rules
- Never modify source artifacts (spec.md, etc.) — only DAG JSON files
- Always validate invariants before confirming node assembly
- Report ALL errors to Supervisor — never silently recover
- Construct NL prompts following ADR-005 conventions
- Infer edges from contract consumes/produces matching
- Infer artifact paths from contract + feature directory convention
- Read domain agent reports from disk, never from Supervisor context

## Error Protocol
- Invariant violation → return {status: "invalid", violation: details}
- Expected artifact missing after agent execution → return {status: "missing_artifact", expected: path}
- Report parse failure → return {status: "partial_parse", extracted: {...}, unparsed_path: "..."}
- Catalog file missing → return {status: "error", message: "catalog not found at path"}
```

### Request/Response Schemas

**Assemble-and-prepare:**

Supervisor → DAG Assembler:
```json
{
  "action": "assemble-and-prepare",
  "next_node": "targeted-research",
  "parameters": {
    "focus_gaps": ["G1", "G2"],
    "context": "Investigate auth protocols and LDAP requirements for existing system"
  }
}
```

DAG Assembler → Supervisor:
```json
{
  "status": "valid",
  "node_added": {"id": "targeted-research", "type": "task", "status": "pending"},
  "edges_inferred": 2,
  "agent_prompt": "Investigate the following knowledge gaps for the feature at specs/001-user-auth/...",
  "agent_type": "Explore"
}
```

**Parse-report:**

Supervisor → DAG Assembler:
```json
{
  "action": "parse-report",
  "node_id": "targeted-research"
}
```

DAG Assembler → Supervisor:
```json
{
  "node_id": "targeted-research",
  "status": "completed",
  "summary": "Found existing system uses OAuth 2.0 with PKCE. JWT tokens with 15-min expiry. LDAP for internal users.",
  "artifacts_produced": ["specs/001-user-auth/.workflow/research-findings.md"],
  "verdict": null,
  "gaps_addressed": ["G1", "G2"],
  "unresolved": []
}
```

**Freeze-pass:**

Supervisor → DAG Assembler:
```json
{
  "action": "freeze-pass",
  "outcome": "completed",
  "outcome_detail": "advocate-verdict-needs-revision",
  "rationale": "Advocate found 3 gaps. Freezing pass 1 for new assembly."
}
```

DAG Assembler → Supervisor:
```json
{
  "pass_frozen": true,
  "dag_path": "specs/001-user-auth/.workflow/dags/pass-001.json",
  "outcome": "completed",
  "outcome_detail": "advocate-verdict-needs-revision",
  "nodes_executed": 3,
  "edges_total": 4
}
```

## Error Handling

| Failure Mode | Detection | Handler | Supervisor Response |
|---|---|---|---|
| Invariant violation | DAG Assembler checks during assembly | DAG Assembler returns `{status: "invalid", violation: "..."}` | Make different assembly decision |
| Domain agent failure | Supervisor sees agent error (it spawned the agent) | Supervisor receives error directly | Decide: retry, skip node, or halt pass |
| Expected artifact missing | DAG Assembler checks during parse-report | DAG Assembler returns `{status: "missing_artifact", expected: "..."}` | Decide: retry agent, skip, or halt |
| Report parse failure | DAG Assembler can't extract structure from prose | DAG Assembler returns `{status: "partial_parse", extracted: {...}}` | Decide: accept partial, retry, or halt |
| Catalog not found | DAG Assembler can't read catalog file | DAG Assembler returns `{status: "error", message: "..."}` | Cannot proceed — surface to user |
| State Briefer can't read history | Corrupted or missing DAG files | State Briefer returns partial briefing with warning | Proceed with available info or halt |

**Principle**: DAG-ops agents detect and report. The Supervisor decides. No silent recovery.

## Agent Definition Format

### DAG-Ops Agents vs. Domain Agents

| Aspect | DAG-Ops Agents (State Briefer, DAG Assembler) | Domain Agents (Analyst, Advocate, etc.) |
|---|---|---|
| **Identity** | Role-defined | Persona-defined |
| **Sections** | Role, Actions, Operational Rules, Error Protocol | Core Identity, What You Reject/Embrace, Skills, Quality Standards |
| **Communication** | Structured protocol with Supervisor | Natural language (ADR-005) |
| **Judgment** | Mechanical — follow operational rules | Creative — apply expertise and domain knowledge |
| **Persistence** | Persistent identity, role-defined | Persistent identity, persona-defined |
| **Skills reference** | None — operational rules are self-contained | Skill-augmented (authoring, analysis, patterns) |

## Risks

- **NL prompt quality**: The DAG Assembler constructs NL prompts for domain agents from structured contracts. If the translation produces unclear or incomplete prompts, domain agent output quality degrades. The Supervisor can't catch this because it doesn't read the full reports. Mitigation: define prompt construction patterns tested against known good agent interactions from current workflows.
- **Parse robustness**: Domain agents return prose reports. The DAG Assembler must reliably extract structured data from natural language. Headings and conventions help (ADR-005), but prose is inherently variable. Mitigation: the DAG Assembler is an LLM — it can handle prose parsing with judgment. Define expected report sections as guidance, not rigid schema.
- **Subagent call volume**: 11 subagent calls for a typical 3-node pass. Each call has latency. For a 5-pass workflow with 3-4 nodes per pass, that's 50+ subagent calls. Mitigation: the flexibility and context protection benefits justify the overhead. Optimize hot paths (e.g., can assemble-and-prepare + parse-report be combined for simple nodes?) only after measuring actual latency.
- **State Briefer staleness**: The State Briefer runs at pass start and on-demand. If the Supervisor executes multiple nodes without re-briefing, the viable nodes list may become stale (artifacts have changed). Mitigation: the Supervisor can request a fresh briefing at any point. The DAG Assembler independently validates invariants at each assembly, catching structural issues regardless of briefing freshness.

## Open Questions

- **NL prompt templates**: Should the DAG Assembler use templates per agent type for NL prompt construction, or generate prompts from scratch each time based on the contract?
- **Report section conventions**: What standard sections should domain agent reports follow to make DAG Assembler parsing reliable? Extend ADR-005's "What I Created / Clarifications Needed / Assumptions Made" convention?
- **Parallel node execution**: The protocol is sequential (one node at a time). Could the Supervisor identify independent nodes and spawn multiple domain agents in parallel? The DAG Assembler would need to handle batch assembly.
- **DAG Assembler state**: Does the DAG Assembler read the full DAG JSON from disk on every call, or should it receive the relevant subset from the Supervisor? Reading from disk is simpler but adds I/O per call.
- **Warm-up cost**: Each subagent spawns fresh. For the DAG Assembler, it reads the catalog and DAG JSON from disk every time. Is this acceptable, or should there be a caching mechanism?

## Recommended Next Steps

1. **Write the State Briefer agent definition**: Create the markdown file following the role-defined format. Include the complete input/output schemas and operational rules.

2. **Write the DAG Assembler agent definition**: Create the markdown file with all three actions (assemble-and-prepare, parse-report, freeze-pass), operational rules, and error protocol.

3. **Design NL prompt construction patterns**: Take 3-4 existing agent invocations from the current specify.md workflow. Show how the DAG Assembler would construct the same NL prompts from structured node contracts. Validate that the translation produces equivalent quality.

4. **Design report parsing patterns**: Take 3-4 existing agent reports (analyst-report.md, advocate-report.md). Show how the DAG Assembler would extract structured summaries. Define the expected report sections that make parsing reliable.

5. **Prototype one full pass end-to-end**: Hand-simulate the complete protocol for Scenario 1 (skip enrichment). Walk through every subagent call: State Briefer produces briefing → Supervisor selects analyst-review → DAG Assembler assembles + prepares → domain agent executes → DAG Assembler parses → Supervisor evaluates → continue to advocate-gate → etc. Validate the protocol works mechanically before building any agents.
