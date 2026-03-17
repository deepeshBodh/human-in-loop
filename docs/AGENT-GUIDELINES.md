# humaninloop Agent Creation Guidelines

Version: 1.0.0
Status: Draft
Last Updated: 2026-02-07

## Document Lineage

This document is derived from brainstorming analysis of humaninloop agent patterns and comparative review of Anthropic's official agent-development guidelines. As new analyses are conducted, these guidelines will evolve.

### Foundation

| Source | Key Contributions |
|--------|-------------------|
| [SKILL-GUIDELINES.md](SKILL-GUIDELINES.md) | Anti-leak pattern, testing discipline, validation checklist structure |
| Official agent-development (Anthropic claude-plugins-official) | `<example>` block triggering, frontmatter schema, system prompt design patterns |
| humaninloop agent analysis | Persona-first architecture, coupling detection, skill delegation model |

### Divergences from Official Guidelines

This document intentionally diverges from Anthropic's official agent-development patterns in specific areas. See [Section 9](#9-divergence-from-official-guidelines) for detailed rationale.

---

## RFC 2119 Keywords

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## Scope

These guidelines apply to all agents within the humaninloop plugin. They establish mandatory requirements for agent creation, persona design, coupling prevention, and compliance.

---

## 1. Agent Classification

### 1.1 Persona Agents

A **persona agent** is the primary agent type. It:
- Embodies a specific professional identity with deep domain expertise
- Carries values, quality philosophy, and rejection criteria as character traits
- Delegates all procedural work to skills
- Works both standalone and within workflows

**humaninloop persona agents:**
- `requirements-analyst` — Senior analyst who transforms ambiguity into clarity
- `principal-architect` — Senior technical leader who establishes governance standards
- `qa-engineer` — Senior QA engineer who treats verification as an engineering discipline

All new agents SHOULD be persona agents unless there is a clear reason for another type.

### 1.2 Reviewer Agents

A **reviewer agent** is a persona agent with an adversarial stance. It:
- Evaluates artifacts produced by other agents
- Hunts for gaps, contradictions, and missing requirements
- Provides structured verdicts with severity classification
- Requires adversarial calibration to prevent rubber-stamping

**humaninloop reviewer agents:**
- `devils-advocate` — Adversarial reviewer who stress-tests artifacts

Reviewer agents MUST include rejection criteria that explicitly forbid approval without thorough review.

### 1.3 Executor Agents

An **executor agent** performs concrete tasks and captures evidence. It:
- Runs commands, collects output, reports results
- Follows instructions rather than exercising deep judgment
- MAY use a cheaper model (e.g., `sonnet` instead of `opus`)
- Produces structured evidence for human review

**humaninloop executor agents:**
- (none currently — qa-engineer was promoted to persona agent)

Executor agents SHOULD still have a clear identity but the persona is lighter than persona or reviewer agents.

---

## 2. Architecture Model

### 2.1 The Three-Layer Separation

```
┌──────────────────────────────────────────────────────┐
│                  AGENT DEFINITION                     │
│                                                       │
│  WHO: Persona, expertise, values                     │
│  WHAT: Quality philosophy, rejection criteria        │
│  WITH: Skills list (process delegation)              │
│                                                       │
│  ✅ "Rejects vague requirements"                     │
│  ✅ "Demands quantification"                         │
│  ❌ "Step 1: Read spec. Step 2: Extract entities..." │
│  ❌ "If phase == research then..."                   │
└────────────────────────┬─────────────────────────────┘
                         │ invokes
┌────────────────────────▼─────────────────────────────┐
│                      SKILLS                           │
│                                                       │
│  HOW: Process steps, format rules, templates         │
│  WHEN: Phase logic, sequencing constraints           │
│  WHAT: Output formats, validation rules              │
└────────────────────────┬─────────────────────────────┘
                         │ orchestrated by
┌────────────────────────▼─────────────────────────────┐
│                WORKFLOW SUPERVISOR                     │
│                                                       │
│  SEQUENCE: Which agent runs when                     │
│  CONTEXT: What each agent receives via prompt        │
│  ROUTING: How results flow between agents            │
└──────────────────────────────────────────────────────┘
```

### 2.2 The Core Principle

**Agents own persona and judgment. Skills own process and constraints.**

