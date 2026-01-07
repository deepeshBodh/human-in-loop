---
description: Create or update the project constitution using the Principal Architect agent.
---

## User Input

```text
$ARGUMENTS
```

## Workflow

This supervisor follows a multi-phase architecture for brownfield-aware constitution setup.

### Phase 0: Brownfield Detection

1. **Ensure directory exists**
   ```bash
   mkdir -p .humaninloop/memory
   ```

2. **Run detection script**
   ```bash
   bash ${CLAUDE_PLUGIN_ROOT}/skills/analysis-codebase/scripts/detect-stack.sh .
   ```

3. **Count source files** (heuristic for brownfield detection)
   ```bash
   find . -type f \( -name "*.ts" -o -name "*.js" -o -name "*.py" -o -name "*.go" -o -name "*.java" -o -name "*.rb" -o -name "*.rs" \) \
     -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/vendor/*" -not -path "*/__pycache__/*" | wc -l
   ```

4. **Check for existing constitution**
   ```bash
   cat .humaninloop/memory/constitution.md 2>/dev/null
   ```
   - If exists: `constitution_mode: amend`
   - If not: `constitution_mode: create`

5. **Determine brownfield status**
   - If file count > 5 AND detect-stack finds framework/ORM → Suggest brownfield mode
   - Otherwise → Default to greenfield mode

6. **Present detection result to user**:
   ```
   AskUserQuestion(
     questions: [{
       question: "Found [N] source files with [framework/language] detected.\n\nBrownfield analysis will:\n- Inventory existing patterns and entities\n- Assess essential floor coverage (Security, Testing, Error Handling, Observability)\n- Produce codebase-analysis.md alongside constitution.md\n- Generate evolution-roadmap.md with gap cards\n\nHow would you like to proceed?",
       header: "Setup Mode",
       options: [
         {label: "Brownfield - Full analysis", description: "Analyze codebase, create 3 artefacts (Recommended for existing codebases)"},
         {label: "Greenfield - Constitution only", description: "Create constitution with defaults, skip analysis"},
         {label: "Amend existing", description: "Update existing constitution without re-analysis"}
       ],
       multiSelect: false
     }]
   )
   ```

7. **Route based on answer**:
   - "Brownfield" → Continue to Phase 1
   - "Greenfield" → Skip to Phase 3 (greenfield mode)
   - "Amend" → Skip to Phase 3 (amend mode)

---

### Phase 1: Brownfield Analysis (Brownfield Mode Only)

1. **Generate context filename with timestamp**
   ```bash
   CONTEXT_FILE=".humaninloop/memory/setup-context-$(date +%Y%m%d-%H%M%S).md"
   ```

2. **Create context artifact** for analysis phase

   Write to `$CONTEXT_FILE`:

   ```markdown
   ---
   type: brownfield-setup
   mode: brownfield
   phase: analysis
   constitution_mode: [create|amend]
   iteration: 1
   created: [ISO date]
   updated: [ISO date]
   ---

   # Setup Context

   ## User Input

   [User's request or "Set up project governance"]

   ## Detection Results

   [Output from detect-stack.sh - JSON or summary]

   ## Project Context

   | Aspect | Value |
   |--------|-------|
   | Project Name | [detected] |
   | Primary Language | [detected] |
   | Framework | [detected] |
   | Source Files | [count] |
   | CLAUDE.md Exists | [Yes/No] |

   ## Existing Constitution

   [If amending: "Existing constitution at .humaninloop/memory/constitution.md"]
   [If creating: "None - creating new constitution"]

   ## Supervisor Instructions

   **Phase**: Brownfield Analysis

   Perform comprehensive codebase analysis using `analysis-codebase` skill (mode: setup-brownfield).

   **Write**:
   - Analysis: `.humaninloop/memory/codebase-analysis.md`
   - Report: `.humaninloop/memory/architect-report.md`

   **Report format**:
   - ## Summary - Key findings (2-3 sentences)
   - ## Essential Floor Status - Table with Security/Testing/Error Handling/Observability
   - ## Entities Found - Count and highlights
   - ## Architecture - Pattern identified
   - ## Clarifications Needed - Questions for user (if any)

   ## Clarification Log

   [Empty on first iteration]
   ```

