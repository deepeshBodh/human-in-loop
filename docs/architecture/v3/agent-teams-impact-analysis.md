# Agent Teams Impact Analysis on V3 Architecture

> **Status**: Research document
> **Date**: 2026-02-27
> **Source**: [Claude Code Agent Teams Documentation](https://code.claude.com/docs/en/agent-teams) (experimental)
> **Scope**: Analysis of how Agent Teams could reshape the V3 three-tier agent model

---

## Executive Summary

Claude Code's experimental **Agent Teams** feature introduces a fundamentally different multi-agent coordination model than the sub-agent (Task tool) pattern that V3 was designed around. Where sub-agents are ephemeral, report-only-to-parent workers, Agent Teams creates persistent, independently-communicating teammates with shared task coordination.

This document analyzes every architectural surface that Agent Teams touches, identifies what V3 decisions it invalidates, what it preserves, and what new capabilities it unlocks.

**Bottom line**: Agent Teams doesn't just optimize V3 — it removes several of V3's core constraints and enables patterns that V3 explicitly worked around. A V4 redesign built on Agent Teams would be structurally different from V3.

---

## 1. Agent Teams — Complete Technical Profile

### 1.1 What Agent Teams Is

Agent Teams lets one Claude Code session (the **team lead**) spawn multiple independent Claude Code instances (**teammates**) that:

- Each have their own full context window
- Communicate directly with each other via a mailbox system
- Share a task list with dependency tracking
- Self-claim available tasks when they finish assigned work
- Persist across multiple task completions (not ephemeral per-call)
- Load the same project context (CLAUDE.md, MCP servers, skills)

### 1.2 Architecture Components

| Component | Description |
|-----------|-------------|
| **Team Lead** | Main Claude Code session that creates the team, spawns teammates, coordinates |
| **Teammates** | Separate Claude Code instances, each with full tool access and independent context |
| **Task List** | Shared work items with states: pending → in_progress → completed. Supports dependencies between tasks. File-lock based claiming prevents race conditions |
| **Mailbox** | Messaging system — teammates can message specific teammates or broadcast to all |

### 1.3 Key Capabilities

| Capability | Detail |
|------------|--------|
| **Direct inter-agent messaging** | `message` (one-to-one) and `broadcast` (one-to-all) |
| **Automatic message delivery** | Messages arrive without polling |
| **Idle notifications** | Teammates auto-notify the lead when they stop |
| **Shared task list** | All agents see task status and can claim available work |
| **Task dependencies** | Tasks can depend on other tasks; blocked tasks auto-unblock when dependencies complete |
| **Plan approval** | Lead can require teammates to plan before implementing; lead approves/rejects plans |
| **Per-teammate models** | Each teammate can use a different model (Sonnet, Opus, Haiku) |
| **Quality gate hooks** | `TeammateIdle` (runs when teammate goes idle) and `TaskCompleted` (runs when task marked complete) — exit code 2 sends feedback and keeps the agent working |
| **Display modes** | In-process (single terminal) or split panes (tmux/iTerm2) |
| **Human interaction** | User can message any teammate directly via Shift+Down or pane click |

### 1.4 Current Limitations

| Limitation | Impact on Architecture |
|------------|----------------------|
| **Experimental** | Not production-stable; API may change |
| **No session resumption** for in-process teammates | Teammates lost on `/resume` or `/rewind` |
| **No nested teams** | Teammates cannot spawn their own teams |
| **One team per session** | Lead manages exactly one team at a time |
| **Lead is fixed** | Cannot promote teammate to lead or transfer leadership |
| **Permissions set at spawn** | All teammates start with lead's permission mode |
| **Higher token cost** | Each teammate has independent context window |
| **Task status can lag** | Teammates sometimes fail to mark tasks complete |
| **Shutdown can be slow** | Teammates finish current request before stopping |

### 1.5 Storage

| Artifact | Location |
|----------|----------|
| Team config | `~/.claude/teams/{team-name}/config.json` |
| Task list | `~/.claude/tasks/{team-name}/` |
| Team config schema | `members` array with each teammate's `name`, `agent_id`, `agent_type` |

---

## 2. Sub-Agents vs. Agent Teams — Structural Comparison

This comparison is critical because V3 was designed entirely around sub-agent constraints.

| Dimension | Sub-Agents (Current V3) | Agent Teams |
|-----------|------------------------|-------------|
| **Lifecycle** | Ephemeral — fresh context per invocation | Persistent — survive across multiple tasks |
| **Communication** | Unidirectional — report results back to parent only | Bidirectional — teammates message each other directly |
| **Context** | Own context window; results summarized back to caller | Own context window; fully independent |
| **Coordination** | Parent manages all work via sequential Task tool calls | Shared task list with self-coordination and dependency tracking |
| **Nesting** | Cannot spawn other sub-agents | Cannot spawn nested teams (but teammates are full sessions with sub-agent access) |
| **State** | Stateless between invocations (unless resumed by agent ID) | Stateful within the team session |
| **Human interaction** | Only through parent | User can message any teammate directly |
| **Project context** | Receives spawn prompt + basic environment | Loads full CLAUDE.md, MCP servers, skills |
| **Task claiming** | Parent assigns all work | Teammates self-claim from shared list |
| **Quality gates** | Parent evaluates all results | Hooks (`TeammateIdle`, `TaskCompleted`) enforce quality automatically |
| **Token cost** | Lower — results summarized back | Higher — each teammate is a full Claude instance |
| **Best for** | Focused tasks where only the result matters | Complex work requiring discussion and collaboration |

### 2.1 The Critical Difference

Sub-agents are **function calls** — invoke, get result, continue. Agent Teams are **collaborators** — they persist, communicate, self-organize, and maintain state.

V3's entire inter-agent protocol (Supervisor asks Analyst, Analyst returns recommendations, Supervisor passes to Assembler, Assembler returns prompt, Supervisor dispatches agent) exists because sub-agents cannot talk to each other. Agent Teams removes this constraint.

---

## 3. V3 Design Decisions That Agent Teams Invalidates

### 3.1 The Supervisor as Pure Dispatcher

**V3 Design**: The Supervisor is a domain-agnostic dispatcher with exactly three outbound verbs:
1. Ask the Analyst (briefing / parse-and-recommend)
2. Tell the Assembler (assemble / freeze / update-status)
3. Dispatch the agent (Task tool with NL prompt)

**Why this existed**: Sub-agents can only report back to the parent. The Supervisor must be the hub of all communication because no other topology is possible.

**What Agent Teams changes**: The State Analyst and DAG Assembler could communicate directly. The Analyst could tell the Assembler what to assemble without the Supervisor relaying the message. The Supervisor's role shifts from **message router** to **strategic coordinator**.

**Impact**: The entire per-node protocol (Section 6 of V3 spec) — which documents 4 sequential message hops per node — could be reduced to 2-3 by allowing Analyst→Assembler direct communication.

### 3.2 The State Analyst's "Recommend, Don't Act" Constraint

**V3 Design**: The State Analyst recommends in intent language with ranked options. It explicitly does NOT assemble nodes, construct prompts, or interact with users.

**Why this existed**: The Analyst is a sub-agent that returns results to the Supervisor. It cannot reach the Assembler or domain agents. Recommendation is all it can do.

**What Agent Teams changes**: As a persistent teammate, the Analyst could directly message the Assembler with assembly instructions, or even trigger domain agent work through the shared task list. The "recommend and wait" pattern becomes "recommend and coordinate."

**Impact**: The merged `parse-and-recommend` action (which combined two v2 round-trips) could go further — the Analyst could parse the report AND tell the Assembler to prepare the next node in one flow, without returning to the Supervisor.

### 3.3 Sequential Node Execution

**V3 Design**: Nodes execute one at a time. The per-node protocol is strictly sequential:
1. Analyst recommends → 2. Supervisor picks → 3. Assembler prepares → 4. Agent executes → 5. Analyst parses → repeat

**Why this existed**: The Supervisor dispatches sub-agents sequentially via the Task tool. Parallel dispatch is possible but all results still flow through the single Supervisor context window.

**What Agent Teams changes**: Independent domain agents could run as parallel teammates. If the Analyst recommends two non-dependent tasks (e.g., requirements analysis and targeted research), both could execute simultaneously as teammates, with results flowing to the Analyst teammate directly.

**Impact**: Pass execution time could be halved for workflows with independent nodes. The `depends_on` edge type already captures dependencies — independent nodes could be parallelized.

### 3.4 The Supervisor's Context Window Pressure

**V3 Design**: Every sub-agent result returns to the Supervisor's context. The V3 spec documents 11 sub-agent calls per 3-node pass — all results accumulate in one context window.

**Why this existed**: Sub-agents report back to parent. There is no alternative.

**What Agent Teams changes**: The Analyst teammate maintains its own context across multiple parse-and-recommend cycles. It doesn't need to re-read the catalog, strategy skills, and DAG file each time — it already has them in context from the briefing phase. Similarly, the Assembler teammate retains graph state across multiple assemblies.

**Impact**: The "fresh context per call" problem that V3 mitigates through structured JSON protocols becomes a non-issue for persistent teammates. The total token cost per workflow could decrease despite Agent Teams' higher per-session cost, because teammates don't redundantly re-read project context.

### 3.5 The 8 Supervisor Decisions Per Pass

**V3 Design**: The Supervisor makes 8 decisions per 3-node pass (pick from recommendations × 3, evaluate results × 3, freeze/continue × 1, pass-start × 1).

**Why this existed**: Every routing decision must go through the Supervisor because it's the only agent with visibility into the overall workflow state.

**What Agent Teams changes**: With a shared task list, the Analyst could create tasks directly (e.g., "assemble analyst-review node", "dispatch requirements-analyst agent"). Teammates self-claim work. The Supervisor's decisions reduce to high-level judgment calls: convergence assessment, captain's calls, human escalation.

**Impact**: The Supervisor shifts from making 8 per-pass routing decisions to making 2-3 strategic decisions: "Are we converging?", "Should we continue or escalate?", "Does this recommendation make sense?"

### 3.6 The DAG Assembler's Model Choice

**V3 Design**: DAG Assembler uses Sonnet because it does "mechanical work, no deep synthesis required."

**Why this existed**: Sub-agents are ephemeral — the cheaper model for commodity work was the right call.

**What Agent Teams changes**: As a persistent teammate, the Assembler accumulates graph state in context. It could use Haiku (even cheaper) for individual operations since the context carries the understanding, or stay on Sonnet for reliability.

**Impact**: Minor cost optimization opportunity.

---

## 4. V3 Design Decisions That Agent Teams Preserves

### 4.1 The Knowledge Distribution Table

| Layer | Knows | Does NOT Know |
|-------|-------|---------------|
| **Supervisor** | DAG vocabulary, goal criteria | Node IDs, strategy patterns |
| **State Analyst** | Catalog, strategy, artifacts, DAG history | Assembly mechanics, prompt construction |
| **DAG Assembler** | Catalog structure, invariants, edge inference | Strategy patterns, artifact content |
| **Domain Agents** | Their domain expertise | Workflow structure, other agents |

**Status**: Fully preserved. Agent Teams changes how agents communicate, not what they know. The separation of concerns remains valid regardless of communication topology.

### 4.2 The Single-DAG Model

The single-DAG-per-workflow-invocation model, node history, pass-entry immutability, derived fields, and the 6 edge types are all infrastructure decisions orthogonal to the agent coordination model.

**Status**: Fully preserved.

### 4.3 The Node Catalog and Capability-Based Resolution

Intent resolution via capability tags, the catalog schema, invariant enforcement — these are deterministic infrastructure that lives in `humaninloop_brain`.

**Status**: Fully preserved.

### 4.4 The `hil-dag` CLI as Single Write Gate

Agents must not write JSON directly. All DAG mutations go through `hil-dag` CLI.

**Status**: Fully preserved. Agent Teams teammates would still use the CLI.

### 4.5 The Domain Agent Tier

Domain agents (Requirements Analyst, Devil's Advocate, Plan Architect, etc.) maintain their domain expertise and artifact conventions. Their internal behavior doesn't change.

**Status**: Fully preserved. How they're dispatched changes, not what they do.

### 4.6 Strategy Skills

Strategy skills remain heuristic guidance consumed by the State Analyst.

**Status**: Fully preserved.

### 4.7 ADR-005 (Natural Language Agent Communication)

Domain agents speak natural language, receive NL prompts, write reports in NL.

**Status**: Fully preserved. Agent Teams inter-agent messaging is also natural language.

---

## 5. New Capabilities Agent Teams Unlocks

### 5.1 Parallel Domain Agent Execution

**Current V3**: Nodes execute sequentially, one at a time.

**With Agent Teams**: Non-dependent domain agents could run as parallel teammates. Example: if the Analyst recommends both `analyst-review` and `targeted-research` (no `depends_on` between them), both could execute simultaneously.

**Mechanism**: The Analyst or Supervisor creates tasks in the shared task list. Domain agent teammates self-claim and execute in parallel. The Analyst teammate monitors completions via `TaskCompleted` hooks.

**Constraint**: File conflicts. If two domain agents write to the same artifact, they'll overwrite each other. The V3 `produces` contracts already document what each node writes — this could enforce non-overlapping file ownership.

### 5.2 Persistent Analyst Context

**Current V3**: The State Analyst is invoked fresh each time via `briefing` or `parse-and-recommend`. It re-reads the catalog, strategy skills, artifacts, and DAG file on every call.

**With Agent Teams**: The Analyst teammate persists across the entire workflow. After the initial briefing, it retains full context — catalog knowledge, strategy patterns, convergence trajectory, gap history. Subsequent `parse-and-recommend` cycles are faster and higher quality because the Analyst has accumulated understanding.

**Impact**: The merged `parse-and-recommend` (which was itself an optimization over v2's separate parse + brief) becomes even more efficient. The Analyst doesn't need to re-synthesize — it updates its running understanding.

### 5.3 Direct Analyst → Assembler Communication

**Current V3**: Analyst produces recommendation → returns to Supervisor → Supervisor forwards to Assembler → Assembler returns prompt → Supervisor dispatches.

**With Agent Teams**: Analyst messages Assembler directly: "Assemble analyst-review with these capability tags and this rationale." Assembler responds directly to Analyst: "Node assembled, here's the NL prompt." Analyst creates a task for the domain agent. Supervisor only needs to be informed, not route every message.

**Impact**: Eliminates the Supervisor as message relay. Reduces per-node latency from 4 hops to 2.

### 5.4 Quality Gate Hooks

**Current V3**: The Supervisor manually evaluates every result. Captain's calls based on structural signals.

**With Agent Teams**: `TaskCompleted` hooks could run automated validation before a task is considered done. Example: a hook that checks whether the Devil's Advocate report contains a valid verdict, or whether the Requirements Analyst output passes schema validation. Exit code 2 rejects the completion and sends feedback.

**Impact**: Quality enforcement moves from Supervisor judgment to automated hooks + Supervisor judgment. The Supervisor focuses on strategic calls; hooks handle structural validation.

### 5.5 Human Interaction with Individual Agents

**Current V3**: All human interaction flows through the Supervisor. Decision nodes require: Supervisor → AskUserQuestion → user → Supervisor → Assembler.

**With Agent Teams**: Users can message any teammate directly. A user could interact directly with the Requirements Analyst to clarify a requirement, or with the Devil's Advocate to challenge a verdict.

**Impact**: Enables richer human-in-the-loop patterns. The user becomes an active participant in the team, not just a decision point.

### 5.6 Persistent Memory for Teammates

Sub-agents introduced a `memory` field (user/project/local scope) that enables persistent cross-session learning. With Agent Teams, this means:

- The State Analyst teammate could maintain a persistent knowledge base of workflow patterns, common gap types, and effective recommendations
- The DAG Assembler teammate could learn from past assembly decisions
- Domain agents could build up project-specific expertise across workflow invocations

**Impact**: Agents improve over time without changing their system prompts.

---

## 6. Proposed V4 Architecture (Agent Teams Native)

### 6.1 Team Structure

```
┌──────────────────────────────────────────────────────────────────────┐
│ TEAM LEAD: SUPERVISOR                                                │
│                                                                      │
│ Role:    Strategic coordinator, human escalation, convergence judge  │
│ Model:   Opus                                                        │
│ Does:    Captain's calls, decision nodes, milestone verification,   │
│          convergence monitoring, human interaction                    │
│ Does NOT: Route messages, relay recommendations, dispatch agents    │
│                                                                      │
│ Hooks:                                                               │
│   TeammateIdle → check if workflow is complete                       │
│   TaskCompleted → structural validation before accepting             │
│                                                                      │
│ Team Lead can:                                                       │
│   - Create/update tasks in shared task list                          │
│   - Message any teammate                                             │
│   - Require plan approval for domain agents                          │
│   - Shut down teammates when workflow completes                      │
└─────┬──────────┬──────────────┬──────────────┬──────────────────────┘
      │          │              │              │
      │ teammate │ teammate     │ teammate     │ teammate(s)
      │          │              │              │
┌─────▼────┐ ┌──▼──────────┐ ┌▼────────────┐ ┌▼────────────────────────┐
│ STATE    │ │ DAG         │ │ DOMAIN      │ │ DOMAIN AGENT N          │
│ ANALYST  │ │ ASSEMBLER   │ │ AGENT 1     │ │ (spawned on demand)     │
│          │ │             │ │             │ │                          │
│ Model:   │ │ Model:      │ │ Model:      │ │ Spawned as teammates    │
│ Opus     │ │ Sonnet      │ │ Opus        │ │ when needed; shut down  │
│          │ │             │ │             │ │ when their work is done  │
│ Messages:│ │ Messages:   │ │ Messages:   │ │                          │
│ → Assemb.│ │ → Analyst   │ │ → Analyst   │ │                          │
│ → Lead   │ │ → Lead      │ │ (via task   │ │                          │
│          │ │             │ │  completion) │ │                          │
│ Persists │ │ Persists    │ │ Per-task    │ │                          │
│ across   │ │ across      │ │ lifecycle   │ │                          │
│ full     │ │ full        │ │             │ │                          │
│ workflow │ │ workflow     │ │             │ │                          │
└──────────┘ └─────────────┘ └─────────────┘ └────────────────────────┘
```

### 6.2 Communication Flow (Per-Node)

```
STATE ANALYST          DAG ASSEMBLER          DOMAIN AGENT         SUPERVISOR
     │                      │                      │                    │
     │ [Analyst has context from prior cycles]      │                    │
     │                      │                      │                    │
     │── message: assemble ──>│                     │                    │
     │   (intent, caps, rationale)                  │                    │
     │                      │ resolves, assembles,  │                    │
     │                      │ builds prompt         │                    │
     │<── message: ready ───│                       │                    │
     │   (node_id, prompt)  │                       │                    │
     │                      │                       │                    │
     │── creates task ──────────────────────────────────────────────────>│
     │   "Execute analyst-review"                   │                    │
     │                      │                       │                    │
     │                      │                  [Teammate spawned         │
     │                      │                   or claims task]         │
     │                      │                       │                    │
     │                      │                  [Executes, writes        │
     │                      │                   report to disk]         │
     │                      │                       │                    │
     │                      │            [TaskCompleted hook fires]      │
     │                      │                       │                    │
     │ [Analyst reads report, records via CLI,      │                    │
     │  synthesizes next recommendation]            │                    │
     │                      │                       │                    │
     │── message: status ───────────────────────────────────────────────>│
     │   (summary, trajectory, next recommendation) │                    │
     │                      │                       │                    │
     │                 [Supervisor evaluates convergence]                │
     │                 [Makes captain's call if needed]                  │
     │                      │                       │                    │
     │<── message: proceed ─────────────────────────────────────────────│
     │   (or: escalate, halt, new-pass)             │                    │
```

**Call count comparison** (3-node pass):

| Metric | V3 (Sub-agents) | V4 (Agent Teams) |
|--------|-----------------|------------------|
| Supervisor decisions | 8 | 3 (start, convergence check, end) |
| Message hops per node | 4 (A→S→B→S→dispatch) | 2 (A→B, A→task-list) |
| Context re-reads | 11 (fresh per call) | 1 (initial briefing only) |
| Total latency per node | 4 sequential calls | 2 sequential + parallel execution |

### 6.3 Shared Task List Integration

The Agent Teams shared task list maps naturally onto the DAG task model:

| DAG Concept | Task List Mapping |
|-------------|-------------------|
| Node pending execution | Task with status `pending` |
| Node dependency (`depends_on`) | Task dependency (`blockedBy`) |
| Node in-progress | Task claimed by teammate |
| Node completed | Task marked `completed` |
| Pass freeze | All tasks in pass marked complete |
| Gate verdict | Task metadata or completion message |

**Key insight**: The shared task list is a lightweight execution layer on top of the DAG. The DAG remains the persistent, immutable record; the task list is the ephemeral coordination mechanism.

### 6.4 Revised Responsibility Boundaries

| Operation | V3 Owner | V4 Owner | Change |
|-----------|----------|----------|--------|
| Pick from recommendations | Supervisor | State Analyst (proposes) + Supervisor (approves/overrides) | Analyst has more autonomy |
| Dispatch domain agents | Supervisor (Task tool) | State Analyst (creates tasks) + Lead (spawns teammates) | Decoupled from Supervisor |
| Route messages between agents | Supervisor (mandatory relay) | Direct agent-to-agent messaging | Supervisor removed from data path |
| Record execution results | State Analyst (per-call fresh read) | State Analyst (persistent context, incremental updates) | More efficient |
| Convergence monitoring | Supervisor (from Analyst summaries) | Supervisor (from Analyst status messages) | Similar, but richer signal |
| Human decision collection | Supervisor only | Supervisor + direct user-to-teammate | More flexible |
| Quality enforcement | Supervisor judgment | Hooks + Supervisor judgment | Automated structural checks |
| Assembly mechanics | DAG Assembler (per-call) | DAG Assembler (persistent, accumulates graph state) | More efficient |

---

## 7. Migration Considerations

### 7.1 What Changes

| V3 Component | V4 Change | Effort |
|-------------|-----------|--------|
| Supervisor system prompt (`specify.md`) | Rewrite from dispatcher to strategic coordinator | High |
| State Analyst agent definition | Add teammate messaging, persistent context, task creation | Medium |
| DAG Assembler agent definition | Add teammate messaging, persistent graph state | Medium |
| Domain agent definitions | Add task completion protocol | Low |
| Per-node protocol | Redesign for direct messaging | High |
| Plugin manifest | Add team configuration | Low |
| Hook definitions | Add `TeammateIdle`, `TaskCompleted` hooks | Medium |

### 7.2 What Stays The Same

| Component | Reason |
|-----------|--------|
| `humaninloop_brain` package | Deterministic infrastructure unchanged |
| `hil-dag` CLI | Still the single write gate |
| Pydantic models | DAG schema unchanged |
| Node catalog | Capability resolution unchanged |
| Strategy skills | Still consumed by Analyst |
| Invariant system | Still enforced by Assembler/CLI |
| Single-DAG model | Orthogonal to coordination model |
| ADR-005 (NL prompts) | Agent Teams messaging is NL |

### 7.3 Incremental Adoption Path

Agent Teams could be adopted incrementally without a full rewrite:

1. **Phase 1 — Persistent Analyst/Assembler**: Convert State Analyst and DAG Assembler from sub-agents to teammates. Supervisor remains the coordinator. Domain agents remain sub-agents dispatched by the Supervisor.

2. **Phase 2 — Direct Analyst→Assembler**: Enable direct messaging between Analyst and Assembler. Supervisor receives status updates instead of routing every message.

3. **Phase 3 — Parallel Domain Agents**: Convert domain agents to teammates that claim tasks from the shared list. Enable parallel execution of non-dependent nodes.

4. **Phase 4 — Quality Hooks**: Add `TaskCompleted` hooks for automated structural validation. Reduce Supervisor evaluation burden.

---

## 8. Risk Analysis

### 8.1 Risks That Agent Teams Introduces

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Experimental status** | High | Feature may change or be removed. V3 sub-agent architecture is a safe fallback. |
| **Token cost increase** | Medium | Each teammate is a full Claude instance. Persistent teammates may use more total tokens than ephemeral sub-agents for short workflows. Monitor cost per workflow. |
| **Coordination complexity** | Medium | Direct messaging between 4+ agents creates more communication paths (N*(N-1)/2 vs. N-1 with hub). Mitigated by structured protocols and shared task list. |
| **No session resumption** | High | If the lead crashes, teammates are lost. No way to resume a partially-completed workflow with Agent Teams. The single-DAG model provides recovery data but the team must be rebuilt. |
| **Task status lag** | Medium | Teammates sometimes fail to mark tasks complete, blocking dependent tasks. Mitigated by `TaskCompleted` hooks and manual lead intervention. |
| **File conflicts** | Medium | Parallel domain agents writing to the same file. Mitigated by `produces` contracts enforcing non-overlapping file ownership. |
| **No nested teams** | Low | Teammates cannot spawn sub-teams. Current V3 workflows don't need this depth. |
| **One team per session** | Low | Cannot run multiple workflows simultaneously. Current design is one workflow at a time anyway. |

### 8.2 Risks That Agent Teams Eliminates

| V3 Risk | How Agent Teams Eliminates It |
|---------|------------------------------|
| **Supervisor context window exhaustion** | Teammates maintain their own context. Supervisor only receives status summaries. |
| **State Analyst cold-start quality** | Persistent Analyst retains cumulative understanding across the workflow. |
| **Single point of recommendation quality** | Analyst and Assembler can cross-check via direct messaging. |
| **Sequential bottleneck** | Parallel domain agent execution for independent nodes. |

---

## 9. Comparison Matrix: Sub-Agents vs. Agent Teams for V3 Patterns

| V3 Pattern | Sub-Agent Implementation | Agent Teams Implementation | Winner |
|------------|--------------------------|---------------------------|--------|
| Analyst briefing | Fresh sub-agent reads everything | Persistent teammate already has context | Agent Teams |
| Parse-and-recommend | Fresh sub-agent re-reads catalog + DAG + report | Teammate reads only the new report | Agent Teams |
| Assembler resolution | Fresh sub-agent re-reads catalog + DAG | Teammate already has graph state | Agent Teams |
| Domain agent dispatch | Supervisor dispatches via Task tool | Task list claim or lead spawns teammate | Agent Teams |
| Supervisor convergence monitoring | Accumulates all results in context | Receives targeted status messages | Agent Teams |
| Simple single-node execution | 4 sub-agent calls | 2 messages + 1 task | Agent Teams |
| Short workflow (1-2 nodes) | Low overhead, fast | Team setup overhead may not justify | Sub-Agents |
| Error recovery | Sub-agent fresh start cleans slate | Persistent state may carry forward errors | Sub-Agents |
| Token cost for 3-node pass | 11 sub-agent calls, shared parent context | 4-5 persistent sessions | Depends on workflow length |
| Reliability / stability | Production-stable Task tool | Experimental, known limitations | Sub-Agents |

---

## 10. Open Questions

1. **Hybrid model**: Could V4 use Agent Teams for Analyst + Assembler (persistent, coordinating) while keeping domain agents as sub-agents (ephemeral, focused)? This would combine the benefits of both.

2. **DAG as task list**: Should the DAG itself serve as the Agent Teams task list, or should they remain separate (DAG for persistent record, task list for ephemeral coordination)?

3. **Plan approval workflow**: Agent Teams supports requiring plan approval before implementation. Should domain agents be required to plan before executing (lead approves)? This adds a quality gate but increases latency.

4. **Team lifecycle**: Should the team persist across the entire workflow (spawn once, reuse), or should teammates be spawned per-pass and shut down at pass freeze?

5. **Memory accumulation**: With persistent teammate memory (`memory: project`), the Analyst could accumulate cross-workflow knowledge. How does this interact with strategy skills?

6. **Stability timeline**: When will Agent Teams move from experimental to stable? Should V4 planning wait for stability, or proceed with a fallback architecture?

7. **Human-in-the-loop expansion**: Agent Teams allows users to message any teammate directly. Should the `human-clarification` decision node pattern be redesigned to leverage direct user-to-agent communication?

---

## 11. Recommendation

### Near-Term (Now)

**Do not rewrite V3 for Agent Teams.** The feature is experimental with known limitations (no session resumption, task status lag, shutdown issues). V3's sub-agent architecture is production-stable.

### Medium-Term (When Agent Teams stabilizes)

**Prototype Phase 1**: Convert State Analyst and DAG Assembler to persistent teammates while keeping domain agents as sub-agents. Measure:
- Token cost per workflow (vs. V3 baseline)
- Workflow completion time (vs. V3 baseline)
- Recommendation quality (persistent context vs. fresh reads)
- Error recovery behavior

### Long-Term

**Design V4 natively on Agent Teams** if the prototype validates the hypothesis that persistent, communicating agents produce better outcomes than ephemeral, hub-and-spoke ones. The V3 knowledge distribution, single-DAG model, catalog system, and invariant enforcement carry forward unchanged — only the coordination layer changes.

---

## Appendix A: Agent Teams Configuration Example

Hypothetical team configuration for the `/specify` workflow:

```json
{
  "team_name": "specify-feature-123",
  "members": [
    {
      "name": "analyst",
      "agent_type": "humaninloop:state-analyst",
      "model": "opus",
      "skills": ["strategy-core", "strategy-specification"],
      "memory": "project"
    },
    {
      "name": "assembler",
      "agent_type": "humaninloop:dag-assembler",
      "model": "sonnet",
      "skills": ["dag-operations"]
    },
    {
      "name": "requirements",
      "agent_type": "humaninloop:requirements-analyst",
      "model": "opus",
      "skills": ["authoring-requirements", "authoring-user-stories"],
      "spawn_on_demand": true
    },
    {
      "name": "advocate",
      "agent_type": "humaninloop:devils-advocate",
      "model": "opus",
      "skills": ["analysis-specifications"],
      "spawn_on_demand": true
    }
  ],
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/validate-task-output.sh"
          }
        ]
      }
    ]
  }
}
```

## Appendix B: References

- [Claude Code Agent Teams Documentation](https://code.claude.com/docs/en/agent-teams)
- [Claude Code Sub-Agents Documentation](https://code.claude.com/docs/en/sub-agents)
- [V3 Architecture Design](./v3-architecture-design.md)
- [Goal-Oriented Supervisor Synthesis](./goal-oriented-supervisor-synthesis.md)
- [State Analyst & DAG Assembler Redesign](./state-analyst-dag-assembler-redesign-synthesis.md)
- [Single-DAG Iteration Model](./single-dag-iteration-model-synthesis.md)