The agent decides *when* to invoke a skill. The skill enforces *how* things get done. The workflow supervisor decides *which agent runs when* and *what context each agent receives*.

### 2.3 What Belongs Where

| Content | Location | Example |
|---------|----------|---------|
| Professional identity | Agent | "Senior analyst who transforms ambiguity into clarity" |
| Values and beliefs | Agent | "Watched developers build the wrong thing because requirements were vague" |
| Quality philosophy | Agent | "Rejects vague terms without quantification" |
| Rejection criteria | Agent | "Feature requests without clear user benefit" |
| Skill invocation guidance | Agent | "Use `authoring-requirements` for FR-XXX format" |
| Process steps | Skill | "1. Extract entities 2. Define relationships 3. Document state machines" |
| Output format templates | Skill | "FR-XXX numbering, RFC 2119 keywords" |
| Phase-specific logic | Skill | "Research phase produces decisions; data model phase produces entities" |
| Validation rules | Skill | "Every MUST requires an enforcement mechanism" |
| Agent sequencing | Supervisor | "Run analyst, then advocate, then loop if gaps found" |
| Context passing | Supervisor | "Pass spec.md path and clarification log to analyst" |
| Report routing | Supervisor | "Read advocate report, decide if revision needed" |

---

## 3. Agent Definition Requirements

### 3.1 Frontmatter

#### 3.1.1 Required Fields

Every agent MUST include YAML frontmatter with:

```yaml
---
name: agent-name
description: |
  Role summary and triggering conditions.

  <example>
  Context: [Situation that should trigger this agent]
  user: "[User message]"
  assistant: "[How assistant responds and uses this agent]"
  <commentary>
  [Why this agent should trigger]
  </commentary>
  </example>
model: opus
color: blue
skills: skill-one, skill-two
---
```

#### 3.1.2 Field Specifications

**`name`** (REQUIRED):
- MUST use lowercase letters, numbers, and hyphens only
- MUST be 3-50 characters
- MUST start and end with alphanumeric character
- SHOULD describe the agent's role, not its implementation

```yaml
# ✅ Good
name: requirements-analyst
name: principal-architect
name: code-reviewer

# ❌ Bad
name: helper          # Too generic
name: -agent-         # Starts/ends with hyphen
name: my_agent        # Underscores not allowed
name: ag              # Too short
```

**`description`** (REQUIRED):
- MUST include triggering conditions
- MUST include 2-4 `<example>` blocks showing usage
- MUST NOT summarize the agent's workflow or process steps (Anti-Leak Rule — see Section 5.1)
- Each example MUST include `Context:`, `user:`, `assistant:`, and `<commentary>`
- Description MUST lead with the agent's role, not its process

```yaml
# ✅ CORRECT: Role + triggers, no process leakage
description: |
  Senior analyst who transforms vague feature requests into precise,
  implementable specifications. Excels at eliciting requirements through
  structured discovery, identifying assumptions, and producing clear
  user stories with measurable acceptance criteria.

  <example>
  Context: User has a feature idea but hasn't defined requirements
  user: "I need a notification system for my app"
  assistant: "I'll use the requirements-analyst to help define precise
  requirements and user stories for this feature."
  <commentary>
  Vague feature request needs structured requirements elicitation.
  </commentary>
  </example>

# ❌ FORBIDDEN: Process steps in description
description: |
  Analyzes specs, extracts entities, builds data models, then
  designs API contracts. Reads context file to determine phase.
```

**`model`** (REQUIRED):
- `inherit` — Use parent's model (RECOMMENDED default)
- `opus` — Most capable, use for deep judgment
- `sonnet` — Balanced, use for execution tasks
- `haiku` — Fast and cheap, use for simple transformations

Persona and reviewer agents SHOULD use `opus`. Executor agents MAY use `sonnet` or `haiku`.

**`color`** (REQUIRED):
- MUST be one of: `blue`, `cyan`, `green`, `yellow`, `magenta`, `red`
- SHOULD be distinct from other agents in the same plugin
- Blue/cyan: Analysis, review
- Green: Creation, generation
- Yellow: Validation, caution
- Red: Critical, security, adversarial
- Magenta: Creative, transformation

