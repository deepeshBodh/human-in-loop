# Phase-Specific Review Checklists

This reference file contains detailed review checklists for each planning phase. Used when reviewing plan artifacts.

## Phase A0: Codebase Discovery Review

### Checklist Table

| Check | Question | Severity |
|-------|----------|----------|
| Coverage | Were all source directories scanned? | Important |
| Entity detection | Were all entity patterns tried? | Critical |
| Endpoint detection | Were all route patterns tried? | Critical |
| Collision assessment | Are risk levels appropriate? | Critical |
| Evidence | Are file paths cited for all findings? | Important |

### Key Questions

- Did we miss any obvious source directories?
- Are there entities or endpoints that should have been found?
- Are collision risk levels realistic?

---

## Phase P1: Analysis Review

Reviews `requirements.md`, `constraints-and-decisions.md`, and `nfrs.md` together.

### Checklist Table — Requirements

| Check | Question | Severity |
|-------|----------|----------|
| FR coverage | Is every functional requirement from spec.md mapped to at least one TR? | Critical |
| Orphan TRs | Are there technical requirements with no business source? | Critical |
| Testable criteria | Does every TR have measurable acceptance criteria? | Critical |
| Dependency references | Do TRs reference relevant constraints and NFRs? | Important |
| Priority assignment | Are TR priorities consistent with source FR priorities? | Important |
| RFC 2119 language | Do requirements use MUST/SHOULD/MAY consistently? | Minor |

### Checklist Table — Constraints and Decisions

| Check | Question | Severity |
|-------|----------|----------|
| Sourced constraints | Is every constraint traceable to a real limitation (not a preference)? | Critical |
| TR-constraint contradictions | Do any requirements conflict with stated constraints? | Critical |
| Alternative analysis | Were 2+ alternatives considered for each decision? | Critical |
| Rationale quality | Does each decision explain WHY, not just WHAT? | Critical |
| Constraint-decision cross-refs | Does each decision reference the constraints that shaped it? | Important |
| Constitution alignment | Do choices follow project principles? | Important |
| Brownfield consideration | Was existing stack evaluated (if brownfield)? | Important |
| Trade-off documentation | Are downsides of chosen options acknowledged? | Important |

### Checklist Table — NFRs

| Check | Question | Severity |
|-------|----------|----------|
| NFR measurability | Does every NFR have a specific, measurable target? | Critical |
| NFR measurement method | Is the measurement approach defined and feasible? | Critical |
| NFR source tracing | Do NFR sources trace to valid TRs or business requirements? | Important |
| NFR-constraint conflicts | Do any NFR targets contradict existing constraints or decisions? | Critical |
| Category coverage | Are all relevant quality categories addressed? | Important |

### Key Questions

- Which functional requirements have NO corresponding technical requirement?
- Are any constraints actually disguised technology preferences?
- Can each acceptance criterion be verified in a test?
- Do any requirements and constraints contradict each other?
- What unknowns were NOT addressed by decisions?
- Are any decisions made without considering alternatives?
- Is the rationale convincing, or just restating the choice?
- Can each NFR target actually be measured with available tooling?
- Do any NFR targets conflict with each other (e.g., latency vs consistency)?

---

## Phase P2: Design Review

Reviews `data-model.md`, `contracts/api.yaml`, and `quickstart.md` together.

### Checklist Table — Data Model

| Check | Question | Severity |
|-------|----------|----------|
| Entity coverage | Is every noun from requirements modeled? | Critical |
| Attribute completeness | Do all entities have required fields? | Critical |
| Relationship definition | Are all connections documented with cardinality and delete behavior? | Critical |
| PII identification | Are sensitive fields annotated with classification? | Critical |
| Sensitivity details | Do Confidential+ attributes have full handling requirements? | Critical |
| Compliance coverage | Are relevant compliance requirements (GDPR, PCI, etc.) addressed? | Important |
| Retention policies | Are data retention and deletion policies specified? | Important |
| Encryption standards | Are encryption requirements specified for each classification level? | Important |
| Validation rules | Are constraints from requirements captured? | Important |
| State machines | Are stateful entities properly modeled? | Important |
| Standard fields | Do all entities have id, createdAt, updatedAt? | Important |
| Traceability | Can we trace entities to requirements? | Important |

