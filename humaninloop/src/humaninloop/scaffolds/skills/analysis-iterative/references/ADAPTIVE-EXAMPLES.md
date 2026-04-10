# Adaptive Examples

Three annotated conversations demonstrating how the iterative analysis skill adapts its behavior to emerging complexity. Each annotation explains the adaptation choice.

---

## Example 1: Light Brainstorm — Notification Strategy

A straightforward decision with a user who knows what they want. Shows fast discovery, structured options, early wrap-up nudge, and lean synthesis.

---

**Turn 1 — Opening + First Question**

The team needs to decide on a notification strategy for the new dashboard. Let's think through the key decisions together.

To start: what's the primary goal of these notifications — keeping users informed of system events, or driving them back into the product for engagement?

**Options:**
- **A) System awareness**: Alert users to things that need attention (errors, thresholds, completions)
- **B) Engagement drivers**: Nudge users back to the product (new features, activity summaries, recommendations)
- **C) Both equally**: Mix of system alerts and engagement notifications

**Recommendation**: Option A — dashboard users typically need operational awareness. Engagement notifications risk being perceived as noise.

> **[Adaptation]**: Opening is brief and topic-specific — no generic "I'll ask you a series of questions" script. The first question doubles as discovery: the answer reveals both preference and thinking depth.

**User**: A, definitely. These are for ops teams monitoring infrastructure.

> **[Adaptation]**: Crisp, specific answer with context ("ops teams"). This signals confidence and domain knowledge — move faster through remaining decisions.

---

**Turn 2 — Structured Options (Moving Fast)**

Clear — operational awareness for ops teams. That rules out engagement-style notifications entirely and focuses the design on actionable alerts.

**Question 2**: How should notification urgency be handled — flat (all notifications equal) or tiered?

**Options:**
- **A) Flat**: All notifications look the same. Simple, but risks alert fatigue.
- **B) Two tiers**: Critical (immediate) vs. informational (batched). Balances urgency with noise.
- **C) Three+ tiers**: Critical / warning / info / debug. Maximum granularity but adds configuration complexity.

**Recommendation**: Option B — two tiers give ops teams a clear signal-to-noise split without overcomplicating the initial implementation. Can always add tiers later.

> **[Adaptation]**: Still using structured options because the user is making confident, fast decisions. No need for open probes — this is a user who knows their domain.

**User**: B. We tried three tiers at my last company and nobody configured the middle ones.

---

**Turn 3 — Convergence Detection + Wrap-Up Nudge**

Good call — two tiers with a clear distinction: critical interrupts, everything else batches. The experience-based reasoning on three tiers is worth capturing.

**Question 3**: For delivery channel — should critical alerts go through a dedicated channel (PagerDuty, SMS) or stay in-app?

**Options:**
- **A) In-app only**: Simpler, but ops teams may miss critical alerts when not watching the dashboard
- **B) In-app + external escalation**: Critical alerts push to PagerDuty/SMS after a timeout. More complex but more reliable.

**Recommendation**: Option B — ops teams cannot watch dashboards 24/7. External escalation for critical alerts is table stakes.

> **[Adaptation]**: Only two options offered because the decision space is genuinely binary here. Offering a third option for completeness would add noise.

**User**: B. Obvious for an ops tool.

> **[Adaptation]**: Three consecutive confident, fast answers with no new dimensions emerging. This is a convergence signal — time to nudge toward wrap-up.

---

**Turn 4 — Wrap-Up**

The core decisions are clear and consistent: operational alerts, two urgency tiers, external escalation for critical. These feel settled.

Is there another dimension to explore, or should the synthesis be generated now?

**User**: That covers it. Let's wrap.

> **[Adaptation]**: Nudge was appropriate — user confirmed immediately. Synthesis will be lean: Problem Statement, Key Decisions (all Confident), and Next Steps. No Decision Trail needed because there was no deliberation. No Risks section because none surfaced.

---

## Example 2: Deep Exploration — API Versioning Strategy

A complex architecture decision with a mix of confident and uncertain answers. Shows discovery revealing complexity, recalibration mid-conversation, disagreement handling, and comprehensive synthesis.

---

**Turn 1 — Opening + Discovery**

API versioning is one of those decisions that's cheap to get right early and expensive to fix later. Let's map the key considerations.

First: what's the current state? Is this a greenfield API, or are there existing consumers that need backward compatibility?

> **[Adaptation]**: Open-ended probe, not structured options — the answer determines which entire branch of questioning to pursue. Premature options would assume too much.

**User**: We have about 20 internal consumers and 3 external partner integrations. The API has been running for 18 months without formal versioning — just additive changes so far.

> **[Adaptation]**: This answer reveals significant complexity: existing consumers, external partners, no versioning yet. Recalibrate — this will be a longer, more careful conversation than a greenfield scenario.

---

**Turn 2 — Structured Options (Versioning Approach)**

That changes the calculus significantly. Twenty internal consumers and three external partners means any versioning scheme needs to handle migration, not just future design.

**Question 2**: Which versioning mechanism fits the existing landscape best?

