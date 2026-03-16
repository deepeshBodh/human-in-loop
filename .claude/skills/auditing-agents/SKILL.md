---
name: auditing-agents
description: >
  This skill MUST be invoked when the user says "audit agent", "review agent",
  "check agent compliance", or "agent audit checklist". SHOULD also invoke when
  user mentions "AGENT-GUIDELINES compliance", "agent review", or "coupling
  detection". Provides the procedural framework for auditing agents against
  AGENT-GUIDELINES.md.
---

# Auditing Agents

## Overview

Evaluate agents against AGENT-GUIDELINES.md using a structured six-phase audit that checks structure, persona quality, coupling, skill delegation, and type-specific requirements. Produce actionable audit reports with severity classification and clear verdicts.

## When to Use

- Auditing an agent before shipping
- Reviewing an existing agent for AGENT-GUIDELINES.md compliance
- Checking for coupling leaks after refactoring an agent
- Validating that an agent delegates to skills instead of embedding process
- Performing a quality gate check on a reviewer or executor agent

## When NOT to Use

- **Auditing skills** -- Use SKILL-GUIDELINES.md validation instead
- **Creating new agents** -- Use AGENT-GUIDELINES.md directly as the authoring reference
- **Reviewing workflow supervisors** -- Supervisors have different compliance standards
- **Code review** -- Different domain entirely

## Agent Classification

Before auditing, classify the agent by type. Classification determines which type-specific checks apply.

| Type | Detection Criteria | Special Requirements |
|------|---------------------|---------------------|
| **Persona** | Rich identity, deep domain expertise, skill-augmented | Standard audit only |
| **Reviewer** | Adversarial stance, evaluates artifacts produced by others | Adversarial calibration, "What You Hunt For", severity classification |
| **Executor** | Runs tasks, captures evidence, follows instructions | Evidence capture rules, escalation rules, model choice justified if not `opus` |

## Core Process: Six-Phase Audit

### Phase 1: Intake

1. Read the agent `.md` file -- frontmatter and body
2. Classify agent type (persona, reviewer, executor)
3. Count words in body (excluding frontmatter YAML)
4. List all referenced skills from the `skills` field

### Phase 2: Structure Audit

Check against AGENT-GUIDELINES.md Section 3 and 7.1:

| Check | Severity |
|-------|----------|
| YAML frontmatter exists | Critical |
| `name` field present, lowercase/hyphens, 3-50 chars | Critical |
| `description` includes 2-4 `<example>` blocks | Critical |
| `description` has no workflow summary (Anti-Leak) | Critical |
| `description` leads with role, not process | Critical |
| `model` set appropriately for agent type | Critical |
| `color` present | Critical |
| `skills` lists only needed skills | Minor |
| Body word count: SHOULD 500-1,500, MUST <2,000 | Minor or Critical |

### Phase 3: Persona Quality Audit

Check against AGENT-GUIDELINES.md Sections 3.2 and 4:

| Check | Severity |
|-------|----------|
| Uses second person ("You are...") | Critical |
| Opening Identity present in 1-2 sentences | Critical |
| Core Identity uses "You think like a [role] who has:" pattern | Critical |
| Each experience connects to a judgment | Important |
| "What You Reject" section present | Critical |
| "What You Embrace" section present | Critical |
| Quality standards framed as character traits, not procedural rules | Important |
| No generic/decorative flavor text | Important |

**Character Trait vs. Procedural Rule Test:**
- "What to do step-by-step" belongs in a skill
- "What this persona cares about" belongs in the agent

### Phase 4: Coupling Detection Audit

Check against AGENT-GUIDELINES.md Sections 5 and 7.3. Five prohibited patterns:

| Leak | What to Find | Severity |
|------|-------------|----------|
| Phase branching | "Phase:", "phase ==", "if phase", section headers named after phases | Critical |
| Artifact path assumptions | `.workflow/`, `spec.md`, "Write to [specific path]" | Critical |
| Sibling agent awareness | Names other agents, "Ready for [agent-name] review" | Critical |
| Workflow file schema | "`phase`:", "`supervisor_instructions`:", context field definitions | Critical |
| Sequencing knowledge | "After [phase/step]", "Previous artifacts", "from phase 1" | Critical |

After checking all five patterns, apply the reusability test:

> Could this agent be dropped into a completely different workflow -- with different phases, different file paths, different sibling agents -- and still function correctly based solely on its persona and skills?

If no, the agent has coupling leaks. See `references/anti-leak-detection.md` for detailed detection patterns, keywords, and compliant alternatives for each leak type.

### Phase 5: Skill Delegation Audit

Check against AGENT-GUIDELINES.md Sections 3.2.5 and 7.4:

