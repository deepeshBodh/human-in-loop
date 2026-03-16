# Artifact Templates

Complete templates and field definitions for the six plan artifacts. Each template shows the full document structure with all required fields.

## 1. Technical Requirements (requirements.md)

### Document Template

```markdown
# Technical Requirements: {feature_id}

> Technical decomposition of business functional requirements.
> Generated during plan workflow.

---

## Traceability Summary

| Source FR | Technical Requirements | Coverage |
|-----------|----------------------|----------|
| FR-001 | TR-001, TR-002, TR-003 | Full |
| FR-002 | TR-004, TR-005 | Full |
| FR-003 | TR-006 | Full |

---

## TR-001: [Descriptive Title]

**Source:** FR-001
**Priority:** MUST

**Description:**
System MUST [technical capability described in technology-agnostic terms].

**Acceptance Criteria:**
- [ ] [Testable condition 1]
- [ ] [Testable condition 2]
- [ ] [Testable condition 3]

**Dependencies:**
- C-001 (constraint that affects this requirement)
- NFR-002 (quality attribute that applies)

---
```

### Field Definitions

| Field | Required | Format | Rules |
|-------|----------|--------|-------|
| ID | Yes | TR-XXX | Sequential, three-digit padded, no gaps |
| Title | Yes | Free text | Descriptive, concise |
| Source | Yes | FR-XXX reference(s) | Must reference existing FR(s) |
| Priority | Yes | MUST / SHOULD / MAY | RFC 2119 keyword |
| Description | Yes | Paragraph | Technology-agnostic; describes WHAT, not HOW |
| Acceptance Criteria | Yes | Checkbox list | Each item independently testable |
| Dependencies | No | ID references | Links to C-XXX, NFR-XXX, other TR-XXX |

### Decomposition Examples

**Business FR:** "Users must be able to sign in to their account" (FR-001)

**Technical decomposition:**

| TR | Title | Aspect |
|----|-------|--------|
| TR-001 | Authentication Flow | Credential validation, error handling |
| TR-002 | Session Management | Token issuance, expiration, refresh |
| TR-003 | Account Lockout | Brute-force protection, lockout thresholds |
| TR-004 | Authentication Audit | Login attempt logging, anomaly flags |

Each TR addresses a distinct technical concern that the single business FR implies but does not state.

### Writing Acceptance Criteria

**Good acceptance criteria are:**
- Independently testable (pass/fail, no ambiguity)
- Technology-agnostic (no specific tools or implementations)
- Complete (cover success, failure, and edge cases)

**Examples:**

```markdown
**TR-001: Authentication Flow**

**Acceptance Criteria:**
- [ ] Valid credentials result in authenticated session
- [ ] Invalid credentials return generic error (no credential-type leakage)
- [ ] Expired accounts cannot authenticate
- [ ] Authentication completes within NFR-001 latency target
- [ ] All authentication attempts logged per TR-004
```

```markdown
**TR-007: Data Export**

**Acceptance Criteria:**
- [ ] Export includes all user-owned data elements
- [ ] Export format is machine-readable and portable
- [ ] Export request completes within NFR-003 time limit
- [ ] Export excludes system-internal data (classified Internal or below)
- [ ] Export availability notified through existing notification channel
```

---

## 2. Constraints and Decisions (constraints-and-decisions.md)

### Document Template

