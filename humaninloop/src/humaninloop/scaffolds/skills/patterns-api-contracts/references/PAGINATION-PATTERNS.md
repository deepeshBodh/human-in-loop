# Pagination, Filtering, and Sorting Patterns

Patterns for implementing list endpoints with pagination, filtering, and sorting capabilities.

## Pagination Strategies

### Offset-Based Pagination

Best for: Simple lists, UIs with page numbers, small datasets.

```
GET /api/users?page=2&limit=20
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (1-indexed) |
| `limit` | integer | 20 | Items per page (max 100) |

**Response:**

```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 150,
    "totalPages": 8,
    "hasNext": true,
    "hasPrev": true
  }
}
```

**OpenAPI Schema:**

```yaml
PaginationMeta:
  type: object
  required:
    - page
    - limit
    - total
    - totalPages
  properties:
    page:
      type: integer
      minimum: 1
      description: Current page number (1-indexed)
      example: 2
    limit:
      type: integer
      minimum: 1
      maximum: 100
      description: Items per page
      example: 20
    total:
      type: integer
      minimum: 0
      description: Total number of items
      example: 150
    totalPages:
      type: integer
      minimum: 0
      description: Total number of pages
      example: 8
    hasNext:
      type: boolean
      description: Whether more pages exist
    hasPrev:
      type: boolean
      description: Whether previous pages exist
```

### Cursor-Based Pagination

Best for: Large datasets, real-time feeds, infinite scroll.

```
GET /api/users?cursor=eyJpZCI6MTIzfQ&limit=20
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cursor` | string | Opaque cursor from previous response |
| `limit` | integer | Items per page (default 20, max 100) |

**Response:**

```json
{
  "data": [...],
  "pagination": {
    "nextCursor": "eyJpZCI6MTQzfQ",
    "prevCursor": "eyJpZCI6MTIzfQ",
    "hasNext": true,
    "hasPrev": true
  }
}
```

**OpenAPI Schema:**

```yaml
CursorPaginationMeta:
  type: object
  required:
    - hasNext
    - hasPrev
  properties:
    nextCursor:
      type: string
      nullable: true
      description: Cursor for next page (null if no more pages)
      example: eyJpZCI6MTQzfQ
    prevCursor:
      type: string
      nullable: true
      description: Cursor for previous page
    hasNext:
      type: boolean
      description: Whether more items exist
    hasPrev:
      type: boolean
      description: Whether previous items exist
```

### Keyset Pagination

Best for: Large sorted datasets, when you need consistency.

```
GET /api/users?after_id=123&limit=20
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `after_id` | string | Return items after this ID |
| `before_id` | string | Return items before this ID |
| `limit` | integer | Items per page |

## Filtering Patterns

### Simple Equality Filters

```
GET /api/users?role=admin&status=active
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `{field}` | string | Exact match on field value |

**OpenAPI:**

```yaml
parameters:
  - name: role
    in: query
    description: Filter by user role
    schema:
      type: string
      enum: [admin, user, guest]
  - name: status
    in: query
    description: Filter by account status
    schema:
      type: string
      enum: [active, suspended, pending]
```

### Multi-Value Filters

```
GET /api/users?role=admin,user
GET /api/users?role[]=admin&role[]=user
```

**OpenAPI:**

```yaml
parameters:
  - name: role
    in: query
    description: Filter by one or more roles
    schema:
      type: array
      items:
        type: string
        enum: [admin, user, guest]
    style: form
    explode: false  # role=admin,user
```

### Range Filters

```
GET /api/orders?createdAt[gte]=2024-01-01&createdAt[lte]=2024-12-31
GET /api/orders?minAmount=100&maxAmount=500
```

**Operator Conventions:**

| Operator | Meaning | Example |
|----------|---------|---------|
| `[eq]` or none | Equals | `status=active` |
| `[ne]` | Not equals | `status[ne]=deleted` |
| `[gt]` | Greater than | `amount[gt]=100` |
| `[gte]` | Greater or equal | `createdAt[gte]=2024-01-01` |
| `[lt]` | Less than | `amount[lt]=500` |
| `[lte]` | Less or equal | `createdAt[lte]=2024-12-31` |
| `[in]` | In list | `status[in]=active,pending` |
| `[nin]` | Not in list | `status[nin]=deleted,archived` |

### Search Filters

```
GET /api/users?search=john
GET /api/users?q=john&searchFields=name,email
```

**OpenAPI:**

```yaml
parameters:
  - name: search
    in: query
    description: Full-text search across searchable fields
    schema:
      type: string
      minLength: 2
      maxLength: 100
  - name: searchFields
    in: query
    description: Comma-separated list of fields to search
    schema:
      type: string
      example: name,email
```

### Boolean Filters

```
GET /api/users?isVerified=true
GET /api/tasks?completed=false
```

**OpenAPI:**

```yaml
parameters:
  - name: isVerified
    in: query
    description: Filter by email verification status
    schema:
      type: boolean
