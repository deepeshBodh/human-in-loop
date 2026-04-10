# Emergent Ceiling Patterns

Beyond the essential floor, identify **existing good patterns** worth codifying from the codebase.

## Discovery Process

1. **Read codebase analysis** - Look for "Strengths to Preserve" section
2. **Identify patterns** - Naming conventions, architecture patterns, error formats
3. **Codify as principles** - With enforcement mechanisms

## Common Pattern Categories

Look for these patterns in brownfield analysis and codify if present:

| Pattern Category | What to Look For | Example Principle |
|------------------|------------------|-------------------|
| **Code Quality** | Documentation requirements, API annotations, deprecation handling | "All public APIs MUST have documentation comments" |
| **Architecture** | Layer rules, dependency injection, module boundaries | "Controllers MUST NOT directly access repositories" |
| **API Design** | Response formats, versioning, pagination | "API responses MUST follow RFC 7807 Problem Details" |
| **Authorization** | Role-based access, permission checks | "All endpoints MUST validate user permissions" |
| **Resilience** | Retry policies, circuit breakers, timeouts | "External calls MUST use retry with exponential backoff" |
| **Configuration** | Strongly-typed options, feature flags | "Configuration MUST use strongly-typed options pattern" |
| **Error Handling** | Error display guidelines, data resilience, user-friendly messages | "Users MUST see actionable error messages, never stack traces" |
| **Observability** | Log levels, context requirements, crash reporting | "Errors MUST be logged with context sufficient for debugging" |
| **Product Analytics** | Event categories, naming conventions, funnel tracking | "Events MUST follow `{object}_{action}` naming in snake_case" |
| **Naming Conventions** | File/class/variable naming, directory structure | "Files MUST use snake_case, classes MUST use PascalCase" |

---

## Example Principles

### Code Quality Standards

All production code MUST meet documentation and annotation requirements.

- Public APIs MUST have XML documentation comments (or JSDoc, docstrings, etc.)
- API endpoints MUST declare response types (e.g., `[ProducesResponseType]`, OpenAPI annotations)
- Deprecated endpoints MUST return warning headers and log deprecation notices
- Configuration MUST use strongly-typed options pattern (no magic strings)

**Enforcement**:
- CI runs documentation coverage check and warns on missing docs
- OpenAPI spec generated from annotations and validated
- Linter rules enforce no magic strings in configuration

**Testability**:
- Pass: All public APIs documented, all endpoints annotated, zero magic strings
- Fail: Missing documentation on public API OR missing response type annotation

**Rationale**: Documentation enables discoverability and correct usage. Annotations enable tooling and client generation. Strongly-typed configuration prevents runtime errors.

---

### Error Response Format

API error responses MUST follow the established format.

- Error responses MUST include `code`, `message`, and `details` fields
- Error codes MUST use the `ERR_DOMAIN_ACTION` naming convention
- Stack traces MUST NOT be exposed in production responses

**Enforcement**:
- Schema validation in API tests
- Code review checklist item

**Testability**:
- Pass: All error responses match schema
- Fail: Any error response missing required fields

**Rationale**: Consistent error format enables client-side error handling and debugging. Pattern established in existing codebase and proven effective.

---

### Single Responsibility & Layer Discipline

Each module, service, and function MUST have one clear purpose.

- Domain layer handles business logic, not infrastructure concerns
- Adapters handle external system integration, not business logic
- Models define data shape, not behavior
- No "utils" or "helpers" modules—find the right home or create a named module

**Clean Architecture Layers**:

Dependencies MUST flow inward—outer layers depend on inner layers, never reverse:

| Layer | Location | MAY import | MUST NOT import |
|-------|----------|------------|-----------------|
| Domain | `src/domain/` | stdlib + approved domain deps | application, adapters, infrastructure |
| Application | `src/application/` | domain, port interfaces | adapters, infrastructure |
| Adapters | `src/adapters/` | application, domain, ports | other adapters directly |
| Infrastructure | `src/infrastructure/` | application (for DI wiring) | domain logic |

**Code Quality Metrics**:

| Metric | Limit | Enforcement |
|--------|-------|-------------|
| Cyclomatic complexity | ≤10 per function | Linter rule in CI |
| Function parameters | ≤5 (use models for more) | Code review |
| File length | ≤300 lines SHOULD, ≤500 MUST | Code review |
| Nesting depth | ≤4 levels | Code review |

**Enforcement**:
- Linter complexity rule configured with `max-complexity = 10` (CI blocks on violation)
- Project structure enforces separation: `domain/`, `application/`, `adapters/`
- Code review MUST reject PRs that mix layers inappropriately
- Type checker strict mode catches type leakage across boundaries

**Testability**:
- Pass: All imports respect layer rules, complexity ≤10, no layer violations
- Fail: Any import from inner to outer layer OR complexity >10

**Rationale**: Clear boundaries make code easier to test, understand, and modify. Mixed responsibilities compound complexity over time.

---

### Dependency Discipline & Port Interfaces

External dependencies MUST be justified and isolated behind port interfaces.

- New dependencies MUST solve a problem that cannot be reasonably solved in-house
- External service calls MUST be isolated behind port interfaces (enable swapping)
- Version pins MUST be explicit in lock files
- Dependency updates MUST be intentional, not automatic

