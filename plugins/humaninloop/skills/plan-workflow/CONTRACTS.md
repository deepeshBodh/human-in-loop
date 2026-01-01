# Phase 2: Contracts Procedures

Detailed procedures for the Contracts phase (plan-builder, phase 2).

---

## Mission

Design API contracts and integration documentation from the specification and data model. Output: `contracts/api.yaml` (OpenAPI) and `quickstart.md`.

---

## Endpoint Mapping

### User Action Inventory

For each user action in spec:
- Identify the HTTP method
- Define the resource path
- Map to entity operations

### Standard REST Patterns

| Action | Method | Path Pattern |
|--------|--------|--------------|
| List | GET | `/resources` |
| Create | POST | `/resources` |
| Read | GET | `/resources/{id}` |
| Update | PUT/PATCH | `/resources/{id}` |
| Delete | DELETE | `/resources/{id}` |
| Action | POST | `/resources/{id}/action` |

### Traceability

Map each endpoint to:
- Source FR-xxx
- Source US#
- Entity from data model

---

## Schema Definition

### Request Schemas

From data model entities:
- Include writable fields only
- Mark required vs optional
- Apply validation rules

### Response Schemas

- Include readable fields
- Add computed fields
- Include relationships (embedded or linked)

### Common Patterns

```yaml
# Paginated list response
ListResponse:
  properties:
    data: array
    pagination:
      total: integer
      page: integer
      per_page: integer

# Error response
ErrorResponse:
  properties:
    code: string
    message: string
    details: array
```

---

## Error Handling

### Standard HTTP Errors

| Code | When |
|------|------|
| 400 | Invalid request format |
| 401 | Authentication required |
| 403 | Permission denied |
| 404 | Resource not found |
| 409 | Conflict (duplicate, state) |
| 422 | Validation failed |
| 500 | Server error |

### Error Response Format

```yaml
ErrorResponse:
  type: object
  required: [code, message]
  properties:
    code:
      type: string
      example: "VALIDATION_FAILED"
    message:
      type: string
      example: "Email format is invalid"
    details:
      type: array
      items:
        type: object
        properties:
          field: string
          error: string
```

---

## OpenAPI Structure

```yaml
openapi: 3.0.3
info:
  title: {Feature Name} API
  version: 1.0.0
  description: API for {feature description}

servers:
  - url: /api

paths:
  /resource:
    get:
      summary: List resources
      operationId: listResources
      tags: [Resources]
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResourceList'

components:
  schemas:
    Resource:
      type: object
      properties:
        ...
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

---

## Quickstart Format

```markdown
# {Feature} Integration Guide

## Authentication

[How to authenticate]

## Common Scenarios

### Scenario 1: [User action]

**Request:**
\`\`\`bash
curl -X POST /api/resource \
  -H "Authorization: Bearer {token}" \
  -d '{"field": "value"}'
\`\`\`

**Response:**
\`\`\`json
{"id": "...", "field": "value"}
\`\`\`

## Error Handling

[Common errors and how to handle them]
```

---

## Endpoint Registry

Populate plan-context.md with:

```markdown
| Endpoint | Method | Source FRs | Request Schema | Response Schema |
|----------|--------|------------|----------------|-----------------|
| /users | POST | FR-001 | CreateUser | User |
| /sessions | POST | FR-003 | CreateSession | Session |
```

---

## Quality Checklist

- [ ] Every user action has corresponding endpoint
- [ ] Every endpoint has request/response schemas
- [ ] Error responses defined for all endpoints
- [ ] OpenAPI spec is valid (3.x)
- [ ] Quickstart has at least one complete scenario
- [ ] Constitution `[phase:2]` API standards checked
- [ ] Endpoint Registry complete
- [ ] Naming consistent with data model