3. **Invoke Principal Architect**
   ```
   Task(
     subagent_type: "humaninloop:principal-architect",
     prompt: "
       Work on the brownfield analysis phase.

       Read the context at: $CONTEXT_FILE

       The context file contains all instructions and where to write output.
     ",
     description: "Analyze existing codebase"
   )
   ```

4. **Verify output exists**
   ```bash
   test -f .humaninloop/memory/codebase-analysis.md && echo "Analysis complete"
   test -f .humaninloop/memory/architect-report.md && echo "Report complete"
   ```

---

### Phase 2: Analysis Checkpoint (Brownfield Mode Only)

1. **Read architect report**
   ```bash
   cat .humaninloop/memory/architect-report.md
   ```

2. **Present analysis summary to user**
   ```
   AskUserQuestion(
     questions: [{
       question: "[Summary from architect-report.md]\n\n**Essential Floor Status:**\n[Table from report]\n\n**Architecture**: [Pattern from report]\n**Entities Found**: [Count from report]\n\nIs this analysis accurate?",
       header: "Analysis Review",
       options: [
         {label: "Confirm - Proceed to constitution", description: "Analysis is accurate, continue"},
         {label: "Edit - Provide corrections", description: "I'll add corrections before proceeding"},
         {label: "Reject - Start over", description: "Analysis is wrong, abort brownfield mode"}
       ],
       multiSelect: false
     }]
   )
   ```

3. **Route based on answer**:

   **If "Confirm"**:
   - Proceed to Phase 3

   **If "Edit"**:
   - Collect user corrections
   - Append to `$CONTEXT_FILE`'s `## Clarification Log`:
     ```markdown
     ### Iteration N - User Corrections
     [User's corrections and clarifications]
     ```
   - Update `$CONTEXT_FILE`'s `## Supervisor Instructions`:
     ```markdown
     User provided corrections to the analysis (see Clarification Log).
     Update codebase-analysis.md incorporating their feedback.
     ```
   - Increment `iteration` in frontmatter
   - **Loop back to Phase 1 step 3** (re-invoke agent)

   **If "Reject"**:
   - Ask user: "Would you like to continue with greenfield mode instead?"
   - If yes → Skip to Phase 3 (greenfield mode)
   - If no → Abort workflow

---

### Phase 3: Constitution Generation

1. **Update context for constitution phase**

   Update `$CONTEXT_FILE` frontmatter:
   ```yaml
   phase: constitution
   updated: [ISO date]
   ```

   Update `## Supervisor Instructions`:

   **For Brownfield Mode**:
   ```markdown
   **Phase**: Constitution (Brownfield)

   Create project constitution informed by codebase analysis.

   **Read**:
   - Codebase analysis: `.humaninloop/memory/codebase-analysis.md`

   **Requirements**:
   - Essential floor principles MUST be included (Security, Testing, Error Handling, Observability)
   - Emergent ceiling from codebase analysis (codify existing good patterns)
   - Each principle: Statement, Enforcement, Testability, Rationale
   - Use RFC 2119 keywords (MUST, SHOULD, MAY)

   **CRITICAL - Populate from Analysis**:
   - Technology Stack: Use ACTUAL tools/versions from codebase-analysis.md, NOT placeholders
   - Quality Gates: Use ACTUAL commands from codebase-analysis.md (e.g., if analysis found "pytest", write `pytest --cov`, NOT `[TEST_COMMAND]`)
   - Coverage thresholds: Use numeric values from analysis OR sensible defaults (warning <80%, blocking <60%)
   - Security scanning: Name specific tools found (e.g., "Trivy + Snyk") NOT `[SECURITY_COMMAND]`
   - Governance Approvers: Check for CODEOWNERS file; if exists, reference it (e.g., "as defined in CODEOWNERS"); otherwise use team/role from analysis
   - If analysis doesn't specify a tool, use industry-standard defaults for the detected language/framework

   **Write**:
   - Constitution: `.humaninloop/memory/constitution.md`
   - Report: `.humaninloop/memory/architect-report.md`

   **Report format**:
   - ## What I Created - Constitution version, principle count
   - ## Essential Floor Principles - List the 4 with status
   - ## Emergent Ceiling Principles - List principles from codebase patterns
   - ## CLAUDE.md Sync Status - What was synced
   - ## Clarifications Needed - Questions (if any)
   - ## Assumptions Made - Decisions made when ambiguous
   ```

   **For Greenfield Mode**:
   ```markdown
   **Phase**: Constitution (Greenfield)

   Create project constitution with opinionated defaults.

   **Requirements**:
   - Essential floor principles with industry-standard defaults
   - Each principle: Statement, Enforcement, Testability, Rationale
   - Use RFC 2119 keywords (MUST, SHOULD, MAY)

   **CRITICAL - No Placeholders**:
   - Technology Stack: Use detected language/framework from Phase 0, or ask user
   - Quality Gates: Use concrete commands appropriate for the detected stack (e.g., `npm test`, `pytest`, `dotnet test`)
   - Coverage thresholds: Use numeric defaults (warning <80%, blocking <60%)
   - Security scanning: Recommend appropriate tools for the stack (e.g., npm audit, pip-audit, Trivy)
   - NEVER write `[PLACEHOLDER]` syntax - always use actual tool names or sensible defaults

   **Write**:
   - Constitution: `.humaninloop/memory/constitution.md`
   - Report: `.humaninloop/memory/architect-report.md`

   **Report format**:
   - ## What I Created - Constitution version, principle count
   - ## Essential Floor Principles - List the 4
   - ## CLAUDE.md Sync Status - What was synced
   - ## Clarifications Needed - Questions (if any)
   - ## Assumptions Made - Decisions made when ambiguous
   ```

   **For Amend Mode**:
   ```markdown
   **Phase**: Constitution (Amend)

   Update existing constitution based on user request.

   **Read**:
   - Existing constitution: `.humaninloop/memory/constitution.md`

   **Requirements**:
   - Preserve existing principles unless explicitly changing
   - Update version per semantic versioning
   - Each changed principle: Statement, Enforcement, Testability, Rationale

   **Write**:
   - Constitution: `.humaninloop/memory/constitution.md`
   - Report: `.humaninloop/memory/architect-report.md`

   **Report format**:
   - ## What I Changed - Summary of amendments
   - ## Version Update - Old → New version with rationale
   - ## CLAUDE.md Sync Status - What was synced
   - ## Clarifications Needed - Questions (if any)
   ```

