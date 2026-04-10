---
name: patterns-entity-modeling
description: This skill MUST be invoked when the user says "extract entities", "define data model", "model relationships", "entity modeling", or "domain model". SHOULD also invoke when user mentions "relationship", "cardinality", "state machine", or "data attributes".
---

# Modeling Domain Entities

## Overview

Extract and model domain entities from requirements using Domain-Driven Design principles. This skill covers entity identification, attribute definition, relationship modeling, and state machine documentation.

## When to Use

- Creating data-model.md from requirements or specifications
- Extracting entities from user stories and functional requirements
- Defining attributes, types, and constraints for entities
- Modeling relationships between entities with cardinality
- Documenting state machines for stateful entities
- Brownfield analysis of existing data models

## When NOT to Use

- **API contract design** - Use `humaninloop:patterns-api-contracts` instead
- **Database schema migration** - This skill is conceptual, not implementation
- **When data model already exists and is complete** - Don't duplicate work
- **Pure validation rules** - Model entities first, then add validation
- **Technical architecture decisions** - Use `humaninloop:patterns-technical-decisions`

## Entity Extraction

### Identification Heuristics

Look for entities in:

| Source | Pattern | Example |
|--------|---------|---------|
| **User stories** | "As a [Role]..." | User, Admin, Guest |
| **Subjects** | "The [Entity] must..." | Task, Order, Product |
| **Actions** | "...create a [Entity]" | Comment, Message, Report |
| **Possessives** | "[Entity]'s [attribute]" | User's profile, Order's items |
| **Status mentions** | "[Entity] status" | TaskStatus, OrderState |

### Entity vs. Attribute Decision

```
IF concept has its own lifecycle → Entity
IF concept only exists within another → Attribute
IF concept connects two entities → Relationship (possibly join entity)
IF concept has just one value → Attribute

Examples:
- "user email" → Attribute of User (just one value)
- "user address" → Could be Entity (if reused) or Attribute (if embedded)
- "order items" → Separate entity (has own lifecycle)
- "task status" → Enum/attribute (limited values)
```

### Brownfield Entity Status

When modeling in brownfield projects:

| Status | Meaning | Action |
|--------|---------|--------|
| `[NEW]` | Entity doesn't exist | Create full definition |
| `[EXTENDS EXISTING]` | Adding to existing entity | Document new fields only |
| `[REUSES EXISTING]` | Using existing as-is | Reference only |
| `[RENAMED]` | Avoiding collision | Document new name + reason |

## Attribute Definition

### Standard Attributes

Every entity typically needs:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | Identifier | Yes | Primary key |
| createdAt | Timestamp | Yes | Creation time |
| updatedAt | Timestamp | Yes | Last modification |
| deletedAt | Timestamp | No | Soft delete marker |

### Attribute Format

```markdown
| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| id | UUID | Yes | auto-generated | Unique identifier |
| email | Email | Yes | - | User's email address |
| name | Text(100) | No | null | Display name |
| role | Enum[admin,member,guest] | Yes | member | Access level |
| isVerified | Boolean | Yes | false | Email verified flag |
```

### Conceptual Types

Use conceptual types (not database-specific):

| Conceptual Type | Description |
|-----------------|-------------|
| `Identifier` / `UUID` | Unique identifier |
| `Text` / `Text(N)` | String with optional max length |
| `Email` | Email format string |
| `URL` | URL format string |
| `Integer` | Whole number |
| `Decimal` / `Decimal(P,S)` | Decimal with precision |
| `Boolean` | True/false |
| `Timestamp` | Date and time |
| `Date` | Date only |
| `Enum[values]` | Fixed set of values |
| `JSON` | Structured data |
| `Reference(Entity)` | Foreign key reference |

### PII Identification

Mark sensitive fields:

```markdown
| Attribute | Type | Required | PII | Description |
|-----------|------|----------|-----|-------------|
| email | Email | Yes | **PII** | User's email |
| phone | Text(20) | No | **PII** | Phone number |
| ssn | Text(11) | No | **PII-SENSITIVE** | Social security |
```

## Relationship Modeling