```markdown
# Constraints and Decisions: {feature_id}

> Hard boundaries and technology choices that shape the implementation.
> Generated during plan workflow.

---

## Part 1: Hard Constraints

### Constraint Summary

| ID | Type | Source | Severity |
|----|------|--------|----------|
| C-001 | infrastructure | Existing production environment | Hard |
| C-002 | regulatory | GDPR Article 17 | Hard |
| C-003 | compatibility | Legacy API consumers | Hard |
| C-004 | migration | Zero-downtime deployment requirement | Hard |

---

### C-001: [Descriptive Title]

**Type:** infrastructure
**Source:** [Where this constraint originates -- existing system, regulation, contract]
**Severity:** Hard

**Description:**
[The hard boundary, stated as a fact, not a preference.]

**Impact:**
- Eliminates [design choice A] as an option
- Requires [design consideration B]
- Affects TR-001, TR-003
- Shapes D-001

**Verification:**
[How to confirm this constraint still applies -- who to ask, what to check.]

---

## Part 2: Technology Decisions

### Decision Summary

| ID | Decision | Choice | Shaped By |
|----|----------|--------|-----------|
| D-001 | Primary database | PostgreSQL 15 | C-001 |
| D-002 | Auth mechanism | JWT with refresh tokens | C-003 |
| D-003 | Caching strategy | Redis with TTL | NFR-001 |

---

### D-001: [Decision Title]

**Context:**
[What problem needed solving and why a decision was required.]

**Shaped By:**
- C-001 (constraint that narrowed options)
- NFR-001 (quality target that influenced choice)

**Options Considered:**

| Option | Pros | Cons |
|--------|------|------|
| [Option A] | [advantages] | [disadvantages] |
| [Option B] | [advantages] | [disadvantages] |
| [Option C] | [advantages] | [disadvantages] |

**Choice:** [Selected option]

**Rationale:**
[WHY this choice — not just restating the choice, but the reasoning that led to it.]

**Consequences:**
- [Trade-off 1 accepted]
- [Trade-off 2 accepted]
- [Future consideration]

**Constitution Alignment:**
[How this decision aligns with project principles, if applicable.]

---

## Part 3: Infrastructure Requirements

### Infrastructure Summary

| ID | Type | Source Constraint | Priority |
|----|------|-------------------|----------|
| IP-001 | compute | C-001 | MUST |
| IP-002 | ci-cd | C-004, NFR-002 | MUST |
| IP-003 | monitoring | NFR-001 | SHOULD |

---

### IP-001: [Descriptive Title]

**Type:** compute
**Source:** C-001, NFR-003
**Priority:** MUST

**Description:**
[What must be provisioned or configured — stated as a requirement, not implementation.]

**Acceptance Criteria:**
- [ ] [Verifiable condition 1]
- [ ] [Verifiable condition 2]

**Dependencies:**
- IP-002 (needs CI/CD before deployment)

---
```

### Field Definitions — Constraints

| Field | Required | Format | Rules |
|-------|----------|--------|-------|
| ID | Yes | C-XXX | Sequential, three-digit padded, no gaps |
| Title | Yes | Free text | Descriptive, concise |
| Type | Yes | infrastructure / compatibility / regulatory / migration / organizational | Exactly one type |
| Source | Yes | Free text | Traceable origin -- system, regulation, contract, team |
| Severity | Yes | Hard | All constraints are hard boundaries by definition |
| Description | Yes | Paragraph | States the boundary as fact |
| Impact | Yes | Bullet list | What design choices this eliminates or forces; references to D-XXX |
| Verification | No | Free text | How to confirm constraint still applies |

### Field Definitions — Decisions

| Field | Required | Format | Rules |
|-------|----------|--------|-------|
| ID | Yes | D-XXX | Sequential, three-digit padded, no gaps |
| Title | Yes | Free text | Descriptive, concise |
| Context | Yes | Paragraph | Problem that needed solving |
| Shaped By | Yes | C-XXX / NFR-XXX references | Constraints and NFRs that narrowed options |
| Options Considered | Yes | Table | Minimum 2 alternatives with pros/cons |
| Choice | Yes | Free text | Selected option |
| Rationale | Yes | Paragraph | WHY, not just WHAT |
| Consequences | Yes | Bullet list | Trade-offs accepted, future considerations |
| Constitution Alignment | No | Paragraph | How choice follows project principles |

### Field Definitions — Infrastructure Requirements

| Field | Required | Format | Rules |
|-------|----------|--------|-------|
| ID | Yes | IP-XXX | Sequential, three-digit padded |
| Title | Yes | Free text | Descriptive, concise |
| Type | Yes | compute / networking / storage / ci-cd / monitoring / security / environment-config | Exactly one |
| Source | Yes | C-XXX / NFR-XXX refs | Constraints/NFRs that necessitate this |
| Priority | Yes | MUST / SHOULD / MAY | RFC 2119 |
| Description | Yes | Paragraph | WHAT to provision, not HOW |
| Acceptance Criteria | Yes | Checkbox list | Independently verifiable |
| Dependencies | No | IP-XXX refs | Other infra items this depends on |

