---
name: analysis-iterative
description: This skill MUST be invoked when the user says "brainstorm", "deep analysis", "let's think through", "analyze this with me", or "help me think through". SHOULD also invoke when feature descriptions lack Who/Problem/Value clarity during specification enrichment.
---

# Iterative Analysis

## Overview

Guide collaborative thinking by adapting questioning style, depth, and output to the complexity that emerges during conversation. Each question builds on the previous answer, and the format of each question adapts to the user's current state — confident, uncertain, or somewhere in between. Conclude with a structured synthesis document whose depth matches the conversation's depth.

## When to Use

- Brainstorming sessions that need structured exploration
- Deep analysis of complex problems with multiple decision points
- Thinking through feature requirements before specification
- Enriching sparse feature descriptions for `humaninloop:specify`
- Exploring trade-offs that require deliberate choices
- When the user is unsure and needs help discovering what they think

## When NOT to Use

- **Quick clarifications** — simple questions do not need iterative questioning
- **Implementation details** — use planning skills instead
- **Specification review** — use `humaninloop:analysis-specifications` instead
- **When user has clear direction** — use confirmations to verify, then wrap up fast. Do not slow down decisive users with unnecessary exploration.
- **Time-sensitive decisions** — iterative questioning takes time

## Adaptive Flow

```
Opening ──→ Discovery ──→ Adaptive Questioning ──→ Conclusion
  │              │                │                      │
  │              │                │                      │
  Brief,         Reveals          Format adapts per      Synthesis depth
  topic-         complexity       turn: structured       matches
  specific       and thinking     options / open         conversation
  entry          depth            probes / confirmations depth
```

**Opening** establishes the topic and asks the first question. Do not recite a fixed introduction script. Adapt tone and framing to the topic — a migration planning session opens differently than a notification brainstorm.

**Discovery** happens through the first 1-2 questions. Their purpose is dual: advance the conversation AND reveal how deep the exploration needs to go. See the Discovery section below.

**Adaptive Questioning** is the core loop. Each turn: read the answer, pick the right question format, ask one question. Continue until convergence signals appear or the user signals completion. See Question Format Adaptation and Reading Confidence Signals below.

**Conclusion** generates the synthesis artifact. See Smart Wrap-up below.

How long each phase lasts adapts to complexity. A crisp 3-question brainstorm may spend one turn in discovery. A complex architecture decision may spend three.

## Discovery

The first 1-2 questions serve a dual purpose: advance the conversation toward substance AND calibrate complexity.

**Principle:** Ask a question that is genuinely useful on its own merit — not a meta-question about "how deep should we go." Read the answer for complexity signals.

**What to look for in the first answer:**

- **Crisp, specific, opinionated** → User knows the domain. Move faster, lean toward structured options.
- **Vague, hedging, "I'm not sure"** → Exploration needed. Lean toward open probes. Do not default to a recommendation when the user has not yet formed a view.
- **Long, detailed, multi-dimensional** → Complex problem space. Plan for more questions and a comprehensive synthesis.

**"Unsure" is a first-class signal.** When the user says "I don't know" or "I'm not sure," it means probe deeper from a different angle — not fill in a default recommendation and move on. After 3+ consecutive "unsure" answers, reframe the question from a different angle or suggest narrowing the scope to a concrete sub-problem.

**Example — crisp answer branch:**
> "A, definitely. These are for ops teams monitoring infrastructure."
>
> → Confident and specific. Next question can offer structured options and move quickly.

**Example — unsure answer branch:**
> "Honestly, I'm not sure how to categorize it. We're moving from a monolith..."
>
> → Unsure with some detail. Next question should be an open probe to help the user map what they know before offering options.

## Question Format Adaptation

Three formats, selected based on the user's current state:

### Structured Options + Recommendation

Use when: a genuine decision point exists and the user has enough context to evaluate options.

```
[Brief context connecting to previous answer]

**Question [N]**: [Clear, focused question]

**Options:**
- **A) [Option]**: [What it means and its implications]
- **B) [Option]**: [What it means and its implications]
- **C) [Option]**: [What it means and its implications]

**Recommendation**: Option [X] because [reasoning based on what is known so far]
```

### Open-Ended Probes

Use when: the user is uncertain, the problem space is not yet mapped, or an answer revealed unexpected complexity. No options — ask a question that helps the user externalize their thinking.

```
[Acknowledge what was shared]

[Open question that helps the user articulate what they know,
or surfaces information needed for the next decision]
```

### Confirmations

