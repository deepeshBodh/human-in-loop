# Phase 1: Domain Model Procedures

Detailed procedures for the Domain Model phase (plan-builder, phase 1).

---

## Mission

Transform feature specifications into structured data models. Output: `data-model.md` with entities, relationships, attributes, validation rules, and state machines.

---

## Entity Extraction

### Sources

Identify entities from:
- User story mentions ("As a User...", "the Task...")
- Requirement subjects ("System MUST store...", "Users MUST have...")
- Key Entities section in spec

### Entity Classification

For each potential entity:
- Is this a first-class entity needing persistence?
- Is this an attribute of another entity?
- Is this a relationship entity (many-to-many)?

### Traceability

Record for each entity:
- Which FR-xxx requires this entity
- Which US# mentions this entity

---

## Attribute Definition

For each entity:

### 1. Extract Attributes
- Information mentioned in requirements
- Information implied by requirements
- Technical attributes (id, timestamps)

### 2. Define Each Attribute
- **Name**: Consistent naming convention
- **Type**: Conceptual (text, number, date, boolean, enum)
- **Required**: Yes/No
- **Default**: If applicable

### 3. Mark Special Attributes
- Primary identifiers
- Foreign keys (relationships)
- Computed/derived values
- PII fields (mark for privacy)

---

## Relationship Modeling

For each entity pair:

### 1. Determine Type
- One-to-one (1:1)
- One-to-many (1:N)
- Many-to-many (N:M)

### 2. Document Details
- Direction (which owns which)
- Cardinality (required vs optional)
- Cascade behavior (on delete)

### 3. Join Entities
For N:M relationships:
- Create explicit relationship entity if needed
- Document any relationship attributes

---

## Validation Rules

### Field-Level
- Format constraints (email, URL)
- Length limits (min, max characters)
- Range constraints (min, max values)
- Enum/allowed values

### Entity-Level
- Required field combinations
- Cross-field validations
- Business rule constraints

### Relationship-Level
- Referential integrity rules
- Cardinality enforcement

---

## State Machine Modeling

For stateful entities:

### 1. Identify States
- Status fields mentioned
- Workflow stages implied
- Lifecycle phases

### 2. Document Transitions
- From state → To state
- Trigger (user action or system event)
- Guards (conditions required)
- Side effects (what happens)

---

## Entity Registry

Populate plan-context.md with:

```markdown
| Entity | Status | Source FRs | PII Fields | State Machine |
|--------|--------|------------|------------|---------------|
| User | [NEW] | FR-001, FR-002 | email | No |
| Session | [EXTENDS EXISTING] | FR-003 | - | Yes |
```

---

## Quality Checklist

- [ ] Every entity from spec is modeled
- [ ] Every attribute has type, required flag, validation
- [ ] All relationships have cardinality and direction
- [ ] PII fields identified and marked
- [ ] State machines documented for stateful entities
- [ ] Constitution `[phase:1]` data privacy checked
- [ ] Entity Registry in plan-context.md complete
- [ ] Traceability to FR-xxx documented