2. **Invoke Principal Architect**
   ```
   Task(
     subagent_type: "humaninloop:principal-architect",
     prompt: "
       Work on the constitution phase.

       Read the context at: $CONTEXT_FILE

       The context file contains all instructions and where to write output.
     ",
     description: "Create project constitution"
   )
   ```

3. **Parse agent output and handle clarifications**

   **If `## Clarifications Needed` has questions:**
   1. Present questions to user
   2. Collect answers
   3. Append to `$CONTEXT_FILE`'s `## Clarification Log`:
      ```markdown
      ### Constitution Round N - Agent Questions
      [Questions from agent output]

      ### Constitution Round N - User Answers
      [User's responses]
      ```
   4. Update `$CONTEXT_FILE`'s `## Supervisor Instructions`:
      ```markdown
      User answered your questions (see Clarification Log).
      Finalize the constitution incorporating their answers.
      ```
   5. Increment `iteration` in frontmatter
   6. **Loop back to step 2** (re-invoke agent)

   **If no clarifications (or max 3 iterations reached):**
   - **Brownfield mode**: Proceed to Phase 4
   - **Greenfield/Amend mode**: Proceed to Phase 5

---

### Phase 4: Evolution Roadmap (Brownfield Mode Only)

1. **Update context for roadmap phase**

   Update `$CONTEXT_FILE` frontmatter:
   ```yaml
   phase: roadmap
   updated: [ISO date]
   ```

   Update `## Supervisor Instructions`:
   ```markdown
   **Phase**: Evolution Roadmap

   Create gap analysis between current codebase state and constitution requirements.

   **Read**:
   - Codebase analysis: `.humaninloop/memory/codebase-analysis.md`
   - Constitution: `.humaninloop/memory/constitution.md`

   **Gap Identification Process**:
   1. For each Essential Floor category with "partial" or "absent" → Gap card
   2. For each constitution principle → Check codebase compliance → Gap card if non-compliant
   3. Prioritize: P1 (security/blocking), P2 (testing/errors), P3 (observability/nice-to-have)
   4. Identify dependencies between gaps

   **Write**:
   - Roadmap: `.humaninloop/memory/evolution-roadmap.md`
   - Report: `.humaninloop/memory/architect-report.md`

   **Report format**:
   - ## Gap Summary - Total count by priority (P1/P2/P3)
   - ## Critical Gaps (P1) - List with brief description
   - ## Dependency Chain - Key blocking relationships
   ```

