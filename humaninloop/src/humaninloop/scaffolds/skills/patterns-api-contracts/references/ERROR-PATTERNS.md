# Error Patterns Reference

Comprehensive error handling patterns for RESTful APIs including HTTP status codes, error response formats, and error code conventions.

## Standard Error Format

All API errors should follow this consistent format:

```yaml
ErrorResponse:
  type: object
  required:
    - code
    - message
  properties:
    code:
      type: string
      description: Machine-readable error code
      example: INVALID_CREDENTIALS
    message:
      type: string
      description: Human-readable message
      example: Invalid email or password
    details:
      type: object
      additionalProperties: true
      description: Additional error context
```

### Error Response Example

```json
{
  "code": "VALIDATION_ERROR",
  "message": "One or more fields are invalid",
  "details": {
    "fields": [
      {"field": "email", "error": "Invalid email format"},
      {"field": "password", "error": "Must be at least 8 characters"}
    ]
  }
}
```

## HTTP Status Codes

### Client Errors (4xx)

| Status | Name | When to Use | Example Codes |
|--------|------|-------------|---------------|
| 400 | Bad Request | Invalid input format, malformed JSON | INVALID_INPUT, VALIDATION_ERROR, MALFORMED_REQUEST |
| 401 | Unauthorized | Missing or invalid authentication | UNAUTHORIZED, TOKEN_EXPIRED, TOKEN_INVALID |
| 403 | Forbidden | Authenticated but no permission | FORBIDDEN, ACCESS_DENIED, INSUFFICIENT_PERMISSIONS |
| 404 | Not Found | Resource does not exist | NOT_FOUND, USER_NOT_FOUND, RESOURCE_NOT_FOUND |
| 405 | Method Not Allowed | HTTP method not supported | METHOD_NOT_ALLOWED |
| 409 | Conflict | State conflict with current resource | CONFLICT, ALREADY_EXISTS, VERSION_CONFLICT |
| 410 | Gone | Resource permanently deleted | GONE, RESOURCE_DELETED |
| 422 | Unprocessable Entity | Business rule violation | UNPROCESSABLE, RULE_VIOLATION, BUSINESS_ERROR |
| 429 | Too Many Requests | Rate limit exceeded | RATE_LIMITED, QUOTA_EXCEEDED |

### Server Errors (5xx)

| Status | Name | When to Use | Example Codes |
|--------|------|-------------|---------------|
| 500 | Internal Server Error | Unexpected error | INTERNAL_ERROR, SERVER_ERROR |
| 502 | Bad Gateway | Upstream service failed | BAD_GATEWAY, UPSTREAM_ERROR |
| 503 | Service Unavailable | Service temporarily down | SERVICE_UNAVAILABLE, MAINTENANCE |
| 504 | Gateway Timeout | Upstream timeout | GATEWAY_TIMEOUT, REQUEST_TIMEOUT |

## Error Code Conventions

### Naming Rules

1. **Use SCREAMING_SNAKE_CASE**: `INVALID_EMAIL`, not `invalidEmail`
2. **Be specific**: `EMAIL_ALREADY_EXISTS`, not just `CONFLICT`
3. **Include resource**: `USER_NOT_FOUND`, not just `NOT_FOUND`
4. **Describe the problem**: `PASSWORD_TOO_WEAK`, not `INVALID_PASSWORD`

### Standard Error Codes by Domain

#### Authentication

| Code | Status | Description |
|------|--------|-------------|
| UNAUTHORIZED | 401 | No authentication provided |
| TOKEN_EXPIRED | 401 | JWT/session has expired |
| TOKEN_INVALID | 401 | Token format or signature invalid |
| INVALID_CREDENTIALS | 401 | Wrong email or password |
| ACCOUNT_LOCKED | 403 | Account locked due to violations |
| ACCOUNT_DISABLED | 403 | Account disabled by admin |
| MFA_REQUIRED | 403 | Multi-factor authentication needed |

#### Authorization

| Code | Status | Description |
|------|--------|-------------|
| FORBIDDEN | 403 | Generic forbidden |
| ACCESS_DENIED | 403 | No access to this resource |
| INSUFFICIENT_PERMISSIONS | 403 | Missing required permission |
| ROLE_REQUIRED | 403 | Specific role needed |
| OWNERSHIP_REQUIRED | 403 | Must be resource owner |

#### Validation

| Code | Status | Description |
|------|--------|-------------|
| VALIDATION_ERROR | 400 | One or more fields invalid |
| INVALID_EMAIL | 400 | Email format invalid |
| INVALID_PASSWORD | 400 | Password doesn't meet requirements |
| REQUIRED_FIELD_MISSING | 400 | Required field not provided |
| INVALID_FORMAT | 400 | Field format doesn't match expected |
| VALUE_OUT_OF_RANGE | 400 | Numeric value outside bounds |
| STRING_TOO_LONG | 400 | String exceeds max length |
| STRING_TOO_SHORT | 400 | String below min length |

