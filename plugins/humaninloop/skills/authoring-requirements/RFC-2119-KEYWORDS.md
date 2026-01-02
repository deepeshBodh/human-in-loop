# RFC 2119 Keywords Reference

RFC 2119 defines key words for use in specifications to indicate requirement levels. Using these consistently ensures clear communication between stakeholders and developers.

## Keyword Definitions

### MUST / REQUIRED / SHALL

**Meaning:** Absolute requirement. There are no exceptions.

**When to use:**
- Core functionality that defines the feature
- Security and data integrity requirements
- Legal or compliance obligations
- Requirements that, if violated, break the system

**Examples:**
```markdown
- System MUST encrypt passwords before storage
- Users MUST authenticate before accessing private data
- System MUST log all financial transactions
- Users MUST accept terms before creating an account
```

**Common mistakes:**
- Using MUST for nice-to-have features
- Every requirement being MUST (inflation)
- MUST for implementation details ("MUST use AES-256")

### MUST NOT / SHALL NOT

**Meaning:** Absolute prohibition. This action is never allowed.

**When to use:**
- Security prohibitions
- Data protection requirements
- Actions that would cause data loss
- Compliance violations

**Examples:**
```markdown
- System MUST NOT store plaintext passwords
- System MUST NOT expose internal error details to users
- Users MUST NOT be able to access other users' private data
- System MUST NOT delete data without confirmation
```

### SHOULD / RECOMMENDED

**Meaning:** Strong recommendation. Valid reasons may exist to ignore, but implications must be understood.

**When to use:**
- Best practices that improve user experience
- Performance optimizations
- Features expected but not essential
- Behaviors that have known acceptable exceptions

**Examples:**
```markdown
- System SHOULD auto-save drafts every 30 seconds
- System SHOULD remember user preferences across sessions
- Error messages SHOULD suggest corrective actions
- System SHOULD provide undo for destructive actions
```

**When exceptions are valid:**
- Technical constraints make it impractical
- Edge cases where the behavior would be confusing
- Performance trade-offs in specific scenarios

### SHOULD NOT / NOT RECOMMENDED

**Meaning:** Strong recommendation against. Valid reasons may exist to do this, but implications must be understood.

**When to use:**
- Patterns that usually cause problems
- Behaviors that degrade experience
- Actions that could be confusing

**Examples:**
```markdown
- System SHOULD NOT require page refresh to see updates
- Forms SHOULD NOT clear on validation errors
- System SHOULD NOT send more than 3 emails per action
- Error messages SHOULD NOT expose system internals
```

### MAY / OPTIONAL

**Meaning:** Truly optional. Implementation can choose either way.

**When to use:**
- Features that enhance but aren't expected
- Implementation choices with no wrong answer
- Future enhancements
- Platform-specific behaviors

**Examples:**
```markdown
- System MAY offer keyboard shortcuts for power users
- System MAY provide dark mode option
- Export MAY include additional metadata
- System MAY cache results for improved performance
```

## Decision Framework

```
Is it a core requirement that must work for the feature to function?
├── Yes → MUST
└── No
    ├── Would most users expect this behavior?
    │   ├── Yes → SHOULD
    │   └── No → MAY
    └── Is it a security or compliance requirement?
        ├── Yes → MUST or MUST NOT
        └── No → Continue evaluation
```

## Requirement Distribution

A well-balanced specification typically has:

| Keyword | Typical % | Purpose |
|---------|-----------|---------|
| MUST | 30-40% | Core requirements |
| SHOULD | 40-50% | Expected behavior |
| MAY | 10-20% | Optional enhancements |

**Warning signs:**
- 80%+ MUST: Everything can't be mandatory; re-evaluate priorities
- 0% MAY: No room for implementation flexibility
- All SHOULD: Unclear what's actually required

## Common Mistakes

### Over-using MUST

**Problem:** Makes everything mandatory, diluting the meaning.

**Bad:**
```markdown
- System MUST have a clean UI
- System MUST be user-friendly
- System MUST perform well
```

**Better:**
```markdown
- System SHOULD follow established UI conventions
- Error messages SHOULD be actionable
- Page load SHOULD complete within 3 seconds under normal load
```

### Under-specifying Security

**Problem:** Security requirements marked as SHOULD when they need MUST.

**Bad:**
```markdown
- System SHOULD encrypt sensitive data
- Users SHOULD use strong passwords
```

**Better:**
```markdown
- System MUST encrypt sensitive data at rest and in transit
- System MUST enforce minimum password complexity
```

### Implementation in Requirements

**Problem:** Specifying HOW instead of WHAT.

**Bad:**
```markdown
- System MUST use bcrypt for password hashing
- System MUST implement OAuth 2.0
- API MUST use JSON format
```

**Better:**
```markdown
- System MUST use industry-standard password hashing
- System MUST support secure third-party authentication
- API MUST use a structured, parseable response format
```

## Combining Keywords

Keywords can be combined for nuanced requirements:

```markdown
- If email notifications are enabled (MAY), the system MUST send
  confirmation within 5 minutes of the triggering action

- System SHOULD provide export functionality; if provided, it MUST
  include all user data in a portable format

- System MAY offer social login; if offered, it MUST NOT share user
  data with third parties without explicit consent
```