Relationships connect entities with defined cardinality: One-to-One (1:1), One-to-Many (1:N), or Many-to-Many (N:M).

See [RELATIONSHIP-PATTERNS.md](references/RELATIONSHIP-PATTERNS.md) for detailed patterns, join entity examples, and documentation formats.

### Relationship Diagram (Text)

```markdown
## Entity Relationships

```
User ──1:N──▶ Task (owns)
User ──1:N──▶ Session (has)
User ◀──N:M──▶ Project (via ProjectMember)
Task ──N:1──▶ Project (belongs to)
```
```

## State Machine Modeling

Entities with status fields need state transition documentation.

See [STATE-MACHINES.md](references/STATE-MACHINES.md) for patterns, diagram formats, and common workflows.

### When to Model State

Model state machines when:
- Entity has a `status` or `state` field
- Requirements mention workflow or lifecycle
- Specific actions change entity state
- Certain actions only valid in certain states

## Validation Rules

Constraints and validation rules ensure data integrity.

See [VALIDATION-RULES.md](references/VALIDATION-RULES.md) for constraint patterns, format validations, and business rule documentation.

## data-model.md Structure

```markdown
# Data Model: {feature_id}

> Entity definitions and relationships for the feature.
> Generated by Domain Architect.

---

## Summary

| Entity | Attributes | Relationships | Status |
|--------|------------|---------------|--------|
| User | 8 | 3 | [EXTENDS EXISTING] |
| Session | 5 | 1 | [NEW] |
| ...

---

## Entity: User [EXTENDS EXISTING]

> Existing entity extended with authentication fields.

### Attributes

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| passwordHash | Text | Yes | - | Hashed password |
| lastLoginAt | Timestamp | No | null | Last login time |

### Existing Attributes (Not Modified)

| Attribute | Type | Description |
|-----------|------|-------------|
| id | UUID | Existing primary key |
| email | Email | Existing email field |

---

## Entity: Session [NEW]

> User authentication session.

### Attributes

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| id | UUID | Yes | auto | Session identifier |
| userId | Reference(User) | Yes | - | Owning user |
| token | Text(255) | Yes | - | Session token |
| expiresAt | Timestamp | Yes | - | Expiration time |
| createdAt | Timestamp | Yes | auto | Creation time |

### Relationships

| Relationship | Type | Target | Description |
|--------------|------|--------|-------------|
| user | N:1 | User | Session belongs to user |

---

## Relationships

[Relationship documentation]

---

## State Machines

[State machine documentation if applicable]

---

## Traceability

| Entity | Source Requirements |
|--------|---------------------|
| User | FR-001, FR-002, US#1 |
| Session | FR-003, US#2 |
```

## Quality Checklist

Before finalizing entity model, verify:

- [ ] Every noun from requirements evaluated for entity status
- [ ] Each entity has id, createdAt, updatedAt fields
- [ ] All attributes have type, required flag, description
- [ ] Relationships include cardinality and direction
- [ ] PII fields marked and documented
- [ ] State machines documented for stateful entities
- [ ] Brownfield status indicated for each entity
- [ ] Traceability to requirements documented

## Common Mistakes

### Missing Entities
❌ Skipping entities mentioned in requirements ("we'll add that later")
✅ Evaluate every noun from requirements for entity status

### Anemic Entities
❌ Entity with only `id` field and no attributes
✅ Every entity needs meaningful attributes that describe its purpose

### Implementation Types
❌ Using `VARCHAR(255)`, `INT(11)`, `BIGINT` in data model
✅ Use conceptual types: `Text(100)`, `Integer`, `Identifier`

### Undefined Relationships
❌ Reference attributes without relationship documentation
✅ Every `Reference(Entity)` needs cardinality and relationship description

### Hidden State Machines
❌ Status/state fields without transition documentation
✅ Every status field needs state machine diagram and valid transitions

### Unmarked PII
❌ Email, phone, address fields without PII markers
✅ Always mark sensitive data with `**PII**` or `**PII-SENSITIVE**`

### Orphan Entities
❌ Entities with no relationships to other entities
✅ Every entity connects to at least one other entity (or is explicitly standalone)
