# Enrichment Document Template

Use this template when concluding a specification-input enrichment session.

## Template

```markdown
## Enriched Feature Description

**Actor**: [The user/role who needs this feature]
**Problem**: [The pain point or need being addressed]
**Value**: [Why solving this matters]
**Out of Scope**: [Explicit boundaries for v1]
**Success Criteria**: [How we'll know it's working]

### Summary

[Actor] needs this feature because [problem]. This matters because [value]. Success will be measured by [success criteria].

### Original Input

> [Original user input preserved verbatim]
```

## Example

For input: "Add dark mode"

After enrichment questions:

```markdown
## Enriched Feature Description

**Actor**: End users of the application
**Problem**: Eye strain during extended use, especially in low-light environments
**Value**: Improved user satisfaction and increased evening usage
**Out of Scope**: System-wide theme sync, scheduled auto-switching, custom color schemes
**Success Criteria**: User feedback indicating reduced eye fatigue; increased usage during evening hours

### Summary

End users need this feature because they experience eye strain during extended use in low-light environments. This matters because it improves user satisfaction and enables evening usage. Success will be measured by user feedback indicating reduced eye fatigue.

### Original Input

> Add dark mode
```

## Guidelines

1. **Actor**: Be specific about the user role. "Users" is vague; "end users of the mobile app" is better.

2. **Problem**: State the pain point, not the solution. "Need dark mode" is a solution; "eye strain in low light" is the problem.

3. **Value**: Explain why this matters to the business or user. Connect the solution to outcomes.

4. **Out of Scope**: List what's explicitly NOT included in v1. Helps prevent scope creep.

5. **Success Criteria**: Make it observable. "Better UX" is vague; "users report less eye fatigue" is observable.

6. **Summary**: This is what gets passed to the Requirements Analyst. Should be a complete narrative.

7. **Original Input**: Always preserve the original. The analyst may find useful context the enrichment missed.
