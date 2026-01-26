---
name: validation-constitution
description: >
  This skill MUST be invoked when the user says "review constitution", "validate principles",
  "check quality", "constitution review", "quality check", "version bump", "anti-patterns",
  or "constitution audit". Use after drafting a constitution and before presenting for approval.
---

# Validating Constitution

## Overview

Constitution validation ensures governance documents are enforceable, testable, and free of anti-patterns before finalization. Every constitution MUST pass quality validation—no exceptions for "simple projects" or "tight deadlines."

**Violating the letter of the rules is violating the spirit of the rules.**

Skipping validation because "the constitution looks fine" or "it's mostly complete" is not following the spirit of quality assurance—it is abandoning it.

## When to Use

- After drafting a constitution with humaninloop:authoring-constitution or humaninloop:brownfield-constitution
- Before presenting a constitution to users for approval
- When updating an existing constitution (any change requires re-validation)
- When user explicitly requests constitution review or quality check
- When determining appropriate version bump for constitution changes
- When auditing existing constitution for anti-patterns

## When NOT to Use

- During initial constitution drafting (validate AFTER drafting, not during)
- For documents that are not constitutions (specs, plans, code)
- When user only wants to READ a constitution without validation
- For informal project notes or temporary governance sketches

## Core Process

### Step 1: Load Quality Checklist

Read [references/QUALITY-CHECKLIST.md](references/QUALITY-CHECKLIST.md) and verify every item. Do not skip items because they "seem obvious" or "clearly pass."

### Step 2: Check Each Principle

Every principle MUST have the three-part structure:

| Part | Purpose | Verification |
|------|---------|--------------|
| **Enforcement** | How is compliance verified? | CI check, code review rule, or audit process named |
| **Testability** | What does pass/fail look like? | Concrete pass and fail conditions defined |
| **Rationale** | Why does this rule exist? | Business or technical justification present |

If any principle lacks any part, the constitution FAILS validation.

### Step 3: Scan for Anti-Patterns

Compare against [references/ANTI-PATTERNS.md](references/ANTI-PATTERNS.md). Common failures:

| Anti-Pattern | Detection |
|--------------|-----------|
| Vague principle | Contains words like "appropriate", "reasonable", "clean" without metrics |
| Missing enforcement | Principle states rule but no verification mechanism |
| Placeholder syndrome | Contains `[PLACEHOLDER]`, `[COMMAND]`, `[THRESHOLD]` syntax |
| Generic thresholds | Says "coverage must be measured" instead of "coverage ≥80%" |

### Step 4: Verify No Placeholders

This is the most commonly rationalized check. Search the entire document for:

- `[PLACEHOLDER]`
- `[COMMAND]`
- `[THRESHOLD]`
- `[TOOL]`
- Any `[BRACKETED_TEXT]` pattern

**No exceptions.** A constitution with placeholders is not ready for validation sign-off.

### Step 5: Determine Version Bump

| Bump | Trigger | Example |
|------|---------|---------|
| **MAJOR** | Principle removed or incompatibly redefined | Removing "Test-First" principle; changing coverage from 80% to 50% |
| **MINOR** | New principle added or significant expansion | Adding "Observability" principle; adding 5+ rules to existing principle |
| **PATCH** | Clarification or non-semantic change | Rewording for clarity; typo fixes; formatting |

### Step 6: Document Validation Result

Produce explicit validation verdict:

```
VALIDATION RESULT: [PASS/FAIL]

Checklist items: [X/Y passed]
Anti-patterns found: [list or "none"]
Version bump: [MAJOR/MINOR/PATCH] (if changes made)

Issues requiring fix:
- [list each failure]
```

## Quantification Requirements

Vague language MUST be replaced with measurable criteria:

