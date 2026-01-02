# Gap Grouping

Rules for grouping related gaps into focused clarification questions.

---

## The Grouping Rule

**Maximum 3 clarifications per iteration.** Group related gaps to minimize user fatigue.

### Why Grouping Matters

- **Reduces user fatigue**: 3 questions vs 10 questions
- **Provides context**: Related gaps form coherent questions
- **Enables compound answers**: One answer can resolve multiple gaps
- **Maintains focus**: User thinks about one domain at a time

---

## Grouping Criteria (Order Matters)

Apply these criteria in sequence:

### 1. Same FR Reference

Gaps referencing the same Functional Requirement belong together.

```markdown
# Input Gaps
G-001: CHK015 -> FR-003 "Auth failure handling?"
G-002: CHK016 -> FR-003 "Retry limit?"
G-003: CHK017 -> FR-003 "Lockout duration?"

# Grouped Output
Group 1 (FR-003): G-001, G-002, G-003
  -> Combined question about authentication error handling
```

### 2. Same Domain

Gaps in the same domain (auth, data, API, UX) group together.

```markdown
# Input Gaps (different FRs, same domain)
G-004: CHK020 -> FR-005 "Token expiration?"
G-005: CHK021 -> FR-008 "Session management?"

# Grouped Output
Group 2 (auth domain): G-004, G-005
  -> Combined question about authentication session handling
```

### 3. Same Section

Gaps in the same spec section group together.

```markdown
# Input Gaps (same section)
G-006: Spec §3.1 "Input validation rules?"
G-007: Spec §3.1 "Error message format?"

# Grouped Output
Group 3 (§3.1): G-006, G-007
  -> Combined question about form validation
```

### 4. Related Concepts

Gaps about related concepts (determined by semantic analysis) group together.

```markdown
# Input Gaps (related concepts)
G-008: "File size limit?"
G-009: "File type restrictions?"

# Grouped Output
Group 4 (file handling): G-008, G-009
  -> Combined question about upload constraints
```

---

## Prioritization Within Groups

When more than 3 groups exist, prioritize by:

### Rule 1: Critical Priority First

Groups containing Critical gaps come before Important-only groups.

```markdown
Group A: [Critical, Critical]     -> Priority 1
Group B: [Critical, Important]    -> Priority 2
Group C: [Important, Important]   -> Priority 3
```

### Rule 2: Larger Groups First

Among same-priority groups, larger groups come first.

```markdown
Group A: [Critical, Critical, Critical] (3 gaps) -> Priority 1
Group B: [Critical, Critical] (2 gaps)           -> Priority 2
```

### Rule 3: User Story Impact

Among same-size groups, P1 story impact comes first.

```markdown
Group A: Affects US-001 (P1) -> Priority 1
Group B: Affects US-005 (P2) -> Priority 2
```

---

## Grouping Algorithm

```python
def group_gaps(gaps_to_process, max_clarifications=3):
    """
    Group gaps into max_clarifications groups.
    """
    groups = []
    ungrouped = list(gaps_to_process)

    # Step 1: Group by FR reference
    fr_groups = group_by_fr(ungrouped)
    groups.extend(fr_groups)
    ungrouped = [g for g in ungrouped if not g.grouped]

    # Step 2: Group by domain
    domain_groups = group_by_domain(ungrouped)
    groups.extend(domain_groups)
    ungrouped = [g for g in ungrouped if not g.grouped]

    # Step 3: Group by section
    section_groups = group_by_section(ungrouped)
    groups.extend(section_groups)
    ungrouped = [g for g in ungrouped if not g.grouped]

    # Step 4: Group remaining by related concepts
    concept_groups = group_by_concepts(ungrouped)
    groups.extend(concept_groups)

    # Step 5: Prioritize and limit
    sorted_groups = prioritize_groups(groups)

    if len(sorted_groups) > max_clarifications:
        # Merge lower-priority groups
        selected = sorted_groups[:max_clarifications]
        deferred = sorted_groups[max_clarifications:]

        # Optionally merge deferred into last group
        # or defer entirely to next iteration

        return selected

    return sorted_groups
```

---

## Spec-Specific Grouping Context

### FR/CHK Traceability

Each gap links to:
- **CHK ID**: The checklist item that identified the gap
- **FR ID**: The functional requirement being validated

```markdown
Gap G-001:
  chk_id: CHK015
  fr_ref: FR-003
  chk_text: "Are auth failure requirements defined?"
  fr_text: "System shall handle authentication failures"
```

### Domain Extraction

Extract domains from spec content:

| Domain | Keywords |
|--------|----------|
| auth | authentication, login, password, session, token |
| data | database, storage, validation, format |
| api | endpoint, request, response, REST, HTTP |
| ux | display, interface, form, button, layout |
| security | encryption, access, permission, role |

### Section Reference

Track spec sections for grouping:

```markdown
§1 - Overview
§2 - User Stories
§3 - Functional Requirements
  §3.1 - Authentication
  §3.2 - Data Management
§4 - Non-Functional Requirements
```

---

## Example: Full Grouping

### Input: 8 Gaps

```markdown
G-001 (Critical): CHK015 -> FR-003 "Auth failure handling?"
G-002 (Critical): CHK016 -> FR-003 "Retry limit?"
G-003 (Important): CHK017 -> FR-003 "Lockout message?"
G-004 (Important): CHK022 -> FR-007 "Session timeout?"
G-005 (Important): CHK023 -> FR-007 "Session renewal?"
G-006 (Minor): CHK030 -> FR-012 "Button color?"
G-007 (Minor): CHK031 -> FR-015 "Tooltip text?"
G-008 (Important): CHK025 -> FR-008 "API error format?"
```

### Step 1: Filter

```markdown
To Process: G-001, G-002, G-003, G-004, G-005, G-008 (6 gaps)
Deferred: G-006, G-007 (2 minor gaps)
```

### Step 2: Group by FR

```markdown
Group A (FR-003): G-001, G-002, G-003 [Critical, Critical, Important]
Group B (FR-007): G-004, G-005 [Important, Important]
Group C (FR-008): G-008 [Important]
```

### Step 3: Prioritize

```markdown
Rank 1: Group A (has Critical gaps, 3 gaps)
Rank 2: Group B (Important only, 2 gaps)
Rank 3: Group C (Important only, 1 gap)
```

### Step 4: Select Top 3

All 3 groups selected -> 3 clarifications.

### Output

```markdown
Clarification C1.1: Auth failure handling (G-001, G-002, G-003)
Clarification C1.2: Session management (G-004, G-005)
Clarification C1.3: API error format (G-008)
```
