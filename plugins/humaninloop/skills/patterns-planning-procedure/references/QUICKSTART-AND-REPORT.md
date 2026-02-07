# Quickstart Guide and Planner Report Reference

This reference provides detailed templates and field-by-field guidance for producing quickstart.md and filling the planner report template.

---

## Table of Contents

1. [Quickstart Guide Template](#quickstart-guide-template)
2. [Quickstart Content Guidelines](#quickstart-content-guidelines)
3. [Planner Report Field Guide](#planner-report-field-guide)
4. [Report Examples by Phase](#report-examples-by-phase)
5. [Roadmap Integration in Reports](#roadmap-integration-in-reports)

---

## Quickstart Guide Template

```markdown
# Quickstart: {feature_id}

> Developer integration guide for {feature description}.
> Generated from API contracts and data model.

---

## Prerequisites

- {Runtime requirements}
- {Authentication credentials}
- {Environment setup}

---

## Authentication

### Login

Request:

\`\`\`bash
curl -X POST {base_url}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "password": "your-secure-password"
  }'
\`\`\`

Response (200 OK):

\`\`\`json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expiresIn": 3600,
  "refreshToken": "dGhpcyBpcyBh..."
}
\`\`\`

### Using the Token

Include in all subsequent requests:

\`\`\`bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  {base_url}/api/resource
\`\`\`

### Token Refresh

\`\`\`bash
curl -X POST {base_url}/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refreshToken": "dGhpcyBpcyBh..."}'
\`\`\`

---

## Common User Flows

### Flow 1: {Primary Action}

\`\`\`bash
# Step 1: {Description}
curl -X POST {base_url}/api/{resource} \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "field1": "realistic-value",
    "field2": 42
  }'

# Response (201 Created)
# {
#   "id": "550e8400-e29b-41d4-a716-446655440000",
#   "field1": "realistic-value",
#   "field2": 42,
#   "createdAt": "2026-02-07T10:30:00Z"
# }

# Step 2: {Description}
curl {base_url}/api/{resource}/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer {token}"
\`\`\`

### Flow 2: {Secondary Action}

\`\`\`bash
# {flow steps with curl examples}
\`\`\`

---

## Error Handling

### Common Errors

| Status | Code | Meaning | Recovery |
|--------|------|---------|----------|
| 400 | INVALID_INPUT | Request body malformed | Check required fields |
| 401 | TOKEN_EXPIRED | Auth token expired | Refresh token |
| 403 | INSUFFICIENT_PERMISSIONS | No access to resource | Check user role |
| 404 | RESOURCE_NOT_FOUND | Resource does not exist | Verify ID |
| 409 | CONFLICT | State conflict | Re-read and retry |
| 422 | BUSINESS_RULE_VIOLATION | Business rule failed | Check error details |
| 429 | RATE_LIMITED | Too many requests | Wait and retry |

### Error Response Format

\`\`\`json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Email field is required",
    "details": [
      {"field": "email", "reason": "required"}
    ]
  }
}
\`\`\`

### Retry Strategy

- 429 responses include `Retry-After` header
- 5xx errors: exponential backoff starting at 1 second
- 4xx errors: do not retry without fixing input

---

## Endpoint Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/login | Authenticate |
| POST | /api/auth/refresh | Refresh token |
| GET | /api/{resource} | List resources |
| POST | /api/{resource} | Create resource |
| GET | /api/{resource}/{id} | Get resource |
| PUT | /api/{resource}/{id} | Update resource |
| DELETE | /api/{resource}/{id} | Delete resource |
```

---

## Quickstart Content Guidelines

### Authentication Sequence

Document the complete authentication lifecycle:

1. **Initial login** - Full request/response with realistic credentials
2. **Token usage** - Show the Authorization header pattern
3. **Token refresh** - When and how to refresh
4. **Error cases** - Invalid credentials, expired tokens

### User Flow Selection

Choose flows that represent the most common developer interactions:

| Priority | Flow Type | Example |
|----------|-----------|---------|
| 1 | Core CRUD | Create, read, update, delete the primary resource |
| 2 | Authentication | Login, token refresh, logout |
| 3 | Relationships | Create parent, create child, list children |
| 4 | State transitions | Create draft, publish, archive |
| 5 | Search/filter | List with query parameters |

### Curl Example Quality

Each curl example MUST:

- Use realistic values that match schema definitions
- Include all required headers
- Show the expected response as a comment
- Include status codes
- Be copy-pasteable (no placeholder tokens that need manual replacement, except auth tokens)

Bad example:
```bash
curl -X POST /api/foo -d '{"bar": "baz"}'
```

Good example:
```bash
curl -X POST http://localhost:3000/api/users \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane.doe@example.com",
    "name": "Jane Doe",
    "role": "member"
  }'

# Response (201 Created)
# {
#   "id": "550e8400-e29b-41d4-a716-446655440000",
#   "email": "jane.doe@example.com",
#   "name": "Jane Doe",
#   "role": "member",
#   "createdAt": "2026-02-07T10:30:00Z"
# }
```

---

## Planner Report Field Guide

The planner report uses the template at `${CLAUDE_PLUGIN_ROOT}/templates/planner-report-template.md`. Below is field-by-field guidance for populating each section.

### Summary Section

| Field | How to Fill |
|-------|-------------|
| Phase | Current phase name: `research`, `datamodel`, or `contracts` |
| Artifact | Relative path to the primary artifact produced |
| Completion | `complete` if all quality gate items pass, `partial` with explanation otherwise |

### What Was Produced

Write a 2-3 paragraph narrative covering:

1. What was built and why (connect to spec requirements)
2. Key decisions made during the phase
3. Constraints that shaped the output

Do NOT list files. Describe the substance of the work.

### Key Outputs

Use the phase-specific table format:

**Research phase:**
```markdown
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Auth mechanism | JWT with refresh | Stateless, team familiarity, fits scale |
| Database | PostgreSQL | Existing stack, relational data model |
| Caching | Redis | Session storage, rate limiting support |
```

**Data model phase:**
```markdown
| Entity | Attributes | Relationships | Status |
|--------|------------|---------------|--------|
| User | 8 | 3 | [EXTENDS EXISTING] |
| Session | 5 | 1 | [NEW] |
| Task | 12 | 4 | [NEW] |
```

**Contracts phase:**
```markdown
| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/auth/login | POST | User authentication |
| /api/users | GET | List users with pagination |
| /api/users/{id} | GET | Get single user |
```

### Constitution Alignment

Document how design decisions align with constitution principles:

```markdown
Decisions align with constitution principles:
- **Security**: JWT tokens with refresh rotation (Principle I)
- **Testing**: All endpoints designed for testability (Principle II)
- **Observability**: Structured error codes for monitoring (Principle IV)
```

If any decision tensions with constitution principles, note the tension and rationale.

### Open Questions

List items that could not be resolved during the phase:

```markdown
1. Rate limiting tier structure - needs business input
2. Email provider selection - dependent on cost analysis
3. Webhook retry policy - needs SLA discussion
```

Write "None identified" if genuinely empty. Do NOT leave this section blank.

### Ready for Review

Self-assess artifact quality:

```markdown
Artifact is ready for review. All quality gate items pass:
- [x] All spec markers resolved
- [x] 3 alternatives evaluated per decision
- [x] Trade-offs documented
- [x] Constitution alignment verified
```

Or flag concerns:

```markdown
Artifact is ready for review with noted concerns:
- [x] Core decisions documented
- [ ] Rate limiting decision deferred (needs business input)
- [x] Brownfield alignment checked
```

---

## Report Examples by Phase

### Research Report Example

```markdown
# Planner Report

> Feature: 003-task-management
> Phase: research
> Iteration: 1
> Generated: 2026-02-07T10:30:00Z

---

## Summary

| Metric | Value |
|--------|-------|
| **Phase** | research |
| **Artifact** | specs/003-task-management/research.md |
| **Completion** | complete |

---

## What Was Produced

Produced a technical research document resolving all unknowns from the task
management specification. Evaluated authentication mechanisms, database
options, and real-time notification strategies against project constraints
and existing stack.

Key focus was maintaining consistency with the existing PostgreSQL setup
while adding WebSocket support for live task updates. Constitution's
security principle guided the JWT refresh token decision.

---

## Key Outputs

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Auth mechanism | JWT with refresh | Stateless, team familiarity (3/4 devs) |
| Real-time | WebSocket via Socket.IO | Existing Node.js stack, team experience |
| Task storage | PostgreSQL with JSONB | Existing DB, flexible metadata |

---

## Constitution Alignment

All decisions align with constitution principles:
- Security (Principle I): JWT rotation prevents token theft
- Testing (Principle II): Stateless auth enables isolated testing
- Observability (Principle IV): Structured error codes for all auth failures

---

## Open Questions

1. WebSocket reconnection policy - needs UX discussion
2. Task attachment storage (S3 vs local) - needs infrastructure decision

---

## Resolved Markers

| Marker | Location | Resolution | Rationale |
|--------|----------|------------|-----------|
| [NEEDS CLARIFICATION]: Notification mechanism | spec.md L34 | WebSocket with fallback polling | Real-time UX requirement |
| [TBD]: File upload limits | spec.md L67 | 10MB per file, 50MB total | Standard for document attachments |

---

## Roadmap Alignment

| Gap ID | Title | Status |
|--------|-------|--------|
| GAP-001 | Configure pytest infrastructure | Not relevant to this feature |
| GAP-005 | Standardize SKILL.md frontmatter | Not relevant to this feature |

No existing gaps are addressed by this feature. No new gaps discovered.

---

## Ready for Review

Artifact is ready for review. All quality gate items pass:
- [x] All [NEEDS CLARIFICATION] markers resolved (2/2)
- [x] 3 alternatives evaluated per decision
- [x] Trade-offs documented for each choice
- [x] Constitution alignment verified
- [x] Brownfield stack evaluated
- [x] Roadmap gaps checked
```

---

## Roadmap Integration in Reports

### When Roadmap Exists

Add a "Roadmap Alignment" section to every planner report:

```markdown
## Roadmap Alignment

| Gap ID | Title | Status |
|--------|-------|--------|
| GAP-001 | {title} | Addressed / Partially addressed / Not relevant |

### Addressed Gaps
- GAP-001: This feature configures pytest for task management validators
  - Commit annotation: `Addressed: GAP-001`

### Suggested New Gaps
- Suggested gap: WebSocket testing infrastructure needed for real-time features
```

### When No Roadmap Exists

```markdown
## Roadmap Alignment

No evolution roadmap found at `.humaninloop/memory/evolution-roadmap.md`.
Consider running `/humaninloop:setup` in brownfield mode to generate one.
```

### Commit Annotation Format

When work addresses a roadmap gap, include in commit messages:

```
feat(task-management): add pytest configuration for validators

Addressed: GAP-001
```

When discovering new gaps during planning, suggest in the planner report but never modify the roadmap directly. The supervisor or human decides whether to add suggested gaps.
