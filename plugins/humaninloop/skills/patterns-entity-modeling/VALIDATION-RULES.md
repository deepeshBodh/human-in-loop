# Validation Rules

Reference documentation for documenting entity constraints, validation rules, and data integrity patterns.

## Validation Rule Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| **Type Constraints** | Data type enforcement | Text length, numeric range |
| **Required Fields** | Mandatory data | Non-null constraints |
| **Uniqueness** | No duplicates | Email unique, compound unique |
| **Format** | Pattern matching | Email format, URL format |
| **Business Rules** | Domain logic | Price > 0, endDate > startDate |
| **Referential** | Data integrity | Foreign key exists |

## Attribute-Level Validation

### Documentation Format

```markdown
### Attributes

| Attribute | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| email | Email | Yes | Unique, Format: email | User email |
| username | Text(30) | Yes | Unique, Pattern: ^[a-z0-9_]+$ | Login name |
| age | Integer | No | Range: 0-150 | User age |
| price | Decimal(10,2) | Yes | Min: 0.01 | Product price |
```

### Validation Column Patterns

| Pattern | Meaning | Example |
|---------|---------|---------|
| `Unique` | No duplicates in table | `Unique` |
| `Unique(scope)` | Unique within scope | `Unique(projectId)` |
| `Format: type` | Must match format | `Format: email` |
| `Pattern: regex` | Must match regex | `Pattern: ^[A-Z]{2}[0-9]{4}$` |
| `Range: min-max` | Numeric range | `Range: 1-100` |
| `Min: value` | Minimum value | `Min: 0` |
| `Max: value` | Maximum value | `Max: 1000` |
| `Length: min-max` | String length | `Length: 8-100` |
| `OneOf: [values]` | Enum enforcement | `OneOf: [draft,active]` |

## Entity-Level Constraints

Document constraints that span multiple attributes:

```markdown
### Constraints

| Name | Type | Fields | Rule |
|------|------|--------|------|
| uk_email | Unique | email | Email must be unique |
| uk_username | Unique | username | Username must be unique |
| uk_project_slug | Unique | projectId, slug | Slug unique within project |
| chk_date_range | Check | startDate, endDate | endDate >= startDate |
| chk_positive_price | Check | price | price > 0 |
```

### Compound Unique Constraints

When uniqueness spans multiple fields:

```markdown
### Constraints

| Name | Type | Fields | Description |
|------|------|--------|-------------|
| uk_member | Unique | userId, projectId | User can only join project once |
| uk_task_order | Unique | projectId, sortOrder | Unique task order per project |
| uk_slug | Unique | workspaceId, slug | Slug unique within workspace |
```

## Format Validation Patterns

### Common Formats

| Format | Pattern | Example Values |
|--------|---------|----------------|
| `email` | RFC 5322 email | user@example.com |
| `url` | Valid URL | https://example.com |
| `uuid` | UUID v4 | 550e8400-e29b-41d4-a716-446655440000 |
| `phone` | E.164 format | +14155551234 |
| `slug` | URL-safe string | my-project-name |
| `iso8601` | ISO 8601 date | 2024-01-15T10:30:00Z |

### Custom Patterns

```markdown
### Validation Rules

| Field | Pattern | Description |
|-------|---------|-------------|
| sku | `^[A-Z]{3}-[0-9]{6}$` | SKU format: ABC-123456 |
| postalCode | `^[0-9]{5}(-[0-9]{4})?$` | US postal code |
| hexColor | `^#[0-9A-Fa-f]{6}$` | Hex color code |
| semver | `^[0-9]+\.[0-9]+\.[0-9]+$` | Semantic version |
```

## Business Rule Validation

### Cross-Field Rules

```markdown
### Business Rules

| Rule ID | Fields | Condition | Error Message |
|---------|--------|-----------|---------------|
| BR-001 | startDate, endDate | endDate >= startDate | End date must be after start date |
| BR-002 | minPrice, maxPrice | maxPrice >= minPrice | Max price must exceed min price |
| BR-003 | quantity, maxQuantity | quantity <= maxQuantity | Quantity exceeds maximum |
```

### State-Dependent Rules

```markdown
### Conditional Validation

| State | Field | Rule |
|-------|-------|------|
| published | title | Required, Min length: 10 |
| published | content | Required, Min length: 100 |
| draft | title | Required only |
| submitted | reviewerId | Required |
```

## Referential Integrity

### Foreign Key Constraints

```markdown
### Foreign Keys

| Field | References | On Delete | On Update |
|-------|------------|-----------|-----------|
| userId | User.id | Cascade | Cascade |
| categoryId | Category.id | Set Null | Cascade |
| projectId | Project.id | Restrict | Cascade |
```

### Soft Delete Considerations

```markdown
### Soft Delete Rules

- Foreign keys should reference only non-deleted records
- Queries should filter: WHERE deletedAt IS NULL
- Cascade delete should set deletedAt, not hard delete
- Unique constraints should include deletedAt or use partial index
```

## Validation in data-model.md

### Inline in Attributes

```markdown
### Attributes

| Attribute | Type | Required | Default | Validation | Description |
|-----------|------|----------|---------|------------|-------------|
| email | Email | Yes | - | Unique, Format: email | User email |
| price | Decimal(10,2) | Yes | - | Min: 0.01 | Item price |
```

### Separate Constraints Section

```markdown
### Constraints

| Constraint | Type | Fields | Rule |
|------------|------|--------|------|
| uk_email | Unique | email | - |
| chk_price | Check | price | price > 0 |
| fk_user | Foreign Key | userId | References User.id |

### Business Rules

| Rule | Condition | Error |
|------|-----------|-------|
| Valid date range | endDate >= startDate | End must be after start |
```

## Common Validation Patterns

### User Registration

```markdown
| Field | Validation |
|-------|------------|
| email | Required, Unique, Format: email |
| username | Required, Unique, Length: 3-30, Pattern: ^[a-z0-9_]+$ |
| password | Required, Length: 8-100 |
| birthDate | Format: date, Range: 1900-today |
```

### E-commerce Product

```markdown
| Field | Validation |
|-------|------------|
| sku | Required, Unique, Pattern: ^[A-Z]{3}-[0-9]{6}$ |
| name | Required, Length: 1-200 |
| price | Required, Min: 0.01 |
| quantity | Required, Min: 0 |
| weight | Min: 0 |
```

### Content Management

```markdown
| Field | Validation |
|-------|------------|
| slug | Required, Unique(siteId), Pattern: ^[a-z0-9-]+$ |
| title | Required, Length: 1-200 |
| content | Conditional: Required when status=published |
| publishedAt | Conditional: Required when status=published |
```

## Validation Checklist

- [ ] All required fields marked in attributes table
- [ ] Unique constraints documented
- [ ] Format validations specified for typed fields
- [ ] Numeric ranges defined where applicable
- [ ] String length constraints specified
- [ ] Cross-field business rules documented
- [ ] Foreign key constraints with delete behavior
- [ ] Conditional validation rules noted
- [ ] Error messages defined for complex rules
