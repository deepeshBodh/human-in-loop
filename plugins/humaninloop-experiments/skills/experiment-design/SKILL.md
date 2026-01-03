---
description: Patterns for designing reproducible experiments that test new workflow patterns, agent architectures, and artifact chains.
trigger_phrases:
  - experiment
  - hypothesis
  - test pattern
  - prototype
  - validate approach
---

# Experiment Design Skill

## When to Apply

Invoke this skill when:
- Designing a new experiment to test a pattern
- Structuring an experimental workflow
- Defining success criteria for an approach
- Creating reproducible test scenarios

## Experiment Design Principles

### 1. Clear Hypothesis

Every experiment needs a testable hypothesis:

```markdown
**Hypothesis**: [Pattern X] will [achieve outcome Y] because [reasoning Z].

Example:
**Hypothesis**: Decoupled agents with artifact chains will reduce agent complexity
by 40% because workflow logic is removed from agent definitions.
```

### 2. Measurable Outcomes

Define what success looks like:

| Metric | Before | Target | How to Measure |
|--------|--------|--------|----------------|
| Agent line count | 200 | 120 | wc -l agent.md |
| Workflow coupling | High | None | Grep for workflow-specific refs |
| Testability | Manual | Automated | Can invoke agent with mock artifact |

### 3. Controlled Variables

Identify what you're changing vs. keeping constant:

**Changing (Independent Variable)**:
- Agent architecture (coupled --> decoupled)

**Constant (Control)**:
- Same feature being specified
- Same skill set available
- Same output quality requirements

### 4. Reproducible Steps

Document steps so anyone can repeat:

```markdown
## Steps to Reproduce

1. Create scaffold artifact at `experiments/test-001/scaffold.md`
2. Populate with test feature description
3. Invoke agent: `Task(subagent_type: "...", prompt: "...")`
4. Measure: [specific metrics]
5. Compare against baseline
```

### 5. Documentation Template

Use this structure for experiment results:

```markdown
# Experiment: [Name]

## Hypothesis
[What you're testing]

## Setup
[How to reproduce]

## Results
| Metric | Expected | Actual | Pass/Fail |
|--------|----------|--------|-----------|

## Observations
[What you noticed during execution]

## Conclusion
[Did hypothesis hold? Why/why not?]

## Recommendations
[Next steps based on findings]
```

## Common Experiment Types

### Pattern Testing

Test a new architectural pattern:
- Define the pattern clearly
- Implement a minimal version
- Compare against current approach
- Measure complexity, clarity, maintainability

### Agent Isolation Testing

Verify an agent works standalone:
- Create mock scaffold artifact
- Invoke agent directly (not through workflow)
- Verify output matches expectations
- Confirm no workflow dependencies

### Artifact Chain Testing

Test the flow through multiple agents:
- Agent A output --> Agent B input
- Verify information preservation
- Check for context loss
- Measure end-to-end quality

### Skill Combination Testing

Test how skills interact:
- Combine multiple skills on same task
- Check for conflicts or redundancy
- Optimize skill triggering
- Document interaction patterns

## Anti-Patterns to Avoid

1. **Vague hypotheses** - "This might work better" is not testable
2. **No baseline** - Can't measure improvement without comparison
3. **Too many variables** - Change one thing at a time
4. **Missing documentation** - If you can't reproduce it, you can't learn from it
5. **Confirmation bias** - Look for evidence that disproves, not just confirms
