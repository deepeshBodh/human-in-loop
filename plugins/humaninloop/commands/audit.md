---
description: Comprehensive artifact analysis with reviewer-friendly output mode. Consolidates checklist and analyze functionality.
---

# Audit Command

Comprehensive analysis of feature artifacts with two output modes:
- **Full mode** (default): Deep diagnostics for authors/maintainers
- **Review mode** (`--review`): Scannable summary for peer reviewers

## User Input

```text
$ARGUMENTS
```

### Parsing Arguments

Parse `$ARGUMENTS` for:
- `--review`: Enable review mode (scannable summary output)
- `--full`: Explicit full mode (default behavior)
- `--security`, `--ux`, `--api`, `--performance`: Domain filters
- Feature ID or path (optional)

If `$ARGUMENTS` is empty, proceed with full mode on auto-detected feature.

### Empty Input Check

If `$ARGUMENTS` is empty (blank string with no content), use AskUserQuestion to handle a known Claude Code bug where inputs containing `@` file references don't reach plugin commands:

```
AskUserQuestion(
  questions: [{
    question: "Known Issue: Input may have been lost\n\nClaude Code has a bug where inputs containing @ file references don't reach plugin commands.\n\nWould you like to re-enter your input?",
    header: "Input",
    options: [
      {label: "Re-enter input", description: "I'll type my input in the terminal"},
      {label: "Continue without input", description: "Proceed with auto-detected feature"}
    ],
    multiSelect: false
  }]
)
```

---

## Operating Constraints

**STRICTLY READ-ONLY**: Do **not** modify any files. Output analysis report only.

**Constitution Authority**: The project constitution (`.humaninloop/memory/constitution.md`) is **non-negotiable**. Constitution conflicts are automatically CRITICAL severity.

---

## Execution Steps

### 1. Initialize Context

Run `${CLAUDE_PLUGIN_ROOT}/scripts/check-prerequisites.sh --json` from repo root and parse JSON for:
- `FEATURE_DIR`: Active feature directory
- `AVAILABLE_DOCS`: List of available artifacts

Derive absolute paths for artifacts that exist:
- SPEC = FEATURE_DIR/spec.md (if exists)
- PLAN = FEATURE_DIR/plan.md (if exists)
- TASKS = FEATURE_DIR/tasks.md (if exists)
- RESEARCH = FEATURE_DIR/research.md (if exists)
- DATA_MODEL = FEATURE_DIR/data-model.md (if exists)
- CONTRACTS = FEATURE_DIR/contracts/ (if exists)

**No artifacts required**: Unlike analyze, this command works on whatever exists.

For single quotes in args, use escape syntax: e.g., `'I'\''m Groot'` (or double-quote: `"I'm Groot"`).

### 2. Load Constitution

Load `.humaninloop/memory/constitution.md` if it exists:
- Extract principle names and MUST/SHOULD normative statements
- These become validation criteria

If constitution doesn't exist, note this in output but continue.

### 3. Detect Artifacts and Load Context

For each artifact that exists, load relevant sections:

**From spec.md:**
- Overview/Context
- User Stories (count and IDs)
- Functional Requirements (count and IDs)
- Non-Functional Requirements
- Edge Cases
- Success Criteria

**From plan.md / research.md / data-model.md:**
- Key decisions
- Entities defined
- Technical constraints

**From tasks.md:**
- Cycle count
- Task count
- Phase groupings
- Coverage markers

**From contracts/:**
- Endpoint count
- Schema definitions

### 4. Execute Analysis Passes

Use existing skills for artifact-specific validation:

#### 4a. Specification Analysis

If spec.md exists, apply `analysis-specifications` skill criteria:
- User story completeness
- Requirement clarity (vague terms flagged)
- Success criteria measurability
- Edge case coverage

#### 4b. Plan Artifact Analysis

If plan artifacts exist, apply `validation-plan-artifacts` skill criteria:
- Research decision quality
- Data model entity coverage
- Contract endpoint coverage
- Cross-artifact consistency

#### 4c. Task Artifact Analysis

If tasks.md exists, apply `validation-task-artifacts` skill criteria:
- Story-to-cycle mapping
- TDD structure (test-first)
- Vertical slice integrity
- File path specificity

#### 4d. Cross-Artifact Analysis

Run these detection passes across all artifacts:

| Pass | Description |
|------|-------------|
| **Duplication** | Near-duplicate requirements across files |
| **Ambiguity** | Vague terms without measurable criteria (fast, scalable, secure, intuitive) |
| **Underspecification** | Requirements with verbs but missing outcomes |
| **Constitution Alignment** | Violations of MUST principles |
| **Coverage Gaps** | Requirements with no corresponding tasks |
| **Inconsistency** | Terminology drift, entity mismatches, conflicting statements |

