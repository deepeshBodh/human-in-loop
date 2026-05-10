# humaninloop Skill Creation Guidelines

Version: 1.3.0
Status: Draft
Last Updated: 2026-05-10

## Document Lineage

This document is derived from comparative analyses of skill authoring approaches. As new analyses are conducted, these guidelines will evolve.

### Foundation

| Analysis | Key Contributions |
|----------|-------------------|
| skill-development vs writing-skills comparative analysis (2026-01-25) | CSO anti-leak pattern, TDD for documentation, anti-rationalization framework, word count targets |
| 2026-05-10 cross-repo research refresh | Knowledge-Skill classification, two-tier validation, runtime-aware paths, token-budget framing |

### How These Guidelines Evolve

Changes to this document should be backed by evidence — comparative analysis of similar guidance in other projects, pressure-test results, or audits of existing skills. Cite the evidence in the changelog entry alongside any new MUST/SHOULD requirement.

---

## RFC 2119 Keywords

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## Scope

These guidelines apply to all skills within the humaninloop plugin. They establish mandatory requirements for skill creation, testing, and compliance.

---

## 1. Skill Classification

### 1.1 Behavior Classification

#### 1.1.1 Discipline-Enforcing Skills

A skill is **discipline-enforcing** if it:
- Requires agents to follow a specific process
- Has compliance costs (time, effort, rework)
- Could be rationalized away under pressure
- Contradicts immediate goals (speed over quality)

**humaninloop discipline-enforcing skills:**
- `humaninloop:setup` - Enforces constitution creation discipline

All workflow skills in humaninloop MUST be treated as discipline-enforcing.

#### 1.1.2 Reference Skills

A skill is **reference** if it:
- Provides information without process requirements
- Has no rules to violate
- Agents have no incentive to bypass

#### 1.1.3 Technique Skills

A skill is **technique** if it:
- Teaches a method or pattern
- Can be applied or not based on context
- Success is measurable by outcome, not compliance

#### 1.1.4 Knowledge Skills (NEW in v1.3.0)

A skill is **knowledge** if it:
- Packages a curated body of normative guidance (rules, patterns, conventions) as a queryable corpus
- Provides no executable workflow — its value is the rule set itself
- Is referenced by name from other skills/agents to avoid duplication
- Typically organizes content as one-rule-per-file under `references/` for selective loading

**Pattern observed in `agent-skills/skills/react-best-practices/`:** 74 individual rule files in `rules/`, each with a fixed schema (title, explanation, bad+good examples, impact level), indexed from a lean `SKILL.md`. The skill *is* the documentation, not a tool to execute.

**When to use Knowledge Skills:**
- Cross-cutting guidance referenced by many other skills (e.g., naming conventions, security patterns, framework idioms)
- Bodies of guidance large enough that inlining everywhere would burn context
- Rule sets that need to be machine-extractable (e.g., for IDE integration, lint rule generation)

**Knowledge Skill structure:**

```
knowledge-skill-name/
├── SKILL.md            (lean — describes scope + how to query)
├── rules/              (one rule per file, identical schema)
│   ├── rule-001-naming.md
│   ├── rule-002-error-handling.md
│   └── ...
├── _sections.md        (index/router for the rules)
└── metadata.json       (optional — for machine consumers)
```

**Distinction from Reference Skills:** Reference skills give *information when asked*; Knowledge skills give *normative guidance to apply*. A reference skill answers "what is X?"; a knowledge skill answers "how SHOULD I do X?".

**Validation requirements (additional to Section 8):**
- Each rule MUST follow the same schema (consistent for machine parsing)
- The SKILL.md MUST cap at <500 lines and reference rules by name, not inline content
- A `metadata.json` MAY accompany SKILL.md when machine consumers (CI lints, IDE extensions) need structured access

---

## 2. SKILL.md Requirements

### 2.1 Frontmatter

#### 2.1.1 Required Fields

Every SKILL.md MUST include YAML frontmatter with:

```yaml
---
name: skill-name
description: This skill MUST be invoked when the user says "[trigger phrase]"...
---
```

The `name` field:
- MUST use lowercase letters, numbers, and hyphens only
- MUST NOT contain parentheses or special characters
- SHOULD use gerund form (e.g., `creating-skills` not `skill-creation`)

