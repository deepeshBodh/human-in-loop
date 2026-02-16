# Traceability Patterns

Cross-reference patterns, dependency chains, and completeness validation rules for the five technical requirement artifacts.

## The Traceability Web

Every artifact connects to others. No artifact stands alone. The traceability web ensures that business intent is preserved through technical translation and that every technical decision traces to a business justification.

```
Business Specifications (FR-XXX, user stories)
        │
        ▼
┌─────────────────────────────────────────────┐
│          Technical Requirements (TR-XXX)      │
│          ← maps to → FR-XXX                   │
│          ← constrained by → C-XXX             │
│          ← qualified by → NFR-XXX             │
│          ← depends on → INT-XXX               │
│          ← handles → DS-XXX                   │
└─────────────────────────────────────────────┘
        │
        ▼
  Design / Architecture (downstream)
```

## Mandatory Cross-References

### TR -> FR (Business Traceability)

Every technical requirement MUST trace to at least one business functional requirement.

**Pattern:**
```markdown
## TR-001: Authentication Flow

**Source:** FR-001, FR-003
```

**Validation rule:** Scan all TR entries. Each MUST have a non-empty `Source` field referencing at least one FR-XXX.

**Reverse check:** Scan all FRs from the business specification. Each FR MUST appear as a source in at least one TR. If an FR has no corresponding TR, it was missed during translation.

### TR -> C (Constraint Awareness)

Technical requirements SHOULD reference constraints that affect their implementation.

**Pattern:**
```markdown
## TR-005: Data Storage

**Dependencies:**
- C-001 (must use existing PostgreSQL cluster)
- C-003 (zero-downtime migration required)
```

**Why this matters:** When architects read a TR, they need to see which constraints apply immediately, not discover them later in a separate document.

### TR -> NFR (Quality Binding)

Technical requirements SHOULD reference NFRs that set quality targets for their operation.

**Pattern:**
```markdown
## TR-001: Authentication Flow

**Dependencies:**
- NFR-001 (p95 latency < 200ms applies to this flow)
- NFR-004 (zero plaintext PII in error responses)
```

### TR -> INT (Integration Dependency)

Technical requirements that consume external systems MUST reference the integration entry.

**Pattern:**
```markdown
## TR-008: Payment Processing

**Dependencies:**
- INT-001 (Stripe API for charge creation)
- INT-002 (SendGrid for payment confirmation email)
```

### TR -> DS (Data Handling)

Technical requirements that create, read, update, or delete classified data SHOULD reference the data sensitivity entry.

**Pattern:**
```markdown
## TR-001: Authentication Flow

**Dependencies:**
- DS-002 (password hash -- restricted classification)
- DS-001 (user email -- confidential classification)
```

### NFR -> Source (Justification)

Every NFR MUST trace to a business source that justifies the target.

**Pattern:**
```markdown
## NFR-001: API Response Latency

**Source:** FR-001 implies real-time user interaction;
           stakeholder expectation of "instant feedback" in spec section 3.2
```

**Validation rule:** No NFR without a source. Targets pulled from thin air are not requirements -- they are guesses.

### INT -> TR (Usage Reference)

Every integration SHOULD be referenced by at least one TR.

**Pattern:**
```markdown
## INT-001: Stripe Payment API

**Referenced By:**
- TR-005 (payment processing flow)
- TR-008 (refund handling)
```

**Validation rule:** An integration entry referenced by no TR is either premature (no requirement needs it yet) or indicates a missing TR.

### DS -> TR (Handling Reference)

Every data sensitivity entry SHOULD be referenced by at least one TR.

**Pattern:**
```markdown
## DS-001: User Email

**Referenced By:**
- TR-001 (authentication flow)
- TR-012 (notification preferences)
```

### INT -> DS (Data Flow Classification)

Integration data exchange SHOULD reference data sensitivity classifications.

**Pattern:**
```markdown
## INT-001: Stripe Payment API

### Data Exchanged

| Direction | Data | Classification |
|-----------|------|---------------|
| Outbound | Payment amount, customer ref | DS-003 (confidential) |
| Inbound | Transaction ID, status | DS-004 (internal) |
```

## Dependency Chains

Some traceability relationships form chains that must be consistent end-to-end.

### Business-to-Technical Chain

```
FR-001 (business: "users can sign in")
  └── TR-001 (technical: authentication flow)
        ├── C-001 (constraint: must use existing identity provider)
        ├── NFR-001 (quality: p95 < 200ms)
        ├── INT-003 (integration: Auth0 OIDC)
        │     └── DS-002 (data: password -- restricted)
        └── DS-001 (data: email -- confidential)
```

**Reading this chain:** Business requirement FR-001 is implemented by TR-001, which is constrained by C-001, must meet NFR-001 latency, depends on INT-003 for identity, and handles DS-001 and DS-002 classified data.

### Constraint Impact Chain

```
C-002 (regulatory: GDPR Art. 17 right to erasure)
  ├── TR-015 (technical: data deletion workflow)
  ├── DS-001 (data: must be deletable within 30 days)
  ├── DS-003 (data: must be deletable within 30 days)
  └── INT-001 (integration: must support deletion API)
```

**Reading this chain:** Regulatory constraint C-002 affects TR-015 implementation, requires DS-001 and DS-003 to have deletion procedures, and requires INT-001 to support data deletion.

