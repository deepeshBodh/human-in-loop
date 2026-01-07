# Quality Checklist

Before finalizing a constitution, verify all items below.

## Principle Quality

- [ ] Every principle has Enforcement section
- [ ] Every principle has Testability section
- [ ] Every principle has Rationale section
- [ ] All MUST statements have enforcement mechanisms
- [ ] All quantifiable criteria have specific thresholds
- [ ] No vague language without measurable criteria

## Structure Quality

- [ ] SYNC IMPACT REPORT present as HTML comment
- [ ] Overview section with project description
- [ ] Core Principles numbered with Roman numerals
- [ ] Technology Stack table complete with rationale
- [ ] Quality Gates table with measurement commands
- [ ] Governance section with amendment process
- [ ] CLAUDE.md Sync Mandate with mapping table
- [ ] Version footer with dates in ISO format

## No Placeholders Rule

- [ ] Technology Stack has NO `[PLACEHOLDER]` syntax - all actual tool names
- [ ] Quality Gates has NO `[COMMAND]` placeholders - all actual commands
- [ ] Coverage thresholds are numeric (e.g., "≥80%", NOT "[THRESHOLD]%")
- [ ] Security tools are named (e.g., "Trivy + Snyk", NOT "[SECURITY_COMMAND]")
- [ ] Test commands are complete (e.g., "`pytest --cov`", NOT "`[TEST_COMMAND]`")

## Governance Quality

- [ ] Version follows semantic versioning
- [ ] Amendment process is actionable
- [ ] Exception registry format defined
- [ ] Compliance review expectations set

## Brownfield-Specific (if applicable)

- [ ] All four essential floor categories have principles
- [ ] Existing good patterns identified and codified
- [ ] Gap references included where codebase lacks capability
- [ ] Technology stack matches codebase analysis
- [ ] Quality gates reflect current + target state
- [ ] Evolution Notes section documents brownfield context
