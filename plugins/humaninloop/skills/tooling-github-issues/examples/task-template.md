# Task/Chore Template

Use this template for tasks, chores, and maintenance work items.

## Template

```markdown
## Summary

[Action-oriented summary: "Migrate X to Y" not "Database stuff"]

## Context

[Why this task exists. What prompted it? What depends on it?]

## Definition of Done

- [ ] [First verifiable deliverable]
- [ ] [Second verifiable deliverable]
- [ ] [Continue as needed]

## Estimated Effort

[T-shirt size: XS / S / M / L / XL, or time estimate]

## Dependencies

- **Blocked by**: [Issues that must complete first]
- **Blocks**: [Issues waiting on this]

## Technical Notes

[Optional: Implementation hints, gotchas, related documentation]
```

---

## Example: Complete Task

```markdown
## Summary

Migrate user session storage from Redis 6 to Redis 7

## Context

Redis 6 reaches EOL in April 2024. Infrastructure team has provisioned Redis 7 cluster. User sessions are the last remaining Redis 6 dependency. Blocks: infrastructure decommissioning timeline.

## Definition of Done

- [ ] Redis 7 client library updated (`ioredis` 5.x → 6.x)
- [ ] Connection configuration updated for new cluster endpoints
- [ ] Session serialization verified compatible (no schema changes needed)
- [ ] Load testing confirms <5ms p99 latency maintained
- [ ] Runbook updated with new cluster details
- [ ] Old Redis 6 connection removed from codebase
- [ ] Monitoring dashboards updated to new cluster

## Estimated Effort

**M (Medium)** - 2-3 days including testing

## Dependencies

- **Blocked by**: #789 (Redis 7 cluster provisioning) - COMPLETE
- **Blocks**: #801 (Redis 6 decommissioning), #802 (Infrastructure audit)

## Technical Notes

- Redis 7 cluster uses different auth mechanism (ACL vs password)
- New endpoints: `redis-7.internal:6379` (primary), `redis-7-ro.internal:6379` (replica)
- Consider implementing gradual migration with feature flag for rollback capability
- Coordinate with on-call during migration window
```

---

## Example: Incomplete Task (What NOT to Do)

```markdown
## Title: Redis upgrade

Need to upgrade Redis. It's getting old.
```

**Why this fails:**
- No clear deliverable (upgrade what exactly?)
- No context (why now? what's the risk of not doing it?)
- No definition of done (how do we know it's complete?)
- No effort estimate (is this an hour or a week?)
- No dependencies (will this break something? is something waiting?)
