# Checklist Item Generation

Templates and patterns for generating requirements quality checklist items.

---

## Item Format

```markdown
- [ ] CHK### - {Question about requirement quality}? [{Dimension(s)}, {Reference}]
```

### Components

| Component | Required | Format | Example |
|-----------|----------|--------|---------|
| Checkbox | Yes | `- [ ]` | `- [ ]` |
| ID | Yes | `CHK###` | `CHK015` |
| Question | Yes | Ends with `?` | `Are requirements defined?` |
| Dimension | Yes | `[Dimension]` | `[Completeness]` |
| Reference | Recommended | `Spec §X` or `Gap` | `Spec §2.1` |

---

## Generation Categories

### 1. Requirement Completeness

Checks if requirements exist for a scenario.

**Template**:
```markdown
- [ ] CHK### - Are [requirement type] defined for [scenario]? [Completeness, {Gap|Spec §X}]
```

**Examples**:
```markdown
- [ ] CHK001 - Are authentication requirements defined for password reset? [Completeness, Gap]
- [ ] CHK002 - Are data validation requirements specified for user input? [Completeness, Spec §3.2]
- [ ] CHK003 - Are error handling requirements defined for API failures? [Completeness, Gap]
- [ ] CHK004 - Are accessibility requirements documented for form controls? [Completeness, Gap]
```

---

### 2. Requirement Clarity

Checks if requirements are unambiguous.

**Template**:
```markdown
- [ ] CHK### - Is '[vague term]' quantified with specific criteria? [Clarity, {Ambiguity|Spec §X}]
```

**Examples**:
```markdown
- [ ] CHK010 - Is "fast response" quantified with specific timing? [Clarity, Ambiguity, Spec §NFR-2]
- [ ] CHK011 - Is "secure access" defined with specific requirements? [Clarity, Ambiguity]
- [ ] CHK012 - Is "user-friendly" defined with measurable criteria? [Clarity, Ambiguity]
- [ ] CHK013 - Is "appropriate" file size limit specified with a number? [Clarity, Spec §4.1]
```

---

### 3. Requirement Consistency

Checks if requirements align without conflicts.

**Template**:
```markdown
- [ ] CHK### - Are [requirements] consistent between [section A] and [section B]? [Consistency]
```

**Examples**:
```markdown
- [ ] CHK020 - Are session timeout values consistent between Security and UX sections? [Consistency]
- [ ] CHK021 - Is terminology for 'user' used consistently throughout? [Consistency]
- [ ] CHK022 - Are priority levels consistent between User Stories and Requirements? [Consistency]
- [ ] CHK023 - Do pagination requirements align between API and UI sections? [Consistency]
```

---

### 4. Acceptance Criteria Quality

Checks if success criteria are measurable.

**Template**:
```markdown
- [ ] CHK### - Can '[success criterion]' be objectively measured? [Measurability, {SC-X|Spec §X}]
```

**Examples**:
```markdown
- [ ] CHK030 - Can SC-001 "User successfully logs in" be objectively verified? [Measurability, SC-001]
- [ ] CHK031 - Are success criteria for search results quantified? [Measurability, SC-005]
- [ ] CHK032 - Can "smooth scrolling" be objectively measured? [Measurability, Ambiguity]
- [ ] CHK033 - Are acceptance criteria for file upload testable? [Measurability, FR-012]
```

---

### 5. Scenario Coverage

Checks if alternate flows are documented.

**Template**:
```markdown
- [ ] CHK### - Are requirements defined for [alternate flow/scenario]? [Coverage, {Gap|Spec §X}]
```

**Examples**:
```markdown
- [ ] CHK040 - Are requirements defined for concurrent user sessions? [Coverage, Gap]
- [ ] CHK041 - Is offline mode behavior documented? [Coverage, Gap]
- [ ] CHK042 - Are requirements defined for first-time user onboarding? [Coverage]
- [ ] CHK043 - Is the guest checkout flow specified? [Coverage, Spec §5.2]
```

---

### 6. Edge Case Coverage

Checks if boundary conditions are defined.

**Template**:
```markdown
- [ ] CHK### - Are boundary requirements defined for [limit condition]? [Edge Case]
```

