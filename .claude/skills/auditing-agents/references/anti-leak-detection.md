# Anti-Leak Detection Patterns

Detailed detection guidance for the five prohibited coupling patterns in agent bodies. Each pattern includes keywords to search for, detection heuristics, and compliant alternatives.

## Leak 1: Phase Branching

Agent bodies MUST NOT contain conditional behavior based on workflow phases.

**Keywords to search for:**
- "Phase:", "phase ==", "if phase"
- "research phase", "data model phase", "planning phase"
- Section headers named after workflow phases

**Detection pattern:**
- Phase-specific instructions with different behaviors per phase
- Conditional logic keyed on phase names
- "Phase Behaviors" sections with sub-sections per phase

**Example violation:**
```markdown
## Phase Behaviors

### Phase: Research
**Goal**: Resolve all technical unknowns.
**Produce**: research.md

### Phase: Data Model
**Goal**: Extract entities and relationships.
**Produce**: data-model.md
```

**Compliant alternative:**
```markdown
## Skills Available
- **patterns-technical-decisions**: Evaluate options, document decisions
- **patterns-entity-modeling**: Extract entities, define relationships

Use the appropriate skill based on the task given in your prompt.
```

---

## Leak 2: Artifact Path Assumptions

Agent bodies MUST NOT hardcode output file paths or directory structures.

**Keywords to search for:**
- `.workflow/`, `spec.md`, `research.md`, `data-model.md`, `tasks.md`
- Specific directory paths like `.humaninloop/memory/`
- Any hardcoded file extension with a specific name

**Detection pattern:**
- "Write to [specific path]"
- "Read from [specific path]"
- "After producing each artifact, write a report to .workflow/planner-report.md"
- "Read the cached codebase analysis from .humaninloop/memory/codebase-analysis.md"

**Compliant alternative:**
- "Write to the location specified in your instructions"
- "Read any context files referenced in your instructions"
- "Write outputs to the locations specified in your instructions"

---

## Leak 3: Sibling Agent Awareness

Agent bodies MUST NOT reference other specific agents or assume awareness of who runs before or after.

**Keywords to search for:**
- Names of other agents: "Devil's Advocate", "requirements analyst", "plan architect", "testing agent"
- "re-invoke [agent-name]"
- "Ready for [agent-name] review"

**Detection pattern:**
- Direct references to named agents
- Assumptions about which agent runs next
- Handoff instructions naming specific agents

**Compliant alternative:**
- "Ready for review" (not "Ready for Devil's Advocate review")
- "Flag issues for the reviewer" (not "Flag issues for the requirements analyst")
- "Available for further review" (not "Re-invoke responsible archetype")

---

## Leak 4: Workflow File Schema Knowledge

Agent bodies MUST NOT define or assume specific context file schemas.

**Keywords to search for:**
- "`phase`:", "`supervisor_instructions`:", "`clarification_log`:"
- "Your context file contains:"
- Field definitions for workflow management files

**Detection pattern:**
- "Your context file contains:" followed by field definitions
- Parsing instructions for specific schema fields
- Enumeration of valid field values (e.g., "research/datamodel/contracts")

**Compliant alternative:**
- "Read your instructions from the prompt or any context files referenced in your prompt"
- No assumption about specific field names or structures

---

## Leak 5: Sequencing Knowledge

Agent bodies MUST NOT encode knowledge about workflow execution order.

**Keywords to search for:**
- "After [phase/step]", "Previous artifacts", "from phase 1"
- "Begin [phase] after [condition]"
- "Check [artifact] from [earlier step]"
- "Once [prior agent/step] completes"

**Detection pattern:**
- Temporal ordering between workflow steps
- References to artifacts produced by earlier phases
- Assumptions about what has already been completed

**Compliant alternative:**
- "Work with whatever artifacts are referenced in your instructions"
- No assumptions about prior execution state

---

## The Reusability Test

After checking all five patterns individually, apply the holistic reusability test as a final gate:

> *Could this agent be dropped into a completely different workflow -- with different phases, different file paths, different sibling agents -- and still function correctly based solely on its persona and skills?*

If the answer is **no**, the agent has coupling leaks that MUST be resolved before shipping.

**Where leaked content belongs:**

| Leaked Content | Correct Location |
|----------------|-----------------|
| Phase branching logic | Skill |
| Artifact path templates | Supervisor prompt or skill |
| Sibling agent references | Supervisor orchestration logic |
| Context file schemas | Supervisor (creates the context) |
| Sequencing knowledge | Supervisor orchestration logic |
| Report format templates | Skill |
