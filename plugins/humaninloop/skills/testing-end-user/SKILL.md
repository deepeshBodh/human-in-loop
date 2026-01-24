---
name: testing-end-user
description: Executes end-user verification tests against real infrastructure. Parses TEST:VERIFY tasks, runs Setup/Action/Assert steps, captures evidence, and generates reports for human review.
---

# End-User Verification Testing

## Purpose

Execute verification tasks that validate real infrastructure behavior, capture evidence, and present checkpoints for human approval. This skill transforms tasks marked with `**TEST:VERIFY**` into executable verification sequences.

## When to Use

- Executing tasks with `**TEST:VERIFY**` markers
- Running CLI commands and verifying output
- Checking file system state changes
- Validating real process behavior (not mocks)

## Task Format

```markdown
- [ ] **TN.X**: **TEST:VERIFY** - {Description}
  - **Setup**: {Prerequisites} (optional)
  - **Action**: {Command} (can have multiple)
  - **Assert**: {Expected outcome} (can have multiple)
  - **Capture**: {console, screenshot, logs} (optional)
  - **Human-Review**: {What human should evaluate} (optional)
```

See [TASK-PARSING.md](TASK-PARSING.md) for detailed field marker rules.

## Execution Flow

### 1. Parse Task

Extract structured data from task description:

```
Task ID: T{N}.{X}
Type: TEST:VERIFY | TEST:CONTRACT
Setup: [list of setup commands]
Actions: [list of actions with modifiers]
Asserts: [list of conditions to verify]
Capture: [evidence types to collect]
Human-Review: [what human should check]
```

### 2. Execute Setup

- Run setup commands sequentially
- Fail fast if any setup fails
- Record setup output for debugging

### 3. Execute Actions

- Run each action respecting modifiers
- Capture all console output
- Track background processes
- Enforce timeouts

Action modifiers:
| Modifier | Example | Behavior |
|----------|---------|----------|
| `(background)` | `npm start (background)` | Run async, track PID |
| `(timeout Ns)` | `curl ... (timeout 10s)` | Override 60s default |
| `(in {path})` | `make build (in ./backend)` | Change directory |

### 4. Evaluate Asserts

Check each assert against captured evidence:

| Pattern | Verification |
|---------|--------------|
| `Console contains "{text}"` | Substring match |
| `Console contains "{text}" (within Ns)` | Timed match |
| `File exists: {path}` | `test -f {path}` |
| `Response status: {code}` | HTTP status check |

See [EVIDENCE-CAPTURE.md](EVIDENCE-CAPTURE.md) for capture details.

### 5. Generate Report

- **All PASS**: Minimal report (just status + duration)
- **Any FAIL**: Rich report with evidence table

See [REPORT-TEMPLATES.md](REPORT-TEMPLATES.md) for templates.

### 6. Present Checkpoint

Ask human to approve, reject, or retry. The human decision gates cycle completion.

## Evidence Types

| Type | Capture Method |
|------|----------------|
| `console` | stdout/stderr from commands |
| `screenshot` | Platform-specific screen capture |
| `logs` | Contents of specified log files |
| `timing` | Duration of each action |

## Result Classification

| Status | Meaning |
|--------|---------|
| `PASS` | All asserts passed |
| `FAIL` | One or more asserts failed |
| `PARTIAL` | Mixed results, needs judgment |
| `TIMEOUT` | Action exceeded time limit |
| `ERROR` | Execution error (not assertion) |

## Quality Gates

Before presenting checkpoint:

- [ ] All setup commands completed
- [ ] All actions executed (or timed out)
- [ ] All asserts evaluated
- [ ] Evidence captured per Capture field
- [ ] Report generated

## Related Files

- [TASK-PARSING.md](TASK-PARSING.md) - Field marker extraction rules
- [EVIDENCE-CAPTURE.md](EVIDENCE-CAPTURE.md) - Console capture, background processes
- [REPORT-TEMPLATES.md](REPORT-TEMPLATES.md) - Minimal and rich report formats
