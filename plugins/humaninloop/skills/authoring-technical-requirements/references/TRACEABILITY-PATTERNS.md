# Traceability Patterns

Cross-reference patterns, dependency chains, and completeness validation rules for plan artifacts.

## The Traceability Web

Every artifact connects to others. No artifact stands alone. The traceability web ensures that business intent is preserved through technical translation and design, and that every technical decision traces to a business justification.

```
Business Specifications (FR-XXX, user stories)
        │
        ▼
┌─────────────────────────────────────────────┐
│          Technical Requirements (TR-XXX)      │
│          ← maps to → FR-XXX                   │
│          ← constrained by → C-XXX             │
│          ← qualified by → NFR-XXX             │
│          ← shaped by → D-XXX                  │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│          Design Artifacts                     │
│          Entity ← traces to → TR-XXX          │
│          Endpoint ← traces to → User Action   │
│          Schema ← matches → Entity            │
│          Integration ← documented in → API    │
│          Sensitivity ← annotated on → Entity  │
└─────────────────────────────────────────────┘
```

## Phase 1 Cross-References (Analysis Artifacts)

### TR → FR (Business Traceability)

Every technical requirement MUST trace to at least one business functional requirement.

**Pattern:**
```markdown
## TR-001: Authentication Flow

**Source:** FR-001, FR-003
```

**Validation rule:** Scan all TR entries. Each MUST have a non-empty `Source` field referencing at least one FR-XXX.

**Reverse check:** Scan all FRs from the business specification. Each FR MUST appear as a source in at least one TR. If an FR has no corresponding TR, it was missed during translation.

### TR → C (Constraint Awareness)

Technical requirements SHOULD reference constraints that affect their implementation.

**Pattern:**
```markdown
## TR-005: Data Storage

**Dependencies:**
- C-001 (must use existing PostgreSQL cluster)
- C-003 (zero-downtime migration required)
```

**Why this matters:** When architects read a TR, they need to see which constraints apply immediately, not discover them later in a separate document.

### TR → NFR (Quality Binding)

Technical requirements SHOULD reference NFRs that set quality targets for their operation.

**Pattern:**
```markdown
## TR-001: Authentication Flow

**Dependencies:**
- NFR-001 (p95 latency < 200ms applies to this flow)
- NFR-004 (zero plaintext PII in error responses)
```

### C → D (Constraint-Decision Link)

Constraints SHOULD reference the decisions they shaped. Decisions MUST reference the constraints that shaped them.

**Pattern (Constraint side):**
```markdown
## C-001: Existing PostgreSQL Infrastructure

**Impact:**
- Eliminates NoSQL options
- Shapes D-001 (database choice)
```

**Pattern (Decision side):**
```markdown
## D-001: Primary Database

**Shaped By:**
- C-001 (must use existing PostgreSQL cluster)
```

**Validation rule:** Every D-XXX entry MUST have a non-empty `Shaped By` field. Every C-XXX entry SHOULD reference at least one D-XXX in its Impact section.

### NFR → Source (Justification)

Every NFR MUST trace to a business source that justifies the target.

**Pattern:**
```markdown
## NFR-001: API Response Latency

**Source:** FR-001 implies real-time user interaction;
           stakeholder expectation of "instant feedback" in spec section 3.2
```

**Validation rule:** No NFR without a source. Targets pulled from thin air are not requirements — they are guesses.

## Phase 2 Cross-References (Design Artifacts)

### Entity → FR (Requirement Traceability)

Every entity MUST trace to at least one functional requirement.

**Pattern:**
```markdown
## User

**Description:** Represents a registered user account
**Traceability:** FR-001, FR-003
```

**Validation rule:** Every entity MUST have a `Traceability` field with at least one FR-XXX reference.

### Entity Attribute → Sensitivity (Data Classification)

Every attribute handling PII or sensitive data MUST have a sensitivity annotation.

**Pattern:**
```markdown
### Attributes

| Attribute | Type | Constraints | Sensitivity |
|-----------|------|------------|-------------|
| email | String(255) | Unique, required | Confidential — encrypt at rest, mask in logs |
| password_hash | String(60) | Required | Restricted — encrypt at rest, never log |
| display_name | String(100) | Required | Public |
```

**Validation rule:** Every Confidential+ attribute MUST have a detailed sensitivity section with encryption, retention, access control, and audit requirements.

### Endpoint → User Action (Action Coverage)

Every user action from the specification SHOULD map to at least one API endpoint.

**Pattern:** The user action "create account" maps to `POST /users`.

**Validation rule:** List all user actions from spec.md user stories. Each SHOULD have a corresponding endpoint in the API contract.

### Schema → Entity (Model Alignment)

API request/response schemas MUST match data model entities.

**Pattern:** The `UserResponse` schema fields must correspond to `User` entity attributes.

**Validation rule:** For each response schema, verify that field names, types, and constraints match the corresponding entity definition.

### Endpoint → Integration (External System Documentation)

Endpoints that wrap external systems MUST include `x-integration` documentation.

**Pattern:**
```yaml
/payments:
  post:
    x-integration:
      system: "Stripe v2024-01"
      criticality: "Critical"
      failure_modes:
        - failure: "Timeout"
          detection: "HTTP timeout"
          impact: "Payment not processed"
          fallback: "Retry with exponential backoff"
```

