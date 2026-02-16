# Phase-Specific Review Checklists

This reference file contains detailed review checklists for each planning phase. Used by the Devil's Advocate when reviewing plan artifacts.

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

## Phase T0: Techspec Core Review

### Checklist Table

| Check | Question | Severity |
|-------|----------|----------|
| FR coverage | Is every functional requirement from spec.md mapped to at least one TR? | Critical |
| Orphan TRs | Are there technical requirements with no business source? | Critical |
| Testable criteria | Does every TR have measurable acceptance criteria? | Critical |
| Sourced constraints | Is every constraint traceable to a real limitation (not a preference)? | Critical |
| TR-constraint contradictions | Do any requirements conflict with stated constraints? | Critical |
| Dependency references | Do TRs reference relevant constraints and integrations? | Important |
| Priority assignment | Are TR priorities consistent with source FR priorities? | Important |
| RFC 2119 language | Do requirements use SHALL/SHOULD/MAY consistently? | Minor |

### Key Questions

- Which functional requirements have NO corresponding technical requirement?
- Are any constraints actually disguised technology preferences?
- Can each acceptance criterion be verified in a test?
- Do any requirements and constraints contradict each other?

---

## Phase T1: Techspec Supplementary Review

### Checklist Table

| Check | Question | Severity |
|-------|----------|----------|
| NFR measurability | Does every NFR have a specific, measurable target? | Critical |
| NFR measurement method | Is the measurement approach defined and feasible? | Critical |
| Integration completeness | Are all external systems catalogued with protocols? | Critical |
| Failure modes | Does every integration point have documented failure modes and fallbacks? | Critical |
| Data classification | Is all PII and sensitive data identified and classified? | Critical |
| Compliance coverage | Are relevant compliance requirements (GDPR, PCI, etc.) addressed? | Important |
| NFR-constraint conflicts | Do any NFR targets contradict existing constraints? | Critical |
| NFR source tracing | Do NFR sources trace to valid TRs or business requirements? | Important |
| Integration-constraint alignment | Do integration patterns respect stated constraints? | Important |
| Data sensitivity-requirements alignment | Does data classification cover all entities implied by requirements? | Important |
| Retention policies | Are data retention and deletion policies specified? | Important |
| Encryption standards | Are encryption requirements specified for each classification level? | Important |

### Key Questions

- Can each NFR target actually be measured with available tooling?
- What external systems are implied by requirements but not catalogued?
- Are fallback strategies realistic or aspirational?
- Is every sensitive data field accounted for across all technical requirements?
- Do any NFR targets conflict with each other (e.g., latency vs consistency)?

### Cross-Artifact Consistency (with Core)

| Check | Question | Severity |
|-------|----------|----------|
| NFR-TR alignment | Do NFR sources reference valid TR IDs from requirements.md? | Critical |
| Integration-constraint alignment | Do integration protocols respect constraints from constraints.md? | Important |
| Data sensitivity coverage | Does data classification cover entities implied by requirements.md? | Important |

---

## Phase B0: Research Review

### Checklist Table

| Check | Question | Severity |
|-------|----------|----------|
| Marker resolution | Are all `[NEEDS CLARIFICATION]` resolved? | Critical |
| Alternative analysis | Were 2+ alternatives considered? | Critical |
| Rationale quality | Is the "why" documented? | Critical |
| Constitution alignment | Do choices follow principles? | Important |
| Brownfield consideration | Was existing stack evaluated? | Important |
| Trade-off documentation | Are downsides acknowledged? | Important |

### Key Questions

- What unknowns were NOT addressed?
- Are any decisions made without considering alternatives?
- Is the rationale convincing, or just restating the choice?
- Were brownfield constraints properly considered?

---

## Phase B1: Data Model Review

### Checklist Table

| Check | Question | Severity |
|-------|----------|----------|
| Entity coverage | Is every noun from requirements modeled? | Critical |
| Attribute completeness | Do all entities have required fields? | Critical |
| Relationship definition | Are all connections documented? | Critical |
| Validation rules | Are constraints from requirements captured? | Important |
| State machines | Are stateful entities properly modeled? | Important |
| PII identification | Are sensitive fields marked? | Critical |
| Traceability | Can we trace entities to requirements? | Important |

### Key Questions

- What entities from the spec are missing?
- Are there relationships that should exist but don't?
- Are validation rules comprehensive?
- Did we miss any PII fields?

---

## Phase B2: Contract Review

### Checklist Table

| Check | Question | Severity |
|-------|----------|----------|
| Endpoint coverage | Does every user action have an endpoint? | Critical |
| Schema completeness | Are request/response schemas defined? | Critical |
| Error handling | Are failure modes documented? | Critical |
| Schema-model consistency | Do schemas match the data model? | Critical |
| Authentication | Are auth requirements clear? | Important |
| Examples | Are realistic scenarios documented? | Important |
| Naming consistency | Do endpoints follow conventions? | Minor |

### Key Questions

- What user actions don't have endpoints?
- Are there error scenarios not handled?
- Do the schemas actually match our data model?
- Is the quickstart documentation usable?

---

## Phase B3: Final Cross-Artifact Review

### Checklist Table

| Check | Question | Severity |
|-------|----------|----------|
| Spec-Research alignment | Do research decisions serve spec goals? | Critical |
| Research-Model consistency | Are model choices consistent with decisions? | Critical |
| Model-Contract consistency | Do schemas reflect the data model? | Critical |
| Requirement traceability | Can we trace from FR to endpoint? | Important |
| Constitution compliance | Do all artifacts follow principles? | Important |

### Cross-Reference Steps

1. **Traceability**: Can trace requirement -> artifact
2. **Consistency**: Artifacts agree with each other
3. **Completeness**: Nothing obviously missing

---

## Automated Validation

Before manual review, run the validation script:

```bash
# Single file
python scripts/check-artifacts.py .spec/plan/data-model.md

# Multiple files (enables entity consistency check)
python scripts/check-artifacts.py .spec/plan/research.md .spec/plan/data-model.md

# All plan artifacts
python scripts/check-artifacts.py .spec/plan/*.md
```

### Automated Check Coverage

| Check | Description | Applies To |
|-------|-------------|------------|
| `unresolved_markers` | Finds `[NEEDS CLARIFICATION]`, `[TBD]`, `[TODO]`, `[PLACEHOLDER]` | All files |
| `required_sections` | Verifies expected markdown headers exist | research.md, data-model.md |
| `traceability` | Confirms FR-XXX or US-XXX references present | All files |
| `pii_markers` | Checks if PII fields (email, phone, ssn, etc.) have `[PII]` annotation | data-model.md |
| `entity_consistency` | Validates entity names appear across related files | When 2+ files provided |

**Note**: OpenAPI/contract files are skipped (use `validate-openapi.py` instead).

### Example Output

```json
{
  "files": ["data-model.md"],
  "checks": [
    {"check": "unresolved_markers", "passed": false, "issues": ["Line 45: [NEEDS CLARIFICATION] marker found"]},
    {"check": "required_sections", "passed": true, "issues": []},
    {"check": "traceability", "passed": true, "fr_count": 5, "us_count": 3, "issues": []},
    {"check": "pii_markers", "passed": false, "issues": ["Line 23: 'email' field may need [PII] annotation"]}
  ],
  "summary": {"total": 4, "passed": 2, "failed": 2}
}
```

### Exit Codes

- `0` - All checks passed
- `1` - One or more checks failed
