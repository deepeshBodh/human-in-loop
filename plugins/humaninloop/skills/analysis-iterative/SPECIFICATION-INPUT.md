# Specification Input Enrichment Mode

Use this mode when invoked by `/humaninloop:specify` to enrich sparse feature descriptions.

## Context

The specify command detects when user input lacks the **Who + Problem + Value** triad and invokes this skill to fill gaps before proceeding to the Requirements Analyst.

## Invocation

```
Skill(
  skill: "analysis-iterative",
  args: "mode:specification-input missing:[who,problem,value] original:\"<user input>\""
)
```

## Question Agenda

Follow the standard iterative questioning pattern: ONE question at a time with options and recommendations.

### Phase 1: Fill Triad Gaps (conditional)

Only ask questions for missing elements (parsed from `missing:[]` arg).

#### 1. WHO Question (if `who` in missing)

```
**Question**: Who is the primary user of this feature?

**Options:**
- **A) End user / Customer**: External user of the product
- **B) Internal user / Admin**: Team member or administrator
- **C) Developer / API consumer**: Technical user integrating with the system

**My Recommendation**: [Based on context clues in original input]
```

#### 2. PROBLEM Question (if `problem` in missing)

```
Based on [actor choice], let's clarify the pain point.

**Question**: What problem does this solve for {actor}?

**Options:**
- **A) Efficiency**: Task takes too long or requires too many steps
- **B) Capability**: Something they can't do today at all
- **C) Reliability**: Current solution is error-prone or fails

**My Recommendation**: [Based on context clues]
```

#### 3. VALUE Question (if `value` in missing)

```
Now that we know {actor} faces {problem}, let's clarify the value.

**Question**: Why does solving this matter?

**Options:**
- **A) Revenue impact**: Enables new revenue or reduces churn
- **B) Efficiency gains**: Saves time or reduces costs
- **C) User satisfaction**: Improves experience or removes friction

**My Recommendation**: [Based on what the problem implies]
```

### Phase 2: Key Decisions (always ask)

These questions are ALWAYS asked, regardless of what was detected in the input.

#### 4. SCOPE Question (always)

```
Let's define boundaries to keep this focused.

**Question**: What's explicitly OUT of scope for v1 of this feature?

**Options:**
- **A) Advanced features**: Keep to core happy path, defer power-user features
- **B) Edge cases**: Handle main flow only, document edge cases for later
- **C) Integrations**: Skip third-party integrations initially

**My Recommendation**: [Based on feature complexity and what would be MVP]
```

#### 5. SUCCESS Question (always)

```
Finally, let's define how we'll know this works.

**Question**: How will you know this feature is working correctly?

**Options:**
- **A) Metric improvement**: Measurable KPI change (conversion, time, errors)
- **B) User feedback**: Qualitative satisfaction signals
- **C) Capability validation**: Users can complete the new workflow end-to-end

**My Recommendation**: [Based on the problem being solved]
```

## Output Format

After questions are answered, generate the enriched description using [ENRICHMENT.md](ENRICHMENT.md) template.

## Key Differences from Standard Mode

| Aspect | Standard Mode | Specification-Input Mode |
|--------|---------------|--------------------------|
| Questions | Adaptive, open-ended | Two-phase: Triad gaps (conditional) + Key decisions (always) |
| Depth | Continue until natural conclusion | 2-5 questions depending on gaps |
| Output | SYNTHESIS.md format | ENRICHMENT.md format |
| Purpose | Explore any topic | Enrich feature descriptions for /specify |
