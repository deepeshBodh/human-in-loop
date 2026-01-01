---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
handoffs:
  - label: Run Analysis
    agent: humaninloop:analyze
    prompt: Analyze cross-artifact consistency after implementation
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. Run `${CLAUDE_PLUGIN_ROOT}/scripts/check-prerequisites.sh --json --require-tasks --include-tasks` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Check checklists status** (if FEATURE_DIR/checklists/ exists):
   - Scan all checklist files in the checklists/ directory
   - For each checklist, count:
     - Total items: All lines matching `- [ ]` or `- [X]` or `- [x]`
     - Completed items: Lines matching `- [X]` or `- [x]`
     - Incomplete items: Lines matching `- [ ]`
   - Create a status table:

     ```text
     | Checklist | Total | Completed | Incomplete | Status |
     |-----------|-------|-----------|------------|--------|
     | ux.md     | 12    | 12        | 0          | ✓ PASS |
     | test.md   | 8     | 5         | 3          | ✗ FAIL |
     | security.md | 6   | 6         | 0          | ✓ PASS |
     ```

   - Calculate overall status:
     - **PASS**: All checklists have 0 incomplete items
     - **FAIL**: One or more checklists have incomplete items

   - **If any checklist is incomplete**:
     - Display the table with incomplete item counts
     - **STOP** and ask: "Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)"
     - Wait for user response before continuing
     - If user says "no" or "wait" or "stop", halt execution
     - If user says "yes" or "proceed" or "continue", proceed to step 3

   - **If all checklists are complete**:
     - Display the table showing all checklists passed
     - Automatically proceed to step 3

3. Load and analyze the implementation context:
   - **REQUIRED**: Read tasks.md for the complete task list and execution plan
   - **REQUIRED**: Read plan.md for tech stack, architecture, and file structure
   - **IF EXISTS**: Read data-model.md for entities and relationships
   - **IF EXISTS**: Read contracts/ for API specifications and test requirements
   - **IF EXISTS**: Read research.md for technical decisions and constraints
   - **IF EXISTS**: Read quickstart.md for integration scenarios

4. **Project Setup Verification**:
   - **REQUIRED**: Create/verify ignore files based on actual project setup:

   **Detection & Creation Logic**:
   - Check if the following command succeeds to determine if the repository is a git repo (create/verify .gitignore if so):

     ```sh
     git rev-parse --git-dir 2>/dev/null
     ```

   - Check if Dockerfile* exists or Docker in plan.md → create/verify .dockerignore
   - Check if .eslintrc* exists → create/verify .eslintignore
   - Check if eslint.config.* exists → ensure the config's `ignores` entries cover required patterns
   - Check if .prettierrc* exists → create/verify .prettierignore
   - Check if .npmrc or package.json exists → create/verify .npmignore (if publishing)
   - Check if terraform files (*.tf) exist → create/verify .terraformignore
   - Check if .helmignore needed (helm charts present) → create/verify .helmignore

   **If ignore file already exists**: Verify it contains essential patterns, append missing critical patterns only
   **If ignore file missing**: Create with full pattern set for detected technology

   **Common Patterns by Technology** (from plan.md tech stack):
   - **Node.js/JavaScript/TypeScript**: `node_modules/`, `dist/`, `build/`, `*.log`, `.env*`
   - **Python**: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `dist/`, `*.egg-info/`
   - **Java**: `target/`, `*.class`, `*.jar`, `.gradle/`, `build/`
   - **C#/.NET**: `bin/`, `obj/`, `*.user`, `*.suo`, `packages/`
   - **Go**: `*.exe`, `*.test`, `vendor/`, `*.out`
   - **Ruby**: `.bundle/`, `log/`, `tmp/`, `*.gem`, `vendor/bundle/`
   - **PHP**: `vendor/`, `*.log`, `*.cache`, `*.env`
   - **Rust**: `target/`, `debug/`, `release/`, `*.rs.bk`, `*.rlib`, `*.prof*`, `.idea/`, `*.log`, `.env*`
   - **Kotlin**: `build/`, `out/`, `.gradle/`, `.idea/`, `*.class`, `*.jar`, `*.iml`, `*.log`, `.env*`
   - **C++**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.so`, `*.a`, `*.exe`, `*.dll`, `.idea/`, `*.log`, `.env*`
   - **C**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.a`, `*.so`, `*.exe`, `Makefile`, `config.log`, `.idea/`, `*.log`, `.env*`
   - **Swift**: `.build/`, `DerivedData/`, `*.swiftpm/`, `Packages/`
   - **R**: `.Rproj.user/`, `.Rhistory`, `.RData`, `.Ruserdata`, `*.Rproj`, `packrat/`, `renv/`
   - **Universal**: `.DS_Store`, `Thumbs.db`, `*.tmp`, `*.swp`, `.vscode/`, `.idea/`

   **Tool-Specific Patterns**:
   - **Docker**: `node_modules/`, `.git/`, `Dockerfile*`, `.dockerignore`, `*.log*`, `.env*`, `coverage/`
   - **ESLint**: `node_modules/`, `dist/`, `build/`, `coverage/`, `*.min.js`
   - **Prettier**: `node_modules/`, `dist/`, `build/`, `coverage/`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
   - **Terraform**: `.terraform/`, `*.tfstate*`, `*.tfvars`, `.terraform.lock.hcl`
   - **Kubernetes/k8s**: `*.secret.yaml`, `secrets/`, `.kube/`, `kubeconfig*`, `*.key`, `*.crt`