### Infrastructure Types

| Type | Scope |
|------|-------|
| compute | Containers, serverless, VMs, orchestration |
| networking | DNS, load balancers, VPN, firewall rules |
| storage | Databases, object storage, caches (provisioning, not schema) |
| ci-cd | Build pipelines, deployment automation, environments |
| monitoring | APM, logging, alerting, health checks |
| security | IAM, certificates, secrets management |
| environment-config | Environment variables, feature flags, config management |

### Constraint Types

| Type | Definition | Examples |
|------|------------|---------|
| **infrastructure** | Existing systems, platforms, or environments that cannot change | "Production database is PostgreSQL 15 on AWS RDS" |
| **compatibility** | Existing consumers, APIs, or interfaces that must continue working | "Mobile app v2.x expects REST API v1 responses" |
| **regulatory** | Laws, regulations, or compliance mandates | "GDPR requires right-to-erasure within 30 days" |
| **migration** | Deployment, transition, or coexistence requirements | "Zero-downtime migration required; both old and new schemas must coexist" |
| **organizational** | Team, process, or business constraints | "Maximum 3-person team for initial implementation" |

### Distinguishing Constraints from Preferences

| Statement | Constraint? | Why |
|-----------|-------------|-----|
| "Must use PostgreSQL" | Maybe | Only if existing production infrastructure mandates it |
| "Must use React" | Probably not | Unless existing codebase and team skills make alternatives infeasible |
| "Must support IE11" | Yes | If contractual obligation exists |
| "Must deploy to AWS" | Yes | If organization has AWS-only policy |
| "Should use TypeScript" | No | Preference, not hard boundary |

**Test:** "If we violated this, what concrete thing would break or what rule would we violate?" If the answer is vague, it is a preference, not a constraint.

---

## 3. Non-Functional Requirements (nfrs.md)

### Document Template

```markdown
# Non-Functional Requirements: {feature_id}

> Measurable quality attributes with specific targets.
> Generated during plan workflow.

---

## NFR Summary

| ID | Category | Target | Source |
|----|----------|--------|--------|
| NFR-001 | performance | p95 < 200ms | FR-001 (user expects instant feedback) |
| NFR-002 | availability | 99.9% monthly | Business SLA commitment |
| NFR-003 | scalability | 10,000 concurrent users | Growth projection Y1 |
| NFR-004 | security | Zero plaintext PII in logs | Compliance requirement |

---

## NFR-001: [Descriptive Title]

**Category:** performance
**Source:** [Business requirement or stakeholder that justifies this target]

**Requirement:**
[The quality attribute in plain language.]

**Target:**
[Specific, measurable numeric threshold.]

**Measurement Method:**
[How to verify the target is met -- tools, conditions, frequency.]

**Applies To:**
- TR-001 (authentication flow must meet this latency)
- TR-005 (search results must meet this latency)

---
```

### Field Definitions

| Field | Required | Format | Rules |
|-------|----------|--------|-------|
| ID | Yes | NFR-XXX | Sequential, three-digit padded, no gaps |
| Title | Yes | Free text | Descriptive, concise |
| Category | Yes | performance / availability / scalability / security / usability / maintainability | Exactly one category |
| Source | Yes | Free text | Business requirement, SLA, or stakeholder justifying the target |
| Requirement | Yes | Paragraph | Plain language quality attribute |
| Target | Yes | Numeric | Specific, measurable threshold |
| Measurement Method | Yes | Paragraph | Tools, conditions, frequency of measurement |
| Applies To | No | TR-XXX references | Which technical requirements this NFR constrains |

### NFR Categories with Examples

| Category | Bad (Vague) | Good (Measurable) |
|----------|-------------|-------------------|
| **performance** | "System must be fast" | "p95 response time < 200ms under 1000 concurrent users, measured by APM" |
| **availability** | "System must be reliable" | "99.9% uptime measured monthly, excluding scheduled maintenance" |
| **scalability** | "Must handle growth" | "Must support 10,000 concurrent users with linear resource scaling to 50,000" |
| **security** | "Must be secure" | "Zero plaintext PII in logs; all data classified confidential+ encrypted AES-256-equivalent at rest" |
| **usability** | "Must be easy to use" | "New users complete primary workflow within 3 minutes without documentation" |
| **maintainability** | "Must be maintainable" | "Mean time to deploy hotfix < 2 hours from commit to production" |