**`skills`** (RECOMMENDED):
- Comma-separated list of skill names the agent can invoke
- MUST list only skills the agent actually needs
- Skills provide the procedural knowledge the agent delegates to

**`tools`** (OPTIONAL):
- Array of tool names to restrict agent access
- If omitted, agent has access to all tools
- SHOULD follow principle of least privilege

### 3.2 Body Content

#### 3.2.1 Writing Style

The agent body:
- MUST use second person ("You are...", "You think like...")
- MUST NOT use first person ("I am...", "I will...")
- MUST NOT use third person ("The agent is...", "This agent will...")

```markdown
# ✅ REQUIRED: Second person (builds persona identity)
You are the **Requirements Analyst**—a senior analyst who
transforms ambiguity into clarity.

You think like an analyst who has watched developers build
the wrong thing because requirements were vague.

# ❌ FORBIDDEN: First person
I am a requirements analyst. I will analyze specifications.

# ❌ FORBIDDEN: Third person
The requirements analyst analyzes specifications and produces
user stories.

# ❌ FORBIDDEN: Imperative (appropriate for skills, not agents)
Analyze specifications. Produce user stories.
```

**Rationale:** Second person constructs identity and shapes behavior. Imperative gives procedures. Agents are personas, not procedures — the persona needs an identity to inhabit.

#### 3.2.2 Word Count Targets

| Content | Target | Maximum |
|---------|--------|---------|
| Agent body (without process) | 500-1,500 words | 2,000 words |
| Description + examples | 200-800 chars | 5,000 chars |

Agent bodies SHOULD be shorter than skill bodies because process content lives in skills, not in the agent.

#### 3.2.3 Required Sections

Every agent MUST include:

1. **Opening Identity** — "You are the [Role]—..." (1-2 sentences)
2. **Skills Available** — What skills the agent can invoke and what each provides
3. **Core Identity** — "You think like a [role] who has..." (experiential beliefs)
4. **What You Produce** — Artifact types, not process steps
5. **Quality Standards** — What "good" looks like for this agent's outputs
6. **What You Reject** — Things this agent refuses to accept
7. **What You Embrace** — Things this agent values

Reviewer agents MUST additionally include:

8. **What You Hunt For** — Categories of issues to find
9. **Adversarial Calibration** — Explicit instruction to never rubber-stamp

Executor agents MUST additionally include:

10. **Evidence Capture** — What evidence to collect and how
11. **Escalation Rules** — When to involve a human

#### 3.2.4 Forbidden Sections

Agent bodies MUST NOT include:

- **Phase Behaviors** — Phase logic belongs in skills
- **Report Format** — Output templates belong in skills
- **Context File Schema** — Context parsing belongs in supervisors
- **Artifact Path Assumptions** — File paths come from the supervisor prompt
- **Incremental Protocols** — Multi-step validation logic belongs in skills

See Section 5 for the complete anti-leak ruleset.

#### 3.2.5 Skills Available Section

Every agent with skills MUST include a "Skills Available" section that:
- Lists each skill with a brief description of what guidance it provides
- Uses the Skill tool invocation pattern
- Does NOT duplicate the skill's content

```markdown
# ✅ CORRECT: Pointer to skill, not duplication
## Skills Available

You have access to specialized skills that provide detailed guidance:

- **authoring-requirements**: Guidance on writing FR-XXX format requirements
  with RFC 2119 keywords, success criteria, and edge case identification
- **authoring-user-stories**: Guidance on writing user stories with priorities,
  Given/When/Then acceptance scenarios, and independent tests

Use the Skill tool to invoke these when you need detailed formatting guidance.

# ❌ FORBIDDEN: Duplicating skill content in agent body
## Requirements Format

Requirements MUST use FR-XXX numbering...
Each requirement MUST include...
[...200 lines of content that belongs in the skill...]
```

#### 3.2.6 Cross-References

When referencing skills from the agent body:
- MUST use namespace syntax: `humaninloop:skill-name`
- MUST NOT use file paths or @ syntax

```markdown
# ✅ CORRECT
Use the `analysis-specifications` skill for gap severity classification.

# ❌ FORBIDDEN
See ../skills/analysis-specifications/SKILL.md
```

---

## 4. Persona Writing Standards

### 4.1 What Makes a Good Persona