4.5. **Pre-Implementation Collision Detection**:

   Analyze ALL tasks for potential file collisions BEFORE any implementation begins.
   This step ensures no silent overwrites of existing code.

   **4.5.1 Extract Target Files from Tasks**:

   Parse tasks.md and extract file paths from task descriptions using these patterns (in priority order):

   1. `... in <path>` at end of description (e.g., "Create User model in src/models/user.py")
   2. `... to <path>` at end (e.g., "Add validation to src/utils/validators.py")
   3. Explicit path pattern: `(src|tests|app|lib|backend|frontend)/...` anywhere in description
   4. `Create/Implement/Add X in <path>` pattern

   For each task matching `^- \[ \] T\d+`:
   - Extract task_id (T###)
   - Extract file_path using patterns above
   - Build list: `task_files = [{task_id, file_path, task_description}, ...]`

   **4.5.2 Check for Existing Files**:

   For each extracted file path:

   1. Check if file exists on filesystem using absolute path
   2. If `{FEATURE_DIR}/.workflow/codebase-inventory.json` exists:
      - Enrich collision info with inventory data (collision_risks, entities, endpoints)
      - Use recommended_action from inventory if available
   3. If no inventory exists: use basic filesystem check only (no enrichment)
   4. Check protected_paths from constitution.md brownfield_overrides (if defined)
   5. Check for brownfield markers in task description and use as default strategy:

   **Brownfield Marker → Strategy Mapping**:

   | Task Marker | Default Strategy | Meaning |
   |-------------|------------------|---------|
   | (none) | Normal create | New file (greenfield default) |
   | `[EXTEND]` | MERGE | Add to existing file |
   | `[MODIFY]` | MERGE | Change existing code |
   | `[CONFLICT]` | (prompt user) | Manual resolution required |

   Build collision list:
   ```
   collisions = [{
     task_id: "T012",
     file_path: "src/models/user.py",
     exists: true,
     line_count: 127,
     brownfield_marker: "[EXTEND]",  // from task description, if present
     inventory_match: { entity: "User", collision_risk: "compatible_extend" },
     protected: false,
     recommended_strategy: "MERGE"   // derived from marker or inventory
   }, ...]
   ```

   **4.5.3 Generate Collision Report**:

   **If collisions.length == 0**:
   - Display: "No file collisions detected. Proceeding with implementation."
   - Proceed to Step 5

   **If collisions.length > 0**:
   Display collision report:

   ```markdown
   ## Pre-Implementation Collision Report

   **Feature**: {feature_id}
   **Tasks Analyzed**: {task_count}
   **Files Extracted**: {file_count}
   **Collisions Detected**: {collision_count}

   | # | Task ID | Target File | Status | Lines | Recommended Strategy |
   |---|---------|-------------|--------|-------|----------------------|
   | 1 | T012 | src/models/user.py | EXISTS | 127 | MERGE |
   | 2 | T014 | src/services/auth.py | EXISTS | 89 | OVERWRITE |
   | 3 | T018 | src/auth/core.py | PROTECTED | 234 | REQUIRE APPROVAL |
   ```

   Proceed to 4.5.4

   **4.5.4 Collect User Strategies via AskUserQuestion**:

   Present overall strategy selection:

   ```
   AskUserQuestion(
     questions: [{
       question: "Found {collision_count} file collisions. Select handling approach:",
       header: "Collision Strategy",
       options: [
         {label: "Review individually", description: "Choose strategy per file or group"},
         {label: "Apply recommendations", description: "Use auto-suggested strategies from report"},
         {label: "MERGE all", description: "Attempt intelligent merge for all conflicts"},
         {label: "OVERWRITE all", description: "Replace all existing files (backups created)"},
         {label: "Abort", description: "Stop implementation for manual review"}
       ],
       multiSelect: false
     }]
   )
   ```

   **Strategy Definitions**:
   - **MERGE**: Intelligently combine new content with existing file (for additive changes)
   - **OVERWRITE**: Replace file entirely (backup created first in {FEATURE_DIR}/.backup/)
   - **SKIP**: Leave existing file unchanged, log skip reason, mark task as skipped
   - **ABORT**: Stop entire implementation workflow, report all conflicts

   **Protected file handling**:
   Protected files (from constitution.brownfield_overrides.protected_paths) ALWAYS require
   individual confirmation, regardless of batch strategy:

   ```
   AskUserQuestion(
     questions: [{
       question: "Protected file: {file_path}\nReason: {protection_reason}\nThis file requires explicit approval to modify.",
       header: "Protected File",
       options: [
         {label: "OVERWRITE anyway", description: "Backup and replace (not recommended)"},
         {label: "SKIP", description: "Keep existing file, skip this task"},
         {label: "Abort", description: "Stop implementation for manual review"}
       ],
       multiSelect: false
     }]
   )
   ```

   **4.5.5 Log Decisions to index.md**:

   Update `{FEATURE_DIR}/.workflow/index.md` Implementation Collision Log section:

   ```markdown
   | Timestamp | Task ID | File Path | Strategy | Status |
   |-----------|---------|-----------|----------|--------|
   | 2025-12-31T14:30:22Z | T012 | src/models/user.py | MERGE | pending |
   | 2025-12-31T14:30:22Z | T014 | src/services/auth.py | OVERWRITE | pending |
   | 2025-12-31T14:30:22Z | T018 | src/auth/core.py | SKIP | pending |
   ```

   **4.5.6 Handle ABORT Strategy**:

   If any collision strategy == "ABORT":
   - Log to index.md with status: "aborted"
   - Display detailed conflict summary
   - Display: "Implementation aborted. Review conflicts manually before retrying."
   - List all files requiring attention
   - STOP workflow (do not proceed to Step 5)

   **4.5.7 Store Strategies for Step 6**:

   Store collision strategies in memory for use during task execution:
   ```
   collision_strategies = {
     "src/models/user.py": { strategy: "MERGE", task_id: "T012" },
     "src/services/auth.py": { strategy: "OVERWRITE", task_id: "T014" },
     "src/auth/core.py": { strategy: "SKIP", task_id: "T018" }
   }
   ```

   Proceed to Step 5.

5. Parse tasks.md structure and extract:
   - **Task phases**: Setup, Tests, Core, Integration, Polish
   - **Task dependencies**: Sequential vs parallel execution rules
   - **Task details**: ID, description, file paths, parallel markers [P]
   - **Execution flow**: Order and dependency requirements

6. Execute implementation following the task plan:

   **Pre-write collision check for each task**:

   Before writing/modifying any file for a task, check if the file_path exists in collision_strategies (from Step 4.5):

   ```
   FOR each task being executed:
     file_path = extract_file_path(task_description)

     IF file_path in collision_strategies:
       strategy = collision_strategies[file_path]

       SWITCH strategy:
         CASE "SKIP":
           - Log: "Skipping {file_path} per collision strategy (keeping existing file)"
           - Mark task as skipped in tasks.md: `- [S] T### [SKIPPED] ...`
           - Update index.md collision log: status = "skipped"
           - CONTINUE to next task (do not write file)

         CASE "MERGE":
           - Read existing file content
           - Generate merged content (combine existing + new, preserving both)
           - Write merged content to file
           - Update index.md collision log: status = "completed"

         CASE "OVERWRITE":
           - Write new content (replacing entire file)
           - Update index.md collision log: status = "completed"
           - Note: Use `git diff` or `git checkout` to recover if needed

     ELSE:
       - Proceed with normal file creation (no collision)
   ```

   **Standard execution rules**:
   - **Phase-by-phase execution**: Complete each phase before moving to the next
   - **Respect dependencies**: Run sequential tasks in order, parallel tasks [P] can run together
   - **Follow TDD approach**: Execute test tasks before their corresponding implementation tasks
   - **File-based coordination**: Tasks affecting the same files must run sequentially
   - **Validation checkpoints**: Verify each phase completion before proceeding

7. Implementation execution rules:
   - **Setup first**: Initialize project structure, dependencies, configuration
   - **Tests before code**: If you need to write tests for contracts, entities, and integration scenarios
   - **Core development**: Implement models, services, CLI commands, endpoints
   - **Integration work**: Database connections, middleware, logging, external services
   - **Polish and validation**: Unit tests, performance optimization, documentation

8. Progress tracking and error handling:
   - Report progress after each completed task
   - Halt execution if any non-parallel task fails
   - For parallel tasks [P], continue with successful tasks, report failed ones
   - Provide clear error messages with context for debugging
   - Suggest next steps if implementation cannot proceed
   - **IMPORTANT** For completed tasks, make sure to mark the task off as [X] in the tasks file.

9. Completion validation:
   - Verify all required tasks are completed
   - Check that implemented features match the original specification
   - Validate that tests pass and coverage meets requirements
   - Confirm the implementation follows the technical plan
   - Report final status with summary of completed work

Note: This command assumes a complete task breakdown exists in tasks.md. If tasks are incomplete or missing, suggest running `/humaninloop:tasks` first to regenerate the task list.