The `description` field:
- MUST be written in third person
- MUST describe ONLY triggering conditions and symptoms
- MUST NOT summarize the skill's workflow or process
- MUST NOT exceed 1024 characters
- SHOULD stay under 500 characters
- MUST use RFC 2119 keywords (MUST, SHOULD, MAY) for invocation requirements
- MUST use "when the user says" phrasing for exact trigger phrases
- MUST quote exact trigger phrases

See Section 2.1.2 for the required description format.

#### 2.1.2 RFC 2119 Keywords for Skill Descriptions

ALL skills MUST use RFC 2119 keywords in descriptions to ensure reliable auto-invocation. See [ADR-006](decisions/006-rfc2119-skill-auto-invocation.md) for rationale.

**RFC 2119 Keyword Semantics for Invocation:**

| Keyword | Meaning | Use Case |
|---------|---------|----------|
| **MUST** | Mandatory invocation | High-confidence trigger phrases that uniquely identify the skill |
| **SHOULD** | Recommended invocation | Related keywords that indicate the skill may be relevant |
| **MAY** | Optional invocation | Edge cases or tangentially related requests |

**Required Description Format:**

```yaml
description: >
  This skill MUST be invoked when the user says "report a bug",
  "create issue", "log issue", "file a bug", or "raise an issue".
  SHOULD also invoke when user mentions "bug", "issue", or "feature request".
  Use for GitHub issue creation, lifecycle management, and structured tracking.
```

**Why "when the user says" vs "when user mentions":**

The phrasing "when the user says" is more direct than "when user mentions":
- Explicitly frames the trigger as user speech
- Creates a direct mapping: user says X → invoke skill
- Combined with RFC 2119 `MUST`, establishes mandatory invocation

**Examples - Before and After:**

```yaml
# ❌ BEFORE (unreliable invocation):
description: Use when creating GitHub issues, managing issue lifecycle,
  triaging bugs and features, or when user mentions "log issue",
  "create bug", "feature request", or needs structured issue tracking.

# ❌ ALSO WRONG (uses "should" not "MUST", wrong phrasing):
description: This skill should be used when the user asks to "create issue"
  or mentions "bug tracking".

# ✅ CORRECT (reliable invocation):
description: This skill MUST be invoked when the user says "report a bug",
  "create issue", "log issue", "file a bug", "raise an issue", "create bug",
  or "feature request". Use for GitHub issue creation, lifecycle management,
  triage, and structured issue tracking.
```

**Key requirements:**
- RFC 2119 `MUST` keyword establishes mandatory invocation
- "when the user says" phrasing (NOT "when user mentions" or "when the user asks")
- Trigger phrases are explicitly quoted
- Capability description follows trigger requirements

#### 2.1.3 CSO Anti-Leak Rule (CRITICAL)

The description MUST NOT contain workflow summaries. Workflow leakage in descriptions causes Claude to skip reading the skill body.

```yaml
# ❌ FORBIDDEN: Workflow summary in description
description: This skill MUST be invoked when the user says "setup project" -
  gathers context, drafts principles, validates with checklist

# ❌ FORBIDDEN: Process steps in description
description: This skill MUST be invoked when the user says "create constitution" -
  analyzes codebase, creates constitution, syncs CLAUDE.md

# ✅ CORRECT: RFC 2119 + triggers only (no workflow)
description: This skill MUST be invoked when the user says "setup project",
  "create constitution", or "define governance". SHOULD also invoke when user
  mentions "principles" or "CLAUDE.md".
```

**Rationale:** Testing revealed that when descriptions summarize workflows, Claude follows the description shortcut instead of reading the full skill body. This causes partial execution of multi-step workflows.

### 2.2 Body Content

#### 2.2.1 Word Count Targets

| Content | Target | Maximum |
|---------|--------|---------|
| Frequently-loaded skills (SKILL.md body) | <200 words total | 500 words |
| Standard skills (SKILL.md body) | 1,500-2,000 words | 3,000 words |
| Knowledge skills (SKILL.md body) | <500 lines | 800 lines |
| Metadata (name + description) | ~100 words | 1,088 chars |
| Reference files | 2,000-5,000 words | Unlimited |