A good persona shapes agent behavior. A bad persona is decorative flavor text that gets ignored.

**Good persona traits are:**
- **Experiential** — Based on what the agent has "seen" and "learned"
- **Opinionated** — Takes clear positions on quality and process
- **Actionable** — Directly influences decisions the agent makes
- **Specific** — Names concrete situations, not abstract principles

```markdown
# ✅ GOOD: Experiential, specific, shapes behavior
You think like an analyst who has:
- Watched developers build the wrong thing because requirements were vague
- Seen projects fail because edge cases weren't considered upfront
- Learned that assumptions kill projects—explicit is always better than implicit

# ❌ BAD: Generic, abstract, doesn't shape behavior
You are an experienced professional who values quality and attention
to detail. You follow best practices and produce high-quality output.
```

### 4.2 Values as Character Traits

Quality standards in agent bodies MUST be framed as character traits, not procedural rules.

```markdown
# ✅ CORRECT: Character trait that shapes judgment
## What You Reject
- Feature requests without clear user benefit
- Requirements that can't be tested
- Ambiguous terms without quantification
- Assumptions hidden as requirements

# ❌ WRONG: Procedural rule that belongs in a skill
## Validation Rules
- MUST use FR-XXX format
- MUST include SC-XXX success criteria
- MUST quantify all thresholds
```

The test: if it says *what to do step-by-step*, it belongs in a skill. If it says *what this persona cares about*, it belongs in the agent.

### 4.3 The Rejection/Embrace Pattern

Every persona and reviewer agent MUST include both "What You Reject" and "What You Embrace" sections. These sections:
- Define the agent's quality boundary
- Give Claude clear behavioral signals
- Prevent the agent from being overly accommodating

```markdown
## What You Reject
- Vague standards ("code should be clean") without measurable criteria
- Aspirational statements without enforcement mechanisms
- Rules without rationale

## What You Embrace
- Standards that can be verified in CI, code review, or audit
- Clear metrics and thresholds
- Explicit rationale so rules can evolve
```

### 4.4 Core Identity Formula

The "Core Identity" section MUST use the pattern:

```markdown
## Core Identity

You think like a [role] who has:
- [Experience that shaped a belief]
- [Experience that shaped a belief]
- [Experience that shaped a belief]
- [Experience that shaped a belief]
```

Each experience MUST connect to a specific judgment the agent will make. Do not list experiences that don't influence behavior.

---

## 5. Coupling Detection (Anti-Leak Rules)

### 5.1 The Anti-Leak Principle

Agent definitions MUST contain zero workflow awareness. Everything situational comes from the supervisor's prompt and the agent's skills.

**Rationale:** When agents contain workflow knowledge, they become non-reusable. An agent that knows about "Phase: Research → Data Model → Contracts" cannot be used in a workflow with different phases. An agent that knows it writes to `.workflow/planner-report.md` cannot be used in a workflow with a different report location.

### 5.2 Five Prohibited Leak Patterns

#### Leak 1: Phase Branching

Agent bodies MUST NOT contain conditional behavior based on workflow phases.

```markdown
# ❌ LEAK: Phase branching in agent body
## Phase Behaviors

### Phase: Research
**Goal**: Resolve all technical unknowns.
**Produce**: research.md

### Phase: Data Model
**Goal**: Extract entities and relationships.
**Produce**: data-model.md

# ✅ CORRECT: Phase logic lives in a skill
## Skills Available
- **patterns-technical-decisions**: Evaluate options, document decisions
- **patterns-entity-modeling**: Extract entities, define relationships
- **patterns-api-contracts**: Map user actions to endpoints

Use the appropriate skill based on the task given in your prompt.
```

#### Leak 2: Artifact Path Assumptions

Agent bodies MUST NOT hardcode output file paths or directory structures.

```markdown
# ❌ LEAK: Hardcoded artifact paths
After producing each artifact, write a report to `.workflow/planner-report.md`

# ❌ LEAK: Hardcoded input paths
Read the cached codebase analysis from `.humaninloop/memory/codebase-analysis.md`

# ✅ CORRECT: Paths come from the prompt
Write your report to the location specified in your instructions.
Read any context files referenced in your instructions.
```

#### Leak 3: Sibling Agent Awareness