2. **Invoke Principal Architect**
   ```
   Task(
     subagent_type: "humaninloop:principal-architect",
     prompt: "
       Work on the evolution roadmap phase.

       Read the context at: $CONTEXT_FILE

       The context file contains all instructions and where to write output.
     ",
     description: "Create evolution roadmap"
   )
   ```

3. **Verify output exists**
   ```bash
   test -f .humaninloop/memory/evolution-roadmap.md && echo "Roadmap complete"
   ```

---

### Phase 5: Finalize

1. **Read final report**
   ```bash
   cat .humaninloop/memory/architect-report.md
   ```

2. **Report to user**

   **For Brownfield Mode**:
   ```markdown
   ## Setup Complete (Brownfield Mode)

   ### Artefacts Created
   - `.humaninloop/memory/codebase-analysis.md` - Codebase inventory and assessment
   - `.humaninloop/memory/constitution.md` - Project governance (v1.0.0)
   - `.humaninloop/memory/evolution-roadmap.md` - Gap cards for improvement

   ### Summary
   - Principles defined: [count from report]
   - Essential floor: [status summary]
   - Gaps identified: [P1 count] critical, [P2 count] important, [P3 count] nice-to-have

   ### Suggested Commit
   ```
   docs: create constitution v1.0.0 with brownfield analysis
   ```

   ### Next Steps
   1. Review the constitution at `.humaninloop/memory/constitution.md`
   2. Review evolution roadmap for prioritized improvements
   3. Address P1 gaps before starting new features
   4. Run `/humaninloop:specify` to start feature specification
   ```

   **For Greenfield Mode**:
   ```markdown
   ## Setup Complete (Greenfield Mode)

   ### Artefacts Created
   - `.humaninloop/memory/constitution.md` - Project governance (v1.0.0)

   ### Summary
   - Principles defined: [count from report]
   - Essential floor: All four categories covered with defaults

   ### Suggested Commit
   ```
   docs: create constitution v1.0.0
   ```

   ### Next Steps
   1. Review the constitution at `.humaninloop/memory/constitution.md`
   2. Run `/humaninloop:specify` to start feature specification
   ```

   **For Amend Mode**:
   ```markdown
   ## Setup Complete (Amendment)

   ### Artefacts Updated
   - `.humaninloop/memory/constitution.md` - Updated to [new version]

   ### Summary
   - [Changes summary from report]

   ### Suggested Commit
   ```
   docs: update constitution to v[X.Y.Z]
   ```

   ### Next Steps
   1. Review the updated constitution
   2. Ensure CLAUDE.md is synchronized (if applicable)
   ```

3. **Cleanup prompt**
   ```
   AskUserQuestion(
     questions: [{
       question: "Would you like to delete the context file used during this setup?\n\nFile: $CONTEXT_FILE",
       header: "Cleanup",
       options: [
         {label: "Yes - Delete context file", description: "Remove temporary setup context"},
         {label: "No - Keep for reference", description: "Retain for debugging or review"}
       ],
       multiSelect: false
     }]
   )
   ```
   - If yes: `rm $CONTEXT_FILE`
   - If no: Inform user the file is retained

---

## State Recovery

If workflow is interrupted, detect resume point from context file:

| Phase | Status Indicator | Resume Point |
|-------|-----------------|--------------|
| `analysis` | `phase: analysis` in context | Phase 1 step 3 |
| `analysis` | `codebase-analysis.md` exists | Phase 2 (checkpoint) |
| `constitution` | `phase: constitution` in context | Phase 3 step 2 |
| `constitution` | `constitution.md` exists + brownfield | Phase 4 |
| `roadmap` | `phase: roadmap` in context | Phase 4 step 2 |
| `completed` | All 3 files exist (brownfield) | Phase 5 (report) |
| `completed` | Constitution exists (greenfield) | Phase 5 (report) |

---

## Supervisor Behaviors

- **Owns the loop**: Decides when to iterate vs. finalize
- **Modifies context**: Updates `$CONTEXT_FILE` instructions and appends to clarification log
- **Presents checkpoints**: User reviews analysis before constitution generation
- **Injects context**: Can add sections to `$CONTEXT_FILE` if needed mid-loop
- **Max iterations**: Limit to 3 rounds per phase to prevent infinite loops
- **Mode awareness**: Tracks brownfield vs greenfield throughout workflow