Use when: the user has clearly decided and the remaining question is just verification. Do not belabor obvious conclusions.

```
[Acknowledge the decision and its implications]

That seems settled. [Brief implication or transition to next topic]
```

**Meta-principle:** Pick the format that serves the user's current state. If uncertain which format to use, prefer the open probe — it gathers information without forcing premature commitment.

**Example — same topic, different formats based on state:**
> Structured: "Which versioning mechanism fits best? A) URL path, B) Header, C) Query parameter"
>
> Open probe: "What's the technical sophistication of the external partners who need to consume this API?"
>
> Confirmation: "URL versioning for all consumers — that sounds settled. Moving on to deprecation policy."

## Reading Confidence Signals

Recalibrate after every answer. The user's state can shift mid-conversation.

| Signal | Meaning | Response |
|--------|---------|----------|
| Crisp, specific, immediate | High confidence | Move faster. Structured options. |
| Hedging, "it depends," "I think maybe" | Moderate uncertainty | Slow down. Mix of probes and options. |
| "I don't know," "I'm not sure" | Low confidence | Switch to open probes. Help discover before deciding. |
| Disagrees with recommendation | Deliberate preference | Explore reasoning, push back once, then respect the choice. |
| Quick agreement without elaboration | Possible passive acceptance | Light challenge: "Just to pressure-test — what makes you prefer this over [alternative]?" |

**Disagreement handling:** When the user picks differently than recommended — explore their reasoning, present counterarguments respectfully but directly, and if they maintain their choice after the challenge, accept it and integrate. Mark the decision as `Contested` in the synthesis.

## Smart Wrap-up

**Convergence signals** — watch for these:
- Answers are becoming confirmatory, not exploratory
- Key trade-offs have been explicitly addressed
- No new dimensions are emerging
- User's confidence in direction is increasing

**Nudge format:** Suggest wrap-up, but always offer an exit:

```
The core decisions feel settled. Should the synthesis be generated, or is there
another dimension to explore?
```

**Asymmetry principle:** Wrapping up too early is worse than wrapping up too late. An extra question costs one turn. A missing decision costs rework. When in doubt, ask one more question.

Never force synthesis. The skill may nudge, but the user always has final say on when to conclude.

## Output

Generate the synthesis document using [SYNTHESIS.md](SYNTHESIS.md).

**Confidence indicators** — assign based on conversation observation:

| Indicator | Meaning |
|-----------|---------|
| `Confident` | Clear, reasoned choice with no hesitation |
| `Assumed` | Inferred from context, never explicitly confirmed |
| `Contested` | User disagreed with recommendation; deliberate choice |
| `Unsure` | Expressed uncertainty; decided provisionally |
| `Deferred` | Explicitly postponed — not enough information now |

**Output scales with conversation.** A 3-question brainstorm produces Problem Statement, Key Decisions, and Next Steps. A 10-question deep exploration produces all sections including Decision Trail and Risks. Never pad a lean conversation with filler sections.

## Common Mistakes

### Always Using Structured Options
Not every turn needs options and a recommendation. When the user is unsure, open probes help them discover what they think. Structured options on an uncertain user force premature decisions.

### Ignoring "Unsure" Signals
"I don't know" means probe deeper, not "doesn't care." Treating uncertainty as indifference leads to recommendations the user passively accepts but does not own.

### Multiple Questions Per Turn
One question per turn — always. Multiple questions fracture attention and produce shallow answers across all of them instead of one thoughtful answer.

### Questions That Don't Connect
Every question must show how the previous answer shapes the direction. Jumping topics without connecting breaks the collaborative momentum.

### Premature Synthesis
The skill may nudge toward wrap-up but must not force it. If core decisions are not yet made or key trade-offs are unaddressed, continue asking.

### Rigid Opening Script
Do not recite a fixed "I'll ask you a series of questions" introduction. Adapt the opening to the topic's tone and the user's apparent energy.

### Padding the Synthesis
Match output depth to conversation depth. A 3-question session does not need a Decision Trail, Risks section, or Open Questions. Include only sections with real content.

---

## Modes

This skill supports specialized modes for specific use cases.

### Specification Input Enrichment

When invoked with `mode:specification-input`, run a focused variant for enriching sparse feature descriptions. See [SPECIFICATION-INPUT.md](SPECIFICATION-INPUT.md) for the question agenda and [ENRICHMENT.md](ENRICHMENT.md) for the output template.

## Reference

See [ADAPTIVE-EXAMPLES.md](references/ADAPTIVE-EXAMPLES.md) for annotated conversations showing these principles in action.