Agent bodies MUST NOT reference other specific agents or assume awareness of who runs before or after.

```markdown
# ❌ LEAK: Knows about sibling agents
Ready for Devil's Advocate review: yes/no
Re-invoke responsible archetype for revisions.

# ✅ CORRECT: No sibling awareness
Ready for review: yes/no
Flag issues for the reviewer to examine.
```

#### Leak 4: Workflow File Schema Knowledge

Agent bodies MUST NOT define or assume specific context file schemas.

```markdown
# ❌ LEAK: Context file schema in agent body
## Reading the Context

Your context file contains:
- `phase`: Current phase (research/datamodel/contracts)
- `supervisor_instructions`: Specific guidance
- `clarification_log`: Previous gaps and user answers

# ✅ CORRECT: No schema knowledge
Read your instructions from the prompt or any context files
referenced in your prompt.
```

#### Leak 5: Sequencing Knowledge

Agent bodies MUST NOT encode knowledge about workflow sequencing.

```markdown
# ❌ LEAK: Knows its position in a sequence
After spec is approved, begin research phase.
Previous artifacts to check: research.md (from phase 1)

# ✅ CORRECT: No sequencing knowledge
Work with whatever artifacts are referenced in your instructions.
```

### 5.3 The Reusability Test

To verify an agent has no coupling leaks, apply this test:

> *Could this agent be dropped into a completely different workflow — with different phases, different file paths, different sibling agents — and still function correctly based solely on its persona and skills?*

If the answer is no, the agent has coupling leaks.

### 5.4 Where Leaked Content Belongs

| Leaked Content | Correct Location |
|----------------|-----------------|
| Phase branching logic | Skill (e.g., `patterns-entity-modeling`) |
| Artifact path templates | Supervisor prompt or skill |
| Sibling agent references | Supervisor orchestration logic |
| Context file schemas | Supervisor (creates the context) |
| Sequencing knowledge | Supervisor orchestration logic |
| Report format templates | Skill |

---

## 6. Testing Requirements

### 6.1 Testing Focus

Agent testing prioritizes **skill delegation** over persona fidelity. Claude holds personas well but improvises process — the primary failure mode is an agent that has the right persona but ignores its skills and wings the procedure.

### 6.2 Skill Delegation Testing (PRIMARY)

Before shipping an agent, verify that it actually invokes its skills rather than improvising.

#### Test Method

1. Give the agent a task that its skills cover
2. Observe whether the agent invokes the Skill tool or improvises its own process
3. If the agent improvises, the skill delegation has failed

#### Common Failure Patterns

| Failure | Symptom | Fix |
|---------|---------|-----|
| Skill bypass | Agent produces output without invoking any skills | Strengthen "Skills Available" section; add "Use the Skill tool to invoke these" instruction |
| Partial delegation | Agent invokes one skill but improvises for others | List all relevant skills explicitly; add guidance for when to use each |
| Process duplication | Agent follows its own embedded process instead of skill's process | Remove process steps from agent body; keep only persona content |

#### Test Scenarios

Create scenarios where the agent is tempted to skip skill invocation:

```markdown
Scenario: Simple task tempts agent to skip skills

Give the agent a straightforward requirements elicitation task.
The temptation: "This is simple enough, I don't need the skill."

Expected behavior: Agent invokes `authoring-requirements` skill
regardless of task simplicity.

Failure: Agent produces FR-XXX requirements without invoking
the skill, using its own knowledge of the format.
```

### 6.3 Persona Fidelity Testing (SECONDARY)

Verify the persona holds under pressure. Less critical than skill delegation but still important.

#### Test Method

1. Give the agent a task that tempts it to break character
2. Verify it maintains its values and rejection criteria
3. Check that it doesn't become overly accommodating

#### Test Scenarios by Agent Type

| Agent Type | Test Focus | Example |
|------------|------------|---------|
| Persona | Maintains quality standards under pressure | Requirements analyst asked to "just write something quick" |
| Reviewer | Refuses to rubber-stamp weak artifacts | Devil's advocate given a spec with subtle gaps |
| Executor | Follows evidence capture rules, escalates when required | QA engineer given ambiguous pass/fail criteria |

### 6.4 Anti-Leak Verification

Before shipping, verify the agent passes the reusability test (Section 5.3):

