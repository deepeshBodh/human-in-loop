# Deep Analysis: OpenSpec vs HumanInLoop

## TL;DR

Both solve the same root problem — **stopping AI from improvising architecture** — but take fundamentally different approaches. OpenSpec is a **lightweight artifact scaffolder** that works across 24 AI tools. HumanInLoop is a **deterministic DAG execution engine** with governance, multi-agent orchestration, and structural validation built into Python infrastructure.

---

## 1. Philosophy & Problem Framing

| Dimension | OpenSpec | HumanInLoop |
|-----------|----------|-------------|
| **Tagline** | "Spec-driven development for AI" | "Stop vibe coding. Ship software that lasts." |
| **Core bet** | Structured *artifacts* prevent AI drift | Deterministic *infrastructure* prevents AI drift |
| **Trust model** | Trust the AI to follow instructions in skill files | Trust Python code, not prompts — graph ops are deterministic |
| **Human role** | Reviews artifacts, approves progression | Reviews at explicit gate nodes; constitution governs decisions |
| **Enforcement** | Convention-based (AI reads templates) | Code-enforced (Pydantic validation, DAG invariants, 381 tests) |

**Key insight**: OpenSpec assumes if you give an AI good templates and instructions, it will produce good specs. HumanInLoop assumes **LLMs take shortcuts** (documented in the dry-run divergence findings) and enforces structure through Python code that agents cannot bypass.

---

## 2. Architecture Comparison

### OpenSpec: Artifact Graph

```
proposal → specs → design → tasks → implement
```

- TypeScript artifact-graph with dependency resolver
- YAML schemas define artifact types, templates, and AI prompts
- On-disk folder structure (`openspec/changes/feature-name/`)
- Delta-based spec system (ADDED/MODIFIED/REMOVED)
- Stateless — no execution history between sessions

### HumanInLoop: StrategyGraph DAG

```
constitution-gate → analyst-review → advocate-review → human-clarification → spec-complete
     (gate)              (task)            (gate)           (decision)        (milestone)
```

- Python DAG with NetworkX graph operations
- Pydantic v2 frozen models (11 enums, 14 models)
- 9-step structural validation at assembly time
- 5 system invariants (INV-001 through INV-005)
- **Persistent, immutable pass history** — every DAG pass is frozen to disk
- **4 node types** (task, gate, decision, milestone) with type-specific status machines

**Verdict**: OpenSpec has a simpler linear pipeline. HumanInLoop has a full graph execution engine where node types, edge types, and invariants are first-class concepts validated by tested Python code.

---

## 3. Workflow Coverage

| Phase | OpenSpec | HumanInLoop |
|-------|----------|-------------|
| **Project setup** | `openspec init` (tool detection, config) | `/setup` (brownfield codebase analysis, constitution creation) |
| **Specification** | `/opsx:propose` (proposal → specs → design → tasks) | `/specify` (DAG-based, multi-pass with adversarial review) |
| **Technical spec** | Embedded in design.md | `/techspec` (5 separate traceable artifacts: requirements, constraints, NFRs, integrations, data sensitivity) |
| **Planning** | Embedded in design.md | `/plan` (4-phase: codebase discovery, research, domain modeling, API contracts) |
| **Task breakdown** | Checkbox list in tasks.md | `/tasks` (vertical slices with TDD cycles: T.1 failing test → T.2 impl → T.3 refactor → T.4 verify) |
| **Implementation** | `/opsx:apply` (works through checklist) | `/implement` (executes cycles with quality gates after each) |
| **Verification** | `/opsx:verify` (expanded profile) | `/audit` (artifact analysis) + testing-agent |
| **Archival** | `/opsx:archive` (merges deltas into specs) | Spec moves to `specs/completed/` |

**Verdict**: OpenSpec bundles planning into fewer artifacts (design.md covers both technical design and architecture). HumanInLoop has deeper phase separation — 7 distinct workflow commands, each producing specific traceable artifacts.

---

## 4. Agent Architecture

| Aspect | OpenSpec | HumanInLoop |
|--------|----------|-------------|
| **Agent model** | Single AI assistant follows skill instructions | 10 specialized agents with distinct roles |
| **Orchestration** | AI follows template prompts sequentially | Supervisor + DAG Assembler + State Analyst (3-agent control plane) |
| **Adversarial review** | Not built-in | Devil's Advocate agent (stress-tests specs, finds gaps) |
| **Specialization** | One agent, many templates | Requirements Analyst, Technical Analyst, Plan Architect, Task Architect, etc. |
| **Skill system** | Tool-specific instruction files (24 tool adapters) | 27 auto-invoked skills with progressive disclosure and reference files |

**Verdict**: OpenSpec relies on a single AI following instructions. HumanInLoop has a multi-agent system where specialized agents have clear contracts, and a control plane (Supervisor/Assembler/Analyst) coordinates execution through the DAG.

---

## 5. Tool Ecosystem

| Aspect | OpenSpec | HumanInLoop |
|--------|----------|-------------|
| **Supported tools** | **24** (Claude, Cursor, Windsurf, Copilot, Gemini, Q, Codex, Cline, Kiro, RooCode, Trae, etc.) | **1** (Claude Code native plugin) |
| **Integration method** | Adapter layer generates tool-specific slash commands | Native Claude Code plugin system (agents, commands, skills) |
| **Portability** | High — same workflow across any AI assistant | Low — deeply integrated with Claude Code's agent infrastructure |

**Verdict**: OpenSpec wins decisively on breadth. HumanInLoop is Claude Code-native and leverages its agent/skill system deeply, which enables the multi-agent architecture but locks it to one platform.

