# Strategy: Core

Universal workflow patterns consumed by the State Briefer to inform Supervisor briefings. These are advisory patterns with rationale — not prescriptive rules. The Supervisor uses judgment informed by these patterns and may deviate when context warrants it.

## Validation

Every agent output should pass through a gate before downstream consumption or milestone achievement. Even when confident in quality, validation catches blind spots. This is the most consistently valuable pattern across all workflows.

**Rationale**: Skipping validation is the single most common source of wasted iterations. A "perfect-looking" analyst output that bypasses the advocate gate frequently contains gaps that surface later — costing a full extra pass to fix.

## Gap Classification

Advocate rejections and gate verdicts carry different gap types that suggest different responses:

- **Knowledge gaps** (factual unknowns, investigable questions) are often resolvable through targeted research without involving the user. Examples: "What auth protocol does the existing system use?", "What's the current database schema?"

- **Preference gaps** (subjective choices, business decisions) require user input — research cannot resolve what only humans can decide. Examples: "Should notifications be opt-in or opt-out?", "What's the acceptable latency threshold?"

- **Scope gaps** (too broad, multiple concerns, feasibility questions) may warrant halting or splitting rather than iterating within the current workflow. Examples: "This feature spans three bounded contexts", "The requirement conflicts with an architectural constraint."

**Rationale**: Treating all gaps identically leads to wasted effort — researching preferences yields nothing, asking users about codebase facts wastes their time, and iterating on scope issues without splitting never converges.

## Pass Evolution

Early passes establish structure. Later passes refine based on feedback. By pass 3+, assess whether gaps are converging (good — the artifact is improving) or recurring (bad — something structural is wrong). Diminishing returns are a signal to surface the situation to the user.

**Rationale**: Recurring gaps indicate a mismatch between what the workflow can produce and what the user needs. More iterations won't fix a structural problem — only user intervention or scope adjustment will.

## Halt Escalation

Never force-exit without user consent. When halting conditions arise, present the situation with clear options (continue iterating, accept current state, stop and review manually). The user always has final say on workflow termination.

**Rationale**: Autonomous halting destroys user trust. The workflow exists to serve the user's intent, and only the user can judge when "good enough" has been reached.

## Anti-Patterns

- **Infinite looping**: Continuing to iterate without checking if the same gaps keep recurring across passes
- **Preference-to-research**: Sending preference gaps to targeted research — research cannot answer "should we" questions
- **Validation bypass**: Skipping validation even when output seems obviously correct — confidence is not evidence
- **Force-termination**: Terminating the workflow without presenting options to the user
- **Re-enrichment**: Running input enrichment after pass 1 when input is already established
