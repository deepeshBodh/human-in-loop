# Priority Definitions

Detailed guidance for assigning P1, P2, and P3 priorities to user stories.

## Priority Levels

### P1 - Core Functionality

**Definition:** Absolute requirements for the feature to be considered functional. Without these, the feature cannot ship.

**Criteria:**
- Blocks other stories or features from working
- Required for the minimum viable product (MVP)
- Addresses the primary user need that motivated the feature
- Failure would make the entire feature unusable

**Business signals:**
- Stakeholders explicitly marked as "must have"
- Legal or compliance requirement
- Core revenue/value driver
- Security or data integrity concern

**Example justifications:**
- "Users cannot complete the primary workflow without this"
- "This is the core value proposition of the feature"
- "Required for regulatory compliance"
- "Blocks P1 stories in dependent features"

### P2 - Important

**Definition:** Significantly enhances the user experience but the feature can technically ship without it. Expected in a complete implementation.

**Criteria:**
- Enhances but doesn't enable the core workflow
- Addresses common but not universal user needs
- Quality-of-life improvements that users will notice
- Can be added in a fast-follow release

**Business signals:**
- Stakeholders marked as "should have"
- Competitive parity features
- Frequent user requests from similar products
- Reduces support burden

**Example justifications:**
- "Improves efficiency for power users"
- "Expected feature based on industry standards"
- "Reduces friction in secondary workflows"
- "Enables self-service for common questions"

### P3 - Nice to Have

**Definition:** Enhancements that improve the experience but aren't expected in the initial release. Future consideration.

**Criteria:**
- Edge case handling beyond basic requirements
- Convenience features for specific user segments
- Polish and delight features
- Can be deferred indefinitely without significant impact

**Business signals:**
- Stakeholders marked as "could have" or "nice to have"
- Infrequent user requests
- Competitive differentiation (not parity)
- Enhancement to already-working functionality

**Example justifications:**
- "Addresses a niche use case"
- "Adds delight but not required for success"
- "Power user feature with narrow audience"
- "Optimization for edge case performance"

## Priority Decision Tree

```
Is the feature unusable without this story?
├── Yes → P1
└── No
    ├── Would users be disappointed if this shipped without it?
    │   ├── Yes → P2
    │   └── No → P3
    └── Is this a common expectation from similar products?
        ├── Yes → P2
        └── No → P3
```

## Priority Distribution Guidelines

A well-balanced feature specification typically has:
- **1-2 P1 stories**: The essential core
- **2-3 P2 stories**: The complete experience
- **0-2 P3 stories**: Optional enhancements

**Warning signs:**
- All stories are P1: Likely inflated priorities; revisit what's truly essential
- No P1 stories: Feature may lack clear focus
- Many P3 stories: Consider deferring to a future phase

## Common Priority Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Everything is P1 | Loses meaning of priority | Ask "can we ship without this?" |
| Priority based on effort | Conflates complexity with value | Focus on user/business impact |
| No justification | Can't defend decisions | Always state "Why this priority" |
| Copying priorities from similar features | Context differs | Evaluate for this specific feature |
