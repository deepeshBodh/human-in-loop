# Domain Model Checks (Phase 1)

> Validation checks for data-model.md artifact.
> Used by Validator Agent during Phase 1 of the plan workflow.

---

## Check Categories

### Entity Coverage

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| MDL-001 | User story entities | All entities mentioned in spec user stories are present | auto-resolve |
| MDL-002 | Requirement entities | All entities implied by functional requirements are present | auto-resolve |
| MDL-003 | No orphan entities | No entities exist that aren't referenced by spec | auto-resolve |

### Relationship Completeness

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| MDL-004 | Relationships defined | All entity relationships are explicitly defined | auto-resolve |
| MDL-005 | Cardinality specified | Each relationship has cardinality (1:1, 1:N, N:M) | auto-resolve |
| MDL-006 | No circular deps | No unjustified circular dependencies between entities | auto-resolve |

### Attribute Clarity

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| MDL-007 | Types defined | All attributes have type definitions | auto-retry |
| MDL-008 | Required marked | Required vs optional clearly marked for each attribute | auto-retry |
| MDL-009 | Validation rules | Validation rules derived from spec constraints are documented | auto-retry |

### State Transitions

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| MDL-010 | State machines | State machines documented for stateful entities | auto-retry |
| MDL-011 | Triggers mapped | State transition triggers mapped to user actions | auto-retry |

### Constitution Alignment [phase:1]

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| MDL-012 | Privacy principles | Data privacy principles from constitution followed | escalate |
| MDL-013 | PII handling | PII fields identified and handling documented | escalate |

---

## Tier Behavior

| Tier | Behavior | Max Retries |
|------|----------|-------------|
| `auto-resolve` | Validator flags, Domain Model Agent auto-fixes and logs | N/A |
| `auto-retry` | Domain Model Agent retries with guidance | 2 |
| `escalate` | Return to Supervisor for user decision | N/A |

---

## Gap Classification

| Priority | Checks | Rationale |
|----------|--------|-----------|
| Critical | MDL-001, MDL-002, MDL-012 | Missing entities or privacy violations are foundational issues |
| Important | MDL-004, MDL-005, MDL-007, MDL-008, MDL-009, MDL-010, MDL-011, MDL-013 | Quality issues affecting downstream contract generation |
| Minor | MDL-003, MDL-006 | Can be auto-resolved; orphan entities and circular deps are cleanable |

---

## Validation Process

```
1. Load data-model.md
2. Load spec.md for requirement/user story comparison
3. Load research.md for technology constraints
4. For each check in order:
   a. Execute check logic
   b. If FAIL:
      - Classify gap priority
      - Assign tier behavior
      - Add to gap queue
5. Build entity_registry from validated data model
6. Return validation_report with:
   - total_checks
   - passed_count
   - gaps[] with priority, tier, description
   - entity_registry{} for downstream agents
   - result: pass | fail | partial
```

---

## Entity Registry Format

On successful validation, populate plan-context.md Entity Registry:

```markdown
| Entity | Attributes | Relationships | Validation Rules | Source FRs |
|--------|------------|---------------|------------------|------------|
| User | id, email, password_hash, created_at | has_many Sessions | email unique, password min 8 chars | FR-001, FR-002 |
| Session | id, user_id, token, expires_at | belongs_to User | expires_at future | FR-003 |
```

---

## Example Gap Output

```json
{
  "gap_id": "G-MDL-001",
  "check_id": "MDL-001",
  "priority": "Critical",
  "tier": "auto-resolve",
  "description": "Entity 'AuditLog' mentioned in US3 not found in data-model.md",
  "affected_fr": "FR-008",
  "affected_us": "US3",
  "suggested_action": "Domain Model Agent should add AuditLog entity"
}
```
