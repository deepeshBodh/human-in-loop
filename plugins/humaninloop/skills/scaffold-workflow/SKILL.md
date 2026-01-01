---
name: scaffold-workflow
description: Execute the scaffolding phase of the HumanInLoop specification workflow. Creates feature branches, directory structures, and initializes hybrid workflow context. EXCLUSIVE TO scaffold-agent - do not invoke from other agents. Use when starting a new feature specification and need to create the initial branch and directories.
---

# Scaffold Workflow Skill

## Purpose

Orchestrate the scaffolding phase of the HumanInLoop specification-driven development workflow. This skill provides a single deterministic script for creating feature infrastructure without modifying specification content.

## Exclusivity Notice

This skill is **exclusively used by scaffold-agent**. Other agents (spec-writer, clarify, plan, tasks) should not invoke these procedures directly. The scaffold-agent declares this skill in its frontmatter to establish ownership.

## Script

The skill provides a single consolidated script: `scripts/create-new-feature.sh`

### create-new-feature.sh

Create the complete feature scaffold (branch + directory + template).

```bash
./scripts/create-new-feature.sh --json "Add user authentication with OAuth2"
# Output: {"BRANCH_NAME":"005-user-auth","SPEC_FILE":"specs/005-user-auth/spec.md","FEATURE_NUM":"005"}
```

**Options**:
- `--json`: Output in JSON format (required for agent integration)
- `--number N`: Override auto-detected feature number
- `--short-name <name>`: Override generated branch slug

**What it does**:
1. Generates a clean branch slug from the feature description
2. Determines the next sequential feature number
3. Creates git branch (if git repository detected)
4. Creates feature directory at `specs/{BRANCH_NAME}/`
5. Copies spec template to `specs/{BRANCH_NAME}/spec.md`
6. Exports `HUMANINLOOP_FEATURE` environment variable

### Internal Behaviors

**Branch Name Generation**:
- Filters common stop words (I, want, add, the, to, for, with, create, build, implement, etc.)
- Preserves technical terms and acronyms (OAuth2, API, JWT, SSO, CRUD, REST, GraphQL)
- Uses lowercase with hyphens as separators
- Limits output to 3-4 meaningful words
- Minimum 3 characters per word (except recognized acronyms)

| Input | Generated Slug |
|-------|----------------|
| "I want to add user authentication" | `user-authentication` |
| "Implement OAuth2 integration for the API" | `oauth2-integration-api` |
| "Create a dashboard for analytics" | `dashboard-analytics` |
| "Add task priority levels" | `task-priority-levels` |

**Feature Number Detection**:
- Fetches all remote branches (if git repository detected)
- Scans both local/remote branches for `###-*` pattern
- Scans specs directory for existing feature directories
- Returns the maximum found + 1
- Zero-pads to 3 digits
- Starts at `001` if no existing features found

## Scaffolding Procedure

Execute these steps in order when scaffolding a new feature:

### Step 1: Run the Scaffold Script

```bash
${SKILL_ROOT}/scripts/create-new-feature.sh \
  --json \
  "{{FEATURE_DESCRIPTION}}"
```

Or with explicit values:
```bash
${SKILL_ROOT}/scripts/create-new-feature.sh \
  --json \
  --number {{NEXT_NUMBER}} \
  --short-name "{{SHORT_NAME}}" \
  "{{FEATURE_DESCRIPTION}}"
```

### Step 2: Parse JSON Output

Extract from the script output:
- `BRANCH_NAME`: Full branch name (e.g., "005-user-auth")
- `SPEC_FILE`: Path to the spec file
- `FEATURE_NUM`: Zero-padded feature number

### Step 3: Create Workflow Directory

```bash
mkdir -p specs/{{BRANCH_NAME}}/.workflow
mkdir -p specs/{{BRANCH_NAME}}/checklists
```

### Step 4: Initialize Hybrid Workflow Context

The hybrid context architecture uses multiple context files for cross-workflow visibility.

**4.1 Create index.md** (shared cross-workflow state):
- Copy from `${CLAUDE_PLUGIN_ROOT}/templates/workflow-index-template.md`
- Destination: `specs/{{BRANCH_NAME}}/.workflow/index.md`
- Fill placeholders:
  - `{{feature_id}}` -> BRANCH_NAME
  - `{{branch_name}}` -> BRANCH_NAME
  - `{{created_timestamp}}` -> Current ISO 8601 timestamp
  - `{{updated_timestamp}}` -> Current ISO 8601 timestamp
  - `{{original_description}}` -> Original feature description verbatim
  - Set all document statuses to `absent` initially
  - Set `specify_status` to `in_progress`, all others to `not_started`