### Writing Measurement Methods

Every NFR target needs a measurement method that specifies:

1. **What tool or technique** measures it
2. **Under what conditions** the measurement is valid
3. **How frequently** measurement occurs

**Example:**

```markdown
## NFR-001: API Response Latency

**Target:** p95 < 200ms, p99 < 500ms

**Measurement Method:**
Measured by application performance monitoring (APM) under the following conditions:
- Load: 1,000 concurrent authenticated users
- Operation mix: 70% reads, 20% writes, 10% searches
- Measurement window: rolling 24-hour periods
- Excludes: scheduled maintenance windows, bulk import operations
- Frequency: Continuous monitoring with daily reporting
```

---

## 4. Data Model (data-model.md)

### Document Template

```markdown
# Data Model: {feature_id}

> Entity definitions with relationships, sensitivity annotations, and state machines.
> Generated during plan workflow.

---

## Data Sensitivity Summary

| Entity | Attribute | Classification | Compliance |
|--------|-----------|---------------|------------|
| User | email | Confidential | GDPR Art. 6 |
| User | password_hash | Restricted | NIST 800-63 |
| Payment | card_number | Restricted | PCI-DSS |
| Order | transaction_id | Internal | - |
| Product | name | Public | - |

### Classification Levels

| Level | Definition | Examples |
|-------|------------|---------|
| **Public** | Freely shareable, no access controls needed | Product names, public profile info |
| **Internal** | Organization-internal, basic access controls | Transaction IDs, internal status codes |
| **Confidential** | Sensitive, role-based access required | Email addresses, billing addresses |
| **Restricted** | Highly sensitive, strict access and audit | Passwords, SSNs, payment card numbers |

---

## Entity Summary

| Entity | Attributes | Relationships | Status |
|--------|-----------|--------------|--------|
| User | 8 | 3 | [NEW] |
| Order | 6 | 2 | [NEW] |
| Product | 5 | 1 | [EXTENDS EXISTING] |

---

## User

**Description:** [What this entity represents]
**Traceability:** FR-001, FR-003

### Attributes

| Attribute | Type | Constraints | Sensitivity |
|-----------|------|------------|-------------|
| id | UUID | PK, auto-generated | Internal |
| email | String(255) | Unique, required | Confidential — encrypt at rest (AES-256), mask in logs (j***@example.com) |
| password_hash | String(60) | Required | Restricted — encrypt at rest, never log, retain until account deletion |
| display_name | String(100) | Required | Public |
| created_at | Timestamp | Auto-set | Internal |
| updated_at | Timestamp | Auto-set | Internal |

### Sensitivity Details (Confidential+ attributes)

#### email (Confidential)

| Aspect | Requirement |
|--------|-------------|
| Encryption at Rest | Required — AES-256 |
| Encryption in Transit | Required — TLS 1.3+ |
| Retention Period | Delete within 30 days of account closure |
| Access Control | Authenticated users read own; admins read all |
| Audit | All access logged with timestamp and user |
| Masking | Displayed masked in logs: j***@example.com |
| Compliance | GDPR Art. 6 (consent via signup), Art. 17 (deletion within 30 days) |

#### password_hash (Restricted)

| Aspect | Requirement |
|--------|-------------|
| Encryption at Rest | Required — AES-256 |
| Encryption in Transit | Required — TLS 1.3+ |
| Retention Period | Retain until account deletion; purge on delete |
| Access Control | System-only; no user or admin read access |
| Audit | All access logged; real-time alerts on anomalous access |
| Masking | Never displayed; never logged |
| Compliance | NIST 800-63 (credential storage) |

### Relationships

| Relationship | Target | Cardinality | Delete Behavior |
|-------------|--------|-------------|-----------------|
| places | Order | 1:N | Cascade soft-delete |
| has | Profile | 1:1 | Cascade delete |
| belongs_to | Organization | N:1 | Nullify |

### State Machine

```
[active] --deactivate--> [inactive]
[inactive] --reactivate--> [active]
[active] --delete--> [deleted]
[inactive] --delete--> [deleted]
```

### Validation Rules

- Email must be valid format (RFC 5322)
- Display name must be 1-100 characters, no special characters
- Password hash must use bcrypt with cost factor ≥ 12

---
```