### Checklist Table — API Contracts

| Check | Question | Severity |
|-------|----------|----------|
| Endpoint coverage | Does every user action have an endpoint? | Critical |
| Schema completeness | Are request/response schemas defined? | Critical |
| Error handling | Are failure modes documented with specific status codes? | Critical |
| Schema-model consistency | Do schemas match the data model entities? | Critical |
| Integration boundaries | Do endpoints wrapping external systems have x-integration documentation? | Critical |
| Failure modes | Does every integration boundary have documented failure modes and fallbacks? | Critical |
| Authentication | Are auth requirements clear? | Important |
| Examples | Are realistic scenarios documented? | Important |
| Naming consistency | Do endpoints follow conventions? | Minor |

### Checklist Table — Integration Guide

| Check | Question | Severity |
|-------|----------|----------|
| Flow coverage | Are common user flows documented with examples? | Important |
| Auth documentation | Is the authentication sequence clear? | Important |
| Error documentation | Are error handling patterns explained? | Important |
| External integrations | Is the external system boundary overview present? | Important |

### Key Questions

- What entities from the spec are missing?
- Are there relationships that should exist but don't?
- Did we miss any PII fields or sensitive data?
- Are encryption and retention requirements complete for all Confidential+ data?
- What user actions don't have endpoints?
- Are there error scenarios not handled?
- Do the schemas actually match our data model?
- Are integration failure modes realistic or aspirational?
- What external systems are implied by requirements but not documented?
- Is the quickstart documentation usable?

---

## Phase P3: Final Cross-Artifact Review

### Checklist Table

| Check | Question | Severity |
|-------|----------|----------|
| Requirements-decisions alignment | Do decisions serve the requirements they reference? | Critical |
| Decisions-model consistency | Are model choices consistent with technology decisions? | Critical |
| Model-contract consistency | Do schemas reflect the data model exactly? | Critical |
| Sensitivity-contract alignment | Do API responses respect data classification (no Restricted data in responses)? | Critical |
| Integration-contract alignment | Do contract integration boundaries match the systems implied by requirements? | Critical |
| Requirement traceability | Can we trace from FR to TR to entity to endpoint? | Important |
| Constitution compliance | Do all artifacts follow project principles? | Important |
| Constraint-design alignment | Do all design artifacts respect stated constraints? | Important |
| NFR-design feasibility | Can the design as specified meet the NFR targets? | Important |

### Cross-Reference Steps

1. **Traceability**: Can trace requirement → artifact
2. **Consistency**: Artifacts agree with each other
3. **Completeness**: Nothing obviously missing

---

## Automated Validation

Before manual review, run the validation script:

```bash
# Single file
python scripts/check-artifacts.py specs/{feature-id}/data-model.md

# Multiple files (enables entity consistency check)
python scripts/check-artifacts.py specs/{feature-id}/requirements.md specs/{feature-id}/data-model.md

# All plan artifacts
python scripts/check-artifacts.py specs/{feature-id}/*.md
```

### Automated Check Coverage

| Check | Description | Applies To |
|-------|-------------|------------|
| `unresolved_markers` | Finds `[NEEDS CLARIFICATION]`, `[TBD]`, `[TODO]`, `[PLACEHOLDER]` | All files |
| `required_sections` | Verifies expected markdown headers exist | All .md artifacts |
| `traceability` | Confirms FR-XXX references present | All files |
| `pii_markers` | Checks if PII fields have sensitivity annotations | data-model.md |
| `entity_consistency` | Validates entity names appear across related files | When 2+ files provided |

**Note**: OpenAPI/contract files are skipped (use `validate-openapi.py` instead).

### Exit Codes

- `0` — All checks passed
- `1` — One or more checks failed