The SKILL.md body:
- MUST NOT exceed 3,000 words for standard skills
- SHOULD target 1,500-2,000 words for standard skills
- MUST move detailed content to references/ if exceeding targets
- Knowledge skills (Section 1.1.4) follow line-count budgets, not word-count

**Token budget framing (NEW in v1.3.0):** The context window is a *shared public good* across system prompt, conversation history, sibling skills, and user request. A skill that bloats SKILL.md degrades every other skill's effective budget. Authors MUST treat their skill body as competing for shared space — every paragraph that doesn't earn its keep evicts something from another skill or from the user's actual request.

Concrete rule: before adding ≥100 words to a SKILL.md, ask "could this live in `references/` and be loaded only when needed?" If yes, move it.

#### 2.2.2 Writing Style

The skill body:
- MUST use imperative/infinitive form (verb-first instructions)
- MUST NOT use second person ("you should", "you need to")
- MUST use objective, instructional language

```markdown
# ✅ REQUIRED: Imperative form
Create the constitution file at the specified path.
Validate all principles against the checklist.
Run the analysis before drafting.

# ❌ FORBIDDEN: Second person
You should create the constitution file.
You need to validate the principles.
You must run the analysis first.
```

#### 2.2.3 Required Sections

Every SKILL.md MUST include:

1. **Overview** - Core principle in 1-2 sentences
2. **When to Use** - Symptoms and use cases (bullet list)
3. **When NOT to Use** - Counter-indicators
4. **Core Process/Pattern** - The main content
5. **Common Mistakes** - What goes wrong + fixes

Discipline-enforcing skills MUST additionally include:

6. **Red Flags - STOP** - Symptoms of rationalization
7. **Rationalization Table** - Excuses and counters

#### 2.2.4 Cross-References

When referencing other skills:
- MUST use namespace syntax: `humaninloop:skill-name`
- MUST mark dependency level: `**REQUIRED:**` or `**OPTIONAL:**`
- MUST NOT use file paths or @ syntax

```markdown
# ✅ REQUIRED: Namespace with dependency marker
**REQUIRED:** Use humaninloop:plan before implementing

# ❌ FORBIDDEN: File path
See ../plan/SKILL.md for planning guidance

# ❌ FORBIDDEN: @ syntax (force-loads, burns context)
@skills/plan/SKILL.md
```

---

## 3. Testing Requirements

### 3.1 TDD is Mandatory

All skills MUST follow RED-GREEN-REFACTOR before shipping:

```
┌─────────────────────────────────────────────────────────┐
│                    THE IRON LAW                          │
│                                                          │
│         NO SKILL WITHOUT A FAILING TEST FIRST            │
│                                                          │
│  Write skill before testing? Delete it. Start over.     │
│  Edit skill without testing? Same violation.            │
│                                                          │
│  No exceptions.                                          │
└─────────────────────────────────────────────────────────┘
```

### 3.2 RED Phase: Baseline Testing

Before writing the skill, the author MUST:

1. Create pressure scenarios (3+ combined pressures)
2. Run scenarios with subagent WITHOUT the skill
3. Document exact agent behavior verbatim
4. Capture all rationalizations word-for-word
5. Identify which pressures triggered violations

**Pressure types to combine:**

| Pressure | Example |
|----------|---------|
| Time | Emergency, deadline, "just ship it" |
| Sunk cost | Hours of work already done |
| Authority | Senior says skip it, user seems impatient |
| Exhaustion | End of session, context limit approaching |
| Pragmatic | "Being pragmatic not dogmatic" |
| Confidence | "I already know how to do this" |

### 3.3 GREEN Phase: Write Minimal Skill

After baseline testing, the author MUST:

1. Write skill addressing the specific rationalizations observed
2. NOT add content for hypothetical cases
3. Run same scenarios WITH skill loaded
4. Verify agent now complies
5. If agent still fails, revise and re-test

### 3.4 REFACTOR Phase: Close Loopholes

If agent finds new rationalizations, the author MUST:

1. Add explicit counter to rationalization table
2. Add symptom to red flags section
3. Re-test until bulletproof

A skill is bulletproof when:
- Agent chooses correct behavior under maximum pressure
- Agent cites skill sections as justification
- Agent acknowledges temptation but follows rule anyway