### Field Definitions — Entity

| Field | Required | Format | Rules |
|-------|----------|--------|-------|
| Entity Name | Yes | PascalCase | Clear, domain-appropriate name |
| Description | Yes | Paragraph | What this entity represents |
| Traceability | Yes | FR-XXX references | Which business requirements this entity serves |
| Attributes | Yes | Table | All fields with types, constraints, and sensitivity |
| Relationships | Yes | Table | Cardinality and delete behavior for each |
| Status | Yes (brownfield) | [NEW] / [EXTENDS EXISTING] / [REUSES EXISTING] | Brownfield status marker |
| State Machine | If stateful | Diagram | All states and transitions |
| Validation Rules | Yes | List | Constraints from requirements |
| Standard Fields | Yes | id, createdAt, updatedAt | Every entity must have these |

### Field Definitions — Sensitivity Annotation

| Field | Required | Format | Rules |
|-------|----------|--------|-------|
| Classification | Yes | Public / Internal / Confidential / Restricted | Per attribute |
| Encryption at Rest | Yes (Confidential+) | Required / Not required + standard | Mandatory for Confidential and Restricted |
| Encryption in Transit | Yes (Confidential+) | Required / Not required + standard | Mandatory for all classifications |
| Retention Period | Yes (Confidential+) | Duration + expiry action | How long kept, what happens after |
| Access Control | Yes (Confidential+) | Role-based description | Who can read, write, delete |
| Audit | Yes (Confidential+) | Yes / No | Whether access is logged |
| Masking | No | Display format | How data appears in UIs and logs |
| Compliance | No | Regulation + requirement | GDPR, HIPAA, PCI-DSS, SOC2 mappings |

### Handling Requirements by Classification Level

| Aspect | Public | Internal | Confidential | Restricted |
|--------|--------|----------|-------------|------------|
| Encryption at rest | Not required | Recommended | Required | Required (strong) |
| Encryption in transit | TLS recommended | TLS required | TLS required | TLS required + additional |
| Access control | None | Basic auth | Role-based | Role-based + MFA |
| Audit logging | Not required | Not required | Required | Required (real-time) |
| Retention limits | None | Organization policy | Defined period | Minimum necessary |
| Masking in logs | Not required | Not required | Required | Required (no logging preferred) |
| Breach notification | Not required | Internal review | Required (regulatory timeline) | Immediate (regulatory timeline) |

### Classification Decision Tree

```
Is the data publicly available or intended for public sharing?
├── Yes → PUBLIC
└── No
    ├── Is it internal operational data with no PII?
    │   ├── Yes → INTERNAL
    │   └── No
    │       ├── Is it PII, financial, or business-sensitive?
    │       │   ├── Yes → Is it highly sensitive (credentials, SSN, payment cards)?
    │       │   │   ├── Yes → RESTRICTED
    │       │   │   └── No → CONFIDENTIAL
    │       │   └── No → INTERNAL
    │       └── When in doubt → CONFIDENTIAL (classify up, not down)
```

---

## 5. API Contracts (contracts/api.yaml)

### Document Template

