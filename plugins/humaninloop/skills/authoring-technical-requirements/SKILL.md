---
name: authoring-technical-requirements
description: This skill MUST be invoked when the user says "write technical requirements", "define constraints", "define NFRs", "map integrations", "classify data sensitivity", or "infrastructure requirements". SHOULD also invoke when user mentions "TR-", "C-", "NFR-", "IP-", "INT-", "DS-", "non-functional", "system integration", "infrastructure provisioning", or "data classification". Produces three traceable analysis artifacts from business specifications.
---

# Authoring Technical Requirements

## Overview

Translate business specifications into three traceable analysis artifacts: requirements, constraints-and-decisions, and NFRs. Every artifact traces to a business source. Every target is measurable. Every constraint accounts for its design impact.

**Violating the letter of the rules is violating the spirit of the rules.**

## When to Use

- Translating functional requirements into technical requirements (TR-XXX)
- Documenting hard technical constraints (C-XXX)
- Defining measurable non-functional requirements (NFR-XXX)
- Cataloguing external system integrations (INT-XXX)
- Classifying data elements by sensitivity level (DS-XXX)
- Quality gate before architectural design begins

## When NOT to Use

- **Writing business requirements** -- Use `humaninloop:authoring-requirements` instead
- **Designing solutions** -- This skill defines the problem space, not solutions
- **Choosing technologies** -- Constraints document real boundaries, not preferences
- **Implementation planning** -- Use planning skills after technical requirements exist

## The Three Analysis Artifacts

Each artifact uses a distinct ID prefix and traces to business sources. These are produced during Phase 1 (Analysis) of `/humaninloop:plan`: requirements.md, constraints-and-decisions.md, and nfrs.md.

> **Note:** Integration maps (INT-XXX) are now embedded as `x-integration` extensions in `contracts/api.yaml` during Phase 2 (Design). Data sensitivity classifications (DS-XXX) are now embedded per-entity in `data-model.md` during Phase 2 (Design). See `humaninloop:patterns-api-contracts` and `humaninloop:patterns-entity-modeling` skills respectively.

See [ARTIFACT-TEMPLATES.md](references/ARTIFACT-TEMPLATES.md) for complete field definitions and examples.

### 1. Technical Requirements (requirements.md) -- TR-XXX

Map every business FR to one or more TRs. A single FR-001 ("users can sign in") may decompose into TR-001 (authentication flow), TR-002 (token management), TR-003 (session handling).

| Field | Required | Purpose |
|-------|----------|---------|
| ID | Yes | TR-XXX sequential format |
| Source FR | Yes | Which FR(s) this implements |
| Description | Yes | Technical capability (WHAT, not HOW) |
| Acceptance Criteria | Yes | Testable technical conditions |
| Dependencies | No | Other TRs, constraints, or NFRs referenced |

**No orphan TRs.** Every TR maps to at least one FR. **No unmapped FRs.** Every FR has at least one TR.

**No exceptions:** Not for "simple" systems. Not for "obvious" mappings. Not even when the FR appears to map 1:1 — decompose anyway.

### 2. Constraints and Decisions (constraints-and-decisions.md) -- C-XXX / D-XXX

Document hard boundaries (constraints) and the technology decisions shaped by them, in a single unified artifact.

**Section 1: Hard Constraints (C-XXX)**

| Field | Required | Purpose |
|-------|----------|---------|
| ID | Yes | C-XXX sequential format |
| Type | Yes | infrastructure / compatibility / regulatory / migration / organizational |
| Description | Yes | The hard boundary |
| Source | Yes | Where this constraint originates |
| Severity | Yes | blocking / significant / minor |
| Impact | Yes | What design choices this eliminates; references D-XXX decisions it shapes |

**Section 2: Technology Decisions (D-XXX)**

| Field | Required | Purpose |
|-------|----------|---------|
| ID | Yes | D-XXX sequential format |
| Context | Yes | The situation requiring a decision |
| Options | Yes | Alternatives evaluated |
| Choice | Yes | Selected option |
| Consequences | Yes | Trade-offs accepted |
| Rationale | Yes | Why this choice; references C-XXX constraints that shaped it |

**Constraints are facts, not preferences.** Each decision record MUST reference the constraints that shaped the choice. Each constraint impact field SHOULD reference decisions it influences.

**No exceptions:** Not for "well-known" constraints. Not for "obvious" technology choices. Not even when the team has consensus — document the constraint and its source explicitly.

**Section 3: Infrastructure Requirements (IP-XXX)**

| Field | Required | Purpose |
|-------|----------|---------|
| ID | Yes | IP-XXX sequential format |
| Type | Yes | compute / networking / storage / ci-cd / monitoring / security / environment-config |
| Source | Yes | C-XXX or NFR-XXX that necessitates this provisioning |
| Description | Yes | What must be provisioned (WHAT, not HOW) |
| Acceptance Criteria | Yes | Verifiable provisioning conditions |

**Every constraint that implies platform work gets an IP-XXX item.** Constraints document boundaries; IP-XXX items document what those boundaries require operationally.

### 3. Non-Functional Requirements (nfrs.md) -- NFR-XXX

Define measurable quality attributes. Every NFR has a numeric target.

| Field | Required | Purpose |
|-------|----------|---------|
| ID | Yes | NFR-XXX sequential format |
| Category | Yes | performance / availability / scalability / security / other |
| Requirement | Yes | The quality attribute |
| Target | Yes | Specific numeric threshold |
| Measurement Method | Yes | How to verify the target is met |
| Source | Yes | Business requirement or stakeholder justifying this |