**Options:**
- **A) URL path versioning** (`/v1/`, `/v2/`): Most visible, easiest for consumers to understand. But forces parallel route maintenance.
- **B) Header versioning** (`Accept: application/vnd.api.v2+json`): Cleaner URLs, but less discoverable. Some external partners may struggle with custom headers.
- **C) Query parameter** (`?version=2`): Easiest to adopt incrementally, but feels informal for a multi-partner API.

**Recommendation**: Option A — with external partners in the mix, visibility and simplicity matter. URL versioning has the widest tooling support and the lowest friction for partner onboarding.

**User**: I'm torn between A and B honestly. URL versioning feels crude but I get the pragmatic argument. Header versioning is cleaner but I worry about our partners.

> **[Adaptation]**: Hedging signal — "I'm torn." Switch from moving forward to exploring the tension. Do not just accept or push; help the user think through the specific trade-off.

---

**Turn 3 — Open Probe (Exploring Tension)**

That tension is worth sitting with. The technical elegance of header versioning vs. the operational reality of partner capabilities.

What's the technical sophistication of the three external partners? Are they teams with API experience who can handle custom headers, or are they more traditional integrations where curl examples matter?

> **[Adaptation]**: Open probe to surface the specific information that would resolve the user's tension. A structured option here would be premature — the user needs to think through the partner dimension, not pick from a list.

**User**: Two of them are solid engineering teams. The third is a small company that basically copied our curl examples verbatim and would struggle with anything beyond basic REST.

---

**Turn 4 — Structured Options (Informed by Probe)**

That's a clear split: two partners can handle anything, one needs simplicity. This narrows the realistic choices.

**Question 4**: Given the partner mix, which path forward?

**Options:**
- **A) URL versioning for all**: Lowest common denominator. All partners succeed, including the simpler integration.
- **B) Header versioning with URL fallback**: Primary mechanism is headers, but provide URL aliases for partners who need them.

**Recommendation**: Option A — the URL fallback in Option B sounds elegant but doubles the routing surface area for three partners. URL versioning everywhere keeps things honest.

**User**: I still want header versioning. We're going to have more partners and I don't want to be locked into URL patterns long term.

> **[Adaptation]**: User disagreeing with recommendation after thoughtful consideration. This is a deliberate choice, not impulsive — push back once, then respect it.

---

**Turn 5 — Disagreement Handling**

The long-term argument has merit. Before locking that in: the migration path concerns me. Twenty internal consumers currently hit unversioned endpoints. How does header versioning handle the transition — do unversioned requests get a default version, or are they rejected?

**User**: Default to latest version if no header is present. That maintains backward compatibility — existing consumers keep working without changes.

---

**Turn 6 — Structured Challenge**

Defaulting to latest is convenient but risky: it means any breaking change in a new version silently affects every consumer that hasn't opted in. If v3 changes a response field, all headerless consumers get v3 behavior unexpectedly.

The safer pattern is default to the version that existed when the consumer was onboarded. Worth the extra complexity?

**User**: Good catch. Yeah, default to v1 for existing consumers. New consumers get whatever's current at registration time.

> **[Adaptation]**: The pushback surfaced a real design flaw the user hadn't considered. The decision changed because of the exploration, not because of preference. Record this in the Decision Trail with `Contested` confidence.

---

**Turn 7 — Convergence**

Strong design: header versioning with a pinned default per consumer. That handles the migration, the partner spectrum, and the long-term evolution.

Two more quick decisions remain — deprecation policy and version lifecycle. Or is the versioning mechanism itself the main thing to settle today?

**User**: Let's cover deprecation quickly, then wrap.

---

**Turn 8 — Final Question + Wrap-Up**

**Question 7**: Deprecation timeline — how long do old versions live after a new version ships?

**Options:**
- **A) 6 months**: Gives consumers a clear window. Tight but manageable for internal teams.
- **B) 12 months**: More breathing room, especially for external partners with slower release cycles.

**Recommendation**: Option B — external partners rarely move fast. Twelve months prevents relationship friction.

**User**: 12 months for external, 6 for internal. We control our own teams.

> **[Adaptation]**: User refined the recommendation into a hybrid. This is a `Confident` decision — specific, reasoned, no hesitation.

Generating synthesis now. This one will include a Decision Trail section for the versioning mechanism deliberation and a Risks section for the default-version pitfall that surfaced.

---

## Example 3: Unsure-Heavy Session — Data Migration Planning

A user who does not know where to start. Shows mostly open probes early, gradual shift to structured options, no premature nudge, and synthesis with Unsure/Deferred indicators.

---

**Turn 1 — Opening + Discovery**

Data migrations are high-stakes and high-anxiety. Let's start by understanding the landscape before getting into strategy.

What's being migrated — is this a database engine swap, a schema redesign, an application replatform, or something else?

> **[Adaptation]**: Open probe with several anchoring possibilities. The user is starting from "help me think through data migration" with no specifics — providing anchor options prevents a blank-page problem without forcing a premature decision.

**User**: Honestly, I'm not sure how to categorize it. We're moving from a monolith's PostgreSQL database to separate databases per microservice. Some tables need to split, some need to move wholesale, and there's a bunch of shared state I haven't figured out yet.