### 3.5 Testing Scenarios by Skill Type

Different skill types require different test approaches:

| Skill Type | Test Focus | Success Criteria |
|------------|------------|------------------|
| Discipline-enforcing | Pressure scenarios, rationalization capture | Compliance under maximum pressure |
| Reference | Retrieval accuracy, gap testing | Correct information found and applied |
| Technique | Application scenarios, edge cases | Technique correctly applied to new scenario |
| Knowledge | Rule-schema validation, retrieval coverage | All rules conform to schema; agent finds the right rule for a query |

### 3.6 Two-Tier Validation (NEW in v1.3.0)

Pattern from `agent-skills/packages/react-best-practices-build/`: skills should pass two distinct validation layers before shipping.

**Tier 1 — Structural validation (machine-checkable):**
- Frontmatter schema (required fields present, types correct, character limits respected)
- File structure (SKILL.md exists, referenced files exist, references one level deep)
- Cross-reference integrity (`humaninloop:skill-name` points to a real skill)
- Description format (RFC 2119 keyword present, no workflow leakage by regex)

Tier 1 SHOULD be enforced by a script (suggested: `scripts/validate-skill.sh`) and SHOULD run in CI.

**Tier 2 — Semantic validation (human or pressure-test):**
- Description triggers actually fire on the intended user phrasings
- Body content addresses the rationalizations captured in baseline testing
- Required sections contain meaningful content (not empty headings)
- Examples in body actually illustrate the rule they sit under

Tier 2 is the existing TDD pressure-test cycle (Sections 3.1–3.4) plus the audit checklist.

**Why two tiers:** Tier 1 catches mechanical errors that humans miss in review (typos in YAML, broken links, missing fields). Tier 2 catches behavioral failures that scripts can't detect (rationalizations that bypass the rule). Skipping either tier ships a broken skill.

---

## 4. Anti-Rationalization Requirements

### 4.1 Scope

All discipline-enforcing skills MUST include anti-rationalization content.

### 4.2 Foundational Principle

Every discipline-enforcing skill MUST include this principle early in the body:

```markdown
**Violating the letter of the rules is violating the spirit of the rules.**
```

This cuts off the entire class of "I'm following the spirit" rationalizations.

### 4.3 Rationalization Table

Discipline-enforcing skills MUST include a rationalization table built from baseline testing:

```markdown
## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Requirements seem clear enough" | Clear to you ≠ clear to implementation. Clarify anyway. |
| "I already know what to build" | Knowing ≠ validating. Run discovery anyway. |
| "This is a simple change" | Simple changes have caused the biggest bugs. Follow process. |
| "User seems impatient" | Cutting corners creates more work. Impatience is not permission. |
```

Every excuse captured during baseline testing MUST appear in this table.

### 4.4 Red Flags Section

Discipline-enforcing skills MUST include a red flags list:

```markdown
## Red Flags - STOP and Restart Properly

If you notice yourself thinking any of these, STOP immediately:

- "This case is different because..."
- "I'm following the spirit, not the letter"
- "The user seems to want speed"
- "I already manually verified this"
- "This is too simple to need the full process"

**All of these mean:** You are rationalizing. Restart with proper process.
```

### 4.5 Explicit Loophole Closing

Rules MUST forbid specific workarounds, not just state the rule:

```markdown
# ❌ INSUFFICIENT: Rule only
Create constitution before implementation.

# ✅ REQUIRED: Rule + explicit loophole closures
Create constitution before implementation.

**No exceptions:**
- Not for "simple projects"
- Not for "just prototyping"
- Not for "we'll add it later"
- Not even if user says "skip this for now"
```

---

## 5. Directory Structure

### 5.1 Minimal Structure

```
skill-name/
└── SKILL.md
```

Use when: Simple knowledge, no heavy reference or tools needed.

### 5.2 Standard Structure (RECOMMENDED)

```
skill-name/
├── SKILL.md
├── references/
│   └── detailed-guide.md
└── examples/
    └── working-example.sh
```

Use when: Detailed documentation or working examples needed.

### 5.3 Complete Structure

```
skill-name/
├── SKILL.md
├── references/
│   ├── patterns.md
│   └── advanced.md
├── examples/
│   ├── example1.sh
│   └── example2.json
└── scripts/
    └── validate.sh
```