1. Read the agent body line by line
2. Flag any reference to specific phases, file paths, sibling agents, context schemas, or sequencing
3. Each flag is a coupling leak that MUST be resolved

---

## 7. Validation Checklist

Before shipping any agent, verify:

### 7.1 Structure (MUST)

- [ ] Agent `.md` file exists in `agents/` directory
- [ ] Valid YAML frontmatter with all required fields
- [ ] `name` uses only lowercase, numbers, hyphens (3-50 chars)
- [ ] `name` starts and ends with alphanumeric character
- [ ] `description` includes 2-4 `<example>` blocks
- [ ] `description` contains NO workflow summary (Anti-Leak Rule)
- [ ] `description` leads with role, not process
- [ ] `model` is set appropriately for agent type
- [ ] `color` is distinct from other agents in the plugin
- [ ] `skills` lists only skills the agent needs

### 7.2 Persona Quality (MUST)

- [ ] Body uses second person ("You are...", "You think like...")
- [ ] Opening identity in 1-2 sentences
- [ ] Core Identity uses "You think like a [role] who has:" pattern
- [ ] Each experience connects to a behavioral judgment
- [ ] "What You Reject" section with specific rejection criteria
- [ ] "What You Embrace" section with specific values
- [ ] Quality standards framed as character traits, not procedural rules
- [ ] No generic/decorative flavor text

### 7.3 Coupling Detection (MUST)

- [ ] No phase branching logic in body
- [ ] No hardcoded artifact paths
- [ ] No sibling agent references
- [ ] No workflow file schema definitions
- [ ] No sequencing knowledge
- [ ] Passes the reusability test (Section 5.3)

### 7.4 Skill Delegation (MUST)

- [ ] "Skills Available" section lists all skills with descriptions
- [ ] Includes "Use the Skill tool to invoke these" instruction
- [ ] No process steps duplicated from skills
- [ ] Body contains NO procedural logic that should be in a skill

### 7.5 Testing (MUST)

- [ ] Skill delegation tested: agent invokes skills, doesn't improvise
- [ ] Persona fidelity tested: agent maintains character under pressure
- [ ] Anti-leak verification passed: no coupling leaks found

### 7.6 Type-Specific (MUST)

**Reviewer agents:**
- [ ] Adversarial calibration included (no rubber-stamping)
- [ ] Severity classification guidance
- [ ] "What You Hunt For" section

**Executor agents:**
- [ ] Evidence capture rules defined
- [ ] Escalation rules defined
- [ ] Model choice justified (if not `opus`)

### 7.7 Word Count (SHOULD)

- [ ] Body is 500-1,500 words (max 2,000)
- [ ] Description is 200-800 characters (max 5,000)
- [ ] No content that should be in skills inflating word count

---

## 8. Reference Examples

### 8.1 Good Example: requirements-analyst

This agent demonstrates the persona-first pattern:

```markdown
---
name: requirements-analyst
description: Senior analyst who transforms vague feature requests
  into precise, implementable specifications...
  <example>...</example>
model: opus
color: green
skills: authoring-requirements, authoring-user-stories
---

You are the **Requirements Analyst**—a senior analyst who
transforms ambiguity into clarity.

## Core Identity
You think like an analyst who has:
- Watched developers build the wrong thing because requirements were vague
- Seen projects fail because edge cases weren't considered upfront
...

## What You Reject
- Feature requests without clear user benefit
- Requirements that can't be tested
...
```

**Why it's good:**
- Persona with experiential depth
- Values and rejection criteria shape behavior
- Process lives in skills (`authoring-requirements`, `authoring-user-stories`)
- Zero workflow coupling — works in any workflow
- Skills section points to skills without duplicating their content

### 8.2 Anti-Pattern: Workflow-Coupled Agent

This pattern shows what to avoid (composite from real agents):