| Vague | Quantified |
|-------|------------|
| "Code should be clean" | "Zero lint warnings from configured rules" |
| "Functions should be short" | "Functions MUST NOT exceed 40 lines" |
| "Tests should cover the code" | "Coverage MUST be ≥80% for new code" |
| "Response should be fast" | "API MUST respond in <200ms p95" |
| "Secure by default" | "All inputs MUST be validated; auth required on all endpoints" |

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|----------------|-----|
| Skipping checklist items | "Obviously passes" | Run every item. Obvious failures happen. |
| Accepting placeholders | "User will fill in later" | Placeholders = incomplete. Return for completion. |
| Validating during drafting | Interrupts creative flow | Draft first, validate second. Separate phases. |
| Soft validation language | "Mostly looks good" | Binary verdict: PASS or FAIL. No middle ground. |
| Missing version bump | "Small change" | Every change needs version bump determination. |
| Validating non-constitutions | Skill triggered by similar keywords | Verify document IS a constitution before validating. |

## Red Flags - STOP and Restart Properly

If you notice yourself thinking any of these, STOP immediately:

- "The constitution looks complete enough"
- "This is just a minor update, doesn't need full validation"
- "I already reviewed it while writing"
- "User seems happy with it"
- "The checklist is too detailed for this simple project"
- "These anti-patterns don't apply to this case"
- "I can skip the placeholder check—I didn't use any"
- "Validation would be redundant since I wrote it carefully"

**All of these mean:** You are rationalizing. Restart validation from Step 1.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Constitution looks complete" | Looking complete ≠ being complete. Run the checklist. |
| "Just a minor update" | Minor updates can introduce major anti-patterns. Full validation. |
| "Already reviewed while writing" | Authoring mode ≠ validation mode. Fresh review catches blind spots. |
| "User seems satisfied" | User satisfaction doesn't verify enforcement mechanisms exist. |
| "Too detailed for simple project" | Simple projects become complex. Governance debt compounds. |
| "Anti-patterns don't apply here" | Every rationalization claims uniqueness. They apply. |
| "I'm being pragmatic" | Pragmatic = following validation process. Skipping is not pragmatic. |
| "Can validate more thoroughly later" | "Later" rarely comes. Validate now or ship broken governance. |

## Explicit Loophole Closures

### "The constitution looks fine"

Looking fine is not validation. Run every checklist item. Document every result. A constitution is validated when all checks pass, not when it "looks fine."

### "This is a small change"

Small changes require validation. A one-line change can introduce vague language, remove enforcement, or add placeholders. Size does not determine validation necessity.

### "I'll add the missing parts later"

Constitutions with missing parts FAIL validation. Return to authoring. Do not sign off on incomplete governance.

### "User asked to skip validation"

User requests do not override process. Explain why validation matters. If user insists, document that validation was skipped against recommendation—but never claim a validated constitution when validation was skipped.

### "The project is just prototyping"

Prototypes become production. Governance established during prototyping persists. Validate now or inherit broken governance later.

## Testing Evidence

### Baseline Testing Results (RED Phase)

Pressure scenarios tested without skill loaded revealed these agent behaviors:

**Scenario 1: Time pressure + "looks complete"**
- Agent rationalized: "The constitution appears comprehensive and I wrote it carefully"
- Skipped checklist, missed placeholder in Quality Gates section
- Verdict: FAIL - proceeded without systematic validation

**Scenario 2: User satisfaction signal**
- Agent rationalized: "User already reviewed the draft and seemed satisfied"
- Skipped anti-pattern scan, missed vague "appropriate level" language
- Verdict: FAIL - treated user satisfaction as validation

**Scenario 3: Minor update context**
- Agent rationalized: "This is just updating one threshold, full validation is overkill"
- Skipped Steps 1-3, only checked the changed line
- Verdict: FAIL - partial validation is not validation

### Skill Effectiveness (GREEN Phase)

Same scenarios re-run with skill loaded:
- Agent cited "letter = spirit" principle when tempted to skip
- Agent ran full checklist despite time pressure
- Agent produced binary PASS/FAIL verdicts
- All placeholders and anti-patterns caught

## Related Skills

- **OPTIONAL:** humaninloop:authoring-constitution - Core authoring for greenfield projects
- **OPTIONAL:** humaninloop:brownfield-constitution - Authoring for existing codebases
