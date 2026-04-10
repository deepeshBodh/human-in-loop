# SYNC IMPACT REPORT Format

The SYNC IMPACT REPORT is an HTML comment embedded at the top of the constitution file. It provides a structured changelog that tracks version history, modifications, and template alignment status.

## Purpose

1. **Track changes** without cluttering the main document
2. **Document version bumps** with explicit rationale
3. **Record template alignment** status for dependent files
4. **Preserve history** of previous amendments in one place

## Full Template

```html
<!--
SYNC IMPACT REPORT
==================
Version change: X.Y.Z → A.B.C (MAJOR|MINOR|PATCH: Brief rationale)

Rationale for bump:
- [Detailed explanation of why this version increment was chosen]
- [Additional context if needed]

Modified Sections:
- [Section Name]: [What changed]
- [Section Name]: [What changed]

Added Sections:
- [New section name]
- [New section name]

Removed Sections:
- [Removed section name]
- (or "None" if nothing removed)

Templates Alignment:
- ✅ CLAUDE.md: Synced to vA.B.C
- ✅ plan-template.md: No update needed
- ⚠️ spec-template.md: Needs analytics section update
- ❌ tasks-template.md: Pending review

Follow-up TODOs:
- [Deferred item requiring manual action]
- (or "None" if nothing deferred)

Previous Reports:
- X.Y.Z (YYYY-MM-DD): [One-line summary]
- W.X.Y (YYYY-MM-DD): [One-line summary]
- V.W.X (YYYY-MM-DD): [One-line summary]
-->
```

## Section-by-Section Guide

### Version Change Line

```
Version change: X.Y.Z → A.B.C (MAJOR|MINOR|PATCH: Brief rationale)
```

| Component | Format | Example |
|-----------|--------|---------|
| Old version | Semantic version | 2.3.1 |
| New version | Semantic version | 2.4.0 |
| Bump type | MAJOR, MINOR, or PATCH | MINOR |
| Brief rationale | 3-8 words | Added observability principle |

**Examples**:
```
Version change: 1.0.0 → 2.0.0 (MAJOR: Removed deprecated CI principle)
Version change: 2.3.1 → 2.4.0 (MINOR: Added dependency management)
Version change: 3.1.0 → 3.1.1 (PATCH: Clarified coverage threshold)
```

### Rationale for Bump

Detailed explanation that future maintainers can reference:

```
Rationale for bump:
- Materially expanded Principle IX with product analytics governance
- Added mandatory event categories and naming conventions
- This constitutes new guidance (MINOR), not breaking change
```

### Modified Sections

List every section that changed with brief description:

```
Modified Sections:
- Core Principles: Added Principle X (API Consistency)
- Quality Gates: Updated coverage from 70% to 80%
- Governance: Added exception registry format
```

For no modifications: `Modified Sections: None (new constitution)`

### Added Sections

List new top-level sections:

```
Added Sections:
- Technology Stack (new mandatory section)
- CLAUDE.md Sync Mandate (new mandatory section)
```

For no additions: `Added Sections: None`

### Removed Sections

List removed sections with brief justification:

```
Removed Sections:
- Legacy CI Section: Merged into Quality Gates
- Appendix A: Moved to separate ADR document
```

For no removals: `Removed Sections: None`

### Templates Alignment

Track sync status of dependent files:

| Status | Icon | Meaning |
|--------|------|---------|
| Synced | ✅ | Template updated and aligned |
| Pending | ⚠️ | Needs update, not yet done |
| Blocked | ❌ | Cannot update, requires action |
| N/A | ➖ | No update needed |

```
Templates Alignment:
- ✅ CLAUDE.md: Synced to v3.4.0
- ✅ plan-template.md: No update needed (generic structure)
- ⚠️ spec-template.md: Needs mandatory analytics section
- ➖ tasks-template.md: No constitution impact
```

**Common templates to track**:
- `CLAUDE.md` - Always check
- `.humaninloop/templates/plan-template.md`
- `.humaninloop/templates/spec-template.md`
- `.humaninloop/templates/tasks-template.md`
- `README.md` (if it references constitution)

### Follow-up TODOs

Document deferred work:

```
Follow-up TODOs:
- Update README.md to reference new principle X
- Create exception registry file at docs/exceptions.md
- Schedule team review of new coverage threshold
```

For no TODOs: `Follow-up TODOs: None`

### Previous Reports

Maintain rolling history (most recent first):

```
Previous Reports:
- 3.3.1 (2025-12-18): Replaced Amplitude with PostHog
- 3.3.0 (2025-12-18): Added Product Management Tooling section
- 3.2.0 (2025-12-18): Added Backend Services section
- 3.1.0 (2025-12-18): Added Amplitude analytics mandate
- 3.0.0 (2025-12-18): Comprehensive specificity overhaul (MAJOR)
```

