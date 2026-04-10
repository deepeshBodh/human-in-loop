# Essential Floor (NON-NEGOTIABLE)

Every constitution MUST include principles for these four categories, regardless of codebase state.

## Detail Requirements

When writing Essential Floor principles, include these specifics:

### Security Principle MUST address:

- **Secret management**: Environment variables OR cloud secret managers (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault, etc.)
- **Secret scanning**: CI MUST run secret scanning tools (e.g., Trivy, Snyk, git-secrets, gitleaks)
- **Config file exclusion**: Sensitive config files (e.g., `*.local.*`, `appsettings.*.json` with secrets) MUST be in `.gitignore`
- **Input validation**: All external inputs MUST be validated before processing

### Testing Principle MUST address:

- **Coverage thresholds**: Specify numeric values (e.g., warning at <80%, blocking at <60%)
- **Ratchet rule**: "Coverage baseline MUST NOT decrease" - prevents coverage regression
- **Test file conventions**: Naming patterns for test files (e.g., `*_test.py`, `*.spec.ts`, `*Test.java`)
- **Test organization**: How tests mirror source structure

### Error Handling Principle MUST address:

- **Response format**: RFC 7807 Problem Details (preferred) or consistent JSON schema
- **Error codes**: Naming convention (e.g., `ERR_DOMAIN_ACTION`)
- **Stack traces**: MUST NOT be exposed in production responses
- **Correlation**: Error responses MUST include correlation/trace IDs

### Observability Principle MUST address:

- **Logging format**: Structured JSON logging with standard fields
- **APM tools**: Name specific tools if detected (e.g., Application Insights, Datadog, New Relic)
- **Health checks**: Endpoint path and what it validates
- **PII prohibition**: Logs MUST NOT contain personally identifiable information

---

## Example Principles

### I. Security by Default (NON-NEGOTIABLE)

All code MUST follow security-first principles.

- Authentication MUST be enforced at API boundaries
- Secrets MUST be loaded from environment variables or AWS Secrets Manager
- Sensitive config files (`appsettings.*.json`, `.env.local`) MUST be in `.gitignore`
- All external inputs MUST be validated before processing
- CI MUST run secret scanning on every push

**Enforcement**:
- CI runs `trivy fs --scanners secret .` and blocks merge on findings
- CI runs `snyk test` for dependency vulnerabilities
- Code review checklist includes auth verification
- Pre-commit hook runs `gitleaks protect`

**Testability**:
- Pass: Zero secrets in codebase, zero high/critical vulnerabilities, auth on all endpoints
- Fail: Any secret detected OR critical vulnerability OR unauthenticated endpoint

**Rationale**: Security breaches are expensive and damage trust. Defense in depth with automated scanning catches issues before they reach production.

---

### II. Testing Discipline (NON-NEGOTIABLE)

All production code MUST have automated tests.

- New functionality MUST have accompanying tests before merge
- Test coverage MUST be ≥80% (warning) and ≥60% (blocking)
- Coverage baseline MUST NOT decrease (ratchet rule)
- Test files MUST follow naming convention: `*_test.py` or `test_*.py`
- Tests MUST mirror source structure in `tests/` directory

**Enforcement**:
- CI runs `pytest --cov --cov-fail-under=60` and blocks merge on failure
- Coverage report generated on every PR via `pytest-cov`
- Pre-commit hook runs `pytest tests/unit/` for fast feedback
- Coverage ratchet enforced by comparing to baseline in CI

**Testability**:
- Pass: All tests pass AND coverage ≥60% AND coverage ≥ previous baseline
- Fail: Any test fails OR coverage <60% OR coverage decreased

**Rationale**: Tests enable confident refactoring and catch regressions early. The 80% warning/60% blocking thresholds balance coverage with pragmatism. The ratchet rule prevents coverage erosion over time.

> Note: Current coverage is 65%. See GAP-002 in evolution-roadmap.md for improvement plan.

---

### III. Error Handling Standards (NON-NEGOTIABLE)

All code MUST handle errors gracefully. Failures MUST NOT crash the app or lose user data.

- All external calls (network, file system, database) MUST be wrapped in try/catch
- Errors MUST be logged with sufficient context for debugging
- Users MUST see friendly error messages, never stack traces or technical jargon
- Error responses MUST follow RFC 7807 Problem Details format
- Error responses MUST include correlation/trace IDs

**Enforcement**:
- Schema validation in API tests verifies error response format
- Integration tests MUST verify error responses
- Code review MUST verify try/catch blocks around external service calls

**Testability**:
- Pass: All error responses match schema, user-friendly messages for all error states
- Fail: Any error response missing required fields OR stack trace exposed

**Rationale**: Users judge software quality by how it handles the unhappy path. Consistent error format enables client-side error handling and debugging.

---

### IV. Observability Requirements (NON-NEGOTIABLE)

The app MUST be observable. When something goes wrong in production, there MUST be enough information to diagnose and fix it.

- Logs MUST use structured JSON format with standard fields
- Logs MUST have appropriate levels (debug, info, warning, error)
- Logs MUST NOT contain sensitive data (PII, tokens, passwords)
- Errors MUST be logged with context (user action, app state, correlation ID)
- Health check endpoint MUST exist at `/health` or `/healthz`

**Log Levels**:

| Level | Use For | Example |
|-------|---------|---------|
| `error` | Failures requiring attention | API call failed, database write error |
| `warning` | Recoverable issues | Retry succeeded, fallback used |
| `info` | Significant state changes | User logged in, sync completed |
| `debug` | Development diagnostics | Request/response bodies, state dumps |

**Enforcement**:
- Structured logging with required fields enforced by wrapper
- Code review MUST verify no PII in log statements
- Health check endpoint verified in integration tests

**Testability**:
- Pass: All errors logged with context, no PII in logs, health check responds
- Fail: Silent failures OR PII in logs OR missing correlation IDs

**Rationale**: You cannot fix what you cannot see. Production issues without observability become guessing games. Good observability reduces mean time to resolution.
