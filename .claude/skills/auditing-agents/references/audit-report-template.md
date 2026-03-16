# Agent Audit Report Template

Use this template to produce the final audit report. Fill in every section. Do not omit sections -- mark them "N/A" if not applicable for the agent type.

---

```markdown
# Agent Audit Report: [agent-name]

## Classification
- **Agent Type**: [persona | reviewer | executor]
- **Rationale**: [why this classification was chosen]

## Metrics
- **Body word count**: [N] ([within target | over limit | under target])
- **Description length**: [N] chars ([compliant | over limit])
- **Skills referenced**: [comma-separated list or "none"]
- **Example blocks**: [N] ([compliant | under minimum])

## Anti-Leak Check
- **Phase branching**: [PASS | VIOLATION -- quote evidence]
- **Artifact paths**: [PASS | VIOLATION -- quote evidence]
- **Sibling awareness**: [PASS | VIOLATION -- quote evidence]
- **Schema knowledge**: [PASS | VIOLATION -- quote evidence]
- **Sequencing knowledge**: [PASS | VIOLATION -- quote evidence]
- **Reusability test**: [PASS | FAIL -- explain why]

## Persona Quality Check
- **Writing style**: [second person | VIOLATION -- first/third/imperative]
- **Opening Identity**: [present | missing]
- **Core Identity pattern**: [experiential | generic | missing]
- **Experiences connect to judgments**: [yes | gaps identified -- list them]
- **Rejection/Embrace sections**: [both present | missing: X]
- **Character traits vs procedural rules**: [clean | process leaked -- quote evidence]

## Skill Delegation Check
- **Skills Available section**: [present | missing | N/A (no skills)]
- **Skill invocation guidance**: [present | missing]
- **Process duplication**: [none found | duplicated content identified -- quote evidence]
- **Cross-reference format**: [namespace syntax | file paths used -- quote evidence]

## Type-Specific Check ([type])

### For Reviewer Agents
- **Adversarial calibration**: [present | missing]
- **"What You Hunt For" section**: [present | missing]
- **Severity classification**: [present | missing]

### For Executor Agents
- **Evidence capture rules**: [present | missing]
- **Escalation rules**: [present | missing]
- **Model choice justification**: [justified | not justified | N/A (uses opus)]

### For Persona Agents
- Standard audit only. No additional type-specific checks.

## Audit Results

### Critical Issues ([count])
1. **[ISSUE NAME]**: [description of the violation]
   - **Location**: [line number or section name]
   - **Fix**: [specific remediation action]

### Important Issues ([count])
1. **[ISSUE NAME]**: [description of the issue]
   - **Location**: [line number or section name]
   - **Fix**: [specific remediation action]

### Minor Issues ([count])
1. **[ISSUE NAME]**: [description of the issue]
   - **Suggestion**: [optional improvement]

## Verdict: [PASS | PASS WITH NOTES | NEEDS REVISION | REJECT]

### Required Actions
1. [First priority fix -- most critical]
2. [Second priority fix]
...

### Recommendations
1. [Optional improvement that would strengthen the agent]
...
```

---

## Verdict Decision Rules

| Verdict | Criteria |
|---------|----------|
| **PASS** | Zero Critical issues AND Zero Important issues |
| **PASS WITH NOTES** | Zero Critical issues AND 1-2 Important issues |
| **NEEDS REVISION** | 1-3 Critical issues OR 3+ Important issues |
| **REJECT** | 4+ Critical issues |

## Report Quality Standards

- Every issue MUST include a specific location (line number or section name)
- Every Critical and Important issue MUST include a concrete fix action
- Anti-Leak Check MUST quote the violating text as evidence when a VIOLATION is found
- Process duplication MUST quote the duplicated content as evidence
- The verdict MUST match the issue counts per the decision rules above
- Do not list the same issue in multiple severity categories