**Examples**:
```markdown
- [ ] CHK050 - Are maximum file size limits defined for uploads? [Edge Case, Gap]
- [ ] CHK051 - Is behavior specified for empty search results? [Edge Case]
- [ ] CHK052 - Are requirements defined for session timeout during form submission? [Edge Case]
- [ ] CHK053 - Is maximum username length specified? [Edge Case, Spec §2.3]
- [ ] CHK054 - Are rate limiting thresholds defined? [Edge Case, Gap]
```

---

### 7. Non-Functional Requirements

Checks if quality attributes are quantified.

**Template**:
```markdown
- [ ] CHK### - Are [NFR type] requirements quantified for [operation]? [NFR, {Gap|Spec §X}]
```

**Examples**:
```markdown
- [ ] CHK060 - Are performance requirements quantified for search operations? [NFR, Gap]
- [ ] CHK061 - Are availability requirements specified with uptime percentage? [NFR]
- [ ] CHK062 - Are scalability requirements defined for concurrent users? [NFR, Spec §NFR-3]
- [ ] CHK063 - Are security requirements specified for data encryption? [NFR, Gap]
```

---

### 8. Dependencies & Assumptions

Checks if external factors are documented.

**Template**:
```markdown
- [ ] CHK### - Are [dependencies/assumptions] documented for [integration]? [Dependency]
```

**Examples**:
```markdown
- [ ] CHK070 - Are external API dependencies documented? [Dependency, Gap]
- [ ] CHK071 - Are third-party service assumptions stated? [Dependency]
- [ ] CHK072 - Are database version requirements documented? [Dependency]
- [ ] CHK073 - Are browser compatibility requirements specified? [Dependency, Spec §7.1]
```

---

## Domain-Specific Patterns

### Authentication/Security Domain

```markdown
- [ ] CHK### - Are authentication failure handling requirements defined? [Completeness, Gap]
- [ ] CHK### - Is account lockout policy specified (attempts, duration)? [Clarity]
- [ ] CHK### - Are password requirements documented (length, complexity)? [Completeness]
- [ ] CHK### - Are session management requirements specified? [Completeness]
- [ ] CHK### - Are data encryption requirements defined for storage and transit? [NFR]
```

### API Domain

```markdown
- [ ] CHK### - Are API response codes documented for all endpoints? [Completeness]
- [ ] CHK### - Are API error response formats specified? [Clarity]
- [ ] CHK### - Are rate limiting requirements defined? [NFR, Edge Case]
- [ ] CHK### - Are API versioning requirements documented? [Completeness]
- [ ] CHK### - Are authentication requirements specified for API access? [Completeness]
```

### UX Domain

```markdown
- [ ] CHK### - Are loading state requirements defined? [Completeness]
- [ ] CHK### - Are error message display requirements specified? [Clarity]
- [ ] CHK### - Are accessibility requirements documented (WCAG level)? [NFR]
- [ ] CHK### - Are responsive design breakpoints specified? [Clarity]
- [ ] CHK### - Are form validation feedback requirements defined? [Completeness]
```

### Data Domain

```markdown
- [ ] CHK### - Are data validation rules specified for all fields? [Completeness]
- [ ] CHK### - Are data retention requirements documented? [NFR]
- [ ] CHK### - Are data format requirements specified? [Clarity]
- [ ] CHK### - Are data migration requirements defined? [Coverage]
- [ ] CHK### - Are data backup requirements documented? [NFR]
```

---

## Checklist Structure Template

```markdown
# [DOMAIN] Requirements Quality Checklist: [FEATURE NAME]

**Purpose**: Validate [domain] requirement completeness and quality
**Created**: [DATE]
**Feature**: [Link to spec.md]

---

## Requirement Completeness

- [ ] CHK001 - [Item text] [Completeness, Reference]

## Requirement Clarity

- [ ] CHK010 - [Item text] [Clarity, Reference]

## Requirement Consistency

- [ ] CHK020 - [Item text] [Consistency]

## Acceptance Criteria Quality

- [ ] CHK030 - [Item text] [Measurability, Reference]

## Scenario Coverage

- [ ] CHK040 - [Item text] [Coverage, Reference]

## Edge Case Coverage

- [ ] CHK050 - [Item text] [Edge Case]

## Non-Functional Requirements

- [ ] CHK060 - [Item text] [NFR, Reference]

## Dependencies & Assumptions

- [ ] CHK070 - [Item text] [Dependency]
```