**Validation rule:** Every endpoint whose implementation depends on an external system MUST have integration boundary documentation with failure modes and fallback strategies.

## Dependency Chains

Some traceability relationships form chains that must be consistent end-to-end.

### Full Traceability Chain

```
FR-001 (business: "users can sign in")
  └── TR-001 (technical: authentication flow)
        ├── C-001 (constraint: must use existing identity provider)
        ├── D-002 (decision: JWT with refresh tokens)
        ├── NFR-001 (quality: p95 < 200ms)
        └── Entity: User
              ├── email (Confidential)
              ├── password_hash (Restricted)
              └── Endpoint: POST /auth/token
                    └── x-integration: Auth0 (Critical)
```

**Reading this chain:** Business requirement FR-001 is implemented by TR-001, which is constrained by C-001, informed by decision D-002, must meet NFR-001 latency, produces the User entity with classified attributes, exposed via POST /auth/token which integrates with Auth0.

### Constraint Impact Chain

```
C-002 (regulatory: GDPR Art. 17 right to erasure)
  ├── TR-015 (technical: data deletion workflow)
  ├── D-004 (decision: soft-delete with 30-day purge)
  ├── Entity: User → email (retention: 30 days after closure)
  └── Endpoint: DELETE /users/{id}
```

**Reading this chain:** Regulatory constraint C-002 drives TR-015 and decision D-004, requires User.email to have a 30-day retention policy, and necessitates a DELETE endpoint.

## Completeness Validation

### Forward Traceability (FR → TR)

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
| FR-003 | (none) | **GAP — missing TR** |
```

### Backward Traceability (TR → FR)

Check that every technical requirement traces to a business source.

**Procedure:**
1. List all TR-XXX entries
2. For each TR, verify Source field references valid FR(s)
3. Flag any TR with no source (orphan)

### Decision Traceability (D → C)

Check that every decision references the constraints that shaped it.

**Procedure:**
1. List all D-XXX entries
2. For each, verify Shaped By field references valid C-XXX or NFR-XXX entries
3. Flag any decision without constraint references

### NFR Measurability Check

Verify every NFR has all three required elements.

**Procedure:**
1. List all NFR-XXX entries
2. For each, verify: target (numeric), measurement method, source
3. Flag any NFR missing elements

### Entity-to-FR Traceability

Check that every entity traces to business requirements.

**Procedure:**
1. List all entities in data-model.md
2. For each, verify Traceability field references valid FR-XXX entries
3. Flag any entity with no FR reference

### Data Sensitivity Coverage

Verify every entity attribute handling PII is classified.

**Procedure:**
1. Identify all attributes in entity definitions
2. For each attribute that could contain PII (email, phone, name, address, etc.), verify sensitivity annotation
3. Flag unclassified sensitive data

### Integration Coverage

Verify every external system dependency has failure mode documentation.

**Procedure:**
1. Identify all endpoints with x-integration in contracts/api.yaml
2. For each, verify failure modes and fallback strategies documented
3. Flag any integration without complete failure mode coverage

## Cross-Artifact Consistency Rules

### Rule 1: ID References Must Resolve

Every cross-reference (TR-XXX, C-XXX, D-XXX, NFR-XXX) appearing in any artifact MUST correspond to an actual entry in the appropriate artifact file.

**Violation example:** TR-005 references "C-003" but constraints-and-decisions.md only has C-001 and C-002.

### Rule 2: Bidirectional References Should Match

If TR-005 lists C-001 as a dependency, then C-001 SHOULD list TR-005 in its Impact section. Mismatches indicate incomplete traceability.

### Rule 3: Schema-Entity Consistency

API response schema fields MUST match entity attribute names and types. If the User entity has `display_name` (String), the UserResponse schema must also have `display_name` (string), not `displayName` or `name`.

### Rule 4: No Contradictory Constraints

If C-001 says "must use existing PostgreSQL" and a TR says "must support any SQL database," there is a contradiction. Constraints restrict — TRs must be compatible with all applicable constraints.

### Rule 5: NFR Targets Must Be Achievable Under Constraints and Decisions

If NFR-001 sets p95 < 50ms but D-001 chose a synchronous external API call with 100ms baseline latency, the combination is infeasible. Flag conflicts between NFRs and design decisions.

### Rule 6: Sensitivity-Response Alignment

If an entity attribute is classified Restricted, it MUST NOT appear in standard API response schemas. Password hashes, SSNs, and payment card numbers should never be returned by the API.

## Traceability Matrix Template

For complex features, produce a summary matrix:

```markdown
## Traceability Matrix

| FR | TRs | Constraints | Decisions | NFRs | Entities | Endpoints |
|----|-----|-------------|-----------|------|----------|-----------|
| FR-001 | TR-001, TR-002, TR-003 | C-001 | D-002 | NFR-001, NFR-004 | User | POST /auth/token |
| FR-002 | TR-004, TR-005 | - | D-001 | NFR-001 | Order, Payment | POST /orders |
| FR-003 | TR-006, TR-007, TR-008 | C-002 | D-004 | NFR-002 | User, Order | DELETE /users/{id} |
```

This matrix provides a single view of the entire traceability web from business requirements through design, making gaps immediately visible.
