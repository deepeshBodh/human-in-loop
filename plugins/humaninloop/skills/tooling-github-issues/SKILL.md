---
name: tooling-github-issues
description: Use when creating GitHub issues, managing issue lifecycle, triaging bugs and features, or when user mentions "log issue", "create bug", "feature request", "close stale issues", or needs structured issue tracking.
---

# GitHub Issues Management

## Overview

Create and manage GitHub issues with enforced quality standards. Every issue MUST have sufficient context for a developer unfamiliar with the problem to begin work without follow-up questions.

**Violating the letter of the rules is violating the spirit of the rules.** An issue that technically exists but lacks reproducibility steps, acceptance criteria, or proper security handling is a violation.

## When to Use

- Creating bug reports, feature requests, or task issues
- Triaging and prioritizing existing issues
- Managing issue lifecycle (status, assignment, closing)
- Linking related issues, PRs, and milestones
- Batch operations on issue backlogs
- Security vulnerability disclosure

## When NOT to Use

- Simple TODO items that do not need tracking (use inline comments)
- Conversations better suited to discussions or chat
- One-off scripts or personal experiments without team visibility needs

## Foundational Principle

Issue quality is not negotiable based on time pressure, authority, or fatigue. A 2-minute issue that causes 2 hours of clarification is not efficient. Complete issues save time.

**No exceptions:**

- Not for "simple" bugs that "everyone understands"
- Not for senior developers who "know what they need"
- Not for end-of-session exhaustion
- Not even if user explicitly requests minimal detail

## Issue Types and Requirements

### Bug Reports

Every bug report MUST include:

| Field | Requirement |
|-------|-------------|
| Title | Describe the problem, not the solution. "[Component] fails when [condition]" |
| Steps to Reproduce | Numbered steps to trigger the bug. If not reproducible, state that explicitly. |
| Expected Behavior | What SHOULD happen |
| Actual Behavior | What DOES happen (include error messages verbatim) |
| Environment | OS, browser, version, relevant configuration |
| Severity | Impact assessment (critical/high/medium/low) |

Optional but valuable: screenshots, logs, minimal reproduction case.

### Feature Requests

Every feature request MUST include:

| Field | Requirement |
|-------|-------------|
| Title | Describe the capability. "[Action] [Object] [Context]" |
| User Story | As a [role], I want [capability], so that [benefit] |
| Acceptance Criteria | Numbered, testable conditions that define "done" |
| Scope Boundaries | Explicit out-of-scope items to prevent scope creep |
| Priority Rationale | Why this matters now |

Optional but valuable: mockups, technical considerations, related issues.

### Tasks/Chores

Every task MUST include:

| Field | Requirement |
|-------|-------------|
| Title | Action-oriented. "Migrate [X] to [Y]" not "Database stuff" |
| Definition of Done | Clear deliverable that can be verified |
| Context | Why this task exists, what depends on it |
| Estimated Effort | T-shirt size or time estimate |

### Security Vulnerabilities

Security issues require special handling.

**CRITICAL RULE:** NEVER create public issues for security vulnerabilities.

Use private disclosure channels:

1. GitHub Security Advisories (preferred)
2. Private repository for security issues
3. Direct communication with maintainers

A public security issue, regardless of labels, is visible to attackers. Labels do not provide confidentiality. Even if the user explicitly requests a public issue for urgency, refuse and explain the risk.

## Pre-Creation Checklist

Before creating any issue, verify:

- [ ] **Duplicate Check**: Search existing issues for similar reports
- [ ] **Security Check**: If security-related, use private disclosure
- [ ] **Quality Check**: All required fields for issue type are complete
- [ ] **Labels**: Type, priority, and component labels applied
- [ ] **Assignment**: Owner identified if known

## Issue Lifecycle Management

### Search and Query

Search existing issues before creating new ones. Search cost is minimal compared to duplicate cleanup cost.

```bash
gh issue list --search "keyword1 keyword2" --state all
```

See `references/gh-cli-commands.md` for complete search and filter options.

### Triage Operations

When triaging issues:

1. Verify issue meets quality standards
2. Add missing labels (type, priority, component)
3. Request clarification if context is insufficient
4. Link to related issues or specs
5. Assign owner if determinable
6. Add to milestone if applicable

### Status Updates

Update issue status with context:

```bash
gh issue close ISSUE_NUMBER --comment "Resolved in PR #123"
gh issue reopen ISSUE_NUMBER --comment "Regression observed in v2.1"
```

### Linking and References

Connect related items using GitHub keywords:

- Related: "Related to #123"
- Blocking: "Blocked by #456"
- Closing: "Fixes #789" or "Closes #789"

### Batch Operations