#### Resource Operations

| Code | Status | Description |
|------|--------|-------------|
| RESOURCE_NOT_FOUND | 404 | Generic resource not found |
| USER_NOT_FOUND | 404 | User doesn't exist |
| EMAIL_ALREADY_EXISTS | 409 | Email already registered |
| USERNAME_TAKEN | 409 | Username already in use |
| VERSION_CONFLICT | 409 | Optimistic locking conflict |
| RESOURCE_DELETED | 410 | Resource was deleted |

#### Rate Limiting

| Code | Status | Description |
|------|--------|-------------|
| RATE_LIMITED | 429 | Too many requests |
| QUOTA_EXCEEDED | 429 | API quota exhausted |
| CONCURRENT_LIMIT | 429 | Too many concurrent requests |

## Endpoint-Specific Error Documentation

### Format for Error Tables

Document errors per endpoint using this format:

```markdown
## Error Responses: POST /api/users

| Status | Code | Condition | Response Details |
|--------|------|-----------|------------------|
| 400 | INVALID_EMAIL | Email format invalid | `details.field: "email"` |
| 400 | INVALID_PASSWORD | Password less than 8 chars or too weak | `details.requirements: [...]` |
| 409 | EMAIL_ALREADY_EXISTS | Email already registered | `details.email: "user@..."` |
| 422 | TERMS_NOT_ACCEPTED | Terms acceptance flag not set | None |
| 429 | RATE_LIMITED | More than 5 attempts per minute | `details.retryAfter: 60` |
```

### Authentication Endpoint Errors

```markdown
## POST /api/auth/login

| Status | Code | Condition |
|--------|------|-----------|
| 400 | INVALID_INPUT | Missing email or password |
| 401 | INVALID_CREDENTIALS | Wrong email or password |
| 403 | ACCOUNT_LOCKED | Too many failed attempts |
| 403 | ACCOUNT_DISABLED | Account disabled by admin |
| 429 | RATE_LIMITED | Too many login attempts |
```

```markdown
## POST /api/auth/refresh

| Status | Code | Condition |
|--------|------|-----------|
| 400 | INVALID_INPUT | Missing refresh token |
| 401 | TOKEN_EXPIRED | Refresh token expired |
| 401 | TOKEN_INVALID | Token revoked or malformed |
```

## Error Response Headers

Include helpful headers with error responses:

| Header | Purpose | Example |
|--------|---------|---------|
| `X-Request-Id` | Trace ID for debugging | `req_abc123xyz` |
| `Retry-After` | Seconds until retry allowed | `60` |
| `X-RateLimit-Limit` | Request limit per window | `100` |
| `X-RateLimit-Remaining` | Requests left in window | `0` |
| `X-RateLimit-Reset` | Unix timestamp of reset | `1699999999` |

## OpenAPI Error Schema

```yaml
components:
  schemas:
    ErrorResponse:
      type: object
      required:
        - code
        - message
      properties:
        code:
          type: string
          description: Machine-readable error code in SCREAMING_SNAKE_CASE
          example: VALIDATION_ERROR
        message:
          type: string
          description: Human-readable error message
          example: One or more fields are invalid
        details:
          type: object
          additionalProperties: true
          description: Additional context about the error
          example:
            fields:
              - field: email
                error: Invalid email format

    ValidationErrorResponse:
      allOf:
        - $ref: '#/components/schemas/ErrorResponse'
        - type: object
          properties:
            details:
              type: object
              properties:
                fields:
                  type: array
                  items:
                    type: object
                    properties:
                      field:
                        type: string
                      error:
                        type: string

  responses:
    BadRequest:
      description: Invalid request format or validation error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            code: VALIDATION_ERROR
            message: One or more fields are invalid

    Unauthorized:
      description: Authentication required or invalid
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            code: UNAUTHORIZED
            message: Authentication required

    Forbidden:
      description: Insufficient permissions
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            code: FORBIDDEN
            message: You do not have permission to access this resource

    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            code: NOT_FOUND
            message: The requested resource was not found

    TooManyRequests:
      description: Rate limit exceeded
      headers:
        Retry-After:
          schema:
            type: integer
          description: Seconds until retry is allowed
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            code: RATE_LIMITED
            message: Too many requests, please try again later
```

## Anti-Patterns

Avoid these common error handling mistakes:

| Anti-Pattern | Problem | Better Approach |
|--------------|---------|-----------------|
| Generic 400/500 | No actionable info | Use specific status + code |
| Error in 200 | Clients miss errors | Use appropriate status codes |
| Stack traces in prod | Security risk | Log internally, return safe message |
| Inconsistent format | Hard to parse | Use standard ErrorResponse |
| Missing codes | Can't programmatically handle | Always include machine-readable code |
| Vague messages | User can't fix issue | Explain what went wrong and how to fix |