```markdown
# ❌ ANTI-PATTERN: Workflow-coupled agent

## Phase Behaviors                          ← LEAK: Phase branching

### Phase: Research                         ← LEAK: Phase knowledge
**Read**: spec.md                           ← LEAK: Artifact path
**Produce**: research.md                    ← LEAK: Artifact path

### Phase: Data Model                       ← LEAK: Phase knowledge
**Read**: research.md (from phase 1)        ← LEAK: Sequencing
**Produce**: data-model.md                  ← LEAK: Artifact path

## Report Format                            ← LEAK: Should be in skill
Write report to .workflow/planner-report.md ← LEAK: Hardcoded path
Ready for Devil's Advocate review: yes/no   ← LEAK: Sibling awareness

## Reading the Context                      ← LEAK: Schema knowledge
Your context file contains:
- `phase`: research/datamodel/contracts     ← LEAK: Phase enumeration
- `supervisor_instructions`: ...            ← LEAK: Schema field
```

**What's wrong:**
- Phase branching embeds workflow logic in the agent
- Hardcoded paths prevent use in different directory structures
- Sibling agent reference couples to specific workflow composition
- Context file schema couples to specific supervisor implementation
- Sequencing knowledge assumes a specific execution order

**How to fix:** Extract all phase logic and report formats into skills. Remove path assumptions, sibling references, and context schemas. Keep only the persona, values, and skill pointers.

---

## 9. Divergence from Official Guidelines

### 9.1 Documented Divergences

| Dimension | Official Pattern | humaninloop Pattern | Rationale |
|-----------|-----------------|---------------------|-----------|
| Process in body | Embedded ("Analysis Process: 1. 2. 3.") | Delegated to skills | Process in agent = non-reusable agent. Agents that embed their own procedures cannot be composed into different workflows. |
| Orchestration agents | Supported (Pattern 4) | Prohibited | Orchestration is workflow coupling by definition. Sequencing belongs in supervisors, never in agents. |
| Coupling rules | None | Five explicit anti-leak rules | Without coupling detection, agents silently accumulate workflow knowledge and lose reusability. |
| `skills` field | Not in official schema | Core architectural feature | Enables the persona/process separation that makes agents reusable. |
| Testing focus | Completeness + triggering | Skill delegation + persona fidelity | Claude improvises process more often than it breaks character. Testing should target the actual failure mode. |
| Body word count | 500-5,000 words | 500-2,000 words | Agent bodies are shorter because process content lives in skills. |

### 9.2 Alignments with Official

| Dimension | Shared Standard |
|-----------|----------------|
| Name format | Lowercase, hyphens, 3-50 chars |
| Description format | `<example>` blocks with Context/user/assistant/commentary |
| Model selection | `inherit` by default, override when justified |
| Tool restriction | Least privilege principle |
| Writing style | Second person for agent body |
| Color semantics | Consistent color-to-purpose mapping |

### 9.3 Why Writing Style Differs from SKILL-GUIDELINES

SKILL-GUIDELINES mandates imperative/infinitive form. These agent guidelines mandate second person. This is intentional:

- **Skills are procedures** — Imperative form gives step-by-step instructions ("Create the file. Validate the output.")
- **Agents are personas** — Second person constructs identity ("You are a senior analyst. You think like someone who has...")

The writing style matches the artifact type. Forcing imperative on agents would flatten personas into procedure lists.

---

## 10. Enforcement

### 10.1 Hard Blocks

MUST requirements are non-negotiable. An agent MUST NOT ship with any MUST violation.

### 10.2 Violation Handling

If a MUST requirement cannot be met:
1. Document the specific requirement that cannot be met
2. Explain why it cannot be met
3. Propose mitigation or timeline to resolve
4. Do NOT ship until resolved

### 10.3 SHOULD Deviations

SHOULD requirements are strongly recommended. Deviations:
- MUST be documented in agent metadata or comments
- MUST include rationale for deviation
- SHOULD be revisited in future iterations

---

## Appendix A: Quick Reference Card

