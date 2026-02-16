---
name: authoring-technical-requirements
description: >
  This skill MUST be invoked when the user says "write technical requirements",
  "define constraints", "define NFRs", "map integrations", or "classify data
  sensitivity". SHOULD also invoke when user mentions "TR-", "C-", "NFR-",
  "INT-", "DS-", "non-functional", "system integration", or "data classification".
  Produces five traceable technical artifacts from business specifications.
---

# Authoring Technical Requirements

## Overview

Translate business specifications into five traceable technical artifacts: requirements, constraints, NFRs, integration maps, and data sensitivity classifications. Every artifact traces to a business source. Every target is measurable. Every integration accounts for failure.

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

## The Five Artifacts

Each artifact uses a distinct ID prefix and traces to business sources. Produce in two passes: Pass 1 (requirements.md + constraints.md), Pass 2 (nfrs.md + integrations.md + data-sensitivity.md).

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

### 2. Technical Constraints (constraints.md) -- C-XXX

Document hard boundaries that limit implementation choices.

| Field | Required | Purpose |
|-------|----------|---------|
| ID | Yes | C-XXX sequential format |
| Type | Yes | infrastructure / compatibility / regulatory / migration |
| Description | Yes | The hard boundary |
| Source | Yes | Where this constraint originates |
| Impact | Yes | What design choices this eliminates |

**Constraints are facts, not preferences.** "Must use existing PostgreSQL cluster" (real infrastructure constraint) differs from "should use the same framework" (preference -- not a constraint).

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

### 4. System Integrations (integrations.md) -- INT-XXX

Catalogue every external system boundary.

| Field | Required | Purpose |
|-------|----------|---------|
| ID | Yes | INT-XXX sequential format |
| System | Yes | External system name and version |
| Protocol | Yes | REST, GraphQL, gRPC, webhook, SDK, etc. |
| Endpoints Used | Yes | Specific endpoints or operations consumed |
| Data Exchanged | Yes | What flows in each direction |
| Failure Modes | Yes | What can go wrong (timeout, 5xx, rate limit) |
| Fallback Strategy | Yes | How the system behaves when this integration fails |

**Optimistic integration maps are incomplete.** Every external dependency fails eventually. Document what happens when it does.

### 5. Data Sensitivity Classifications (data-sensitivity.md) -- DS-XXX

Classify every data element the system handles.

| Field | Required | Purpose |
|-------|----------|---------|
| ID | Yes | DS-XXX sequential format |
| Data Element | Yes | What data this is |
| Classification | Yes | public / internal / confidential / restricted |
| Encryption | Yes | At rest and in transit requirements |
| Retention | Yes | How long, and what happens after |
| Compliance | No | GDPR, HIPAA, PCI-DSS, SOC2 mappings |
| Access Control | Yes | Who can read, write, delete |

## Traceability Rules

Every artifact connects to others. No artifact stands alone.

See [TRACEABILITY-PATTERNS.md](references/TRACEABILITY-PATTERNS.md) for detailed cross-reference patterns and dependency chains.

**Mandatory links:**
- TR -> FR (every technical requirement traces to business source)
- NFR -> source (every quality attribute has a justification)
- INT -> TR (integrations referenced by the TRs that need them)
- DS -> TR (data elements referenced by TRs that handle them)
- C -> impact (every constraint identifies what it restricts)

**Completeness check:** No FR without a TR. No TR without acceptance criteria. No NFR without a numeric target. No integration without failure modes. No data element without classification.

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
- [ ] Every constraint has a source and type classification
- [ ] Every NFR has a numeric target AND measurement method
- [ ] Every integration has failure modes AND fallback strategies
- [ ] Every data element has classification, encryption, and retention
- [ ] Cross-references between artifacts are consistent
- [ ] Language is technology-agnostic (except real infrastructure constraints)
- [ ] ID sequences are sequential with no gaps (TR-001, TR-002...)

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