**Guidelines**:
- Keep last 10-15 entries
- One line per version
- Date in YYYY-MM-DD format
- Summary in 5-10 words

## First-Time Constitution

For a brand new constitution:

```html
<!--
SYNC IMPACT REPORT
==================
Version change: (none) → 1.0.0 (MAJOR: Initial constitution)

Rationale for bump:
- Initial ratification of project constitution
- Establishes 7 core principles for development governance

Modified Sections: N/A (initial version)

Added Sections:
- Core Principles (I through VII)
- Technology Stack
- Quality Gates
- Governance
- CLAUDE.md Sync Mandate

Removed Sections: None

Templates Alignment:
- ✅ CLAUDE.md: Created with constitution sync
- ⚠️ plan-template.md: Review for constitution compliance
- ⚠️ spec-template.md: Review for constitution compliance

Follow-up TODOs:
- Review existing code for constitution compliance
- Create initial exception registry for known deviations

Previous Reports: None (initial version)
-->
```

## Amendment Examples

### MINOR: Adding a Principle

```html
<!--
SYNC IMPACT REPORT
==================
Version change: 2.3.0 → 2.4.0 (MINOR: Added Observability principle)

Rationale for bump:
- Added Principle IX (Observability) with structured logging requirements
- New principle adds governance, does not modify existing principles
- MINOR bump per amendment process (new principle = MINOR)

Modified Sections:
- Table of Contents: Added entry for Principle IX

Added Sections:
- Principle IX: Observability

Removed Sections: None

Templates Alignment:
- ✅ CLAUDE.md: Added Observability to principles summary
- ➖ plan-template.md: No update needed
- ➖ spec-template.md: No update needed

Follow-up TODOs: None

Previous Reports:
- 2.3.0 (2025-12-15): Added exception registry format
- 2.2.0 (2025-12-10): Expanded error handling principle
-->
```

### PATCH: Clarification

```html
<!--
SYNC IMPACT REPORT
==================
Version change: 3.1.0 → 3.1.1 (PATCH: Clarified coverage threshold)

Rationale for bump:
- Clarified that 80% coverage applies to new code, not entire codebase
- No semantic change to the rule, just clearer wording
- PATCH bump per amendment process (clarification only)

Modified Sections:
- Principle I (Testing): Added "for new code" clarification

Added Sections: None

Removed Sections: None

Templates Alignment:
- ✅ CLAUDE.md: No change needed (summary already accurate)
- ➖ Other templates: No impact

Follow-up TODOs: None

Previous Reports:
- 3.1.0 (2025-12-18): Added CLAUDE.md sync mandate
- 3.0.0 (2025-12-15): Major restructure for specificity
-->
```

### MAJOR: Breaking Change

```html
<!--
SYNC IMPACT REPORT
==================
Version change: 2.5.0 → 3.0.0 (MAJOR: Restructured principles, removed deprecated rules)

Rationale for bump:
- Removed Principle V (Deprecated CI Integration) - breaking change
- Merged Principle VI into Principle III - incompatible reorganization
- Increased coverage requirement from 70% to 80% - stricter constraint
- MAJOR bump required per governance (principle removal = MAJOR)

Modified Sections:
- All principle numbers shifted due to removal
- Principle III: Now includes merged content from old Principle VI
- Quality Gates: Coverage threshold changed 70% → 80%

Added Sections: None

Removed Sections:
- Principle V: Deprecated CI Integration (redundant with Quality Gates)

Templates Alignment:
- ⚠️ CLAUDE.md: Needs principle renumbering
- ⚠️ plan-template.md: References old principle numbers
- ⚠️ spec-template.md: References old coverage threshold
- ⚠️ All code: May reference old principle numbers in comments

Follow-up TODOs:
- Update all template files with new principle numbers
- Search codebase for old principle references
- Communicate breaking change to team
- Update exception registry entries that reference old principles

Previous Reports:
- 2.5.0 (2025-12-01): Added dependency management
- 2.4.0 (2025-11-15): Added observability
-->
```

## Validation Checklist

Before finalizing a SYNC IMPACT REPORT:

- [ ] Version change line has old → new format
- [ ] Bump type (MAJOR/MINOR/PATCH) matches actual changes
- [ ] Rationale explains "why" not just "what"
- [ ] All modified sections listed with descriptions
- [ ] Added/Removed sections accurately reflect changes
- [ ] Template alignment status is current
- [ ] TODOs are actionable (not vague)
- [ ] Previous reports list is maintained (newest first)
- [ ] Dates use ISO format (YYYY-MM-DD)
