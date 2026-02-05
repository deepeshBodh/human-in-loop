# Evaluation Matrix Reference

Detailed criteria, scoring frameworks, and technology category comparisons for evaluating technology choices.

## Evaluation Criteria

| Criterion | Description | Questions to Ask |
|-----------|-------------|------------------|
| **Fit** | How well does it solve the problem? | Does it cover all requirements? Any gaps? |
| **Complexity** | How hard to implement and maintain? | Learning curve? Operational overhead? |
| **Team Familiarity** | Does the team know this tech? | Existing expertise? Training needed? |
| **Ecosystem** | Library support, community, docs? | Good documentation? Active community? |
| **Scalability** | Will it grow with the project? | Performance at scale? Cost at scale? |
| **Security** | Security posture and track record? | Known vulnerabilities? Security features? |
| **Cost** | Total cost of ownership? | Licensing? Infrastructure? Maintenance? |
| **Brownfield Alignment** | Fits existing stack? | Integrates well? Introduces conflict? |

## Decision Matrix Format

For complex decisions requiring weighted scoring:

```markdown
## Decision: [What needs to be decided]

### Context

[Why this decision matters. What depends on it.]

### Criteria Weights

| Criterion | Weight | Reason |
|-----------|--------|--------|
| Fit | High | Must fully solve auth requirements |
| Team Familiarity | Medium | Small team, learning time matters |
| Brownfield Alignment | High | Must integrate with existing Express app |

### Options Evaluated

| Option | Fit | Complexity | Team Familiarity | Alignment | Score |
|--------|-----|------------|------------------|-----------|-------|
| JWT + refresh tokens | High | Low | High | High | **Best** |
| Session cookies | Medium | Low | High | High | Good |
| OAuth2 only | Low | Medium | Low | Medium | Poor |

### Decision: JWT with refresh tokens

### Rationale

[Why this was chosen - connect to criteria]

### Trade-offs Accepted

[What are we giving up by choosing this option]
```

## Comparison Table Format

For quick side-by-side evaluation:

```markdown
### Options Comparison

| Aspect | Option A | Option B | Option C |
|--------|----------|----------|----------|
| **Description** | [Brief] | [Brief] | [Brief] |
| **Pros** | + Pro 1<br>+ Pro 2 | + Pro 1<br>+ Pro 2 | + Pro 1<br>+ Pro 2 |
| **Cons** | - Con 1<br>- Con 2 | - Con 1<br>- Con 2 | - Con 1<br>- Con 2 |
| **Best For** | [When to use] | [When to use] | [When to use] |
| **Risk** | Low/Medium/High | Low/Medium/High | Low/Medium/High |
```

## Common Technology Categories

### Authentication

| Option | When to Use | Trade-offs |
|--------|-------------|------------|
| **JWT** | Stateless APIs, microservices | Token revocation complexity |
| **Session cookies** | Traditional web apps | Server state required |
| **OAuth2/OIDC** | Third-party auth, SSO | Integration complexity |
| **API keys** | Machine-to-machine | Less granular control |

### Data Storage

| Option | When to Use | Trade-offs |
|--------|-------------|------------|
| **PostgreSQL** | Complex queries, relations | Operational complexity |
| **MongoDB** | Flexible schema, documents | Transaction limitations |
| **Redis** | Caching, sessions, queues | Data persistence concerns |
| **SQLite** | Local storage, prototypes | Concurrency limitations |

### API Style

| Option | When to Use | Trade-offs |
|--------|-------------|------------|
| **REST** | CRUD operations, caching | Over/under-fetching |
| **GraphQL** | Complex queries, flexibility | Complexity, caching |
| **gRPC** | Service-to-service, performance | Browser support |
| **WebSocket** | Real-time, bidirectional | Connection management |

## Brownfield Considerations

### Questions to Answer

1. **Does the existing stack solve this?**
   - Check existing dependencies for solutions
   - Prefer extension over addition

2. **Does this integrate cleanly?**
   - Same language/runtime?
   - Compatible patterns?

3. **Does this introduce conflict?**
   - Competing libraries (e.g., two ORMs)?
   - Incompatible patterns (e.g., callbacks vs async)?

### Alignment Scoring

| Scenario | Alignment | Action |
|----------|-----------|--------|
| Existing dep solves problem | High | Prefer reuse |
| New dep, same ecosystem | Medium | Document justification |
| New dep, different ecosystem | Low | Strong justification needed |
| Conflicting with existing | None | Avoid or escalate |
