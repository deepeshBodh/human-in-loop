# Report Templates

## Table of Contents

- [Overview](#overview)
- [Success Report (Minimal)](#success-report-minimal)
- [Failure Report (Rich)](#failure-report-rich)
- [Partial Success Report](#partial-success-report)
- [Timeout Report](#timeout-report)
- [Error Report](#error-report)
- [Checkpoint Presentation](#checkpoint-presentation)
- [Report Truncation](#report-truncation)
- [Report Storage](#report-storage)

## Overview

This document defines report formats for different verification outcomes. Reports are adaptive: minimal for success, rich for failures.

## Success Report (Minimal)

When all assertions pass, use minimal format:

```markdown
## Verification: T{N}.{X} - PASS

**Description**: {task description}
**Result**: All {count} assertions passed
**Duration**: {time}s

**Recommendation**: Approve
```

### Example

```markdown
## Verification: T2.4 - PASS

**Description**: File watcher detects changes
**Result**: All 2 assertions passed
**Duration**: 3.2s

**Recommendation**: Approve
```

## Failure Report (Rich)

When any assertion fails, use rich format:

```markdown
## Verification: T{N}.{X} - NEEDS REVIEW

**Description**: {task description}
**Duration**: {time}s

### Assertion Results

| # | Assert | Expected | Actual | Status |
|---|--------|----------|--------|--------|
| 1 | {assert description} | {expected value} | {actual value} | PASS/FAIL |
| 2 | {assert description} | {expected value} | {actual value} | PASS/FAIL |

### Console Output

```
{relevant console output, truncated if > 50 lines}
```

### Actions Executed

| # | Command | Duration | Exit Code |
|---|---------|----------|-----------|
| 1 | `{command}` | {time}s | {code} |
| 2 | `{command}` | {time}s | {code} |

### Analysis

{Brief analysis of what might have gone wrong}

### Recommendation

{Approve | Reject | Retry with adjustments}

**Reasoning**: {Why this recommendation}
```

### Example

```markdown
## Verification: T2.4 - NEEDS REVIEW

**Description**: File watcher detects changes
**Duration**: 5.1s

### Assertion Results

| # | Assert | Expected | Actual | Status |
|---|--------|----------|--------|--------|
| 1 | Console contains "FileWatchEvent: created" | Match found | No match | FAIL |
| 2 | File exists: /tmp/watcher-test/test.jsonl | Exists | Exists | PASS |

### Console Output

```
Starting file watcher...
Watching directory: /tmp/watcher-test
Error: Permission denied for inotify
```

### Actions Executed

| # | Command | Duration | Exit Code |
|---|---------|----------|-----------|
| 1 | `dart run bin/watcher.dart /tmp/watcher-test` (bg) | N/A | N/A |
| 2 | `touch /tmp/watcher-test/test.jsonl` | 0.1s | 0 |

### Analysis

The file watcher failed to start due to inotify permissions. The touch command succeeded, but no event was detected.

### Recommendation

Reject

**Reasoning**: File watcher infrastructure needs configuration (inotify limits).
```

## Partial Success Report

When some assertions pass and some fail:

```markdown
## Verification: T{N}.{X} - PARTIAL ({pass}/{total})

**Description**: {task description}
**Duration**: {time}s
**Pass Rate**: {percentage}%

### Assertion Results

| # | Assert | Status |
|---|--------|--------|
| 1 | {assert description} | PASS |
| 2 | {assert description} | FAIL |
| 3 | {assert description} | PASS |

### Failed Assertion Details

**Assert #2**: {full assert description}
- **Expected**: {expected}
- **Actual**: {actual}
- **Context**: {relevant output}

### Recommendation

Needs Human Judgment

**Options**:
1. **Approve**: If failed assertion is non-critical
2. **Reject**: If failed assertion blocks functionality
3. **Retry**: If failure might be transient
```

## Timeout Report

When action exceeds time limit:

```markdown
## Verification: T{N}.{X} - TIMEOUT

**Description**: {task description}
**Duration**: {elapsed}s (limit: {limit}s)

### Timeout Details

**Command**: `{command}`
**Elapsed**: {elapsed}s
**Limit**: {limit}s

### Partial Output

```
{any output captured before timeout}
```

### Recommendation

Retry with adjustments

**Suggestions**:
1. Increase timeout with `(timeout Ns)` modifier
2. Check if command has startup delay
3. Verify system resources available
```

## Error Report

When execution fails (not assertion failure):

```markdown
## Verification: T{N}.{X} - ERROR

**Description**: {task description}

### Error Details

**Phase**: {setup | action | assert}
**Command**: `{command}`
**Exit Code**: {code}

### Error Output

```
{error message}
```

### Recommendation

Reject

**Reasoning**: Execution error prevents verification. Fix the underlying issue before retrying.
```

## Checkpoint Presentation

After generating report, present to human.

### All Pass

```
AskUserQuestion(
  questions: [{
    question: "Verification T{N}.{X} passed.\n\nAll {count} assertions passed in {time}s.\n\nRecommendation: Approve",
    header: "Checkpoint",
    options: [
      {label: "Approve", description: "Proceed to next task"},
      {label: "View Details", description: "Show full evidence"},
      {label: "Retry", description: "Re-run verification"}
    ],
    multiSelect: false
  }]
)
```

### Any Failure

```
AskUserQuestion(
  questions: [{
    question: "Verification T{N}.{X} needs review.\n\n{pass}/{total} assertions passed.\nFailed: {failed_assert_summary}\n\nRecommendation: {recommendation}",
    header: "Checkpoint",
    options: [
      {label: "Approve", description: "Accept despite failures"},
      {label: "Reject", description: "Block cycle completion"},
      {label: "Retry", description: "Re-run with adjustments"}
    ],
    multiSelect: false
  }]
)
```

### If Retry Selected

Prompt for adjustments:

```
AskUserQuestion(
  questions: [{
    question: "What adjustments should be made?",
    header: "Retry",
    options: [
      {label: "Increase timeout", description: "Add more time for slow operations"},
      {label: "Retry as-is", description: "Run again without changes"},
      {label: "Skip assertion", description: "Remove problematic assertion"}
    ],
    multiSelect: false
  }]
)
```

## Report Truncation

### Console Output

If output exceeds 50 lines:

```markdown
### Console Output (first 25 / last 25 lines)

```
{first 25 lines}
...
[{N} lines truncated]
...
{last 25 lines}
```

Full log: `/tmp/claude/testing-agent-T{N}.{X}-output.log`
```

### Large Tables

If more than 10 assertions:

```markdown
### Assertion Results (10/{total})

| # | Assert | Status |
|---|--------|--------|
{first 10 rows}

**Note**: {remaining} additional assertions. See full report for details.
```

## Report Storage

Reports are not persisted to disk by default. They are:

1. Generated in memory
2. Presented to human via checkpoint
3. Discarded after human decision

If human requests "View Details", regenerate with full evidence.