**Domain Layer Dependencies**:

The domain layer MAY import libraries from the approved domain dependencies registry. These are gold standard libraries (>80% ecosystem adoption) that provide domain modeling capabilities without I/O coupling. See `authoring-constitution/RECOMMENDED-PATTERNS.md` for qualification criteria and the full registry at `${CLAUDE_PLUGIN_ROOT}/templates/approved-domain-deps.md`.

**Port Interface Requirements**:

All external service calls MUST go through port interfaces:

| External Service | Port Interface Location | Adapter Location |
|------------------|------------------------|------------------|
| AI Providers | `application/ports/outbound/ai_provider.py` | `adapters/outbound/ai/` |
| Storage | `application/ports/outbound/storage.py` | `adapters/outbound/storage/` |
| Database | `application/ports/outbound/repository.py` | `adapters/outbound/persistence/` |
| External APIs | `application/ports/outbound/[service].py` | `adapters/outbound/[service]/` |

**Port Design Rules**:
- Port interfaces MUST be defined as `Protocol` or `ABC` classes
- Port interfaces MUST use domain types in signatures, not SDK types
- Adapters MUST implement port interfaces, not extend them
- One port per logical capability (not per provider)
- Async methods for all I/O operations

**Enforcement**:
- Security scanner blocks merge on known vulnerabilities
- Lock file committed to repo ensures reproducible builds
- Code review MUST justify new dependencies in PR description
- Code review MUST verify external calls use port interfaces

**Testability**:
- Pass: All external calls through ports, no direct SDK usage in domain/application
- Pass: Approved domain dependencies registry maintained and linter configured
- Fail: Any external SDK imported in domain layer OR direct HTTP call without port
- Fail: Domain imports library not in approved registry

**Rationale**: Each dependency is a liability—maintenance burden, security surface, potential breaking changes. Isolation via ports enables evolution without rewrite and makes the codebase testable without hitting real external services.

---

### Product Analytics

Product analytics MUST be systematic, consistent, and actionable. Every feature MUST be instrumented to measure adoption, engagement, and conversion.

**Mandatory Event Categories**:

| Category | Description | When to Track |
|----------|-------------|---------------|
| Screen View | User navigates to a screen | Every screen entry |
| User Action | Intentional user interaction | Taps, clicks with business meaning |
| Conversion | Funnel milestone achieved | Signup, onboarding, first value |
| Error | User-facing error occurred | Errors shown to user (not crashes) |
| Feature | Feature-specific engagement | Feature used meaningfully |

**Event Naming Convention**:

All events MUST follow the `{object}_{action}` pattern in `snake_case`:

| Pattern | Format | Examples |
|---------|--------|----------|
| Screen views | `screen_viewed` | Differentiate via properties |
| User actions | `{element}_{action}` | `continue_button_tapped`, `item_selected` |
| Conversions | `{milestone}_completed` | `onboarding_completed`, `signup_completed` |
| Features | `{feature}_{action}` | `ai_suggestion_accepted`, `photo_uploaded` |

**Required Event Properties**:

All events MUST include:
- `timestamp` - Event occurrence time
- `user_id` - Anonymized user identifier
- `session_id` - Current session identifier
- `app_version` - Semantic version
- `platform` - Platform identifier

**Enforcement**:
- Specs MUST include "Analytics Events" section with event tables
- Code review MUST verify events match specification
- No PII in any event properties (automated scan if possible)

**Testability**:
- Pass: All specified events firing, properties complete, no PII
- Fail: Missing events OR incomplete properties OR PII detected

**Rationale**: Product analytics enables data-driven decisions about feature development and user experience optimization. Consistent naming enables cross-feature analysis.

---

### Naming Conventions

All code artifacts MUST follow consistent naming conventions for discoverability and maintainability.

| Item | Convention | Example |
|------|------------|---------|
| Files | snake_case | `user_provider.dart`, `auth_service.py` |
| Classes | PascalCase | `UserProvider`, `AuthService` |
| Variables/functions | camelCase | `getUserById()`, `isAuthenticated` |
| Constants | SCREAMING_SNAKE or camelCase | `MAX_RETRIES`, `apiTimeout` |
| Interfaces/Protocols | IPascalCase or PascalCase | `IUserRepository`, `UserRepository` |
| Test files | {source}_test.{ext} | `user_service_test.dart` |
| Config files | kebab-case or snake_case | `app-config.yaml`, `database_config.py` |

**Directory Naming**:
- Feature directories: `kebab-case` or `snake_case` (consistent within project)
- Layer directories: lowercase (`domain/`, `application/`, `adapters/`)
- Test directories mirror source: `test/unit/services/` → `src/services/`

**Enforcement**:
- Linter rules configured for naming violations
- Code review MUST reject non-compliant names
- New developers MUST be onboarded to conventions

**Testability**:
- Pass: All names follow conventions, test files mirror source structure
- Fail: Any naming violation OR test file in wrong location

**Rationale**: Consistent naming enables quick navigation, reduces cognitive load, and makes codebase searchable. Developers can predict file locations without searching.
