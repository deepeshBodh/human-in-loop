---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

### Empty Input Check

If `$ARGUMENTS` is empty (blank string with no content), use AskUserQuestion to handle a known Claude Code bug where inputs containing `@` file references don't reach plugin commands:

```
AskUserQuestion(
  questions: [{
    question: "⚠️ Known Issue: Input may have been lost\n\nClaude Code has a bug where inputs containing @ file references don't reach plugin commands.\n\nWould you like to re-enter your input?",
    header: "Input",
    options: [
      {label: "Re-enter input", description: "I'll type my input in the terminal"},
      {label: "Continue without input", description: "Proceed with no input provided"}
    ],
    multiSelect: false
  }]
)
```

- If user selects "Re-enter input" → wait for user to type their input in the terminal, then use that as the effective `$ARGUMENTS`
- If user selects "Continue without input" → proceed with empty input (existing behavior)

## Outline

1. Run `${CLAUDE_PLUGIN_ROOT}/scripts/check-prerequisites.sh --json --require-tasks --include-tasks` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

1.5. **Entry Gate: Verify Tasks Workflow Complete**

   Check if the tasks workflow completed successfully before proceeding:

   **1.5.1 Check for tasks-context.md**:
   ```bash
   test -f {FEATURE_DIR}/.workflow/tasks-context.md
   ```

   **1.5.2 If found**: Read frontmatter and check `status` field

   **1.5.3 Route based on status**:

   | Status | Action |
   |--------|--------|
   | `completed` | Proceed to step 2 |
   | `awaiting-architect` / `awaiting-advocate` / `awaiting-user` | Tasks workflow incomplete - prompt user |
   | Not found | No workflow context - proceed with warning |

   **If status is not `completed`**:
   ```
   AskUserQuestion(
     questions: [{
       question: "Tasks workflow not complete (status: {status}). Implementation requires completed tasks.\n\nPhase: {phase}, Iteration: {iteration}",
       header: "Entry Gate",
       options: [
         {label: "Complete tasks first", description: "Return to /humaninloop:tasks to finish"},
         {label: "Proceed anyway", description: "Implement with current tasks.md (may be incomplete)"},
         {label: "Abort", description: "Cancel implementation"}
       ],
       multiSelect: false
     }]
   )
   ```

   **1.5.4 Optional context from workflow artifacts**:
   - If `{FEATURE_DIR}/.workflow/planner-report.md` exists: Note any assumptions made by Task Architect
   - If `{FEATURE_DIR}/.workflow/advocate-report.md` exists: Note any known gaps/limitations flagged

2. Load and analyze the implementation context:
   - **REQUIRED**: Read tasks.md for the complete task list and execution plan
   - **REQUIRED**: Read plan.md for tech stack, architecture, and file structure
   - **IF EXISTS**: Read task-mapping.md for:
     - Story-to-cycle mapping and coverage verification
     - Cycle dependencies and parallel opportunities
     - Per-cycle deliverables with specific file paths
     - Success criteria and traceability to requirements
     - Risk assessment and mitigation strategies
   - **IF EXISTS**: Read data-model.md for entities and relationships
   - **IF EXISTS**: Read contracts/ for API specifications and test requirements
   - **IF EXISTS**: Read research.md for technical decisions and constraints
   - **IF EXISTS**: Read quickstart.md for integration scenarios

3. **Project Setup Verification**:
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

4. Parse tasks.md structure and extract:

   **4.1 Summary Metrics** (from `## Summary` table):
   - Total cycles, foundation cycles, feature cycles
   - Total tasks count
   - Parallel opportunities (which cycles can run concurrently)

   **4.2 Enrich with task-mapping.md** (if exists):
   - Use `## Cycle Details` for per-cycle success criteria
   - Use `## Dependency Graph` for visual verification of execution order
   - Use `## Risk Assessment` to identify cycles needing extra care
   - Use deliverable tables to verify expected file paths

   **4.3 Foundation Cycles** (from `## Foundation Cycles (Sequential)`):
   - These MUST complete in order (C1 → C2 → C3 → ...)
   - Each cycle has: Stories, Dependencies, Type in metadata block
   - Parse cycle headers: `### Cycle N: Title`

   **4.4 Feature Cycles** (from `## Feature Cycles`):
   - Can begin only after ALL foundation cycles complete
   - Cycles marked `[P]` are parallel-eligible
   - Parse cycle headers: `### Cycle N: Title [P]`
   - Dependencies in metadata show required prior cycles

   **4.5 Task Details**:
   - Task pattern: `- [ ] **T{cycle}.{task}**: Description`
   - File paths in backticks within description
   - Brownfield markers `[EXTEND]` or `[MODIFY]` in task description
   - Multi-line task descriptions with sub-bullets for details
   - Checkpoint at end of each cycle defines done criteria

   **4.6 Quality Gates** (from `## Quality Gates`):
   - Build/lint requirements that apply to all cycles
   - These should be verified after each cycle completes

