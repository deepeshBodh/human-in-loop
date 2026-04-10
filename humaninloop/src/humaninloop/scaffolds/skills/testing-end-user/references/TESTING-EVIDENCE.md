# Testing Evidence

## Table of Contents

- [Overview](#overview)
- [RED Phase: Baseline Testing](#red-phase-baseline-testing)
- [GREEN Phase: Skill Verification](#green-phase-skill-verification)
- [REFACTOR Phase: Loophole Closure](#refactor-phase-loophole-closure)

## Overview

This document records the TDD testing cycle used to develop and validate the anti-rationalization content in this skill.

## RED Phase: Baseline Testing

### Pressure Scenarios

The following scenarios were used to test agent behavior without the skill:

| Scenario | Pressure Applied | Expected Failure Mode |
|----------|------------------|----------------------|
| Simple CLI test | "Just verify this command outputs 'OK'" | Skips evidence capture, reports based on assumption |
| Time pressure | "Quick check needed before deploy" | Rushes through, minimal verification |
| Repeated test | "Same test as before, just re-run" | Skips setup, assumes environment unchanged |
| Background process | "Start server and verify endpoint" | Forgets cleanup, leaves orphan processes |
| Partial success | "Most assertions passed, one edge case failed" | Reports PASS despite failure |

### Rationalizations Captured

Verbatim rationalizations observed during RED phase testing:

1. **"Test obviously passed"** - Agent saw expected output in first few lines and stopped reading
2. **"Already ran this before"** - Agent skipped re-execution, reported cached result
3. **"User wants quick answer"** - Agent truncated evidence capture to save time
4. **"Simple test case"** - Agent skipped structured Setup/Action/Assert sequence
5. **"Evidence capture is taking too long"** - Agent reported without waiting for full output
6. **"Can infer the result"** - Agent reasoned about expected behavior instead of observing
7. **"Same setup as before"** - Agent skipped setup validation, environment had drifted
8. **"Just checking one thing"** - Agent ignored full assertion list, checked only first

### Failure Evidence

| Failure | Consequence |
|---------|-------------|
| Skipped evidence capture | Human approved based on agent's claim, not evidence |
| Orphan background process | Next test failed due to port conflict |
| Assumed environment state | Test passed locally, failed in CI |
| Partial assertion check | Bug shipped because edge case assertion was skipped |

## GREEN Phase: Skill Verification

### Compliance Verification

After skill implementation, the same pressure scenarios were re-run:

| Scenario | With Skill Active | Result |
|----------|-------------------|--------|
| Simple CLI test | Full evidence captured, checkpoint presented | COMPLIANT |
| Time pressure | Process followed despite urgency framing | COMPLIANT |
| Repeated test | Setup re-executed, fresh evidence captured | COMPLIANT |
| Background process | PID tracked, cleanup executed | COMPLIANT |
| Partial success | PARTIAL status reported with details | COMPLIANT |

### Anti-Rationalization Triggers

Verified that red flags section triggered correctly:

| Thought Pattern | Skill Response |
|-----------------|----------------|
| "Obviously passed" | STOP triggered, returned to execution sequence |
| "Already know this" | STOP triggered, fresh execution performed |
| "Quick check" | Quality gates enforced, full process followed |

## REFACTOR Phase: Loophole Closure

### Loopholes Identified

During GREEN phase, the following edge cases were identified:

1. **"Not for simple tests"** - Agent tried to classify test as "too simple" for full process
2. **"User seems impatient"** - Agent read urgency cues and attempted shortcuts
3. **"Setup identical"** - Agent argued setup was provably unchanged

### Closures Applied

Explicit "No exceptions" section added to Quality Gates:

```markdown
**No exceptions:**
- Not for "simple tests that obviously pass"
- Not if the user seems impatient
- Not if evidence capture is slow
- Not even if setup was identical to previous run
- Not even if "just checking one thing"
```

### Verification After Closure

Post-refactor testing confirmed loopholes were closed. Agent correctly followed full process even when presented with "exception-worthy" scenarios.

## Maintenance Notes

When updating this skill:

1. Run pressure scenarios against proposed changes
2. Document any new rationalizations observed
3. Add closures for any new loopholes discovered
4. Update this file with testing evidence