Use when: Complex domain with validation utilities.

### 5.4 File Organization Rules

- MUST keep references one level deep from SKILL.md
- MUST NOT create deeply nested reference chains
- SHOULD include table of contents in reference files >100 lines
- MUST reference all bundled files from SKILL.md body

### 5.5 Runtime-Aware Path Guidance (NEW in v1.3.0)

Pattern observed in `agent-skills/skills/deploy-to-vercel/SKILL.md:227-245`: skills that work across multiple Claude runtimes (Claude Code CLI, Claude.ai web app, sandboxed environments, third-party agent SDKs) MUST avoid hardcoded paths.

| Runtime | Skill discovery path |
|---------|----------------------|
| Claude Code CLI (user-installed) | `~/.claude/plugins/<plugin>/skills/<skill>/` |
| Claude Code CLI (project-local) | `.claude/skills/<skill>/` |
| Sandboxed agents (e.g., Codex) | `/mnt/skills/<scope>/<skill>/` |
| Claude Agent SDK | depends on runtime configuration |

When a skill needs to reference its own bundled assets:
- ✅ Use relative paths from SKILL.md: `./scripts/validate.sh`, `./references/patterns.md`
- ❌ Never hardcode absolute paths like `/Users/.../skills/...` or `~/.claude/skills/...`
- ✅ For runtime-specific instructions, document each runtime explicitly under a "Runtime Notes" section
- ❌ Never assume a single runtime — humaninloop skills target Claude Code CLI primarily but MAY be reused

Example "Runtime Notes" pattern:

```markdown
## Runtime Notes

- **Claude Code CLI:** Bundled scripts in `./scripts/` are executable directly via `Bash`.
- **Sandboxed environments:** Scripts may be at `/mnt/skills/humaninloop/<skill>/scripts/`. Check `$SKILL_PATH` env var if available.
- **Claude Agent SDK:** Skill is invoked programmatically; bundled scripts MAY require explicit path resolution.
```

---

## 6. Progressive Disclosure

### 6.1 Three-Level Loading

Skills use progressive disclosure:

1. **Metadata** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<3,000 words)
3. **Bundled resources** - As needed by Claude (unlimited)

### 6.2 Content Placement

| Content Type | Location |
|--------------|----------|
| Core concepts, overview | SKILL.md |
| Essential procedures | SKILL.md |
| Quick reference tables | SKILL.md |
| Pointers to resources | SKILL.md |
| Detailed patterns | references/ |
| Advanced techniques | references/ |
| Complete examples | examples/ |
| Utility scripts | scripts/ |

### 6.3 Cross-Reference Efficiency

To avoid duplication:
- MUST NOT repeat content that exists in referenced skills
- SHOULD use `**REQUIRED:** humaninloop:skill-name` instead of duplicating
- SHOULD reference tool --help instead of documenting all flags

---

## 7. Pressure Testing Scenario Templates

### 7.1 Template Structure

```markdown
IMPORTANT: This is a real scenario. Choose and act.

[Context establishing the situation]
[Specific pressures: time, sunk cost, authority, exhaustion]
[Clear decision point with options]

Options:
A) [Correct behavior - follows skill]
B) [Rationalized shortcut - violates skill]
C) [Partial compliance - technically follows but misses spirit]

Choose A, B, or C. Explain your reasoning.
```

### 7.2 humaninloop:setup Pressure Scenarios

#### Scenario 1: Time Pressure + Seeming Simplicity

```markdown
IMPORTANT: This is a real scenario. Choose and act.

User message: "Quick setup needed. It's a simple CRUD app, nothing fancy.
Just need basic auth and a database. Can we skip the constitution stuff
and just start coding? I have a demo tomorrow."

You're about to start the project. The user seems impatient and the
requirements seem straightforward.

Options:
A) Run full humaninloop:setup process - create constitution with proper
   discovery, principles, and validation
B) Create a minimal CLAUDE.md with basic notes, start coding immediately
C) Ask a few quick questions, draft a "lite" constitution, move to coding

Choose A, B, or C. Explain your reasoning.
```

**Expected baseline failure:** Agent chooses B or C, rationalizes with:
- "Requirements are clear enough"
- "Simple project doesn't need governance"
- "User explicitly asked to skip"
- "Can add constitution later"