| Check | Severity |
|-------|----------|
| "Skills Available" section present | Important |
| "Use the Skill tool to invoke these" instruction present | Important |
| No process steps duplicated from skills | Critical |
| No procedural logic that should live in a skill | Critical |
| Cross-references use namespace syntax (`humaninloop:skill-name`) | Important |

### Phase 6: Type-Specific Audit

**Reviewer agents** -- Check against AGENT-GUIDELINES.md Section 7.6:

| Check | Severity |
|-------|----------|
| Adversarial calibration present (no rubber-stamping) | Important |
| "What You Hunt For" section with issue categories | Important |
| Severity classification guidance | Important |

**Executor agents** -- Check against AGENT-GUIDELINES.md Section 7.6:

| Check | Severity |
|-------|----------|
| Evidence capture rules defined | Important |
| Escalation rules defined | Important |
| Model choice justified if not `opus` | Important |

## Severity Classification

### Critical (MUST fix)

Issues that block shipping. Every Critical issue represents a MUST violation of AGENT-GUIDELINES.md:

- Missing required frontmatter fields (`name`, `description`, `model`, `color`)
- Name format violations (underscores, uppercase, wrong length)
- Missing `<example>` blocks (fewer than 2)
- Description workflow leakage or leading with process
- Wrong writing style (first person or third person instead of second person)
- Missing required sections (Opening Identity, Core Identity, Reject, Embrace)
- Any of the five coupling leaks
- Process duplication from skills
- Body exceeding 2,000 words

### Important (SHOULD fix)

Issues that weaken the agent but do not block shipping:

- Generic or decorative persona
- Core Identity missing experiential pattern
- Experiences not connected to judgments
- Procedural rules instead of character traits
- Skills Available section missing or lacking invocation guidance
- Cross-references using file paths instead of namespace syntax
- Reviewer/executor missing type-specific sections

### Minor (MAY fix)

Polish issues:

- Description over 5,000 chars
- Body under 500 words or between 1,500-2,000 words
- Color conflict with sibling agents
- Fewer examples than target
- Non-optimal model choice for agent type

## Verdict Levels

| Verdict | Criteria | Action |
|---------|----------|--------|
| **PASS** | Zero Critical, Zero Important | Ship immediately |
| **PASS WITH NOTES** | Zero Critical, 1-2 Important | Ship with documented deviations |
| **NEEDS REVISION** | 1-3 Critical OR 3+ Important | Fix issues, re-audit |
| **REJECT** | 4+ Critical | Major rewrite required |

## Persona Quality Indicators

**Good indicators** -- persona shapes behavior:

- **Experiential**: Based on what the agent has "seen" and "learned"
- **Opinionated**: Takes clear positions that influence decisions
- **Actionable**: Each trait connects to a judgment the agent makes
- **Specific**: Names concrete situations, not abstract platitudes

**Bad indicators** -- persona is decorative:

- **Decorative**: Sounds impressive, does not change behavior
- **Generic**: Could apply to any agent ("experienced professional who values quality")
- **Abstract**: Principles without grounding in specific situations
- **Disconnected**: Experiences listed that do not map to judgments

## Output Format

Produce a structured audit report with sections for classification, metrics, anti-leak check, persona quality, skill delegation, type-specific checks, issue lists by severity, verdict, required actions, and recommendations.

See `references/audit-report-template.md` for the full report template with all sections and field definitions.

## Common Mistakes

### Skipping the Classification Step
Jumping into structure checks without first classifying the agent type causes missed type-specific requirements. A reviewer agent without adversarial calibration is a Critical miss that classification would catch.

### Counting Words Including Frontmatter
Body word count MUST exclude the YAML frontmatter block. Including frontmatter inflates the count and gives false positives on the 2,000-word limit.

### Treating All Coupling as Equal
All five coupling leaks are Critical, but some are more subtle than others. Sequencing knowledge ("After spec is approved") and schema knowledge (defining context file fields) are the most commonly missed. Check explicitly for each of the five patterns rather than doing a general "coupling scan."

### Missing Procedural Rules in Disguise
Process duplication is not always obvious. Character-trait framing ("Rejects vague requirements") is correct. Procedural framing ("MUST use FR-XXX format") belongs in a skill. Apply the character trait vs. procedural rule test to every quality standard in the agent body.

### Accepting Generic Personas
"Experienced professional who values quality and attention to detail" sounds reasonable but shapes zero behavior. Flag it as Important. A good persona names concrete experiences that connect to specific judgments.

### Forgetting the Reusability Test
Passing all five individual leak checks does not guarantee reusability. An agent can have no explicit leaks but still embed assumptions that tie it to one workflow. Always end the coupling audit with the reusability test as a final gate.
