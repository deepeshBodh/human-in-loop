# Anti-Patterns

Prohibited patterns that MUST NOT appear in requirements quality checklists.

If ANY of these appear, the checklist FAILS validation.

---

## Implementation Verbs (NEVER USE)

These verbs test implementation behavior, not requirement quality:

| Prohibited Pattern | Why It's Wrong |
|-------------------|----------------|
| "Verify [system] [does/shows/displays]..." | Tests runtime behavior |
| "Test [feature] [works/responds]..." | Tests implementation |
| "Confirm [element] [navigates/clicks]..." | Tests UI interaction |
| "Check [API] [returns/responds]..." | Tests API behavior |
| "Validate [form] [submits/saves]..." | Tests form submission |
| "Ensure [component] [renders/loads]..." | Tests rendering |

### Examples of Violations

```markdown
# WRONG - Tests implementation
- [ ] Verify the login button displays correctly
- [ ] Test that the API returns 200 on success
- [ ] Confirm clicking submit saves the form
- [ ] Check that error messages appear on validation failure

# RIGHT - Tests requirements
- [ ] Are display requirements defined for the login button? [Completeness]
- [ ] Are API response codes documented for success/failure? [Clarity]
- [ ] Are form submission requirements specified? [Completeness]
- [ ] Are error message requirements defined for validation failures? [Completeness, Gap]
```

---

## Implementation References (NEVER USE)

These phrases describe implementation outcomes, not requirement quality:

| Prohibited Phrase | Why It's Wrong |
|------------------|----------------|
| "...displays correctly" | Subjective implementation outcome |
| "...works properly" | Subjective implementation outcome |
| "...renders successfully" | Implementation outcome |
| "...responds quickly" | Vague implementation outcome |
| "...handles gracefully" | Subjective behavior |
| "...functions as expected" | Implementation validation |

### Examples of Violations

```markdown
# WRONG - Implementation references
- [ ] Error messages display correctly
- [ ] The form works properly on mobile
- [ ] Charts render successfully with large datasets
- [ ] The API responds quickly to requests

# RIGHT - Requirement questions
- [ ] Are error message display requirements defined? [Completeness]
- [ ] Are mobile-specific requirements documented? [Coverage]
- [ ] Are chart performance requirements quantified for large datasets? [Measurability]
- [ ] Are API response time requirements specified? [Clarity, NFR]
```

---

## Test-Focused Language (NEVER USE)

These patterns belong in test plans, not requirements checklists:

| Prohibited Pattern | Why It's Wrong |
|-------------------|----------------|
| "Test that..." | Test execution language |
| "Verify functionality of..." | Functional testing |
| "Validate behavior when..." | Behavior testing |
| "Check performance of..." | Performance testing |
| "Ensure compliance with..." | Compliance testing |

### Examples of Violations

```markdown
# WRONG - Test language
- [ ] Test that users can log in with valid credentials
- [ ] Verify functionality of the search feature
- [ ] Validate behavior when session expires
- [ ] Check performance of database queries

# RIGHT - Requirement questions
- [ ] Are login requirements defined for valid credentials? [Completeness]
- [ ] Are search feature requirements fully specified? [Completeness]
- [ ] Are session expiration requirements documented? [Coverage]
- [ ] Are database query performance requirements quantified? [Measurability, NFR]
```

---

## Technology-Specific Language (AVOID)

Avoid referencing specific technologies unless the spec explicitly uses them:

| Avoid | Use Instead |
|-------|-------------|
| "React component renders..." | "UI component requirements defined..." |
| "PostgreSQL query returns..." | "Database query requirements documented..." |
| "JWT token contains..." | "Authentication token requirements specified..." |
| "REST API endpoint..." | "API endpoint requirements..." |

---

## Quick Detection Checklist

Scan your checklist for these red flags:

| Red Flag | Category |
|----------|----------|
| Starts with "Verify", "Test", "Confirm", "Check", "Validate", "Ensure" | Implementation verb |
| Contains "displays", "works", "renders", "responds", "functions" | Implementation reference |
| Contains "correctly", "properly", "successfully", "as expected" | Subjective outcome |
| References specific technology names | Technology-specific |
| Describes user actions ("when user clicks...") | Implementation scenario |
| Describes system behavior ("system should...") | Implementation behavior |

---

## Self-Correction Process

When you find an anti-pattern, transform it:

1. **Identify the underlying requirement** - What requirement quality are you actually checking?
2. **Reframe as a question** - "Are [requirements] defined for [scenario]?"
3. **Add quality dimension** - Which dimension does this check?
4. **Add reference** - Link to spec section or mark as Gap

### Transformation Examples

```markdown
# Original (WRONG)
Verify the login form displays error messages when credentials are invalid

# Step 1: Underlying requirement
Error message display for invalid credentials

# Step 2: Reframe as question
Are error message requirements defined for invalid login credentials?

# Step 3: Add dimension
[Completeness] - checking if requirements exist

# Step 4: Add reference
[Gap] - this is likely missing from spec

# Result (RIGHT)
- [ ] CHK015 - Are error message requirements defined for invalid login credentials? [Completeness, Gap]
```