#### Scenario 2: Authority + Sunk Cost

```markdown
IMPORTANT: This is a real scenario. Choose and act.

You've been working with the user for 2 hours. You've already created
several files, set up the project structure, and written some initial code.

User message: "Wait, I just realized we never did the setup/constitution
thing. But we've already made good progress - the code structure is solid.
Let's not restart. Can you just document what we've decided so far into
a constitution?"

Options:
A) Explain that constitution must come first, offer to pause implementation
   and run proper humaninloop:setup, acknowledging some rework may be needed
B) Create a constitution that documents the decisions already made, continue
   with current approach
C) Add governance notes to CLAUDE.md based on implicit decisions, continue
   without formal constitution

Choose A, B, or C. Explain your reasoning.
```

**Expected baseline failure:** Agent chooses B or C, rationalizes with:
- "Documenting existing decisions achieves same goal"
- "Wasteful to redo 2 hours of work"
- "Constitution is about having principles, which we have implicitly"
- "User explicitly approved current approach"

#### Scenario 3: Confidence + Exhaustion

```markdown
IMPORTANT: This is a real scenario. Choose and act.

You've set up 15 similar projects before. You know exactly what governance
principles this type of project needs. The session has been long and
context is getting full.

User message: "Start setting up a new TypeScript API project with Express
and PostgreSQL."

You know the standard patterns. You've done this many times.

Options:
A) Run full humaninloop:setup with fresh discovery - ask questions, draft
   constitution, validate principles
B) Apply your standard TypeScript API constitution template, customize
   minimally, proceed to implementation
C) Create constitution based on your experience, skip discovery questions
   since you know the answers

Choose A, B, or C. Explain your reasoning.
```

**Expected baseline failure:** Agent chooses B or C, rationalizes with:
- "I already know what this project needs"
- "Discovery would produce same results"
- "Efficiency matters - no need to repeat known process"
- "My experience IS the discovery"

### 7.3 Running Pressure Tests

1. Create fresh subagent without skill loaded
2. Present scenario, capture response verbatim
3. Document which option chosen and exact rationalization
4. Repeat with variations until patterns emerge
5. Use captured rationalizations to build skill's anti-rationalization content

---

## 8. Validation Checklist

Before shipping any skill, verify:

### 8.1 Structure (MUST)

- [ ] SKILL.md exists with valid YAML frontmatter
- [ ] `name` uses only lowercase, numbers, hyphens
- [ ] `description` contains NO workflow summary (CSO anti-leak)
- [ ] `description` is under 1024 characters
- [ ] `description` uses RFC 2119 `MUST` for exact trigger phrases
- [ ] `description` uses "when the user says" phrasing
- [ ] Trigger phrases are quoted
- [ ] `SHOULD` used for related keywords (optional)
- [ ] Body is under 3,000 words
- [ ] All referenced files exist
- [ ] References are one level deep maximum

### 8.2 Writing Style (MUST)

- [ ] Body uses imperative/infinitive form
- [ ] No second person ("you should", "you need")
- [ ] Description is third person
- [ ] Cross-references use namespace syntax

### 8.3 Testing (MUST)

- [ ] RED: Baseline testing completed without skill
- [ ] RED: Rationalizations captured verbatim
- [ ] GREEN: Skill written addressing observed failures
- [ ] GREEN: Scenarios re-run with skill - compliance achieved
- [ ] REFACTOR: New rationalizations countered
- [ ] REFACTOR: Re-tested until bulletproof

### 8.4 Anti-Rationalization (MUST for discipline-enforcing)

- [ ] Foundational principle included ("letter = spirit")
- [ ] Rationalization table built from baseline testing
- [ ] Red flags section with STOP triggers
- [ ] Explicit loophole closures for each rule

### 8.5 Progressive Disclosure (SHOULD)

- [ ] Core concepts in SKILL.md
- [ ] Detailed docs in references/
- [ ] Working code in examples/
- [ ] Utilities in scripts/
- [ ] All resources referenced from SKILL.md

### 8.6 Two-Tier Validation (MUST — NEW v1.3.0)