```yaml
openapi: 3.0.3
info:
  title: "{feature_id} API"
  version: "1.0.0"
  description: "API contracts for {feature_id}"

paths:
  /users:
    post:
      summary: "Create a new user"
      operationId: createUser
      tags: [Users]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
            example:
              email: "jane@example.com"
              display_name: "Jane Doe"
              password: "secureP@ssw0rd"
      responses:
        '201':
          description: "User created successfully"
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserResponse'
        '400':
          description: "Invalid request"
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '409':
          description: "Email already exists"
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
      # Integration boundary (for endpoints wrapping external systems)
      x-integration:
        system: "Auth0"
        protocol: "OIDC / OAuth 2.0"
        criticality: "Critical"
        failure_modes:
          - failure: "Auth0 timeout (>3s)"
            detection: "HTTP timeout"
            impact: "User creation blocked"
            fallback: "Retry with exponential backoff (max 3 attempts)"
          - failure: "Auth0 5xx"
            detection: "HTTP status code"
            impact: "Registration unavailable"
            fallback: "Queue registration; notify user of delay"

components:
  schemas:
    CreateUserRequest:
      type: object
      required: [email, display_name, password]
      properties:
        email:
          type: string
          format: email
          maxLength: 255
        display_name:
          type: string
          maxLength: 100
        password:
          type: string
          minLength: 8
          maxLength: 128

    UserResponse:
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        display_name:
          type: string
        created_at:
          type: string
          format: date-time

    ErrorResponse:
      type: object
      required: [error]
      properties:
        error:
          type: object
          required: [code, message]
          properties:
            code:
              type: string
            message:
              type: string
            details:
              type: array
              items:
                type: object
```

### Integration Boundary Documentation

For endpoints that wrap external systems, use the `x-integration` OpenAPI extension:

| Field | Required | Format | Rules |
|-------|----------|--------|-------|
| system | Yes | Name + version | Specific external system |
| protocol | Yes | REST / GraphQL / gRPC / webhook / SDK / queue | Communication mechanism |
| criticality | Yes | Critical / Important / Optional | Impact if unavailable |
| failure_modes | Yes | Array of failure objects | Every realistic failure scenario |

Each failure mode object:

| Field | Required | Description |
|-------|----------|-------------|
| failure | Yes | What goes wrong |
| detection | Yes | How to detect it |
| impact | Yes | User-visible effect |
| fallback | Yes | What to do instead |

### Criticality Levels

| Level | Definition | Failure Impact |
|-------|------------|----------------|
| **Critical** | System cannot function without this integration | Full feature outage; user-visible immediately |
| **Important** | Feature degraded but partially functional | Reduced capability; some operations unavailable |
| **Optional** | Nice-to-have; system works without it | Minor feature loss; most users unaffected |

---

## 6. Integration Guide (quickstart.md)

### Document Template

```markdown
# Integration Guide: {feature_id}

> Common flows, authentication, and error handling patterns.
> Generated during plan workflow.

---

## Authentication

[How to obtain and use credentials]

```bash
# Obtain token
curl -X POST /auth/token \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "..."}'

# Use token
curl -X GET /users/me \
  -H "Authorization: Bearer <token>"
```

---

## Common Flows

### Create a User

```bash
curl -X POST /users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"email": "jane@example.com", "display_name": "Jane Doe", "password": "secureP@ssw0rd"}'
```

---

## Error Handling

All errors follow the standard format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is already in use",
    "details": [{"field": "email", "reason": "duplicate"}]
  }
}
```

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 400 | Invalid request | Check request body against schema |
| 401 | Not authenticated | Refresh or re-obtain token |
| 403 | Not authorized | Check user permissions |
| 404 | Not found | Verify resource ID |
| 429 | Rate limited | Respect Retry-After header |
| 500 | Server error | Retry with backoff; report if persistent |

---

## External Integrations

[Overview of external system boundaries and their impact on API behavior]

| System | Endpoints Affected | Criticality | Failure Behavior |
|--------|-------------------|-------------|------------------|
| Auth0 | POST /users, POST /auth/token | Critical | Registration/login unavailable; queued for retry |
| Stripe | POST /payments, GET /payments/{id} | Critical | Payments blocked; user notified of delay |
| SendGrid | POST /notifications | Important | Notifications delayed; no user-visible error |

---
```

---

## ID Numbering Rules (All Artifacts)

All artifact types follow the same numbering conventions:

1. **Three-digit padding:** TR-001, not TR-1
2. **Sequential, no gaps:** TR-001, TR-002, TR-003 (never TR-001, TR-003)
3. **Prefix identifies type:** TR- / C- / D- / NFR- / IP-
4. **Cross-references use full ID:** "See TR-001" not "See requirement 1"
5. **Grouping by concern:** Related items should be sequential where possible
