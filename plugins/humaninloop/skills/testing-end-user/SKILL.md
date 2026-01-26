---
name: testing-end-user
description: >
  This skill MUST be invoked when the user says "run test task", "execute test",
  "run the test", "run tests", "test this", "execute verification", "run verification",
  "verify this", or when tasks contain "TEST:", "TEST:VERIFY", "TEST:CONTRACT", or
  Setup/Action/Assert markers. Use for verification testing against real infrastructure.
---

# End-User Verification Testing

## Overview

Execute verification tasks that validate real infrastructure behavior through structured Setup/Action/Assert sequences. Classify tasks at runtime (CLI/GUI/SUBJECTIVE) to determine whether to auto-approve or present human checkpoints. This skill transforms tasks marked with `**TEST:**` into executable verification sequences with captured evidence.

**Violating the letter of the rules is violating the spirit of the rules.**

Verification testing exists to catch failures before they reach production. Every shortcut in this process is a potential production incident waiting to happen.

## When to Use

- Tasks marked with `**TEST:**`, `**TEST:VERIFY**`, or `**TEST:CONTRACT**`
- Legacy `**HUMAN VERIFICATION**` tasks (mapped to unified format)
- CLI command verification with expected output
- File system state validation
- Real process behavior testing (not mocks)
- GUI/UI verification requiring human judgment
- End-to-end validation before deployment

## When NOT to Use

- Unit tests that run in isolation
- Mock-based testing without infrastructure
- Static code analysis tasks
- Documentation review tasks
- Tasks without clear pass/fail criteria
- When verification environment is unavailable

## Core Process

### Task Detection

Identify tasks containing verification markers:

```markdown
- [ ] **TN.X**: **TEST:** - {Description}
  - **Setup**: {Prerequisites} (optional)
  - **Action**: {Command or instruction}
  - **Assert**: {Expected outcome}
  - **Capture**: {console, screenshot, logs} (optional)
```

**Supported markers** (all normalized to unified format):
- `**TEST:**` - Unified format (preferred)
- `**TEST:VERIFY**` - Legacy format
- `**TEST:CONTRACT**` - Legacy format
- `**HUMAN VERIFICATION**` - Legacy format (maps Setup/Action/Verify fields)

See [references/TASK-PARSING.md](references/TASK-PARSING.md) for field marker extraction rules.

### Execution Sequence

Execute in strict order. No skipping steps. No reordering.

**1. Parse Task**

Extract structured data:
- Task ID (T{N}.{X})
- Test type (VERIFY or CONTRACT)
- Setup commands
- Actions with modifiers
- Assert conditions
- Capture requirements
- Human review criteria

**2. Execute Setup**

Run setup commands sequentially. Fail fast if any setup fails. Record all output for debugging. Setup failures block action execution.

**3. Execute Actions**

Run each action respecting modifiers:

| Modifier | Example | Behavior |
|----------|---------|----------|
| `(background)` | `npm start (background)` | Run async, track PID |
| `(timeout Ns)` | `curl ... (timeout 10s)` | Override 60s default |
| `(in {path})` | `make build (in ./backend)` | Change directory |

Capture all console output. Track background processes. Enforce timeouts. See [references/EVIDENCE-CAPTURE.md](references/EVIDENCE-CAPTURE.md) for capture details.

**4. Evaluate Asserts**

Check each assert against captured evidence:

| Pattern | Verification |
|---------|--------------|
| `Console contains "{text}"` | Substring match |
| `Console contains "{text}" (within Ns)` | Timed match |
| `File exists: {path}` | `test -f {path}` |
| `Response status: {code}` | HTTP status check |

**5. Generate Report**

- **All PASS**: Minimal report (status + duration)
- **Any FAIL**: Rich report with evidence table

See [references/REPORT-TEMPLATES.md](references/REPORT-TEMPLATES.md) for templates.

**6. Present Checkpoint**

Ask human to approve, reject, or retry. Human decision gates cycle completion. No proceeding without explicit human approval.

### Task Classification

Before execution, classify the task based on Action and Assert content:

| Classification | Criteria | Checkpoint Behavior |
|----------------|----------|---------------------|
| **CLI** | Backtick commands + measurable asserts | May auto-approve if 100% pass |
| **GUI** | UI actions (`click`, `tap`) or screenshot capture | Always human checkpoint |
| **SUBJECTIVE** | Qualitative terms (`looks`, `feels`, `appears`) | Always human checkpoint |