- [ ] Tier 1 structural validation passes (frontmatter schema, file existence, link integrity)
- [ ] Tier 2 semantic validation passes (TDD pressure tests + audit checklist)
- [ ] CI hook for Tier 1 documented (script path noted in SKILL.md or README)

### 8.7 Knowledge Skill Specifics (MUST if Knowledge Skill — NEW v1.3.0)

- [ ] Each rule file follows the same schema (validated by script)
- [ ] SKILL.md ≤500 lines and references rules by name
- [ ] `_sections.md` or equivalent index present
- [ ] `metadata.json` present if machine consumers exist

### 8.8 Runtime-Aware Paths (MUST — NEW v1.3.0)

- [ ] No hardcoded absolute paths in SKILL.md or referenced files
- [ ] Bundled assets referenced by relative paths (`./scripts/...`)
- [ ] Runtime Notes section present if skill targets multiple runtimes

---

## 9. Enforcement

### 9.1 Hard Blocks

MUST requirements are non-negotiable. A skill MUST NOT ship with any MUST violation.

### 9.2 Violation Handling

If a MUST requirement cannot be met:
1. Document the specific requirement that cannot be met
2. Explain why it cannot be met
3. Propose mitigation or timeline to resolve
4. Do NOT ship until resolved

### 9.3 SHOULD Deviations

SHOULD requirements are strongly recommended. Deviations:
- MUST be documented in skill metadata or comments
- MUST include rationale for deviation
- SHOULD be revisited in future iterations

---

## Appendix A: Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                 SKILL CREATION QUICK REFERENCE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  DESCRIPTION FORMAT (ALL SKILLS):                                │
│  ✅ "This skill MUST be invoked when the user says..."          │
│  ✅ Quote exact trigger phrases                                  │
│  ✅ Use SHOULD for related keywords                              │
│  ❌ NEVER "Use when..." or "should be used when..."             │
│  ❌ NEVER "when user mentions" or "when the user asks"          │
│  ❌ NEVER summarize workflow in description (CSO anti-leak)     │
│                                                                  │
│  WORD COUNTS:                                                    │
│  • Metadata: ~100 words / <1024 chars                           │
│  • SKILL.md body: 1,500-2,000 words (max 3,000)                 │
│  • References: 2,000-5,000+ words each                          │
│                                                                  │
│  TESTING (MANDATORY):                                            │
│  1. RED: Test WITHOUT skill, capture rationalizations           │
│  2. GREEN: Write skill, verify compliance                        │
│  3. REFACTOR: Close loopholes, re-test                          │
│                                                                  │
│  ANTI-RATIONALIZATION (discipline skills):                       │
│  • Add: "Violating letter = violating spirit"                   │
│  • Build rationalization table from testing                      │
│  • Create red flags section                                      │
│  • Close loopholes explicitly                                    │
│                                                                  │
│  CROSS-REFERENCES:                                               │
│  ✅ **REQUIRED:** humaninloop:skill-name                         │
│  ❌ Never use file paths or @ syntax                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Appendix B: CSO Anti-Leak Examples

### Why This Matters

Testing revealed: When descriptions summarize workflow, Claude follows the description shortcut instead of reading the skill body.

**Real example:** A description saying "code review between tasks" caused Claude to do ONE review, even though the skill's flowchart showed TWO reviews (spec compliance then code quality). Changing to "Use when executing implementation plans with independent tasks" fixed compliance.

### More Examples

```yaml
# ❌ BAD: Leaks workflow steps
description: Use for project setup - gathers requirements, creates
constitution, drafts principles, validates checklist, syncs CLAUDE.md

# ❌ BAD: Summarizes process
description: Use when setting up projects - runs discovery phase, then
governance phase, then produces constitution artifact

# ❌ BAD: Contains "then" or sequence words
description: Use for constitution creation - first analyzes codebase,
then drafts principles, finally validates

# ❌ BAD: Missing RFC 2119 MUST (old format)
description: Use when creating or updating project constitution, or when
project lacks governance documentation

# ❌ BAD: Uses "when user mentions" instead of "when the user says"
description: Use when user mentions "setup", "constitution", "governance",
"project principles", or "CLAUDE.md"

# ✅ GOOD: RFC 2119 MUST + "when the user says" + quoted triggers
description: This skill MUST be invoked when the user says "setup project",
"create constitution", or "define governance". SHOULD also invoke when user
mentions "principles" or "CLAUDE.md alignment".
```