```

### Date Range Filters

```
GET /api/orders?createdAfter=2024-01-01&createdBefore=2024-12-31
GET /api/logs?since=2024-01-01T00:00:00Z&until=2024-01-02T00:00:00Z
```

**OpenAPI:**

```yaml
parameters:
  - name: createdAfter
    in: query
    description: Filter items created on or after this date
    schema:
      type: string
      format: date
      example: "2024-01-01"
  - name: createdBefore
    in: query
    description: Filter items created on or before this date
    schema:
      type: string
      format: date
      example: "2024-12-31"
```

## Sorting Patterns

### Single Field Sort

```
GET /api/users?sort=createdAt
GET /api/users?sort=-createdAt      # Descending
GET /api/users?sortBy=createdAt&sortOrder=desc
```

**Conventions:**

| Pattern | Meaning |
|---------|---------|
| `sort=field` | Ascending order |
| `sort=-field` | Descending order (prefix with `-`) |
| `sortBy=field&sortOrder=asc\|desc` | Explicit direction |

**OpenAPI (Prefix Style):**

```yaml
parameters:
  - name: sort
    in: query
    description: "Sort field. Prefix with - for descending order."
    schema:
      type: string
      example: "-createdAt"
```

**OpenAPI (Explicit Style):**

```yaml
parameters:
  - name: sortBy
    in: query
    description: Field to sort by
    schema:
      type: string
      enum: [createdAt, updatedAt, name, email]
      default: createdAt
  - name: sortOrder
    in: query
    description: Sort direction
    schema:
      type: string
      enum: [asc, desc]
      default: desc
```

### Multi-Field Sort

```
GET /api/users?sort=role,-createdAt
GET /api/users?sort[]=role&sort[]=-createdAt
```

**OpenAPI:**

```yaml
parameters:
  - name: sort
    in: query
    description: "Comma-separated sort fields. Prefix with - for descending."
    schema:
      type: string
      example: "role,-createdAt"
```

## Complete List Endpoint Example

```yaml
/users:
  get:
    summary: List users
    description: Retrieve a paginated, filterable, sortable list of users.
    operationId: listUsers
    tags:
      - Users
    parameters:
      # Pagination
      - name: page
        in: query
        description: Page number (1-indexed)
        schema:
          type: integer
          minimum: 1
          default: 1
      - name: limit
        in: query
        description: Items per page
        schema:
          type: integer
          minimum: 1
          maximum: 100
          default: 20

      # Filtering
      - name: role
        in: query
        description: Filter by role
        schema:
          type: string
          enum: [admin, user, guest]
      - name: status
        in: query
        description: Filter by account status
        schema:
          type: string
          enum: [active, suspended, pending]
      - name: isVerified
        in: query
        description: Filter by verification status
        schema:
          type: boolean
      - name: createdAfter
        in: query
        description: Filter users created after this date
        schema:
          type: string
          format: date-time
      - name: search
        in: query
        description: Search by name or email
        schema:
          type: string
          minLength: 2

      # Sorting
      - name: sort
        in: query
        description: "Sort field with optional - prefix for descending"
        schema:
          type: string
          default: "-createdAt"
          example: "-createdAt"

    responses:
      '200':
        description: Paginated list of users
        content:
          application/json:
            schema:
              type: object
              required:
                - data
                - pagination
              properties:
                data:
                  type: array
                  items:
                    $ref: '#/components/schemas/UserResponse'
                pagination:
                  $ref: '#/components/schemas/PaginationMeta'
            example:
              data:
                - id: "550e8400-e29b-41d4-a716-446655440000"
                  email: "user@example.com"
                  name: "John Doe"
                  role: "user"
                  createdAt: "2024-01-15T10:30:00Z"
              pagination:
                page: 1
                limit: 20
                total: 150
                totalPages: 8
                hasNext: true
                hasPrev: false
```

## Response Headers for Pagination

Include helpful headers in list responses:

| Header | Description | Example |
|--------|-------------|---------|
| `X-Total-Count` | Total items | `150` |
| `X-Page` | Current page | `2` |
| `X-Per-Page` | Items per page | `20` |
| `X-Total-Pages` | Total pages | `8` |
| `Link` | RFC 5988 pagination links | `<...?page=3>; rel="next"` |

**Link Header Example:**

```
Link: </api/users?page=1&limit=20>; rel="first",
      </api/users?page=3&limit=20>; rel="next",
      </api/users?page=1&limit=20>; rel="prev",
      </api/users?page=8&limit=20>; rel="last"
```

## Best Practices

### Do

- Use consistent parameter names across all list endpoints
- Document max limits and defaults
- Return total count for offset pagination
- Include `hasNext`/`hasPrev` for UI state
- Validate and sanitize filter inputs
- Use indexes on sortable/filterable fields

### Avoid

- Allowing unlimited page sizes (set max like 100)
- Deep pagination with offset (use cursor for large datasets)
- Sorting on non-indexed fields
- Case-sensitive search without documentation
- Ignoring invalid filter values silently

## Filter Validation Error Example

```json
{
  "code": "INVALID_FILTER",
  "message": "Invalid filter parameters",
  "details": {
    "errors": [
      {
        "field": "role",
        "value": "superuser",
        "error": "Must be one of: admin, user, guest"
      },
      {
        "field": "createdAfter",
        "value": "not-a-date",
        "error": "Must be a valid ISO 8601 date-time"
      }
    ]
  }
}
```
