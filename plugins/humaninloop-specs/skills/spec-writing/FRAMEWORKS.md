# Decision Frameworks

Three frameworks for consistent judgment calls when writing specifications.

---

## Priority Assessment Framework (P1/P2/P3)

Use these signals to extract priority from feature descriptions:

| Priority | Signals | Examples |
|----------|---------|----------|
| **P1** | Blocks other features, MVP-critical, user cannot proceed without, explicitly requested as "must have" | "Users need to log in before..." (blocking), "Core feature for launch" |
| **P2** | Important for completeness, workaround exists, can ship without initially, "should have" language | "Would be nice to also show...", "Users expect to be able to..." |
| **P3** | Enhances experience, user-requested but not essential, "could have", future consideration | "Eventually we want...", "Nice to have...", "For power users..." |

### Extraction from Vague Descriptions

| Description | Extracted Priority | Reasoning |
|-------------|-------------------|-----------|
| "Add user authentication" | P1 | Blocking—nothing works without auth |
| "Let users customize their dashboard" | P2 | Important UX but app functions without |
| "Add keyboard shortcuts for power users" | P3 | Enhancement, not core functionality |

---

## Clarification Threshold Framework

Apply this decision tree when encountering ambiguity:

```
1. Does ambiguity significantly affect SCOPE?
   └─ YES → [NEEDS CLARIFICATION] with priority: scope
   └─ NO → Continue to step 2

2. Are there SECURITY or COMPLIANCE implications?
   └─ YES → [NEEDS CLARIFICATION] with priority: security
   └─ NO → Continue to step 3

3. Does an INDUSTRY STANDARD provide a sensible default?
   └─ YES → Make assumption, document it
   └─ NO → Continue to step 4

4. Is the choice EASILY REVERSIBLE?
   └─ YES → Make assumption, document it
   └─ NO → Continue to step 5

5. Do MULTIPLE EQUALLY VALID interpretations exist?
   └─ YES → [NEEDS CLARIFICATION] with priority: ux or technical
   └─ NO → Make assumption based on minimal user friction
```

### Good vs Bad Clarification Decisions

| Situation | Good Decision | Bad Decision |
|-----------|---------------|--------------|
| "Support social login" (which providers?) | Clarify—scope impact, not reversible | Assume all major providers—over-commits |
| "Show timestamps" (which timezone?) | Assume user's local timezone—industry standard | Clarify—has sensible default |
| "Validate email" (how strictly?) | Assume RFC 5322 basic—reversible | Clarify—technical detail, low impact |
| "Allow file uploads" (which types?) | Clarify—security implications | Assume all types—security risk |

---

## Requirement Strength Framework (MUST/SHOULD/MAY)

| Keyword | When to Use | Examples |
|---------|-------------|----------|
| **MUST** | User safety, data integrity, core functionality, legal/compliance, feature doesn't work without | "System MUST encrypt passwords", "Users MUST authenticate before accessing data" |
| **SHOULD** | Best practice, recommended UX, performance expectations, important but workaround exists | "System SHOULD display loading indicator", "Form SHOULD validate before submission" |
| **MAY** | Convenience features, optional enhancements, future extensibility, nice-to-have | "System MAY remember user preferences", "Users MAY customize notification frequency" |

### Calibration Examples

| Requirement | Strength | Why |
|-------------|----------|-----|
| "Validate email format before submission" | MUST | Core functionality—prevents bad data |
| "Show password strength indicator" | SHOULD | Best practice UX, but submission works without |
| "Allow users to change email display format" | MAY | Convenience, not essential |

---

## Framework Interconnections

These frameworks work together:

- A **P1 requirement** is more likely to use **MUST**
- Ambiguity in a **MUST** warrants **clarification** more than ambiguity in a **MAY**
- **Security-related** requirements are typically **P1** and **MUST**
