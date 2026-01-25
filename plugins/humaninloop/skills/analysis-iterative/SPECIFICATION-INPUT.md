# Specification Input Mode

Alias for `mode:depth-quick,output-enrichment`. Use when invoked by `/humaninloop:specify` to enrich sparse feature descriptions.

## Context

The specify command detects when user input lacks the **Who + Problem + Value** triad and invokes this skill to fill gaps before proceeding to the Requirements Analyst.

## Invocation

```
Skill(
  skill: "analysis-iterative",
  args: "mode:specification-input missing:[who,problem,value] original:\"<user input>\""
)
```

## Configuration

| Setting | Value |
|---------|-------|
| Depth | 2-5 questions (triad gaps + key decisions) |
| Output | `output-enrichment` format |

## Question Agenda

Follow standard iterative questioning pattern: ONE question at a time with options and recommendations.

### Phase 1: Fill Triad Gaps (Conditional)

Only ask questions for missing elements (parsed from `missing:[]` arg).

#### WHO Question (if `who` in missing)

```
**Question**: Who is the primary user of this feature?

**Options:**
- **A) End user / Customer**: External user of the product
- **B) Internal user / Admin**: Team member or administrator
- **C) Developer / API consumer**: Technical user integrating with system

**My Recommendation**: [Based on context clues in original input]
```

#### PROBLEM Question (if `problem` in missing)

```
Based on [actor choice], let's clarify the pain point.

**Question**: What problem does this solve for {actor}?

**Options:**
- **A) Efficiency**: Task takes too long or requires too many steps
- **B) Capability**: Something they can't do today at all
- **C) Reliability**: Current solution is error-prone or fails

**My Recommendation**: [Based on context clues]
```

#### VALUE Question (if `value` in missing)

```
Now that we know {actor} faces {problem}, let's clarify the value.

**Question**: Why does solving this matter?

**Options:**
- **A) Revenue impact**: Enables new revenue or reduces churn
- **B) Efficiency gains**: Saves time or reduces costs
- **C) User satisfaction**: Improves experience or removes friction

**My Recommendation**: [Based on what the problem implies]
```

### Phase 2: Key Decisions (Always)

These questions are ALWAYS asked, regardless of what was detected in input.

#### SCOPE Question

```
Let's define boundaries to keep this focused.

**Question**: What's explicitly OUT of scope for v1 of this feature?

**Options:**
- **A) Advanced features**: Keep to core happy path, defer power-user features
- **B) Edge cases**: Handle main flow only, document edge cases for later
- **C) Integrations**: Skip third-party integrations initially

**My Recommendation**: [Based on feature complexity and MVP scope]
```

#### SUCCESS Question

```
Finally, let's define how we'll know this works.

**Question**: How will you know this feature is working correctly?

**Options:**
- **A) Metric improvement**: Measurable KPI change (conversion, time, errors)
- **B) User feedback**: Qualitative satisfaction signals
- **C) Capability validation**: Users can complete the new workflow end-to-end

**My Recommendation**: [Based on the problem being solved]
```

## Output

After questions answered, generate enriched description using `output-enrichment` template from [OUTPUT-TEMPLATES.md](OUTPUT-TEMPLATES.md).

## Differences from Standard Mode

| Aspect | Standard Mode | Specification-Input Mode |
|--------|---------------|--------------------------|
| Questions | Adaptive or configured depth | Two-phase: Triad gaps (conditional) + Key decisions (always) |
| Depth | 2-10+ depending on mode | 2-5 questions depending on gaps |
| Output | Configured format | Always enrichment format |
| Purpose | Explore any topic | Enrich feature descriptions for /specify |
| Question agenda | Dynamic based on topic | Fixed agenda based on triad |

## Anti-Shortcuts

Do NOT rationalize skipping questions:

| Excuse | Reality |
|--------|---------|
| "Actor is obvious from context" | Obvious to you =/= explicit for spec. Ask anyway. |
| "Problem is stated in the request" | Stated =/= validated. Confirm with options. |
| "This is a small feature" | Small features grow. Scope it properly now. |
| "User seems clear on what they want" | Clear desire =/= clear requirement. Enrich anyway. |
