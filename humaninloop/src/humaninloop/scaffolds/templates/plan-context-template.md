---
type: plan-request
phase: {{phase}}
status: {{status}}
iteration: {{iteration}}
feature_id: {{feature_id}}
created: {{created}}
updated: {{updated}}
analysis_status: {{analysis_status}}
design_status: {{design_status}}
---

# Plan Request

## Feature Context

| Aspect | Value |
|--------|-------|
| Feature ID | {{feature_id}} |
| Spec Status | {{spec_status}} |
| Current Phase | {{phase}} |
| Constitution | {{constitution_path}} |
| Project Type | {{project_type}} |
| Codebase Analysis | {{codebase_analysis_path}} |

## File Paths

| File | Path | Status |
|------|------|--------|
| Spec | {{spec_path}} | {{spec_status}} |
| Requirements | {{requirements_path}} | {{requirements_status}} |
| Constraints & Decisions | {{constraints_decisions_path}} | {{constraints_decisions_status}} |
| NFRs | {{nfrs_path}} | {{nfrs_status}} |
| Data Model | {{datamodel_path}} | {{datamodel_status}} |
| Contracts | {{contracts_path}} | {{contracts_status}} |
| Quickstart | {{quickstart_path}} | {{quickstart_status}} |
| Analyst Report | {{analyst_report_path}} | - |
| Architect Report | {{architect_report_path}} | - |
| Advocate Report | {{advocate_report_path}} | - |

## Constitution Principles

{{constitution_principles}}

## Codebase Context

| Field | Value |
|-------|-------|
| Project Type | {{project_type}} |
| Analysis Path | {{codebase_analysis_path}} |
| Analysis Age | {{codebase_analysis_age}} |

{{codebase_context}}

## Supervisor Instructions

{{supervisor_instructions}}

## Clarification Log

{{clarification_log}}
