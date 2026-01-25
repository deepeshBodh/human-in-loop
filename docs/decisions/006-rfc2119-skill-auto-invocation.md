# ADR-006: RFC 2119 Keywords for Skill Auto-Invocation

**Status:** Accepted
**Date:** 2026-01-26

## Context

The humaninloop plugin has 21 skills with descriptions designed to trigger Claude's semantic matching for auto-invocation. However, skills are inconsistently invoked when users speak trigger phrases. Investigation revealed two categories of skills:

1. **Agent-invoked skills** - Called by agents during structured workflows (e.g., `patterns-api-contracts` called by `plan-architect`)
2. **User-invoked skills** - Should auto-trigger when users speak natural phrases (e.g., `using-github-issues` when user says "report a bug")

The problem: User-invoked skills use the same description format as agent-invoked skills, leading to unreliable auto-invocation. When a user said "I would like to report a bug and raise it as issue", the `using-github-issues` skill was not invoked until explicitly prompted.

Related issue: [#55](https://github.com/deepeshBodh/human-in-loop/issues/55)

## Decision

Use RFC 2119 keywords (MUST, SHOULD, MAY) in skill descriptions to establish clear invocation requirements for user-invoked skills.

### Description Format for User-Invoked Skills

```yaml
description: >
  This skill MUST be invoked when the user says "[exact phrase 1]",
  "[exact phrase 2]", or "[exact phrase 3]". SHOULD also invoke when
  user mentions "[keyword 1]", "[keyword 2]". [Capability description].
```

### RFC 2119 Keyword Semantics

| Keyword | Meaning | Use Case |
|---------|---------|----------|
| **MUST** | Mandatory invocation - skill is required for these phrases | High-confidence trigger phrases that uniquely identify the skill's domain |
| **SHOULD** | Recommended invocation - skill is appropriate | Related keywords that indicate the skill may be relevant |
| **MAY** | Optional invocation - skill could help | Edge cases or tangentially related requests |

### Skill Categories

| Category | Invocation Pattern | RFC Keywords | Example |
|----------|-------------------|--------------|---------|
| **User-invoked** | Direct user trigger phrases | MUST/SHOULD | `using-github-issues`, `analysis-iterative` |
| **Agent-invoked** | Called by agents in workflows | Not needed | `patterns-api-contracts`, `authoring-requirements` |
| **Hybrid** | Both user and agent invoked | MUST/SHOULD for user triggers | `analysis-codebase` |

### Example: Before and After

**Before** (unreliable invocation):
```yaml
description: Use when creating GitHub issues, managing issue lifecycle,
  triaging bugs and features, or when user mentions "log issue",
  "create bug", "feature request", "close stale issues", or needs
  structured issue tracking.
```

**After** (reliable invocation):
```yaml
description: This skill MUST be invoked when the user says "report a bug",
  "create issue", "log issue", "file a bug", "raise an issue", "create bug",
  or "feature request". Use for GitHub issue creation, lifecycle management,
  triage, and structured issue tracking.
```

Key changes:
- RFC 2119 `MUST` keyword establishes mandatory invocation
- "when the user says" is more direct than "when user mentions"
- Trigger phrases are explicitly quoted
- Capability description follows trigger requirements

## Rationale

### Why RFC 2119 Keywords

1. **Explicit requirement levels** - MUST/SHOULD/MAY provide clear invocation priority
2. **Familiar standard** - RFC 2119 is widely understood in technical documentation
3. **Semantic weight** - "MUST" carries stronger weight than "Use when" in Claude's interpretation
4. **Testable** - Clear requirements enable validation ("Did skill invoke on MUST phrase?")

### Why "when the user says" vs "when user mentions"

The `analysis-iterative` skill (which works reliably) uses:
> "when the user says 'brainstorm', 'deep analysis', 'let's think through'"

This phrasing:
- Explicitly frames the trigger as user speech
- Uses quoted exact phrases
- Creates a direct mapping: user says X → invoke skill

### Why Not Apply to All Skills

Agent-invoked skills don't need RFC keywords because:
- Invocation is controlled by agent logic, not semantic matching
- Agent prompts explicitly reference which skills to use
- Adding MUST would create false expectations for semantic triggering

## Consequences

### Positive

- Reliable auto-invocation for user-invoked skills
- Clear distinction between skill categories
- Testable invocation requirements
- Improved user experience (skills "just work")

### Negative

- Must audit existing skills to categorize and update descriptions
- Dual maintenance: agent-invoked vs user-invoked description patterns
- No guarantee Claude's semantic matching respects RFC keywords (empirical testing required)

### Neutral

- Description format diverges from Anthropic's generic examples
- Skills may need periodic tuning based on invocation success rates

## Implementation

### Immediate (This ADR)

Update `using-github-issues` skill description with RFC 2119 format.

### Future (As Needed)

Audit and update other user-invoked skills:
- `using-git-worktrees`
- `analysis-codebase` (hybrid)
- Other skills identified through usage patterns

### Validation

Monitor skill invocation success through:
1. Manual testing with trigger phrases
2. User feedback on missed invocations
3. Conversation logs showing skill activation patterns

## Related

- [Issue #55: Skill auto-invocation not working](https://github.com/deepeshBodh/human-in-loop/issues/55)
- [ADR-004: Skill-Augmented Agents Architecture](./004-skill-augmented-agents.md)
- [Agent Skills Documentation](../agent-skills-documentation.md)
- [RFC 2119: Key words for use in RFCs](https://www.rfc-editor.org/rfc/rfc2119)