---

## 6. Determinism & Reliability

| Aspect | OpenSpec | HumanInLoop |
|--------|----------|-------------|
| **Graph validation** | Schema validation (Zod) on config/specs | 9-step structural validation + 5 system invariants + contract checking |
| **Execution history** | Stateless — no pass history between sessions | Immutable DAG passes frozen to JSON on disk |
| **LLM guardrails** | Instructions in skill files (convention) | Python code enforces constraints (deterministic) |
| **Test coverage** | Vitest suite (size unknown) | 381 tests, 97.41% coverage, 90% blocking CI gate |
| **Reproducibility** | Same templates → similar (not identical) output | Lexicographic topological sort → deterministic node ordering |

**Verdict**: HumanInLoop has significantly stronger determinism guarantees. Its core insight — that LLMs take shortcuts and only code-level enforcement works reliably — is validated by documented dry-run findings.

---

## 7. Specification Quality

| Aspect | OpenSpec | HumanInLoop |
|--------|----------|-------------|
| **Spec format** | Delta specs (ADDED/MODIFIED/REMOVED) with Given/When/Then | Full spec.md with user stories, edge cases, RFC 2119 keywords |
| **Brownfield handling** | Designed for it (delta approach avoids conflicts) | Codebase analysis → evolution roadmap → constitution |
| **Governance** | None | Constitution (v3.0.0, 12 principles) with enforcement levels |
| **Iterative refinement** | Manual — user decides when to continue | Automated — advocate-review gate loops until verdict is "ready" |

**Verdict**: OpenSpec's delta-based approach is elegant for managing spec changes over time. HumanInLoop's adversarial review loop (analyst → advocate → revision) produces higher-confidence specs but requires more cycles.

---

## 8. Maturity & Adoption

| Metric | OpenSpec | HumanInLoop |
|--------|----------|-------------|
| **GitHub stars** | **28,100** | Small/private |
| **Version** | 1.2.0 | 3.0.0 |
| **npm/PyPI** | Published (`@fission-ai/openspec`) | Python package (`humaninloop_brain`) |
| **Tests** | Vitest suite | 381 tests, 97% coverage |
| **ADRs** | None visible | 7 ADRs |
| **Enterprise** | Enterprise offering (teams@openspec.dev) | Dogfooding-validated |
| **Community** | Discord + 28k stars | — |
| **Telemetry** | PostHog analytics | None |

**Verdict**: OpenSpec has massive community traction and is post-1.0 with enterprise ambitions. HumanInLoop has deeper engineering rigor (ADRs, constitutional governance, 97% coverage) but lacks community adoption signals.

---

## 9. Strengths Each Has That The Other Lacks

### OpenSpec has, HumanInLoop lacks

- **Multi-tool support** (24 AI assistants vs 1)
- **Delta-based spec system** (elegant for incremental spec evolution)
- **Fast-forward mode** (`/opsx:ff` generates all artifacts at once)
- **Exploration mode** (`/opsx:explore` for unclear requirements)
- **Bulk operations** (`/opsx:bulk-archive`)
- **Community momentum** (28k stars)
- **Lower barrier to entry** (simpler mental model)

### HumanInLoop has, OpenSpec lacks

- **Deterministic graph infrastructure** (Python code, not prompts)
- **Multi-agent orchestration** (10 specialized agents with control plane)
- **Adversarial review** (Devil's Advocate stress-tests every spec)
- **Constitutional governance** (12 enforceable principles)
- **Immutable execution history** (DAG passes frozen to disk)
- **Structural validation** (9-step + invariants + contract checking)
- **TDD-structured tasks** (red-green-refactor cycles)
- **Layer dependency enforcement** (entities → graph → validators → passes → cli)
- **Type-safe entity modeling** (Pydantic v2 frozen models)
- **Brownfield constitution** (codifies existing patterns, not just adds new ones)

---

## 10. Strategic Assessment

| Question | Answer |
|----------|--------|
| **Who should use OpenSpec?** | Teams using multiple AI tools who want lightweight spec structure without heavy process. Good for teams that trust their AI assistant to follow instructions reliably. |
| **Who should use HumanInLoop?** | Teams using Claude Code who need **governance guarantees** — regulated industries, complex architectures, brownfield projects where AI improvisation is costly. |
| **Are they competitors?** | Partially. They target the same problem (AI improvisation) but different trust levels. OpenSpec trusts conventions; HumanInLoop trusts code. |
| **Could they complement each other?** | Yes — OpenSpec's multi-tool adapter + delta spec system could be combined with HumanInLoop's deterministic validation + adversarial review. |
| **Which is more defensible?** | HumanInLoop's Python infrastructure is harder to replicate than OpenSpec's template system. But OpenSpec's 24-tool breadth and 28k-star community create network effects. |

---

## Bottom Line

**OpenSpec** is the **accessible, broad** play — lightweight scaffolding that works everywhere. It's the "good enough" spec layer that 80% of teams need.

**HumanInLoop** is the **deep, rigorous** play — deterministic infrastructure with constitutional governance for teams where "good enough" specs lead to expensive mistakes. Its core innovation (graph operations in tested Python, not in LLM prompts) is architecturally sound but limits it to Claude Code.

The biggest threat to HumanInLoop from OpenSpec is **adoption momentum** — 28k stars means mindshare, ecosystem contributions, and enterprise contracts. The biggest threat to OpenSpec from HumanInLoop is **reliability** — as teams scale, convention-based enforcement breaks down and code-enforced determinism becomes necessary.
