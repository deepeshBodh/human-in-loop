# Contract Checks (Phase 2)

> Validation checks for contracts/ and quickstart.md artifacts.
> Used by Validator Agent during Phase 2 of the plan workflow.

---

## Check Categories

### Endpoint Coverage

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| CON-001 | User actions mapped | All user actions from spec have corresponding endpoints | auto-resolve |
| CON-002 | CRUD operations | All CRUD operations for entities are covered where needed | auto-resolve |
| CON-003 | No orphan endpoints | No endpoints exist without mapping to requirements | auto-resolve |

### Schema Completeness

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| CON-004 | Request schemas | Request schemas match data model entities | auto-resolve |
| CON-005 | Response schemas | Response schemas match data model entities | auto-resolve |
| CON-006 | Required fields | All required fields from data model marked in schemas | auto-resolve |

### Error Handling

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| CON-007 | Error responses | Error responses defined for all endpoints | auto-retry |
| CON-008 | Standard format | Error format is consistent across all endpoints | auto-retry |
| CON-009 | Edge case errors | Edge case errors covered (rate limit, timeout, validation) | auto-retry |

### Integration Quality

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| CON-010 | Happy path | Quickstart covers at least one happy path scenario | auto-retry |
| CON-011 | Error handling | Quickstart shows error handling example | auto-retry |
| CON-012 | Auth flow | Authentication flow documented in quickstart if applicable | auto-retry |

### Constitution Alignment [phase:2]

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| CON-013 | API standards | API design follows constitution API Standards principles | escalate |
| CON-014 | Security headers | Security requirements documented (auth, CORS, rate limits) | escalate |

---

## Tier Behavior

| Tier | Behavior | Max Retries |
|------|----------|-------------|
| `auto-resolve` | Validator flags, Contract Agent auto-fixes and logs | N/A |
| `auto-retry` | Contract Agent retries with guidance | 2 |
| `escalate` | Return to Supervisor for user decision | N/A |

---

## Gap Classification

| Priority | Checks | Rationale |
|----------|--------|-----------|
| Critical | CON-001, CON-013 | Missing endpoints or API standard violations are foundational |
| Important | CON-002, CON-004, CON-005, CON-006, CON-007, CON-008, CON-014 | Quality issues affecting implementation |
| Minor | CON-003, CON-009, CON-010, CON-011, CON-012 | Can be auto-resolved or are enhancement-level |

---

## Validation Process

```
1. Load contracts/*.yaml (OpenAPI specs)
2. Load quickstart.md
3. Load spec.md for requirement/user action comparison
4. Load data-model.md and entity_registry for schema validation
5. For each check in order:
   a. Execute check logic
   b. If FAIL:
      - Classify gap priority
      - Assign tier behavior
      - Add to gap queue
6. Build endpoint_registry from validated contracts
7. Return validation_report with:
   - total_checks
   - passed_count
   - gaps[] with priority, tier, description
   - endpoint_registry[] for traceability
   - result: pass | fail | partial
```

---

## Endpoint Registry Format

On successful validation, populate plan-context.md Endpoint Registry:

```markdown
| Method | Path | Request Schema | Response Schema | Error Codes | Source FRs |
|--------|------|----------------|-----------------|-------------|------------|
| POST | /auth/login | LoginRequest | AuthResponse | 400, 401 | FR-001, FR-002 |
| DELETE | /auth/logout | - | SuccessResponse | 401 | FR-003 |
| POST | /auth/reset | ResetRequest | SuccessResponse | 400, 404 | FR-004 |
```

---

## Contract File Validation

For OpenAPI contracts, validate:

```yaml
# Required sections
openapi: "3.0.0"
info:
  title: required
  version: required
paths:
  # At least one path
  /example:
    # At least one operation
    get:
      summary: required
      responses:
        200: required  # Success case
        4xx: required  # At least one error
```

---

## Example Gap Output

```json
{
  "gap_id": "G-CON-001",
  "check_id": "CON-001",
  "priority": "Critical",
  "tier": "auto-resolve",
  "description": "User action 'reset password' from US2 has no corresponding endpoint",
  "affected_fr": "FR-004",
  "affected_us": "US2",
  "suggested_action": "Contract Agent should add POST /auth/reset endpoint"
}
```
