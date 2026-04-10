# Feature Request Template

Use this template when creating feature requests.

## Template

```markdown
## User Story

As a [role/persona],
I want [capability/feature],
So that [benefit/value].

## Description

[Expanded description of the feature and its context]

## Acceptance Criteria

1. [ ] [First testable criterion]
2. [ ] [Second testable criterion]
3. [ ] [Third testable criterion]
4. [ ] [Continue as needed]

## Scope Boundaries

### In Scope
- [What IS included]

### Out of Scope
- [What is NOT included - prevents scope creep]

## Priority Rationale

[Why this matters now. Business impact, user requests, dependencies.]

## Technical Considerations

[Optional: Known constraints, suggested approaches, related systems]

## Mockups/Examples

[Optional: Wireframes, screenshots of similar features, example outputs]
```

---

## Example: Complete Feature Request

```markdown
## User Story

As a **report analyst**,
I want **to export report data to CSV format**,
So that **I can analyze data in Excel and share with stakeholders who don't have system access**.

## Description

Add CSV export functionality to the Reports page. Users should be able to export the currently displayed report data with a single click. The export should respect any active filters and include all visible columns.

## Acceptance Criteria

1. [ ] "Export CSV" button appears on Reports page header
2. [ ] Clicking export downloads a .csv file with current report data
3. [ ] Export respects active date range and filter selections
4. [ ] CSV includes headers matching visible column names
5. [ ] CSV uses UTF-8 encoding with BOM for Excel compatibility
6. [ ] Large exports (>10,000 rows) show progress indicator
7. [ ] Export filename includes report name and date: `{report-name}-{YYYY-MM-DD}.csv`

## Scope Boundaries

### In Scope
- Single report export to CSV
- Filtered data export
- All standard report types (Daily, Weekly, Monthly)

### Out of Scope
- Scheduled/automated exports (future enhancement)
- PDF export (separate feature request)
- Multi-report batch export
- Custom column selection (exports visible columns only)
- Excel native format (.xlsx)

## Priority Rationale

- Requested by 3 enterprise customers in Q4 feedback
- Current workaround (copy-paste to Excel) fails for reports >500 rows
- Blocks renewal discussion with Acme Corp ($50k ARR)
- Low technical complexity, high user value

## Technical Considerations

- Use streaming for large exports to avoid memory issues
- Consider rate limiting to prevent abuse
- Audit log export events for compliance

## Mockups/Examples

Export button placement:
```
[Reports Header]
[Filter Controls]                    [Export CSV ↓]
[Report Data Table...]
```
```

---

## Example: Incomplete Feature Request (What NOT to Do)

```markdown
## Title: Add CSV export

We need CSV export for reports. Users have been asking for it.
```

**Why this fails:**
- No user story (who needs this and why?)
- No acceptance criteria (what defines "done"?)
- No scope boundaries (does this include all reports? scheduling? other formats?)
- No priority rationale (why now?)
- Developer will make assumptions that may not match user expectations
