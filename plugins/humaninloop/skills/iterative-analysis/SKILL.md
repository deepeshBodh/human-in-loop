---
name: iterative-analysis
description: This skill should be used when the user says "brainstorm", "deep analysis", "let's think through", "analyze this with me", or "help me think through". Provides progressive deep analysis through one-by-one questioning with 2-3 options per question and clear recommendations. Challenges disagreement to strengthen thinking and concludes with a synthesis document.
---

# Iterative Analysis

## Purpose

Guide deep thinking through progressive, one-at-a-time questioning. Each question builds on previous answers, creating a collaborative exploration that concludes with a structured synthesis document.

## Workflow Phases

### Phase 1: Opening

When triggered, acknowledge the topic and set expectations:

```
I'll help you think through [topic] with a series of focused questions.

For each question, I'll present options with my recommendation. Feel free to
disagree—I'll push back to help strengthen your thinking.

Let's begin.
```

Then ask the first question.

### Phase 2: Iterative Questioning

**Core Rules:**
1. ONE question per turn—never multiple questions
2. Always provide 2-3 concrete options
3. Always state your recommendation with reasoning
4. After each answer, briefly show how it affects the analysis before the next question

**Question Format:**

```
[Brief context showing current understanding and how previous answer shaped thinking]

**Question [N]**: [Clear, focused question]

**Options:**
- **A) [Option name]**: [What this means and its implications]
- **B) [Option name]**: [What this means and its implications]
- **C) [Option name]**: [What this means and its implications]

**My Recommendation**: Option [X] because [clear reasoning based on what we know so far]
```

**After receiving an answer:**

```
[Acknowledge the choice]

[Show how this shapes the analysis—what it opens up, what it rules out,
what becomes more important to explore]

[Transition to next question]
```

### Phase 3: Handling Disagreement

When the user picks differently than recommended:

1. **Explore their reasoning**: "What's drawing you to that direction?"
2. **Present counterarguments**: Share your concerns respectfully but directly
3. **If they maintain their choice**: Accept it, integrate it, and proceed

Example:
```
Interesting—you're leaning toward [their choice] over [your recommendation].

Before we lock that in, let me push back: [specific concern or trade-off they
may not have considered].

What's your thinking on that?
```

If they confirm after the challenge, acknowledge and integrate:
```
Fair enough. That's a deliberate choice with eyes open to the trade-offs.
Let me factor that in...

[Show how this affects the analysis]
```

### Phase 4: Conclusion

When core decisions are made or user signals completion, generate the synthesis.

**Transition to synthesis:**
```
I think we've covered the key decision points. Let me synthesize what we've
worked through...
```

Then generate the synthesis document. See [SYNTHESIS.md](SYNTHESIS.md) for the template.

## Adaptive Depth

Do NOT force a fixed number of questions. Continue until:
- Core decisions are made
- The user signals they're ready to conclude
- A natural stopping point is reached

Signs to wrap up:
- Answers are becoming more confirmatory than exploratory
- Key trade-offs have been explicitly addressed
- The user's confidence in direction is increasing

## Examples

### Good Question
```
Based on your focus on rapid iteration, we need to decide on the feedback mechanism.

**Question 3**: How quickly do users need to see the impact of their changes?

**Options:**
- **A) Real-time (< 100ms)**: Changes reflect instantly. Highest technical complexity
  but most responsive feel.
- **B) Near-real-time (1-3 seconds)**: Brief processing delay. Simpler to implement,
  still feels responsive.
- **C) On-demand refresh**: User explicitly triggers update. Simplest, but breaks flow.

**My Recommendation**: Option B because your team is small and time-to-market
matters. Real-time adds significant complexity for marginal UX gain at this stage.
You can always upgrade later.
```

### Good Disagreement Handling
```
You're leaning toward real-time over my near-real-time recommendation.

I want to make sure you've weighed this: real-time means WebSocket infrastructure,
handling reconnection logic, and conflict resolution—easily 2-3x the implementation
work. Your team of three would be stretched thin.

Is the instant feedback worth that trade-off, or is there a specific user flow
where real-time is non-negotiable?
```

### Good Transition After Answer
```
Got it—you're prioritizing simplicity with the on-demand refresh approach.

That's a pragmatic call. It means we can skip the real-time infrastructure entirely
and focus engineering time on the core value proposition. Users will need a clear
"refresh" affordance, but that's a UI detail we can nail.

This actually opens up our next question about data freshness expectations...
```

## Anti-Patterns to Avoid

- Asking multiple questions in one turn
- Presenting options without a clear recommendation
- Accepting user's choice without exploring disagreement
- Asking questions that don't build on previous answers
- Rushing to conclusion before core decisions are made
- Making the synthesis before explicitly transitioning