### 5. Classify Findings

Assign severity to each finding:

| Severity | Definition |
|----------|------------|
| **CRITICAL** | Blocks progress: constitution violation, missing core artifact, zero-coverage requirement |
| **HIGH** | Significant gap: duplicate/conflicting requirement, untestable criterion |
| **MEDIUM** | Quality issue: terminology drift, missing NFR coverage, underspecified edge case |
| **LOW** | Polish: wording improvements, minor redundancy |

### 6. Generate Output

Output format depends on mode:

---

## Review Mode Output (`--review`)

Scannable summary for peer reviewers:

```markdown
# Audit Summary: {feature-id}

**Mode**: Review | **Generated**: {date}
**Artifacts**: {list with checkmarks}

---

## Coverage

| Category | Status | Count | Reference |
|----------|--------|-------|-----------|
| User Stories | {status} | {n/total} | Spec US |
| Functional Reqs | {status} | {n/total} | Spec FR |
| Non-Functional | {status} | {n/total} | Spec NFR |
| Edge Cases | {status} | {n/total} | Spec EC |
| Task Coverage | {status} | {n/total} | Tasks |

Status key: ✓ Complete | ⚠ Partial | ✗ Gaps

---

## Flagged Issues ({count})

| ID | Severity | Issue | Location |
|----|----------|-------|----------|
{top issues, max 10}

---

## Metrics

- **Coverage**: {pct}% ({covered}/{total} requirements with tasks)
- **Critical Issues**: {count}
- **Important Issues**: {count}
- **Minor Issues**: {count}

---

## Recommendation

{verdict with one-line rationale}
```

**Verdict options:**
- `Ready for review` - No critical/high issues
- `Review with caution` - Has high-severity issues to note
- `Not ready` - Has critical issues blocking progress

---

## Full Mode Output (default)

Detailed diagnostics for authors/maintainers:

```markdown
# Audit Report: {feature-id}

**Mode**: Full | **Generated**: {date}
**Artifacts Analyzed**: {list}

---

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
{all findings, max 50}

---

## Coverage Summary

| Requirement | Has Task? | Task IDs | Notes |
|-------------|-----------|----------|-------|
{coverage mapping}

---

## Constitution Alignment

{issues or "No violations detected"}

---

## Unmapped Items

**Requirements without tasks:**
{list or "None"}

**Tasks without requirements:**
{list or "None"}

---

## Metrics

- Total Requirements: {count}
- Total Tasks: {count}
- Coverage: {pct}%
- Findings by Severity:
  - Critical: {count}
  - High: {count}
  - Medium: {count}
  - Low: {count}

---

## Next Actions

{prioritized recommendations based on findings}
```

---

## Domain Filters

When domain filter is specified (`--security`, `--ux`, `--api`, `--performance`):

1. Focus analysis on domain-relevant sections
2. Prioritize domain-specific checks
3. Filter output to domain-relevant findings
4. Adjust coverage metrics to domain scope

| Filter | Focus Areas |
|--------|-------------|
| `--security` | Auth, permissions, data protection, input validation, secrets |
| `--ux` | User flows, error messages, accessibility, responsiveness |
| `--api` | Endpoints, schemas, error handling, versioning, rate limits |
| `--performance` | Latency, throughput, caching, optimization, load handling |

---

## Remediation Offer (Full Mode Only)

After full mode output, offer remediation:

```
AskUserQuestion(
  questions: [{
    question: "Would you like suggestions for resolving the top issues?",
    header: "Remediation",
    options: [
      {label: "Yes", description: "Show concrete fix suggestions"},
      {label: "No", description: "I'll handle it myself"}
    ],
    multiSelect: false
  }]
)
```

If yes, provide specific remediation suggestions for top 5 issues. Do NOT apply changes automatically.

---

## Examples

### Review Mode

```bash
/humaninloop:audit --review
```

Output: Scannable coverage summary with flagged issues for PR review.

### Full Mode with Domain Filter

```bash
/humaninloop:audit --security
```

Output: Detailed security-focused analysis with all findings.

### Review Mode with Domain Filter

```bash
/humaninloop:audit --review --ux
```

Output: UX-focused coverage summary for design review.

---

## Background

This command consolidates functionality that was previously split across two commands:
- **Checklist functionality** → Now available via `audit --review`
- **Analyze functionality** → Now available via `audit` (default mode)
