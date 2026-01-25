---
name: analysis-iterative
description: Use when user says "brainstorm", "deep analysis", "let's think through", "analyze this with me", or "help me think through". Also use for specification enrichment when feature descriptions lack clarity. Supports configurable depth (quick, thorough, adaptive) and output formats (synthesis, bullets, matrix, actions).
---

# Iterative Analysis

## Overview

Guide deep thinking through progressive, one-at-a-time questioning. Each question builds on previous answers with options and recommendations. Challenge disagreement to strengthen thinking.

**Violating the letter of the rules is violating the spirit of the rules.**

## When to Use

- User wants to think through a problem collaboratively
- Feature description lacks Who/Problem/Value clarity
- Decision requires exploring trade-offs
- Topic benefits from structured exploration with options

## When NOT to Use

- User needs quick factual answer (no exploration needed)
- Decision is already made (use validation, not exploration)
- User explicitly wants to skip discussion

## Depth Modes

Specify depth in invocation: `mode:depth-[quick|thorough|adaptive]`

| Mode | Questions | Use When |
|------|-----------|----------|
| `depth-quick` | 2-3 | Time-boxed decisions, clear scope |
| `depth-thorough` | 6-10 | Complex decisions, many stakeholders |
| `depth-adaptive` | Until natural conclusion | Open exploration (default) |

**Default:** `depth-adaptive`

### Depth Signals

For adaptive mode, wrap up when:
- Answers become confirmatory rather than exploratory
- Key trade-offs are explicitly addressed
- User confidence in direction increases
- User signals completion ("I think that covers it")

## Output Modes

Specify output in invocation: `mode:output-[synthesis|bullets|matrix|actions|enrichment]`

| Mode | Format | Use When |
|------|--------|----------|
| `output-synthesis` | Full document with decision trail | Complex analysis needing audit trail |
| `output-bullets` | Bullet point summary | Quick reference, sharing with others |
| `output-matrix` | Decision matrix table | Comparing multiple options |
| `output-actions` | Numbered action items only | Implementation focus |
| `output-enrichment` | Who/Problem/Value structure | Feature specification input |

**Default:** `output-synthesis`

See [OUTPUT-TEMPLATES.md](OUTPUT-TEMPLATES.md) for all output templates.

## Core Process

### Phase 1: Opening

Acknowledge topic and set expectations:

1. State the topic being explored
2. Announce configuration (depth mode, output format)
3. Explain that each question includes options with a recommendation
4. Invite disagreement - indicate challenges will strengthen thinking
5. Begin first question

### Phase 2: Iterative Questioning

**Core Rules:**
1. ONE question per turn - never multiple questions
2. Always provide 2-3 concrete options
3. Always state recommendation with reasoning
4. After each answer, show how it affects analysis before next question

**No exceptions:**
- Not for "user seems to already know the answer"
- Not for "obvious answer doesn't need options"
- Not for "quick mode means less structure"
- Not even if user says "just give me the answer"

**Question Format:**

```
[Brief context showing current understanding]

**Question [N]**: [Clear, focused question]

**Options:**
- **A) [Option]**: [Implications]
- **B) [Option]**: [Implications]
- **C) [Option]**: [Implications]

**My Recommendation**: Option [X] because [reasoning based on what we know]
```

**After receiving answer:**

```
[Acknowledge choice]

[Show how this shapes analysis - what it opens, what it rules out]

[Transition to next question]
```

### Phase 3: Handling Disagreement

When user picks differently than recommended:

1. **Explore reasoning**: Ask what draws them to that direction
2. **Present counterarguments**: Share concerns respectfully but directly
3. **If they maintain choice**: Accept it, integrate it, proceed

**Challenge template:**

```
Interesting - you're leaning toward [their choice] over [your recommendation].

Before we lock that in, let me push back: [specific concern or trade-off
they may not have considered].

What's your thinking on that?
```

**After confirmed disagreement:**

```
Fair enough. That's a deliberate choice with eyes open to the trade-offs.
Let me factor that in...

[Show how this affects analysis]
```

### Phase 4: Conclusion

When depth target reached or user signals completion:

```
I think we've covered the key decision points. Let me synthesize
what we've worked through...
```

Generate output using the configured format template.

## Red Flags - STOP

If noticing any of these thoughts, STOP immediately:

- "User seems impatient, I'll skip the recommendation"
- "This option is obviously correct, no need to present alternatives"
- "I'll ask multiple questions to save time"
- "They disagreed but I won't push back - it's their choice"
- "The depth mode says quick, so I won't challenge their answers"

**All of these mean:** Process is being shortcut. Return to proper questioning format.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "User seems to know what they want" | Options reveal blind spots. Present them anyway. |
| "Pushing back feels confrontational" | Challenge strengthens thinking. Discomfort is productive. |
| "Multiple questions would be more efficient" | One question builds on the last. Efficiency destroys depth. |
| "Quick mode means less rigor" | Quick means fewer questions, not weaker questions. |
| "They've already decided" | Decided =/= validated. Questioning tests conviction. |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Asking multiple questions per turn | Split into separate turns with options each |
| Options without recommendation | Always state which option and why |
| Accepting disagreement without challenge | Push back once before accepting |
| Questions don't build on answers | Reference previous choice in next question context |
| Rushing to conclusion | Check depth signals before synthesizing |
| Skipping output format | Always generate structured output at end |

## Mode Combinations

Combine depth and output modes in invocation:

```
mode:depth-quick,output-bullets
mode:depth-thorough,output-matrix
mode:depth-adaptive,output-synthesis
mode:specification-input  # Alias for depth-quick,output-enrichment
```

### Specification Input Mode

When invoked with `mode:specification-input`, use the question agenda in [SPECIFICATION-INPUT.md](SPECIFICATION-INPUT.md) with:
- Depth: 2-5 questions (triad gaps + key decisions)
- Output: Enrichment format

## Examples

### Good Question

```
Based on your focus on rapid iteration, we need to decide on feedback timing.

**Question 3**: How quickly do users need to see impact of changes?

**Options:**
- **A) Real-time (<100ms)**: Instant reflection. Highest complexity.
- **B) Near-real-time (1-3s)**: Brief delay. Simpler, still responsive.
- **C) On-demand refresh**: User triggers. Simplest, breaks flow.

**My Recommendation**: Option B because your team is small and time-to-market
matters. Real-time adds complexity for marginal UX gain. Upgrade later.
```

### Good Disagreement Handling

```
You're leaning toward real-time over my near-real-time recommendation.

I want to make sure you've weighed this: real-time means WebSocket
infrastructure, reconnection logic, and conflict resolution - easily
2-3x implementation work. Your team of three would be stretched thin.

Is instant feedback worth that trade-off, or is there a specific user
flow where real-time is non-negotiable?
```

---

## References

- [OUTPUT-TEMPLATES.md](OUTPUT-TEMPLATES.md) - All output format templates
- [SPECIFICATION-INPUT.md](SPECIFICATION-INPUT.md) - Question agenda for enrichment mode