**"Fast" is not a requirement.** "p95 response time < 200ms under 1000 concurrent users, measured by APM" is.

**No exceptions:** Not for "standard" performance expectations. Not for "obvious" availability targets. Every NFR gets a number, a measurement method, and a source — no deferrals to "later during design."

### 4. [Phase 2] System Integrations -- INT-XXX (embedded in contracts/api.yaml)

> Integrations are now documented as `x-integration` extensions per endpoint in `contracts/api.yaml` during Phase 2 (Design). See the `humaninloop:patterns-api-contracts` skill for details.

Fields per integration: system name, protocol, API version, criticality, failure modes (detection, impact, fallback), authentication details.

**Optimistic integration maps are incomplete.** Every external dependency fails eventually. Document what happens when it does.

### 5. [Phase 2] Data Sensitivity Classifications -- DS-XXX (embedded in data-model.md)

> Sensitivity classifications are now documented per-entity/per-attribute in `data-model.md` during Phase 2 (Design). See the `humaninloop:patterns-entity-modeling` skill for details.

Fields per entity: classification level, encryption at rest/in transit, retention period, access control, audit requirements, masking rules. Compliance mapping table per entity.

## Traceability Rules

Every artifact connects to others. No artifact stands alone.

See [TRACEABILITY-PATTERNS.md](references/TRACEABILITY-PATTERNS.md) for detailed cross-reference patterns and dependency chains.

**Mandatory links:**
- TR -> FR (every technical requirement traces to business source)
- NFR -> source (every quality attribute has a justification)
- C -> D (constraints reference the decisions they shape; decisions reference constraints that shaped them)
- C -> impact (every constraint identifies what it restricts)
- C/NFR -> IP (constraints and NFRs with infrastructure implications reference IP-XXX items)

**Completeness check:** No FR without a TR. No TR without acceptance criteria. No NFR without a numeric target. No constraint without a source. No decision without referenced constraints. No infrastructure-implying constraint without an IP-XXX.

## Technology-Agnostic Writing

Describe WHAT the system must achieve, not HOW.

| Wrong (HOW) | Right (WHAT) |
|-------------|--------------|
| "Must use PostgreSQL" | "Must support ACID transactions on relational data" |
| "Must implement OAuth 2.0" | "Must support secure delegated authentication" |
| "Must use Redis for caching" | "Must cache frequently-accessed data with < 10ms retrieval" |
| "Must encrypt with AES-256" | "Must encrypt at rest using industry-standard algorithms" |

**Exception:** Constraints MAY name specific technologies when they reflect real infrastructure facts (e.g., "existing production database is PostgreSQL 15").

## Quality Checklist

Before finalizing, verify:

- [ ] Every FR has at least one TR (no unmapped business requirements)
- [ ] Every TR maps to at least one FR (no orphan technical requirements)
- [ ] Every TR has testable acceptance criteria
- [ ] Every constraint has a source, type, and severity classification
- [ ] Every decision references the constraints that shaped it (C-XXX ↔ D-XXX)
- [ ] Every NFR has a numeric target AND measurement method
- [ ] Every constraint implying platform provisioning has a corresponding IP-XXX
- [ ] Cross-references between artifacts are consistent
- [ ] Language is technology-agnostic (except real infrastructure constraints)
- [ ] ID sequences are sequential with no gaps (TR-001, TR-002..., C-001..., D-001..., IP-001...)

## Common Mistakes

### Transcribing Instead of Translating
Copying FRs as TRs unchanged. Translation means decomposition: one FR often becomes multiple TRs with distinct technical concerns.

### Unmeasurable NFRs
"System must be highly available." Replace with: "System MUST maintain 99.9% uptime measured monthly, excluding scheduled maintenance windows."

### Missing Failure Modes
Listing integrations without documenting what happens when they fail. Every `INT-XXX` entry needs explicit failure modes and fallback strategies.

### Preferences Disguised as Constraints
"Must use React" is a preference unless there is a real constraint (existing team expertise, existing codebase). Constraints trace to facts.

### Unclassified Data
Handling user data without explicit sensitivity classification. Every data element touching the system needs a DS-XXX entry before design begins.

### Orphan Artifacts
TRs that trace to no FR. NFRs with no source justification. Integrations referenced by no TR. Every artifact connects to the web of traceability.

## Red Flags -- STOP and Restart Properly

If any of these thoughts arise, STOP immediately:

- "This FR is straightforward, no need for a separate TR"
- "NFR targets can be filled in during planning"
- "Only two integrations, no need for a formal catalogue"
- "Data sensitivity is obvious, no need to classify"
- "Constraints are implied, everyone knows them"
- "This is a simple system, skip the failure modes"

**All of these mean:** A shortcut is being rationalized. Restart with the full process.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Requirements are straightforward, TRs would just duplicate FRs" | Straightforward FRs hide technical complexity. Decompose anyway -- translation is the job, not transcription. |
| "NFR targets can be refined later during design" | Targets set during design are reverse-engineered from implementation, not derived from business needs. Define now. |
| "Only a few integrations, formal mapping is overkill" | Few integrations with undocumented failure modes cause the worst outages. Catalogue every one. |
| "Data classification is a security team concern" | Every technical requirement that touches data needs classification before design. Security reviews supplement, not replace. |
| "Constraints are well-known to the team" | Implicit constraints cause the costliest mid-implementation discoveries. Make every one explicit. |
| "This is a simple system" | Simple systems with missing technical requirements become complex debugging sessions. Follow the full process. |