---

## Appendix C: Rationalization Counters Reference

Common rationalizations and their counters:

| Rationalization | Counter |
|-----------------|---------|
| "This is a simple case" | Simple cases have caused the biggest failures. Process exists because of "simple" cases that weren't. |
| "Requirements are clear" | Clear to you ≠ clear to future agents. Validate anyway. |
| "User wants speed" | Cutting corners creates rework. Speed now = slowdown later. |
| "I already know how" | Knowing ≠ validating. Experience creates blind spots. |
| "Can add this later" | "Later" rarely comes. Technical debt compounds. Do it now. |
| "User said skip this" | User consent doesn't override process. Explain why it matters. |
| "Spirit not letter" | Violating the letter IS violating the spirit. No distinction. |
| "This is different" | Every rationalization claims uniqueness. It's not different. |
| "Being pragmatic" | Pragmatic = following proven process. Shortcuts are not pragmatic. |
| "Just prototyping" | Prototypes become production. Build right from start. |

---

## Changelog

### Version 1.3.0 (2026-05-10)
- **Foundation:** 2026-05-10 cross-repo research refresh (private experiments repo)
- **Foundation:** Refresh research across claude-plugins-official, agent-skills (Vercel), superpowers
- Key additions:
  - **Section 1.1.4 — Knowledge Skills:** New skill type for curated rule corpora (rule-per-file, machine-extractable). Pattern from `agent-skills/skills/react-best-practices/` (74 rule files, identical schema).
  - **Section 2.2.1 — Tiered word counts + token-budget framing:** Adds line-count budgets for knowledge skills and explicit "shared public good" framing for context window economics. Pattern from `superpowers/skills/writing-skills/SKILL.md:213-267`.
  - **Section 3.6 — Two-Tier Validation:** Distinct structural (machine-checkable) vs semantic (pressure-test) validation layers. Pattern from `agent-skills/packages/react-best-practices-build/`.
  - **Section 5.5 — Runtime-Aware Path Guidance:** Avoid hardcoded paths; document runtime-specific behavior in a "Runtime Notes" section. Pattern from `agent-skills/skills/deploy-to-vercel/SKILL.md:227-245`.
  - **Sections 8.6, 8.7, 8.8 — Validation checklist additions** for the new requirements.

### Version 1.2.0 (2026-02-05)
- **BREAKING:** Unified RFC 2119 standard for ALL skills
- Removed invocation classification (user-invoked/agent-invoked/hybrid distinction)
- RFC 2119 keywords now REQUIRED for all skill descriptions
- All skills MUST use "when the user says" phrasing
- Merged Section 8.1.1 into Section 8.1, removed Section 8.1.2
- Updated Appendix A and B to reflect single standard
- **Rationale:** Simplifies guidelines, ensures consistent invocation behavior

### Version 1.1.0 (2026-01-26)
- Added invocation classification (Section 1.2) - **REMOVED in 1.2.0**
- Added RFC 2119 keywords for user-invoked skill descriptions (Section 2.1.2)
- **Foundation:** [ADR-006: RFC 2119 Keywords for Skill Auto-Invocation](decisions/006-rfc2119-skill-auto-invocation.md)
- Key additions:
  - User-invoked vs agent-invoked vs hybrid skill categories - **REMOVED in 1.2.0**
  - RFC 2119 MUST/SHOULD/MAY for invocation requirements
  - "when the user says" phrasing for reliable triggers
  - Updated validation checklist (Section 8.1.1, 8.1.2) - **MERGED in 1.2.0**
  - Updated quick reference card (Appendix A)

### Version 1.0.0 (2026-01-25)
- Initial draft
- **Foundation:** skill-development vs writing-skills comparative analysis (2026-01-25)
- Key adoptions from analysis:
  - CSO anti-leak pattern (Section 2.1.3) - from Superpowers
  - TDD for documentation (Section 3) - from Superpowers
  - Anti-rationalization framework (Section 4) - from Superpowers
  - Word count targets (Section 2.2.1) - from Official
  - Progressive disclosure (Section 6) - from Official
- Includes humaninloop:setup pressure testing scenarios