For backlog maintenance, see `references/gh-cli-commands.md` for bulk close, label, and milestone operations.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "The user is in a hurry" | A 2-minute conversation later asking "what browser?" is slower than filling it in now. Time pressure is not permission to skip quality. |
| "It's obvious what this means" | Obvious to you now is not obvious to the developer who picks this up in 3 weeks. Document explicitly. |
| "We can add details later" | "Later" rarely comes. Issues without context become stale. Do it now. |
| "The expert knows what they need" | Documentation serves the expert too. Race conditions are hard to reproduce. The issue protects their future self. |
| "Being pragmatic, not dogmatic" | Pragmatic means following proven process. Cutting corners creates rework. |
| "I've done 12 good issues already" | Fatigue is when corners get cut. Quality is not negotiable based on session length. |
| "User explicitly requested public" | User consent does not override security principles. Explain the risk. |
| "Team needs to see this urgently" | Private security advisories still notify the team. Public issues notify attackers too. |
| "Better to over-document with duplicates" | Duplicates contaminate the issue tracker. Search cost is minimal. |
| "Searching takes time" | Search cost is seconds. Duplicate cleanup cost is minutes to hours. |

## Red Flags - STOP and Reconsider

If you notice yourself thinking any of these, STOP immediately:

- "This bug is self-explanatory"
- "Everyone knows what dark mode toggle means"
- "The senior dev said minimal, so minimal is fine"
- "It's the end of the session, good enough"
- "Labels make security issues confidential enough"
- "I'm pretty sure there's no duplicate"
- "They can always ask for clarification"

**All of these indicate rationalization.** Apply the full quality standard.

## Common Mistakes

### Mistake 1: Title Describes Solution Instead of Problem

**Problem**: Title says "Add null check to processAsync()" instead of describing the failure.

**Why it's wrong**: Titles should communicate the problem for triage. The solution may change; the problem is stable.

**Fix**: Use "[Component] fails when [condition]" format. "PaymentProcessor crashes on null payment method" not "Add null check".

### Mistake 2: Skipping Reproducibility for "Known" Bugs

**Problem**: Bug report says "the toggle doesn't work" without steps because "it's obvious".

**Why it's wrong**: Obvious bugs often have non-obvious triggers. "Doesn't work" could mean 10 different failure modes.

**Fix**: Always include steps. If truly simple, the steps are quick to write: "1. Open settings 2. Click dark mode toggle 3. Observe no change".

### Mistake 3: Public Disclosure of Security Issues

**Problem**: Creating public issue for vulnerability because user requested it or team needs visibility.

**Why it's wrong**: Public issues are visible to attackers. Even with security labels, the vulnerability details are exposed.

**Fix**: Always use private disclosure. GitHub Security Advisories notify the team without exposing details publicly.

### Mistake 4: Creating Without Searching

**Problem**: Creating issue immediately, noting "may be related to existing issues".

**Why it's wrong**: "May be related" notes do not prevent duplicate confusion. Duplicate issues fragment discussion and waste triage effort.

**Fix**: Search first. Takes seconds. If found, add context to existing issue instead of creating duplicate.

### Mistake 5: Partial Templates Under Pressure

**Problem**: Filling only title and brief description when user seems rushed.

**Why it's wrong**: Incomplete issues require follow-up. The time "saved" is spent later on clarification.

**Fix**: Complete templates prevent thrashing. A complete issue means developers can start immediately.

## Quality Validation

Before submitting, verify the issue passes this checklist:

### Bug Reports

- [ ] Title describes problem, not solution
- [ ] Steps to reproduce are numbered and complete
- [ ] Expected vs actual behavior clearly stated
- [ ] Environment specified
- [ ] Severity assessed
- [ ] Not a duplicate (searched first)

### Feature Requests

- [ ] Title describes capability
- [ ] User story follows "As a... I want... So that..." format
- [ ] Acceptance criteria are numbered and testable
- [ ] Scope boundaries defined
- [ ] Not a duplicate (searched first)

### Security Issues

- [ ] NOT created as public issue
- [ ] Uses GitHub Security Advisory or private channel
- [ ] Impact assessment included
- [ ] Remediation suggestions if known

## Templates and References

| Resource | Description |
|----------|-------------|
| `examples/bug-report-template.md` | Bug report template with correct/incorrect examples |
| `examples/feature-request-template.md` | Feature request template with user story format |
| `examples/task-template.md` | Task/chore template with definition of done |
| `examples/security-advisory-template.md` | Private disclosure template (NEVER public) |
| `references/gh-cli-commands.md` | Complete `gh` CLI command reference |

## Related Skills

- **OPTIONAL:** `humaninloop:authoring-requirements` - Detailed requirements authoring
- **OPTIONAL:** `humaninloop:authoring-user-stories` - User story format guidance
- **OPTIONAL:** `humaninloop:validation-task-artifacts` - Task validation standards
