# Quality Dimensions

The 8 quality dimensions for evaluating requirements. Each dimension targets a specific aspect of requirement quality.

---

## Primary Dimensions (Always Check)

### [Completeness]

**Purpose**: Verify all necessary requirements are documented.

**What it checks**:
- All user stories have corresponding functional requirements
- All functional requirements have success criteria
- Dependencies are documented
- Assumptions are stated

**Question patterns**:
```markdown
- Are [requirement type] defined for [scenario]?
- Is [component] fully specified?
- Are all dependencies for [feature] documented?
```

**Example items**:
```markdown
- [ ] CHK001 - Are error handling requirements defined for authentication failures? [Completeness, Gap]
- [ ] CHK002 - Are data validation requirements specified for all input fields? [Completeness]
```

---

### [Clarity]

**Purpose**: Verify requirements are unambiguous and specific.

**What it checks**:
- Vague terms are quantified ("fast" -> "< 2 seconds")
- Subjective language is replaced with measurable criteria
- Technical jargon is defined
- Pronouns have clear referents

**Question patterns**:
```markdown
- Is '[vague term]' quantified with specific criteria?
- Is '[technical term]' defined in the glossary?
- Does '[requirement]' have a clear, measurable definition?
```

**Example items**:
```markdown
- [ ] CHK010 - Is "fast response" quantified with specific timing criteria? [Clarity, Ambiguity, Spec §NFR-2]
- [ ] CHK011 - Is "secure access" defined with specific security requirements? [Clarity]
```

---

### [Consistency]

**Purpose**: Verify requirements align without conflicts.

**What it checks**:
- No contradictory requirements
- Terminology used consistently
- Priorities don't conflict
- Edge cases don't violate main requirements

**Question patterns**:
```markdown
- Are requirements consistent between [section A] and [section B]?
- Is terminology for '[concept]' used consistently?
- Do [requirements] conflict with [other requirements]?
```

**Example items**:
```markdown
- [ ] CHK020 - Are session timeout requirements consistent between Security and UX sections? [Consistency]
- [ ] CHK021 - Is the term "user" used consistently (vs "customer", "client")? [Consistency]
```

---

### [Measurability]

**Purpose**: Verify requirements can be objectively verified.

**What it checks**:
- Success criteria are testable
- Acceptance criteria are quantified
- Performance requirements have numbers
- Quality attributes are measurable

**Question patterns**:
```markdown
- Can '[success criterion]' be objectively measured?
- Is '[requirement]' testable without subjective judgment?
- Are acceptance criteria for '[feature]' quantified?
```

**Example items**:
```markdown
- [ ] CHK030 - Can SC-001 "User successfully logs in" be objectively measured? [Measurability, Spec §SC-001]
- [ ] CHK031 - Are performance requirements quantified with specific thresholds? [Measurability]
```

---

## Secondary Dimensions (Context-Dependent)

### [Coverage]

**Purpose**: Verify all scenarios are addressed.

**What it checks**:
- Happy path defined
- Error paths defined
- Alternate flows documented
- Edge cases covered

**Question patterns**:
```markdown
- Are requirements defined for [alternate flow]?
- Is the [error scenario] documented?
- Are all user personas covered by [feature]?
```

**Example items**:
```markdown
- [ ] CHK040 - Are requirements defined for concurrent user sessions? [Coverage]
- [ ] CHK041 - Is the offline mode behavior documented? [Coverage, Gap]
```

---

### [Edge Case]

**Purpose**: Verify boundary conditions are defined.

**What it checks**:
- Minimum/maximum values specified
- Empty/null cases handled
- Overflow/underflow addressed
- Timing edge cases documented

**Question patterns**:
```markdown
- Are boundary requirements defined for [limit condition]?
- Is behavior specified when [value] is empty/null/zero?
- Are limits defined for [quantity]?
```

**Example items**:
```markdown
- [ ] CHK050 - Are maximum file size limits defined for uploads? [Edge Case]
- [ ] CHK051 - Is behavior specified for empty search results? [Edge Case]
- [ ] CHK052 - Are requirements defined for session timeout during form submission? [Edge Case]
```

---

## Tag Dimensions (Indicators)

### [Gap]

**Purpose**: Indicates a missing requirement that must be added.

**Usage**:
- Combined with other dimensions to indicate missing content
- Signals that content needs to be written, not just clarified
- Often paired with [Completeness] or [Coverage]

**Example items**:
```markdown
- [ ] CHK060 - Are rate limiting requirements defined for the API? [Completeness, Gap]
- [ ] CHK061 - Are accessibility requirements defined for form controls? [Coverage, Gap]
```

---

### [Ambiguity]

**Purpose**: Indicates vague language that needs clarification.

**Usage**:
- Combined with [Clarity] to highlight specific vague terms
- Signals that existing content needs refinement
- Points to specific terms or phrases

**Example items**:
```markdown
- [ ] CHK070 - Is "timely manner" defined with specific timing? [Clarity, Ambiguity]
- [ ] CHK071 - Is "appropriate level of security" quantified? [Clarity, Ambiguity]
```

---

## Dimension Selection Guidelines

| Situation | Primary Dimensions | Secondary Dimensions |
|-----------|-------------------|---------------------|
| New feature spec | Completeness, Clarity | Coverage, Edge Case |
| Security-focused | Measurability, Consistency | Edge Case |
| API design | Clarity, Consistency | Edge Case |
| User experience | Completeness, Coverage | Clarity |
| Performance requirements | Measurability | Edge Case |

---

## Coverage Analysis Formula

```
Coverage = (items with spec reference or gap marker) / (total items) x 100
```

- **Target**: >= 80% coverage
- **Below threshold**: Add missing traceability markers (Spec §X.Y or [Gap])
