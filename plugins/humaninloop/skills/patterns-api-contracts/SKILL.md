---
name: patterns-api-contracts
description: RESTful API design following best practices with endpoint mapping, schema definition, and error handling. Use when mapping endpoints, defining schemas, or when you see "API", "endpoint", "REST", "OpenAPI", "schema", "contract", or "HTTP".
---

# Designing API Contracts

## Purpose

Design RESTful API contracts that map user actions to endpoints with complete schema definitions and comprehensive error handling. This skill covers endpoint design, request/response schemas, and OpenAPI specification.

## Endpoint Mapping

### User Action to Endpoint Mapping

| User Action | HTTP Method | Endpoint Pattern |
|-------------|-------------|------------------|
| Create resource | POST | `/resources` |
| List resources | GET | `/resources` |
| Get single resource | GET | `/resources/{id}` |
| Update resource | PUT/PATCH | `/resources/{id}` |
| Delete resource | DELETE | `/resources/{id}` |
| Perform action | POST | `/resources/{id}/{action}` |
| Get nested resource | GET | `/resources/{id}/children` |

### Method Selection

| Scenario | Method | Idempotent? |
|----------|--------|-------------|
| Create new resource | POST | No |
| Full replacement | PUT | Yes |
| Partial update | PATCH | No |
| Read resource | GET | Yes |
| Remove resource | DELETE | Yes |
| Trigger action | POST | Usually No |

### Resource Naming Conventions

- Use plural nouns: `/users`, not `/user`
- Use kebab-case for multi-word: `/user-profiles`
- Use path params for IDs: `/users/{userId}`
- Use query params for filtering: `/users?role=admin`
- Use nested paths for relationships: `/users/{userId}/tasks`

## Endpoint Documentation Format

Document each endpoint with description, source requirements, request/response schemas, and error cases:

```markdown
## POST /api/auth/login

**Description**: Authenticate user with email and password

**Source Requirements**: FR-001, US#1

### Request
{JSON request body example}

### Response (200 OK)
{JSON response body example}

### Error Responses
| Status | Code | Description |
|--------|------|-------------|
| 400 | INVALID_INPUT | Missing or malformed fields |
| 401 | INVALID_CREDENTIALS | Wrong email or password |
```

## Schema Definition

### Request Schema Format

```yaml
LoginRequest:
  type: object
  required:
    - email
    - password
  properties:
    email:
      type: string
      format: email
      description: User's email address
    password:
      type: string
      minLength: 8
      description: User's password
```

### Type Mapping from Data Model

| Data Model Type | OpenAPI Type | Format |
|-----------------|--------------|--------|
| UUID | string | uuid |
| Text | string | - |
| Email | string | email |
| URL | string | uri |
| Integer | integer | int32/int64 |
| Decimal | number | float/double |
| Boolean | boolean | - |
| Timestamp | string | date-time |
| Date | string | date |
| Enum[a,b,c] | string | enum: [a,b,c] |

## Error Response Design

Use standard error format with machine-readable codes and human-readable messages.

See [ERROR-PATTERNS.md](ERROR-PATTERNS.md) for complete HTTP status codes, error code conventions, and response formats.

### Quick Reference

| Status | When to Use |
|--------|-------------|
| 400 | Invalid input format |
| 401 | Missing/invalid auth |
| 403 | No permission |
| 404 | Resource missing |
| 409 | State conflict |
| 422 | Business rule violation |
| 429 | Rate limit exceeded |
| 500 | Server error |

## List Endpoints

For endpoints returning collections, implement pagination, filtering, and sorting.

See [PAGINATION-PATTERNS.md](PAGINATION-PATTERNS.md) for offset vs cursor pagination, filtering operators, and sorting patterns.

### Quick Reference

```
GET /api/users?page=1&limit=20&role=admin&sort=-createdAt
```

## Brownfield Considerations

When existing API patterns are detected, align new endpoints:

| Aspect | Check For |
|--------|-----------|
| Base path | `/api/v1`, `/api`, etc. |
| Auth pattern | Bearer, API key, session |
| Error format | Existing error structure |
| Pagination | page/limit, cursor, offset |

Handle endpoint collisions:
- REUSE existing endpoints when possible
- RENAME to match existing patterns
- NEW only when no existing endpoint fits

## OpenAPI Structure

See [OPENAPI-TEMPLATE.yaml](OPENAPI-TEMPLATE.yaml) for a complete, copy-ready template with all sections.

### Minimal Structure

```yaml
openapi: 3.0.3
info:
  title: {Feature Name} API
  version: 1.0.0

servers:
  - url: /api

paths:
  /resource:
    get: ...
    post: ...

components:
  schemas: ...
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer

security:
  - bearerAuth: []
```

## Traceability

Track endpoint to requirement mapping:

| Endpoint | Method | FR | US | Description |
|----------|--------|-----|-----|-------------|
| /auth/login | POST | FR-001 | US#1 | User login |
| /users/me | GET | FR-004 | US#4 | Get current user |

## Validation

Validate OpenAPI specifications using the validation script:

```bash
python scripts/validate-openapi.py path/to/openapi.yaml
```

Checks: OpenAPI syntax, REST conventions, error responses, request bodies, operation IDs, security schemes, examples, and descriptions.

## Quality Checklist

Before finalizing API contracts:

- [ ] Every user action has an endpoint
- [ ] All endpoints have request schema (if applicable)
- [ ] All endpoints have success response schema
- [ ] All endpoints have error responses defined
- [ ] Naming follows REST conventions
- [ ] Authentication requirements documented
- [ ] Brownfield patterns matched (if applicable)
- [ ] OpenAPI spec is valid
- [ ] Traceability to requirements complete

## Anti-Patterns

| Avoid | Instead |
|-------|---------|
| Verb in URL (`/getUsers`) | Noun resource (`/users`) |
| GET for actions | POST for actions (`POST /users/{id}/archive`) |
| Missing error responses | Define all error cases |
| Inconsistent naming | Pick one style (kebab-case recommended) |
| Generic errors (just 400/500) | Specific error codes |
| No examples | Include realistic examples |
