# Edge Case Patterns

Detailed guidance for identifying and documenting edge cases in specifications.

## Edge Case Categories

### 1. System Limits and Capacity

Boundaries where the system reaches its designed limits.

**Common patterns:**
- Maximum number of items (tasks, users, files)
- File size limits
- Rate limiting thresholds
- Concurrent user limits
- Storage quotas

**Example edge cases:**
- User attempts to create task #1001 when limit is 1000
- File upload exceeds 100MB maximum
- User makes 101st API call within rate limit window
- 10,001st user tries to join a room limited to 10,000

**Documentation format:**
```markdown
**Maximum tasks per user**: When a user attempts to create a task that
would exceed the 1000 task limit, the system MUST display a clear error
message and suggest archiving completed tasks.
```

### 2. Invalid or Malformed Input

Input that doesn't conform to expected formats or constraints.

**Common patterns:**
- Empty or missing required fields
- Wrong data types (string where number expected)
- Boundary values (negative numbers, zero, MAX_INT)
- Special characters and encoding issues
- Injection attempts (SQL, XSS, command)

**Example edge cases:**
- User submits form with empty required field
- Date field receives "not-a-date" string
- Quantity field receives -1 or 0
- Name field contains `<script>` tags
- Search query contains SQL `'; DROP TABLE`

**Documentation format:**
```markdown
**Empty task title**: When a user attempts to save a task with an empty
title, the system MUST prevent submission and highlight the required field
with a clear validation message.
```

### 3. External Dependency Failures

Scenarios where external services or resources are unavailable.

**Common patterns:**
- Network timeouts
- Third-party service unavailable
- Authentication service down
- Payment processor errors
- Email/SMS delivery failures

**Example edge cases:**
- Payment gateway times out during checkout
- OAuth provider returns 503
- Email service rejects message
- CDN is unreachable for static assets
- Database connection pool exhausted

**Documentation format:**
```markdown
**Payment timeout**: When the payment processor doesn't respond within
30 seconds, the system MUST NOT charge the user, MUST display a clear
error message, and SHOULD offer retry options.
```

### 4. Concurrent Access and Race Conditions

Multiple users or processes accessing shared resources simultaneously.

**Common patterns:**
- Simultaneous edits to same resource
- Duplicate form submissions
- Inventory race conditions
- Lock contention
- Stale data reads

**Example edge cases:**
- Two users edit the same document simultaneously
- User double-clicks submit button
- Two customers try to buy last item in stock
- Cron job runs while user is editing
- Cache shows stale data during update

**Documentation format:**
```markdown
**Simultaneous edits**: When two users edit the same task simultaneously,
the system MUST detect the conflict and SHOULD offer merge options or
show which changes would be overwritten.
```

### 5. Permission and Access Boundaries

Authorization edge cases where access rights are in question.

**Common patterns:**
- Accessing resources without permission
- Expired authentication tokens
- Role changes during active session
- Shared resource permissions
- Cross-tenant access attempts

**Example edge cases:**
- User's session expires mid-workflow
- Admin demotes user while user is active
- User tries to access teammate's private task
- API key rotated during long-running process
- User removed from team while viewing team data

**Documentation format:**
```markdown
**Session expiry during save**: When a user's session expires while
they're editing, the system MUST preserve their unsaved changes locally
and prompt for re-authentication, then SHOULD restore their work.
```

## Edge Case Discovery Process

### Step 1: Identify Boundaries

For each feature, ask:
- What are the numeric limits?
- What inputs are required vs optional?
- What external systems are involved?
- Can multiple users interact simultaneously?
- What permissions govern access?

### Step 2: Explore Failure Modes

For each boundary, ask:
- What happens at the exact limit?
- What happens just beyond the limit?
- What if the input is completely wrong?
- What if the dependency fails?
- What if timing is unexpected?

### Step 3: Prioritize by Impact

Classify edge cases by:
- **Critical**: Data loss, security breach, financial impact
- **Important**: Broken workflow, poor user experience
- **Minor**: Cosmetic issues, edge cases affecting few users

### Step 4: Document Expected Behavior

For each edge case, specify:
- The exact condition/trigger
- The expected system behavior
- Whether it MUST, SHOULD, or MAY be handled
- User feedback/messaging requirements

## Edge Case Documentation Template

```markdown
## Edge Cases

### [Category]: [Brief Description]

**Trigger**: [Exact condition that causes this edge case]

**Expected Behavior**: System [MUST/SHOULD/MAY] [specific action]

**User Feedback**: [What the user sees/experiences]

**Priority**: [Critical/Important/Minor]
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Too vague | "Handle errors gracefully" | Specify exact error and response |
| Implementation-focused | "Catch NullPointerException" | Describe user-visible behavior |
| Missing edge cases | Only happy path covered | Systematically explore boundaries |
| No priority | All edge cases equal | Classify by business impact |