> **[Adaptation]**: "I'm not sure" + description of ambiguity + "haven't figured out yet" — classic unsure signals across multiple dimensions. This will be a longer session. Stick with open probes to help the user discover what they think before offering structured options.

---

**Turn 2 — Open Probe (Mapping the Landscape)**

That's a significant decomposition — not just moving data, but restructuring ownership boundaries. The shared state is usually where these projects get stuck.

Before getting into strategy: which services are the clearest candidates? Where is the data ownership already obvious, and where is it contested?

> **[Adaptation]**: Open probe, not structured options. The user needs to externalize what they already know before being asked to decide anything. This question helps them separate the known from the unknown.

**User**: Orders and Payments are pretty clear — each has distinct tables that nobody else writes to. The problem is the Users table. Everyone reads from it, three services write to it, and it has like 40 columns that probably belong to different domains.

---

**Turn 3 — Open Probe (Deepening on the Hard Part)**

The Users table is the crux. Forty columns across multiple domains is a classic "God table" pattern.

What kinds of data live in that Users table? Not all 40 columns, but at a high level — is it identity/auth data, profile/preferences, billing info, activity state?

> **[Adaptation]**: Still probing, not offering options. The user identified their core problem but hasn't articulated the decomposition dimensions yet. Premature structuring ("Should you split vertically or horizontally?") would force a choice the user is not ready to make.

**User**: All of the above. Auth credentials, profile fields, subscription tier, notification preferences, last-login timestamps, feature flags per user... it's everything. Some of it probably shouldn't even be in the Users table.

---

**Turn 4 — First Structured Options (User is Ready)**

That confirms the God table diagnosis. The decomposition pattern matters here because it determines the migration order and the interim state.

**Question 4**: For the Users table specifically, which decomposition approach feels right?

**Options:**
- **A) Domain-first split**: Carve out logical domains (auth, profile, billing, preferences) as separate tables/services first, then migrate
- **B) Read/write split**: Separate read replicas per service first (low risk), then gradually migrate write ownership
- **C) Strangler pattern**: New services write to their own stores, sync back to the monolith, gradually cut over

**Recommendation**: Option C — it's the lowest risk because the monolith remains the source of truth until each service proves itself. The interim complexity is higher but the blast radius per step is smaller.

> **[Adaptation]**: Now offering structured options. The user has externalized enough understanding through the probes to make an informed choice. The three options are genuine architecture patterns, not generic buckets.

**User**: I don't know enough about the strangler pattern to evaluate it honestly. Can you explain the interim state?

> **[Adaptation]**: Another unsure signal, but different — this is an information gap, not an uncertainty about preferences. Answer the question directly rather than probing further. The user is asking for help evaluating, not help discovering.

---

**Turn 5 — Explanation + Re-ask**

In the strangler pattern, the interim state looks like this: new service writes to both its own database and the monolith (dual-write or event-based sync). Other services still read from the monolith. Once the new service is stable and all consumers have migrated their reads, the monolith table gets decommissioned.

The risk is the dual-write period: data can diverge if sync fails. Mitigation is usually an event bus with guaranteed delivery and a reconciliation job.

Does that change the calculus, or is the dual-write complexity a concern?

**User**: That actually makes sense. But I'm worried about our team's capacity to manage the dual-write sync. We're a small team.

> **[Adaptation]**: Hedging again — "makes sense but worried." The user likes the approach conceptually but doubts execution feasibility. This is a constraint to capture, not a decision to force.

---

**Turn 6 — Open Probe (Capacity Constraint)**

Team capacity is a real constraint that should drive the approach, not just the architecture. How small is the team, and what's the timeline pressure? Is this a "must complete by Q3" mandate or a "get there eventually" evolution?

**User**: Four backend engineers, and leadership wants the first two services extracted by end of Q2. The rest is "eventually."

---

**Turn 7 — Structured Options (Informed by Constraints)**

Four engineers, two service extractions by Q2. That's tight but scoped. The Q2 deadline favors starting with the easy wins — Orders and Payments, where ownership is already clear.

**Question 7**: Execution strategy for the Q2 deadline:

**Options:**
- **A) Orders first, then Payments**: Sequential, all four engineers on one service at a time
- **B) Parallel extraction**: Split the team — two engineers per service simultaneously
- **C) Payments first, then Orders**: Payments touches billing, which is higher risk. Doing it first under less time pressure is safer.

**Recommendation**: Option A — Orders is the clearest ownership boundary, making it the best candidate for the team to learn the extraction pattern. Apply lessons to Payments. Parallel extraction with four engineers risks coordination overhead.

**User**: A makes sense. Learn on the easy one.

> **[Adaptation]**: First confident, fast answer in the session. The user's comfort zone is execution sequencing, not architecture patterns. Note the shift — no need to probe further on this dimension.

After generating the Q2 extraction plan, the Users table decomposition remains an open question — the team will have more information after completing the first two extractions. This should appear in the synthesis as `Deferred` with a rationale.

Generating synthesis now. It will include Unsure/Deferred indicators for the Users table strategy, Confident for the extraction sequence, and an Open Questions section for the dual-write capacity concern.