**4.2 Create specify-context.md** (specify workflow state):
- Copy from `${CLAUDE_PLUGIN_ROOT}/templates/specify-context-template.md`
- Destination: `specs/{{BRANCH_NAME}}/.workflow/specify-context.md`
- Fill placeholders:
  - `{{feature_id}}` -> BRANCH_NAME
  - `{{original_description}}` -> Original feature description
  - `{{branch_name}}` -> BRANCH_NAME
  - `{{timestamp}}` -> Current ISO 8601 timestamp
  - `{{status}}` -> `scaffolding`
  - `{{current_agent}}` -> `scaffold`

**4.3 Create placeholder context files** for other workflows:
- Copy `checklist-context-template.md` -> `checklist-context.md`
- Copy `plan-context-template.md` -> `plan-context.md`
- Copy `tasks-context-template.md` -> `tasks-context.md`
- Set their status to `not_started`

### Step 5: Add Decision Log Entry

Add initial entry to **both** index.md and specify-context.md:

```markdown
| {{timestamp}} | specify | scaffold | Created feature branch and directory | Auto-generated from description |
```

### Step 6: Update Handoff Notes

In specify-context.md, update the handoff notes section:

```markdown
### From Scaffold Agent
- Branch created: {{BRANCH_NAME}}
- Spec template copied to: {{SPEC_FILE}}
- Index initialized: specs/{{BRANCH_NAME}}/.workflow/index.md
- Ready for Spec Writer Agent
```

## Quality Verification

Before returning success, verify all of the following:

- [ ] Git branch exists locally (if git repository)
- [ ] Feature directory created at `specs/{{BRANCH_NAME}}/`
- [ ] Spec template file exists at `specs/{{BRANCH_NAME}}/spec.md`
- [ ] Checklists directory exists at `specs/{{BRANCH_NAME}}/checklists/`
- [ ] index.md created and populated at `specs/{{BRANCH_NAME}}/.workflow/index.md`
- [ ] specify-context.md created at `specs/{{BRANCH_NAME}}/.workflow/specify-context.md`
- [ ] Placeholder context files created for checklist, plan, tasks workflows
- [ ] All template placeholders have been replaced
- [ ] All paths in output JSON are valid and accessible

## Error Handling

| Error Type | Detection | Response |
|------------|-----------|----------|
| Script not found | Check if script exists before execution | Report missing dependency with path |
| Git error | Check git command exit status | Report specific git error message |
| Permission error | Check file operation results | Report path with permission issue |
| Partial failure | Track each step completion | Document partial state, attempt cleanup, report accurately |
| Duplicate branch | Check if branch already exists | Increment feature number and retry |
| Template not found | Check if template file exists | Create empty file as fallback, warn in output |

### Partial Failure Recovery

If scaffolding partially completes:
1. Document what succeeded and what failed
2. Attempt cleanup of partial work if safe (e.g., remove incomplete directories)
3. Report the partial state in the error response:

```json
{
  "success": false,
  "error": "Failed to copy template: permission denied",
  "partial_state": {
    "branch_created": true,
    "dirs_created": true,
    "template_copied": false,
    "context_initialized": false
  },
  "cleanup_performed": true
}
```

## Integration Notes

### Template Paths

Templates are located in the shared templates directory:
- `${CLAUDE_PLUGIN_ROOT}/templates/workflow-index-template.md`
- `${CLAUDE_PLUGIN_ROOT}/templates/specify-context-template.md`
- `${CLAUDE_PLUGIN_ROOT}/templates/checklist-context-template.md`
- `${CLAUDE_PLUGIN_ROOT}/templates/plan-context-template.md`
- `${CLAUDE_PLUGIN_ROOT}/templates/tasks-context-template.md`
- `${CLAUDE_PLUGIN_ROOT}/templates/spec-template.md`

### Environment Variables

- `CLAUDE_PLUGIN_ROOT`: Path to the humaninloop plugin directory
- `HUMANINLOOP_FEATURE`: Set by create-new-feature.sh to the branch name

### Workflow Chain Position

This skill supports the first agent in the HumanInLoop workflow:

1. **Scaffold Agent** (uses this skill) -> Creates structure
2. **Spec Writer Agent** -> Fills specification content
3. **Clarify Agent** -> Identifies gaps
4. **Plan Agent** -> Creates implementation plan
5. **Tasks Agent** -> Generates task list

The output from this skill becomes the input context for the Spec Writer Agent.
