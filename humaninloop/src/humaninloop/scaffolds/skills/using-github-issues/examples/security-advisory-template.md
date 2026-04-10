# Security Advisory Template

Use this template for security vulnerability disclosure. **NEVER create public issues for security vulnerabilities.**

## Disclosure Channels (In Order of Preference)

1. **GitHub Security Advisories** - Private, built-in, notifies maintainers
2. **SECURITY.md contact** - Follow repository's security policy
3. **Private repository** - Dedicated security issue tracker
4. **Direct maintainer contact** - Email if no other channel exists

---

## Template

```markdown
## Vulnerability Summary

**Type**: [e.g., SQL Injection, XSS, CSRF, Authentication Bypass, Information Disclosure]
**Severity**: [Critical / High / Medium / Low]
**CVSS Score**: [If calculated, e.g., 9.8]

## Affected Components

- **File(s)**: [Path to vulnerable code]
- **Endpoint(s)**: [Affected API routes or pages]
- **Version(s)**: [Affected versions, e.g., "< 2.3.1", "all"]

## Description

[Clear explanation of the vulnerability and its impact]

## Proof of Concept

[Steps to reproduce - be specific enough to verify but not weaponized]

1. [Setup step]
2. [Trigger step]
3. [Observe vulnerability]

## Impact Assessment

- **Confidentiality**: [What data could be exposed?]
- **Integrity**: [What data could be modified?]
- **Availability**: [Could this cause denial of service?]
- **Scope**: [Who is affected? All users? Admins only?]

## Suggested Remediation

[If known, how to fix. Be helpful, not prescriptive.]

## Timeline

- **Discovered**: [Date]
- **Reported**: [Date]
- **Suggested Disclosure**: [Date, typically 90 days from report]

## Reporter

[Your name/handle and contact for follow-up]
```

---

## Example: Complete Security Advisory

```markdown
## Vulnerability Summary

**Type**: SQL Injection
**Severity**: Critical
**CVSS Score**: 9.8 (Critical)

## Affected Components

- **File(s)**: `src/api/auth/login.js:45`
- **Endpoint(s)**: `POST /api/auth/login`
- **Version(s)**: All versions prior to fix

## Description

The `username` parameter in the login endpoint is concatenated directly into a SQL query without sanitization or parameterization. An attacker can inject arbitrary SQL to bypass authentication, extract database contents, or modify data.

## Proof of Concept

1. Navigate to login page
2. Enter username: `admin'--`
3. Enter any password
4. Observe successful login as admin without valid password

The vulnerable code:
```javascript
// VULNERABLE - DO NOT USE
const query = `SELECT * FROM users WHERE username = '${username}'`;
```

## Impact Assessment

- **Confidentiality**: Complete database readable (user data, passwords, API keys)
- **Integrity**: Arbitrary data modification possible
- **Availability**: Database could be dropped or corrupted
- **Scope**: All users and all data in the system

## Suggested Remediation

Use parameterized queries:
```javascript
const query = `SELECT * FROM users WHERE username = $1`;
const result = await db.query(query, [username]);
```

Additionally:
- Audit all database queries for similar patterns
- Implement input validation layer
- Add SQL injection detection to WAF

## Timeline

- **Discovered**: 2024-01-15
- **Reported**: 2024-01-15
- **Suggested Disclosure**: 2024-04-15 (90 days)

## Reporter

security-researcher@example.com
```

---

## What NOT to Do

### Never Create Public Issues

```markdown
## Title: CRITICAL SQL INJECTION IN LOGIN

Found SQL injection in /api/auth/login. The username field is not sanitized.
Payload: admin'--
This bypasses authentication completely!
```

**Why this is dangerous:**
- Publicly visible to attackers
- Provides exact exploit details
- No time for maintainers to fix before exploitation
- Labels like "security" or "confidential" do NOT hide the content
- Even closed issues remain searchable

### Never Assume Labels Provide Confidentiality

GitHub issue labels are metadata, not access controls. A "security" or "confidential" label does not:
- Hide the issue from public view
- Restrict who can read the content
- Prevent search engine indexing
- Protect sensitive details

**Always use private disclosure channels.**