### Integration Failure Chain

```
INT-001 (integration: Stripe -- CRITICAL)
  ├── TR-005 (dependent: payment processing)
  │     └── FR-003 (business: "users can purchase")
  └── Failure impact: FR-003 completely blocked
```

**Reading this chain:** If INT-001 fails, TR-005 cannot function, which means FR-003 is not satisfied. This chain justifies the "Critical" classification and the need for robust fallback strategies.

## Completeness Validation

### Forward Traceability (FR -> TR)

Check that every business requirement has technical coverage.

**Procedure:**
1. List all FR-XXX from the business specification
2. For each FR, find TR entries that reference it as Source
3. Flag any FR with zero TR coverage

**Output format:**
```markdown
## Forward Traceability Check

| FR | Technical Requirements | Status |
|----|----------------------|--------|
| FR-001 | TR-001, TR-002, TR-003 | Covered |
| FR-002 | TR-004, TR-005 | Covered |
| FR-003 | (none) | **GAP -- missing TR** |
```

### Backward Traceability (TR -> FR)

Check that every technical requirement traces to a business source.

**Procedure:**
1. List all TR-XXX entries
2. For each TR, verify Source field references valid FR(s)
3. Flag any TR with no source (orphan)

**Output format:**
```markdown
## Backward Traceability Check

| TR | Source FRs | Status |
|----|-----------|--------|
| TR-001 | FR-001 | Valid |
| TR-002 | FR-001 | Valid |
| TR-007 | (none) | **ORPHAN -- no business source** |
```

### NFR Measurability Check

Verify every NFR has all three required elements.

**Procedure:**
1. List all NFR-XXX entries
2. For each, verify: target (numeric), measurement method, source
3. Flag any NFR missing elements

**Output format:**
```markdown
## NFR Measurability Check

| NFR | Has Target | Has Method | Has Source | Status |
|-----|-----------|------------|-----------|--------|
| NFR-001 | 200ms p95 | APM monitoring | FR-001 | Complete |
| NFR-002 | 99.9% | (missing) | SLA doc | **INCOMPLETE -- no method** |
| NFR-003 | (missing) | Load test | Growth plan | **INCOMPLETE -- no target** |
```

### Integration Failure Coverage Check

Verify every integration has failure mode analysis.

**Procedure:**
1. List all INT-XXX entries
2. For each, verify: failure modes documented, fallback for each mode
3. Flag any integration with incomplete coverage

**Output format:**
```markdown
## Integration Failure Coverage

| INT | System | Failure Modes | Fallbacks | Status |
|-----|--------|--------------|-----------|--------|
| INT-001 | Stripe | 5 modes | 5 fallbacks | Complete |
| INT-002 | SendGrid | 3 modes | 1 fallback | **INCOMPLETE -- 2 modes without fallback** |
```

### Data Classification Coverage Check

Verify every data element handled by TRs is classified.

**Procedure:**
1. Identify all data elements mentioned in TR acceptance criteria
2. For each, verify a DS-XXX entry exists
3. Flag unclassified data

**Output format:**
```markdown
## Data Classification Coverage

| Data Element | DS Entry | Classification | Status |
|-------------|----------|---------------|--------|
| User email | DS-001 | Confidential | Classified |
| Session token | DS-006 | Restricted | Classified |
| User avatar URL | (none) | (unclassified) | **GAP -- needs DS entry** |
```

## Cross-Artifact Consistency Rules

### Rule 1: ID References Must Resolve

Every cross-reference (TR-XXX, C-XXX, NFR-XXX, INT-XXX, DS-XXX) appearing in any artifact MUST correspond to an actual entry in the appropriate artifact file.

**Violation example:** TR-005 references "INT-003" but integrations.md only has INT-001 and INT-002.

### Rule 2: Bidirectional References Should Match

If TR-005 lists INT-001 as a dependency, then INT-001 SHOULD list TR-005 in its "Referenced By" section. Mismatches indicate incomplete traceability.

### Rule 3: Classification Consistency

If INT-001 says data exchanged references DS-003, then DS-003 SHOULD list INT-001 in its "Referenced By" section. The classification level in the integration table MUST match the level in the DS entry.

### Rule 4: No Contradictory Constraints

If C-001 says "must use existing PostgreSQL" and a TR says "must support any SQL database," there is a contradiction. Constraints restrict -- TRs must be compatible with all applicable constraints.

### Rule 5: NFR Targets Must Be Achievable Under Constraints

If NFR-001 sets p95 < 50ms but C-001 constrains to a legacy system known to have 100ms baseline latency, the combination is infeasible. Flag conflicts between NFRs and constraints.

## Traceability Matrix Template

For complex features, produce a summary matrix:

```markdown
## Traceability Matrix

| FR | TRs | Constraints | NFRs | Integrations | Data |
|----|-----|-------------|------|-------------|------|
| FR-001 | TR-001, TR-002, TR-003 | C-001 | NFR-001, NFR-004 | INT-003 | DS-001, DS-002 |
| FR-002 | TR-004, TR-005 | - | NFR-001 | INT-001 | DS-003 |
| FR-003 | TR-006, TR-007, TR-008 | C-002 | NFR-002 | INT-001, INT-002 | DS-003, DS-004 |
```

This matrix provides a single view of the entire traceability web, making gaps immediately visible.
