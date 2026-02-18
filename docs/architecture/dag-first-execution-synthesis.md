# DAG-First Execution Architecture — Analysis Synthesis

## Problem Statement

The humaninloop plugin's workflow commands (setup, specify, techspec, plan, tasks, implement, audit) are implemented as hand-coded supervisor state machines in markdown. Each command reimplements the same patterns — clarification loops, agent invocation, state recovery, entry gates — as procedural prose. The dependency graph between phases and agents is implicit, buried in 500-600 line command files. This creates rigidity: workflows cannot be composed dynamically, phases cannot be reordered or skipped based on context, and adding new workflows requires writing large markdown files from scratch. The Supervisor should have the flexibility to build agent harnesses using DAGs, with the structure, visibility, and trackability that a graph-based model provides.

## Context & Constraints

- **Current architecture**: 7 commands, 8 agents, 25 skills. Commands are supervisors that orchestrate agents through context files with YAML frontmatter. Routing logic, phase transitions, and loop management are hardcoded in each command. See ADR-001 (multi-agent), ADR-005 (decoupled agents).
- **Inspiration**: The [human-in-loop-context-harness](https://github.com/deepeshBodh/human-in-loop-context-harness) project models strategic execution as a canonical JSON DAG with typed nodes and edges, NetworkX for graph computation, and a generic traversal model. Different application domain, but the DAG-as-execution-substrate concept transfers directly.
- **Claude Code runtime**: The Supervisor operates as an LLM with a finite context window. Subagents are spawned via the Task tool. Context preservation for the Supervisor is a first-class concern — execution details must be delegated to subagents to keep the Supervisor's context budget available for DAG-level reasoning.
- **Plugin format**: Commands, agents, and skills are markdown files declared in `plugin.json`. Any architectural change must work within or extend this format.
- **Pragmatic migration**: Start with `/specify` as the proving ground. Prove the architecture before touching other workflows.

## Key Decisions

| Decision | Choice | Confidence | Rationale |
|----------|--------|------------|-----------|
| Primary pain point | Rigidity (B) — inability to compose, reorder, or skip workflow phases dynamically. Opacity (C) and duplication (A) are secondary concerns. | Confident | User identified rigidity as the core problem; opacity and duplication flow from it |
| Architecture model | Catalog-with-constraints — Supervisor assembles DAGs from a node catalog and constraint registry. No templates. | Confident | Templates still encode fixed workflows. The catalog model gives the Supervisor genuine assembly autonomy. Command boundaries can collapse over time. |
| Constraint architecture | Both: node-level contracts (consumes/produces) AND system-level invariants (rules that hold regardless of DAG shape) | Confident | Clean separation — nodes are self-describing, system has guardrails. Supervisor satisfies contracts while respecting invariants. |
| Iteration model | DAG-per-pass with versioning — each iteration produces a new immutable DAG. Previous DAGs preserved as history. | Confident | Immutability gives trackability. Supervisor can genuinely reassemble each pass (not just patch). Aligns with context harness invalidate-and-re-execute philosophy. |
| Assembly context | Full history with progressive summarization — Supervisor sees all prior DAG versions, with increasing compression for older passes | Confident | Full history enables pattern recognition across passes. Progressive summarization manages context budget. Raw history always available on disk for audit. |
| Execution model | Specialist subagents orchestrated by Supervisor — subagents execute nodes and report back structured summaries | Confident | Preserves Supervisor context for DAG-level decisions. Subagents handle execution details. Supervisor never sees the 600-line spec — it sees "spec produced, advocate found 3 gaps." |
| Node type philosophy | General types with configurable behavior — 4 types (task, gate, decision, milestone) cover the domain. Behavior differences expressed through node contracts, not type proliferation. | Confident | Mirrors context harness philosophy. An analyst invocation and an enrichment step are both `task` nodes — they differ in contract and agent assignment, not type. |
| Edge type philosophy | Expressive semantics — 5 edge types (depends_on, produces, validates, constrained_by, informed_by) with distinct cascade behavior | Confident | Rich edge types make Supervisor assembly decisions sharper. The Supervisor reasons differently about a `validates` edge (expect verdict) vs. a `produces` edge (artifact flow). |
| Command evolution | Commands remain as thin entry points / goal declarations. Fewer, less specific, less rigid. Workflow intelligence moves to Supervisor + catalog + constraints. | Confident | Commands give the Supervisor a goal ("produce a validated specification"). All orchestration logic moves out of command files. |
| Proof-of-concept scope | Functional parity PLUS demonstrated flexibility — DAG-based `/specify` produces same artifacts AND shows at least one scenario where the Supervisor assembles a different DAG than the hardcoded flow would | Confident | Proves the architecture works AND adds value. Flexibility demonstration is essential to justify the migration. |

## Decision Trail

### Architecture model: Template-with-flexibility vs. Catalog-with-constraints

- **Options considered**: (A) Template DAGs per command that the Supervisor can modify, (B) Node catalog with constraint rules where the Supervisor assembles DAGs from scratch
- **Recommendation was**: Presented both as ends of a spectrum
- **Chosen**: Catalog-with-constraints (option B)
- **Key reasoning**: User's vision is that hard command boundaries should collapse over time. Templates still encode fixed workflows and preserve those boundaries. The catalog model gives the Supervisor genuine autonomy — `/specify` and `/techspec` could eventually merge into a single DAG if the Supervisor determines both are needed. "The Supervisor should be building agent harnesses using DAGs."

### Iteration model: Unrolling vs. Meta-DAG vs. DAG-per-pass

- **Options considered**: (A) Unrolling — extend the DAG with new nodes per iteration, keeping a single growing graph. (B) Meta-DAG + micro-DAGs — top-level macro flow with nested iteration cycles. (C) DAG-per-pass — each iteration is a complete new immutable DAG.
- **Recommendation was**: Asked user's instinct; they leaned toward C
- **Chosen**: DAG-per-pass with versioning (option C)
- **Key reasoning**: Immutability is the key property. Each DAG is a frozen snapshot of what the Supervisor decided and what happened. The Supervisor can genuinely reassemble each pass — pass 2 might skip enrichment, add a research node, or restructure the agent sequence. B's nesting adds two-level complexity without earning it. A mutates the graph during execution, complicating the executor. C keeps it flat: one DAG, one executor, versioned.

### Node granularity: Specific types vs. General types

- **Options considered**: 5+ specific types (agent-invocation, validation-gate, human-checkpoint, artifact-check, enrichment) vs. fewer general types with configurable behavior
- **Recommendation was**: Proposed the 5 specific types
- **Chosen**: General types — user pushed for fewer types with behavior configured through contracts
- **Key reasoning**: User referenced the context harness node type taxonomy where `task` covers all work (from "implement billing" to "analyze competitors") and behavior comes from node attributes. An analyst invocation and an enrichment step are both `task` nodes — they differ in their contract (consumes/produces) and agent assignment, not their type. This is cleaner and more composable.

## Architecture Overview

### Node Types

| Type | Purpose | Lifecycle States | Plugin Examples |
|------|---------|-----------------|-----------------|
| `task` | Work that produces artifacts. Behavior configured by agent assignment, skills, and contract. | pending → in-progress → done | Analyst writes spec, advocate reviews, enrichment transforms input, research explores unknowns |
| `gate` | Checkpoint that evaluates and produces a verdict. | pending → passed / failed / needs-revision | Artifact existence check, validation against criteria, constitution compliance check |
| `decision` | Point where input is needed to determine the path forward. | pending → decided | Human clarification, routing choice, scope decision |
| `milestone` | Completion marker — binary event. | pending → achieved | Spec complete, plan complete, feature shipped |

### Edge Types

| Edge Type | Semantics | Supervisor Reasoning | Example |
|-----------|-----------|---------------------|---------|
| `depends_on` | Execution ordering — B cannot start until A completes | Topological sort for execution order | enrichment → analyst |
| `produces` | Artifact flow — A creates what B consumes | Track what artifacts are available downstream; enables Supervisor to wire artifact dependencies | analyst →(produces spec.md)→ advocate |
| `validates` | Review relationship — A evaluates B's output, produces verdict | Expect verdict from this node; verdict may trigger new DAG pass | advocate validates analyst output |
| `constrained_by` | Boundary — A must operate within limits set by B | Check invariant before execution; flag violation if constraint not met | all spec work constrained by constitution |
| `informed_by` | Context — A's behavior is shaped by B's output, not blocked by it | Include as context without creating hard dependency | pass 2 analyst informed by pass 1 advocate gaps |

### Node Contract Schema (Conceptual)

Each node in the catalog declares:

```yaml
node_id: "analyst-review"
type: task
contract:
  consumes:
    - artifact: "enriched-input OR raw-input"
      required: true
    - artifact: "constitution.md"
      required: true
    - artifact: "clarification-log"
      required: false
  produces:
    - artifact: "spec.md"
    - artifact: "analyst-report.md"
  agent: "requirements-analyst"
  skills: ["authoring-requirements", "authoring-user-stories"]
  report_schema:
    sections: ["What I Created", "Clarifications Needed", "Assumptions Made"]
```

### System Invariants (Conceptual)

```yaml
invariants:
  - id: "INV-001"
    rule: "Every task node output must pass through a gate node before being treated as complete"
    scope: "all DAGs"

  - id: "INV-002"
    rule: "Constitution must exist and be accessible before any specification work"
    scope: "all DAGs containing spec-related task nodes"

  - id: "INV-003"
    rule: "A validates edge must connect to a gate node, not a task node"
    scope: "DAG assembly validation"

  - id: "INV-004"
    rule: "Maximum 5 DAG passes per workflow invocation before mandatory human checkpoint"
    scope: "iteration control"
```

### Execution Model

```
User invokes command (goal declaration)
    │
    ▼
Supervisor reads:
    ├── Goal definition (from command)
    ├── Current state (existing artifacts, context)
    ├── Node catalog (available nodes + contracts)
    ├── System invariants (assembly constraints)
    └── DAG history (progressive summary of prior passes)
    │
    ▼
Supervisor assembles DAG v(N)
    ├── Selects nodes from catalog
    ├── Wires edges (depends_on, produces, validates, constrained_by, informed_by)
    ├── Validates against invariants
    └── Produces immutable JSON DAG
    │
    ▼
Supervisor executes DAG v(N)
    ├── Topological traversal
    ├── For each node:
    │   ├── task → spawn subagent, receive structured report
    │   ├── gate → evaluate, produce verdict
    │   ├── decision → present to user, collect input
    │   └── milestone → mark achieved
    └── Capture execution trace (node results, timings, verdicts)
    │
    ▼
Supervisor evaluates outcome
    ├── All gates passed, milestone achieved → DONE
    ├── Gate verdict: needs-revision → assemble DAG v(N+1) with history
    └── Gate verdict: critical-gaps → present to user, decide next action
```

### DAG-Per-Pass Versioning

```
DAG v1: [enrich] → [analyst] → [advocate-gate]
         Result: advocate verdict "needs-revision", 3 gaps

DAG v2: [analyst-with-clarifications] → [advocate-gate]
         (Supervisor skipped enrichment — input already enriched)
         (Supervisor added clarification context from v1 via informed_by edge)
         Result: advocate verdict "ready"

DAG v3: [completion-milestone]
         Result: spec marked complete
```

Each DAG version is a complete, immutable JSON document stored on disk. The Supervisor sees:
- `[summary of v1: analyst produced spec, advocate found 3 gaps in areas X, Y, Z]`
- `[full detail of v2: current pass]`

Progressive summarization keeps context budget manageable while preserving full audit trail on disk.

### Command as Goal Declaration

**Before** (specify.md — 600 lines of orchestration):
```markdown
## Phase 1: Enrichment
[50 lines of enrichment logic]

## Phase 2: Analyst Invocation
[80 lines of agent spawning, context setup]

## Phase 3: Advocate Review
[60 lines of validation logic]

## Phase 4: Routing
[40 lines of verdict parsing, loop management]
...
```

**After** (specify.md — thin goal declaration):
```markdown
## Goal
Produce a validated feature specification.

## Success Criteria
- spec.md exists with user stories and functional requirements
- Advocate verdict is "ready"

## Initial Context
- Feature description (from user input or arguments)
- Constitution (from .humaninloop/memory/constitution.md)

## Supervisor Instructions
Assemble and execute DAGs from the node catalog until success criteria are met.
Consult system invariants during assembly.
```

## Relationship to Existing ADRs

| ADR | Relationship |
|-----|-------------|
| **ADR-001 (Multi-Agent)** | Extended, not replaced. Agents remain specialized. The change is in HOW they're orchestrated (DAG assembly vs. hardcoded sequences). |
| **ADR-005 (Decoupled Agents)** | Strengthened. DAG model deepens the decoupling — agents are now catalog nodes with contracts, fully independent of any specific workflow. The artifact chain concept from ADR-005 maps to `produces` edges in the DAG. |

## Relationship to Context Harness

| Context Harness Concept | Plugin Domain Mapping |
|---|---|
| JSON as canonical graph format | DAG definitions stored as JSON, diffable in git |
| NetworkX for DAG computation | Topological sort for execution order; potentially for impact analysis when invariants change |
| Typed nodes with lifecycle states | 4 node types (task, gate, decision, milestone) with configurable behavior |
| Typed edges with distinct semantics | 5 edge types (depends_on, produces, validates, constrained_by, informed_by) |
| Invalidate-and-re-execute | DAG-per-pass model — new immutable DAG per iteration, not patching |
| Graph Orchestrator | Supervisor role — assembles and executes DAGs |
| Domain agents | Specialist subagents (analyst, advocate, etc.) |
| Cascade protocol with human approval | Gate verdicts trigger new DAG pass; human checkpoints at decision nodes |
| Progressive branch history | Progressive DAG summarization for Supervisor context |

## Risks

- **Supervisor assembly quality**: The Supervisor is an LLM assembling DAGs from a catalog. If its assembly logic is poor — missing nodes, wrong edge wiring, violated invariants — the workflow breaks. Invariant validation is the safety net, but it catches structural errors, not strategic ones (e.g., the Supervisor decides to skip the advocate entirely). Mitigation: system invariants should encode critical workflow rules (e.g., "every agent output must be validated").
- **Context budget pressure**: Even with progressive summarization, the Supervisor needs to hold the node catalog, system invariants, DAG history summaries, and current execution state simultaneously. For complex multi-pass workflows, this could strain the context window. Mitigation: keep the catalog compact (node contracts, not full agent definitions); subagents handle all execution details.
- **Migration complexity**: The current architecture works. Migrating to DAG-first while maintaining backward compatibility with existing workflows is non-trivial. Each command must be decomposed into catalog nodes, invariants extracted, and the Supervisor logic proven. Mitigation: start with `/specify` only; prove the architecture before touching other workflows.
- **Debugging opacity**: When a hardcoded workflow fails, you read the command file and trace the logic. When a dynamically-assembled DAG fails, you need to understand why the Supervisor assembled that particular graph. The DAG JSON helps (it's inspectable), but the assembly reasoning is in the LLM's context, not in a file. Mitigation: the Supervisor should emit assembly rationale alongside the DAG JSON.
- **Over-engineering risk**: The catalog-with-constraints model is powerful but complex. If the actual workflow variations are limited (the Supervisor always builds roughly the same DAG), the architecture overhead may not justify itself. The proof-of-concept with `/specify` must demonstrate genuine flexibility — not just functional parity through a more complex mechanism. Mitigation: the PoC success criterion explicitly requires demonstrated flexibility beyond functional parity.

## Open Questions

- **Catalog format**: What is the concrete JSON/YAML schema for node definitions in the catalog? How are nodes discovered and loaded by the Supervisor?
- **Invariant enforcement**: Are invariants checked at assembly time (before execution), execution time (during traversal), or both? What happens when an invariant is violated mid-execution?
- **DAG storage**: Where do the immutable DAG versions live on disk? In `.workflow/dags/v1.json, v2.json, ...`? How are they cleaned up?
- **Supervisor prompting**: How does the Supervisor receive the catalog and invariants? As part of its system prompt? As files it reads? This affects context budget directly.
- **Parallel execution**: Can the Supervisor identify independent nodes in the DAG and execute them in parallel (e.g., two task nodes with no dependency between them)?
- **Cross-workflow composition**: When command boundaries collapse, how does a single DAG span what's currently `/specify` + `/techspec`? What signals tell the Supervisor to extend scope?
- **NetworkX or simpler**: Does the plugin domain need NetworkX-level graph computation, or is a simpler JSON traversal sufficient? NetworkX adds a Python dependency; the plugin currently runs in a Node/shell environment.
- **Backward compatibility**: Can the old command-based workflows coexist with DAG-based ones during migration? Or is this a cut-over?
- **Assembly rationale**: How does the Supervisor document its DAG assembly reasoning for auditability? A separate `assembly-rationale.md` per pass?
- **Catalog extensibility**: Can users or third-party plugins contribute nodes to the catalog? This is the "marketplace" vision applied to workflow components.

## Recommended Next Steps

1. **Design the node catalog schema for `/specify`**: Define the concrete JSON structure for each node that currently participates in the specify workflow (enrichment, analyst invocation, advocate review, human clarification, routing). Include contracts (consumes/produces), agent assignments, and lifecycle states. This is the foundation everything else builds on.

2. **Extract system invariants from specify.md**: Read the current command file and identify every implicit rule (constitution must exist, analyst before advocate, validation after agent output, iteration limits). Formalize these as the invariant registry. This reveals whether the current workflow's constraints are expressible in the invariant format.

3. **Prototype a single DAG pass for specify**: Hand-write the JSON for one pass of the specify workflow (enrichment → analyst → advocate → verdict). Build or simulate the Supervisor assembling this DAG from the catalog, executing it via subagents, and capturing the result. Validate the execution model end-to-end before building tooling.

4. **Design the DAG-per-pass versioning scheme**: Define where DAG versions are stored, how progressive summarization works, and what the Supervisor sees when assembling pass N+1. This is critical for iteration quality.

5. **Prove flexibility with a divergent scenario**: Identify at least one concrete scenario where the Supervisor would assemble a different DAG than the current hardcoded flow — e.g., a detailed feature description that skips enrichment, or an advocate rejection that triggers a research node. Implement this scenario to demonstrate the architecture's value beyond functional parity.

6. **Write ADR-007**: Once the proof-of-concept validates the approach, formalize this as an Architecture Decision Record that supersedes the workflow aspects of ADR-005 while preserving its agent decoupling principles.