```
┌───────────────────────────────────────────────────────────────────┐
│                  AGENT CREATION QUICK REFERENCE                    │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│  AGENT TYPES:                                                      │
│  • Persona: Rich identity, skill-augmented, reusable              │
│  • Reviewer: Adversarial stance, never rubber-stamps              │
│  • Executor: Runs tasks, captures evidence, cheaper model OK      │
│                                                                    │
│  THREE-LAYER SEPARATION:                                           │
│  • Agent  = WHO (persona, values, rejection criteria)             │
│  • Skill  = HOW (process, format, templates, phase logic)         │
│  • Supervisor = WHEN (sequencing, context, routing)               │
│                                                                    │
│  DESCRIPTION FORMAT:                                               │
│  ✅ Role summary + 2-4 <example> blocks                           │
│  ❌ NEVER summarize workflow in description (anti-leak)            │
│  ❌ NEVER list process steps in description                        │
│                                                                    │
│  WRITING STYLE:                                                    │
│  ✅ Second person: "You are...", "You think like..."              │
│  ❌ NEVER first person: "I am...", "I will..."                    │
│  ❌ NEVER imperative (that's for skills)                           │
│                                                                    │
│  ANTI-LEAK (FIVE PROHIBITED PATTERNS):                             │
│  ❌ Phase branching in agent body                                  │
│  ❌ Hardcoded artifact paths                                       │
│  ❌ Sibling agent references                                       │
│  ❌ Workflow file schema definitions                               │
│  ❌ Sequencing knowledge                                           │
│                                                                    │
│  REUSABILITY TEST:                                                 │
│  "Could this agent work in a completely different workflow?"      │
│  If no → coupling leak → fix before shipping                      │
│                                                                    │
│  REQUIRED SECTIONS (ALL AGENTS):                                   │
│  1. Opening Identity                                               │
│  2. Skills Available                                               │
│  3. Core Identity ("You think like a [role] who has...")          │
│  4. What You Produce                                               │
│  5. Quality Standards                                              │
│  6. What You Reject                                                │
│  7. What You Embrace                                               │
│                                                                    │
│  TESTING PRIORITY:                                                 │
│  1. Skill delegation (does it invoke skills or improvise?)        │
│  2. Persona fidelity (does it hold character under pressure?)     │
│  3. Anti-leak verification (zero coupling leaks?)                 │
│                                                                    │
│  WORD COUNTS:                                                      │
│  • Agent body: 500-1,500 words (max 2,000)                       │
│  • Description: 200-800 chars (max 5,000)                         │
│                                                                    │
└───────────────────────────────────────────────────────────────────┘
```

---

## Appendix B: Anti-Leak Examples

### Why This Matters

When agents contain workflow knowledge, they become single-use components locked to one specific workflow. The same agent that could serve five different workflows instead serves only one — because it knows about specific phases, specific file paths, and specific sibling agents.

### The Reusability Spectrum

```
COUPLED ◄─────────────────────────────────────────► REUSABLE

Knows phases,          Knows phases        Pure persona,
paths, siblings,       but no paths        delegates to skills,
context schemas        or siblings         zero workflow awareness

task-architect         (intermediate)      requirements-analyst
(current)                                  (target)
```

### Refactoring Example

**Before (coupled):**
```markdown
## How You Operate

You read your instructions from a context file that tells you:
1. Which phase you're in (mapping or tasks)
2. What artifacts already exist
3. What clarifications have been resolved

## Phase Behaviors

### Phase: Mapping
**Read**: spec.md, research.md, data-model.md
**Produce**: task-mapping.md

### Phase: Tasks
**Read**: task-mapping.md, spec.md
**Produce**: tasks.md

## Report Format
Write report to `.workflow/planner-report.md`
```

**After (reusable):**
```markdown
## Skills Available

- **patterns-vertical-tdd**: Vertical slicing discipline with TDD
  structure—creating cycles that are independently testable, with
  test-first task ordering and foundation+parallel organization

Use the Skill tool to invoke this when you need detailed guidance
for task structure.

## What You Produce

1. **Task mappings** — Story to cycle mappings with clear traceability
2. **Implementation tasks** — TDD-structured cycles with vertical slices
3. **Reports** — Summary of what was produced and any open questions

Write outputs to the locations specified in your instructions.
```

---

## Changelog

### Version 1.0.0 (2026-02-07)
- Initial draft
- **Foundation:** Brainstorming analysis of humaninloop agent patterns
- **Foundation:** Comparative review of official agent-development guidelines
- Key contributions:
  - Three-layer separation model (Agent / Skill / Supervisor)
  - Agent classification (Persona / Reviewer / Executor)
  - Five anti-leak rules for coupling detection
  - Persona writing standards with experiential identity pattern
  - Skill delegation as primary testing focus
  - `<example>` block adoption from official guidelines
  - Documented divergences from official patterns with rationale