5. Execute implementation following the task plan:

   **Cycle-based execution rules**:

   **Foundation Cycles (Sequential)**:
   - Execute C1 completely before starting C2, C2 before C3, etc.
   - Within each cycle, execute tasks in order (T1.1 → T1.2 → T1.3 → ...)
   - Each cycle starts with a failing test task (TN.1)
   - Verify cycle checkpoint before proceeding to next cycle

   **Feature Cycles (After Foundation)**:
   - Only begin feature cycles after ALL foundation cycles complete
   - Cycles marked `[P]` can execute in parallel with each other
   - Non-parallel feature cycles respect their Dependencies metadata
   - Within each cycle, execute tasks sequentially (TDD order)

   **TDD Discipline**:
   - Task TN.1 is always "Write failing test" - execute first
   - Subsequent tasks implement code to make tests pass
   - Final task in cycle is typically "Demo and verify"

   **Verification Task Detection and Routing**:

   When encountering a task with verification markers:

   **Detection** (any of these markers):
   - `**TEST:**` - Unified format (preferred)
   - `**TEST:VERIFY**` - Legacy format
   - `**TEST:CONTRACT**` - Legacy format
   - `**HUMAN VERIFICATION**` - Legacy format

   All markers route to testing-agent.

   **Routing to Testing Agent**:
   ```
   Task(
     subagent_type: "humaninloop:testing-agent",
     prompt: "Execute verification task {TASK_ID} from {FEATURE_DIR}/tasks.md. Classify the task (CLI/GUI/SUBJECTIVE), execute Setup/Action/Assert steps, capture evidence, and decide whether to auto-approve or present checkpoint.",
     description: "Execute TEST task"
   )
   ```

   **Handling Testing Agent Response**:

   The testing-agent returns a decision object:
   ```json
   {
     "task_id": "T{N}.{X}",
     "classification": "CLI|GUI|SUBJECTIVE",
     "execution": { "status": "PASS|FAIL|PARTIAL", "pass_rate": "N/M" },
     "decision": {
       "result": "approved|rejected|retry",
       "decided_by": "auto|human",
       "checkpoint_presented": true|false,
       "human_response": "Approve|Reject|Retry"
     }
   }
   ```

   **Route based on `decision`**:

   | `decided_by` | `result` | Action |
   |--------------|----------|--------|
   | `auto` | `approved` | Mark task complete, proceed silently |
   | `human` | `approved` | Mark task complete, proceed |
   | `human` | `rejected` | Stop cycle, report failure |
   | `human` | `retry` | Re-run testing-agent with same task |

   **Note**: Testing-agent owns checkpoint presentation. Do NOT present an additional checkpoint here—the human has already decided (or auto-approval occurred).

   **Checkpoints**:
   - Each cycle ends with a `**Checkpoint**:` statement
   - Verify checkpoint criteria before marking cycle complete
   - Run quality gates (`pnpm lint`, `pnpm build`, tests) after each cycle

6. Implementation execution guidance:

   **Per-Task Execution**:
   - Read full task description including sub-bullets
   - Extract file path from backticks in description
   - For `[EXTEND]` tasks: read existing file, add new code
   - For `[MODIFY]` tasks: read existing file, modify specific sections
   - Mark task complete: change `- [ ]` to `- [x]`
   - **Do NOT run git commands** - leave version control to the user

   **Per-Cycle Completion**:
   - After final task in cycle, verify checkpoint criteria
   - Run quality gates if defined (lint, build, tests)
   - Report cycle completion to user before starting next cycle

   **Error Handling Within Cycles**:
   - If a task fails, stop the cycle and report
   - Do not proceed to next task until current task passes
   - For test tasks (TN.1): failing test is EXPECTED initially
   - For implementation tasks: failing means fix before continuing

7. Progress tracking and error handling:
   - Report progress after each completed task and cycle
   - Halt cycle execution if any task fails (except TN.1 failing tests which are expected)
   - For parallel cycles `[P]`, can run multiple cycles concurrently
   - Provide clear error messages with context for debugging
   - Suggest next steps if implementation cannot proceed
   - **IMPORTANT**: Mark completed tasks as `- [x] **T#.#**:` in tasks.md
   - **IMPORTANT**: Report cycle checkpoint verification before proceeding

8. Completion validation:
   - Verify all cycles are completed (all tasks marked `[x]`)
   - Verify all cycle checkpoints passed
   - Run final quality gates (`pnpm lint`, `pnpm build`, full test suite)
   - Check traceability matrix coverage (all user stories have implementing cycles)
   - Validate constitution alignment (if `## Constitution Alignment` section exists)
   - Report final status:
     ```markdown
     ## Implementation Complete

     **Feature**: {feature_id}

     | Metric | Value |
     |--------|-------|
     | Foundation Cycles | {N}/{N} complete |
     | Feature Cycles | {N}/{N} complete |
     | Total Tasks | {N}/{N} complete |

     ### Quality Gates
     - Lint: ✓ Pass
     - Build: ✓ Pass
     - Tests: ✓ Pass ({N} passing)

     ### Next Steps
     - Review implementation at `{paths}`
     - Deploy or continue with next feature
     ```

Note: This command assumes a complete task breakdown exists in tasks.md. If tasks are incomplete or missing, suggest running `/humaninloop:tasks` first to regenerate the task list.
