# Task Parsing Rules

## Table of Contents

- [Overview](#overview)
- [Task Detection](#task-detection)
- [Field Markers](#field-markers)
- [Parsing Algorithm](#parsing-algorithm)
- [Action Modifier Parsing](#action-modifier-parsing)
- [Assert Pattern Parsing](#assert-pattern-parsing)
- [Parsed Task Structure](#parsed-task-structure)
- [Error Handling](#error-handling)
- [Legacy Format Support](#legacy-format-support)

## Overview

This document defines how to extract structured data from verification task markers in tasks.md. The unified `**TEST:**` format is preferred, with legacy formats supported for backward compatibility.

## Task Detection

### Unified Format (Preferred)

```regex
\*\*TEST:\*\* - (.+)
```

### Legacy Formats (Supported)

```regex
\*\*TEST:VERIFY\*\* - (.+)
\*\*TEST:CONTRACT\*\* - (.+)
\*\*HUMAN VERIFICATION\*\* - (.+)
```

All formats are internally normalized to the unified structure.

### Context Lines

Task descriptions may span multiple lines with sub-bullets:

```markdown
- [ ] **T2.4**: **TEST:VERIFY** - File watcher detects changes
  - **Setup**: `mkdir /tmp/watcher-test`
  - **Action**: `dart run bin/watcher.dart /tmp/watcher-test` (background)
  - **Action**: `touch /tmp/watcher-test/test.jsonl`
  - **Assert**: Console contains "FileWatchEvent: created"
  - **Human-Review**: Events appear within 1 second
```

## Field Markers

### Required Fields

| Field | Pattern | Description |
|-------|---------|-------------|
| `**Action**:` | `\*\*Action\*\*:\s*(.+)` | Command to execute |
| `**Assert**:` | `\*\*Assert\*\*:\s*(.+)` | Condition to verify |

### Optional Fields

| Field | Pattern | Description |
|-------|---------|-------------|
| `**Setup**:` | `\*\*Setup\*\*:\s*(.+)` | Prerequisites |
| `**Capture**:` | `\*\*Capture\*\*:\s*(.+)` | Evidence types |
| `**Human-Review**:` | `\*\*Human-Review\*\*:\s*(.+)` | Human focus |

## Parsing Algorithm

### 1. Identify Task Boundaries

```
START: Line matching `- [ ] **T{N}.{X}**: **TEST:`
END: Next task line OR end of cycle
```

### 2. Extract Task ID

```regex
\*\*T(\d+)\.(\d+)\*\*:
```
Result: Cycle number and task number

### 3. Extract Test Type

```regex
\*\*TEST:(VERIFY|CONTRACT)?\*\*
```
Result: `VERIFY`, `CONTRACT`, or empty (unified format)

For unified `**TEST:**` format, type defaults to `UNIFIED`.

### 4. Extract Description

Text after ` - ` on the marker line:
```regex
\*\*TEST:\w+\*\* - (.+)
```

### 5. Extract Field Values

For each sub-bullet line:

```regex
^\s+- \*\*(\w+(?:-\w+)?)\*\*:\s*(.+)
```

Group 1: Field name (Setup, Action, Assert, Capture, Human-Review)
Group 2: Field value

### 6. Handle Multiple Same-Field Lines

Fields like Action and Assert can appear multiple times:

```markdown
- **Action**: `npm start` (background)
- **Action**: `curl localhost:3000`
- **Assert**: Response status: 200
- **Assert**: Console contains "Server started"
```

Result:
```json
{
  "actions": [
    {"command": "npm start", "modifiers": ["background"]},
    {"command": "curl localhost:3000", "modifiers": []}
  ],
  "asserts": [
    {"type": "response_status", "expected": "200"},
    {"type": "console_contains", "pattern": "Server started"}
  ]
}
```

## Action Modifier Parsing

### Background

```regex
(.+)\s*\(background\)
```
Command: Group 1
Modifier: `background`

### Timeout

```regex
(.+)\s*\(timeout\s+(\d+)s?\)
```
Command: Group 1
Timeout: Group 2 (seconds)

### Directory

```regex
(.+)\s*\(in\s+([^\)]+)\)
```
Command: Group 1
Directory: Group 2

### Combined Modifiers

```markdown
**Action**: `npm test` (timeout 120s) (in ./backend)
```
Parse each modifier independently.

## Assert Pattern Parsing

### Console Contains

```regex
Console contains "([^"]+)"(?:\s*\(within\s+(\d+)s?\))?
```
Pattern: Group 1
Timeout: Group 2 (optional, seconds)

### File Exists

```regex
File exists:\s*`?([^`\s]+)`?
```
Path: Group 1

### Response Status

```regex
Response status:\s*(\d+)
```
Status: Group 1

### Custom Assertion

Any other text becomes a custom assertion for human evaluation:
```markdown
**Assert**: Application shows welcome screen
```

## Parsed Task Structure

```json
{
  "id": "T2.4",
  "cycle": 2,
  "task": 4,
  "type": "VERIFY",
  "description": "File watcher detects changes",
  "setup": [
    {"command": "mkdir /tmp/watcher-test"}
  ],
  "actions": [
    {
      "command": "dart run bin/watcher.dart /tmp/watcher-test",
      "modifiers": {"background": true}
    },
    {
      "command": "touch /tmp/watcher-test/test.jsonl",
      "modifiers": {}
    }
  ],
  "asserts": [
    {
      "type": "console_contains",
      "pattern": "FileWatchEvent: created",
      "timeout": null
    }
  ],
  "capture": ["console"],
  "human_review": "Events appear within 1 second"
}
```

## Error Handling

### Missing Required Fields

If `**Action**:` or `**Assert**:` missing:
- Report parsing error
- Do not attempt execution
- Ask human how to proceed

### Malformed Patterns

If modifiers or patterns do not match expected format:
- Log warning
- Use literal text as fallback
- Include in report for human review

### Nested Quotes

Handle escaped quotes in patterns:
```markdown
**Assert**: Console contains "User said \"Hello\""
```
Parse with quote escaping awareness.

## Legacy Format Support

### HUMAN VERIFICATION Mapping

When parsing `**HUMAN VERIFICATION**` tasks, map fields to unified format:

| Legacy Field | Unified Field |
|--------------|---------------|
| `Setup:` | `**Setup**:` |
| `Action:` | `**Action**:` |
| `Verify:` | `**Assert**:` |
| `**Human confirms**:` | (ignored - testing-agent handles) |

### Example Legacy Task

```markdown
- [ ] **T2.12**: **HUMAN VERIFICATION** - File watcher detects changes
  - Setup: `mkdir /tmp/test`
  - Action: Run `dart run bin/watcher.dart /tmp/test`
  - Verify: Console outputs "FileWatchEvent: created"
  - **Human confirms**: Events appear in real time ✓
```

Normalized to:

```json
{
  "id": "T2.12",
  "type": "UNIFIED",
  "description": "File watcher detects changes",
  "setup": [{"command": "mkdir /tmp/test"}],
  "actions": [{"command": "dart run bin/watcher.dart /tmp/test", "modifiers": {}}],
  "asserts": [{"type": "console_contains", "pattern": "FileWatchEvent: created"}],
  "capture": ["console"]
}
```

### Format Detection Priority

1. Check for `**TEST:**` (unified) → use as-is
2. Check for `**TEST:VERIFY**` or `**TEST:CONTRACT**` → treat as unified
3. Check for `**HUMAN VERIFICATION**` → map fields to unified format
4. No marker found → reject task