Default to SUBJECTIVE if uncertain (safe fallback).

### Result Classification

| Status | Meaning |
|--------|---------|
| `PASS` | All asserts passed |
| `FAIL` | One or more asserts failed |
| `PARTIAL` | Mixed results, needs judgment |
| `TIMEOUT` | Action exceeded time limit |
| `ERROR` | Execution error (not assertion) |

### Evidence Types

| Type | Capture Method |
|------|----------------|
| `console` | stdout/stderr from commands |
| `screenshot` | Platform-specific screen capture |
| `logs` | Contents of specified log files |
| `timing` | Duration of each action |

## Quality Gates

Before presenting checkpoint, verify completion of ALL items:

- [ ] All setup commands completed
- [ ] All actions executed (or timed out)
- [ ] All asserts evaluated
- [ ] Evidence captured per Capture field
- [ ] Report generated with proper detail level

No presenting partial results. No skipping evidence capture. No proceeding without human approval.

**No exceptions:**
- Not for "simple tests that obviously pass"
- Not if the user seems impatient
- Not if evidence capture is slow
- Not even if setup was identical to previous run
- Not even if "just checking one thing"

## Red Flags - STOP and Restart Properly

If any of these thoughts arise, STOP immediately:

- "The test obviously passed, no need for full evidence capture"
- "I already know this works from previous runs"
- "Just a quick verification, minimal report is fine"
- "The user seems impatient, skip to the result"
- "This is a simple test, full process is overkill"
- "Evidence capture is taking too long"
- "I can infer the result without running the test"
- "The setup is the same as last time"

**All of these mean:** Rationalization in progress. Return to the execution sequence. Follow every step.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Test obviously passed" | Obvious passes hide subtle failures. Capture evidence anyway. |
| "Already ran this before" | Previous runs are stale. Each execution is independent. Run again. |
| "User wants quick answer" | Quick answers without evidence are unreliable. Process protects user. |
| "Simple test case" | Simple tests catch complex bugs. Full process regardless of simplicity. |
| "Evidence capture is slow" | Slow capture beats fast wrong answer. Time investment protects quality. |
| "Can infer the result" | Inference is not verification. Execute and observe. |
| "Same setup as before" | Environments change. Run setup fresh. Validate assumptions. |
| "Just checking one thing" | One thing has dependencies. Full sequence catches hidden failures. |

## Common Mistakes

### Mistake: Skipping Setup Validation

**What goes wrong:** Action fails mysteriously because setup was assumed complete.

**Fix:** Always run setup commands. Always capture setup output. Fail explicitly if setup fails.

### Mistake: Missing Background Process Cleanup

**What goes wrong:** Background processes from previous tests interfere with current test.

**Fix:** Track all PIDs. Kill processes after test (pass or fail). Verify cleanup completed.

### Mistake: Truncating Evidence Prematurely

**What goes wrong:** Critical failure information cut off from report.

**Fix:** Follow truncation rules in REPORT-TEMPLATES.md. Always include log file locations. Preserve full evidence for human review.

### Mistake: Reporting PASS Without Assert Verification

**What goes wrong:** Claiming PASS when asserts were not actually evaluated.

**Fix:** Each assert MUST have an explicit pass/fail evaluation. No default to PASS. Unevaluated asserts are failures.

### Mistake: Proceeding After Rejected Checkpoint

**What goes wrong:** Continuing execution when human explicitly rejected.

**Fix:** Rejection gates completion. Human approval is mandatory. Retry or abort on rejection.

### Mistake: Skipping Checkpoint Presentation

**What goes wrong:** Test runs but human never sees results. No audit trail. No approval gate.

**Fix:** Every test MUST end with checkpoint presentation. No silent completion. Human-in-loop is the point.

## Reference Files

- [references/TASK-PARSING.md](references/TASK-PARSING.md) - Field marker extraction rules and parsing algorithm
- [references/EVIDENCE-CAPTURE.md](references/EVIDENCE-CAPTURE.md) - Console capture, background processes, timeout handling
- [references/REPORT-TEMPLATES.md](references/REPORT-TEMPLATES.md) - Minimal and rich report formats, checkpoint presentation
- [references/TESTING-EVIDENCE.md](references/TESTING-EVIDENCE.md) - RED/GREEN/REFACTOR testing cycle documentation
