# Recommended Patterns for Greenfield Projects

Beyond the Essential Floor (Security, Testing, Error Handling, Observability), greenfield constitutions SHOULD include architectural principles that establish good foundations from day one.

## Why Architectural Principles Matter for Greenfield

Starting with architectural discipline is easier than retrofitting it later. These patterns:
- Prevent coupling that becomes painful to untangle
- Enable testing without complex mocks or real dependencies
- Make the codebase navigable as it grows
- Allow swapping implementations without rewriting business logic

## Recommended Architectural Principles

Include these principles in greenfield constitutions unless the project has specific reasons not to.

---

### V. Hexagonal Architecture (Ports & Adapters)

The application core MUST be isolated from external concerns. Dependencies flow inward—outer layers depend on inner layers, never reverse.

**Layer Structure**:

| Layer | Purpose | Location | MAY Import | MUST NOT Import |
|-------|---------|----------|------------|-----------------|
| **Domain** | Business logic, entities, value objects | `src/domain/` | Standard library + approved domain deps | application, adapters, infrastructure |
| **Application** | Use cases, orchestration, port definitions | `src/application/` | domain, port interfaces | adapters, infrastructure |
| **Adapters** | External system integration (DB, APIs, UI) | `src/adapters/` | application, domain, ports | other adapters directly |
| **Infrastructure** | DI wiring, configuration, entry points | `src/infrastructure/` | all layers (for wiring) | domain logic directly |

**Approved Domain Dependencies**:

The domain layer MAY import libraries from the approved domain dependencies registry when they meet qualification criteria:

1. **Ubiquity (>80% adoption)**: Effectively a standard in the ecosystem
2. **Domain-relevance**: Provides domain modeling capabilities without I/O

Common approved libraries by language:

| Language | Approved Libraries | Purpose |
|----------|-------------------|---------|
| Python | `pydantic`, `attrs` | Data validation, immutable models |
| TypeScript | `zod`, `decimal.js`, `uuid` | Schema validation, precise arithmetic, identifiers |
| Go | `go-playground/validator`, `shopspring/decimal`, `google/uuid` | Struct validation, decimals, identifiers |
| Rust | `serde`, `rust_decimal`, `uuid` | Serialization, decimals, identifiers |

See full registry at `${CLAUDE_PLUGIN_ROOT}/templates/approved-domain-deps.md`.

**Port Interface Requirements**:

All external service interactions MUST go through port interfaces:

- Port interfaces MUST be defined as `Protocol` (Python), `interface` (TypeScript/Go), or `trait` (Rust)
- Port interfaces MUST use domain types in signatures, not SDK/library types
- Adapters MUST implement port interfaces
- One port per logical capability (e.g., `StoragePort`), not per provider (e.g., `S3Adapter`, `GCSAdapter`)

**Example Port Structure**:

```
src/
├── domain/
│   ├── entities/
│   └── value_objects/
├── application/
│   ├── use_cases/
│   └── ports/
│       ├── inbound/      # Driving ports (API, CLI)
│       └── outbound/     # Driven ports (DB, external APIs)
├── adapters/
│   ├── inbound/          # Controllers, CLI handlers
│   └── outbound/         # Repository implementations, API clients
└── infrastructure/
    ├── config/
    └── di/               # Dependency injection wiring
```

**Enforcement**:
- Import linter rules configured to detect layer violations (e.g., `import-linter` for Python, ESLint import rules for TypeScript)
- CI blocks merge on any import from inner to outer layer
- Domain layer allowlist derived from approved-domain-deps.md registry
- CI blocks merge on domain imports not in approved registry
- Code review MUST verify new code respects layer boundaries
- Code review MUST verify domain dependency additions meet qualification criteria
- Type checker strict mode catches type leakage across boundaries

**Testability**:
- Pass: All imports respect layer rules, domain imports only approved dependencies
- Pass: All use cases testable with mock adapters (no real DB/API needed)
- Fail: Domain imports from adapters OR application imports infrastructure
- Fail: Domain imports unapproved library not in registry

**Rationale**: Hexagonal architecture isolates business logic from infrastructure concerns. This enables testing without real databases or APIs, swapping implementations (e.g., switching from PostgreSQL to MongoDB), and reasoning about business rules without infrastructure noise. The cost is additional abstraction; the benefit is long-term maintainability.

---

### VI. Single Responsibility & Module Boundaries

Each module, class, and function MUST have one clear purpose. When a component has multiple reasons to change, it should be split.

**Module Responsibility Rules**:

- Domain layer handles business logic, not infrastructure concerns
- Adapters handle external system integration, not business logic
- Models define data shape; behavior belongs in services or use cases
- No "utils" or "helpers" modules—find the right home or create a named module

**Code Quality Metrics**:

| Metric | Guideline | Limit | Enforcement |
|--------|-----------|-------|-------------|
| Cyclomatic complexity | Per function | ≤10 | Linter rule, CI blocks |
| Function parameters | Use models for more | ≤5 | Code review |
| Function length | Lines of code | ≤40 SHOULD, ≤60 MUST | Linter warning/error |
| File length | Lines of code | ≤300 SHOULD, ≤500 MUST | Code review |
| Nesting depth | Levels of indentation | ≤4 | Code review |

**Enforcement**:
- Linter complexity rule configured (e.g., `max-complexity = 10`)
- CI blocks on complexity violations
- Code review MUST reject PRs that mix responsibilities inappropriately
- Quarterly review of module boundaries for drift

**Testability**:
- Pass: All functions ≤10 complexity, no module mixing concerns
- Pass: Each class/module testable in isolation
- Fail: Complexity >10 OR file >500 lines without exception

**Rationale**: Single responsibility makes code easier to test, understand, and modify. Mixed responsibilities compound complexity over time. When a module cannot be named in one sentence, it is doing too much.

---

### VII. Dependency Discipline

External dependencies MUST be justified, minimal, and isolated. Every dependency is a liability—maintenance burden, security surface, potential breaking changes.

**Dependency Rules**:

- New dependencies MUST be justified in PR description
- Dependencies MUST be pinned to specific versions in lock files
- External service calls MUST go through port interfaces (see Hexagonal Architecture)
- Transitive dependencies MUST be audited for known vulnerabilities

**Dependency Evaluation Criteria**:

Before adding a dependency, evaluate:

| Question | Red Flag |
|----------|----------|
| Can this be reasonably implemented in-house? | Yes, and it's < 100 lines |
| Is the dependency actively maintained? | No commits in 12+ months |
| Does it have known vulnerabilities? | Yes, unpatched |
| Does it pull in many transitive dependencies? | > 10 transitive deps |
| Is the license compatible? | GPL in proprietary project |

**Enforcement**:
- Dependency scanner runs in CI (e.g., `pip-audit`, `npm audit`, `cargo audit`)
- CI blocks merge on known high/critical vulnerabilities
- Lock file MUST be committed to repository
- Code review MUST verify justification for new dependencies

**Testability**:
- Pass: All dependencies pinned, zero high/critical vulnerabilities
- Pass: All external calls go through port interfaces
- Fail: Unpinned dependency OR critical vulnerability OR direct SDK usage in domain

**Rationale**: Dependencies are borrowed code with borrowed problems. Each one increases attack surface, maintenance burden, and upgrade complexity. Isolation via ports enables swapping implementations without rewriting business logic.

---

## Principle Numbering

When including these in a constitution:

- Essential Floor principles are I-IV (Security, Testing, Error Handling, Observability)
- Recommended architectural principles start at V
- Adjust numbering based on which patterns you include

## Tailoring for Your Stack

These patterns apply universally but implementation details vary:

| Stack | Import Linter | Complexity Checker | Dependency Audit | Domain Allowlist Config |
|-------|---------------|-------------------|------------------|------------------------|
| Python | `import-linter` | `ruff` (C901) | `pip-audit` | `pyproject.toml` contracts |
| TypeScript | ESLint `import/no-restricted-paths` | ESLint `complexity` | `npm audit` | `.eslintrc` zones |
| Go | `go-cleanarch` | `gocyclo` | `govulncheck` | `.go-cleanarch.yaml` |
| Rust | Custom clippy rules | `clippy` | `cargo audit` | `clippy.toml` |
| Java | ArchUnit | SonarQube | OWASP Dependency-Check | ArchUnit rules |

---

## When to Skip Architectural Principles

These patterns add abstraction. Consider skipping for:

- **Prototypes/spikes**: Code you'll throw away in < 1 month
- **Scripts/tools**: Single-file utilities with no business logic
- **Extremely simple services**: < 500 lines total, single responsibility

Even then, the Essential Floor (Security, Testing, Error Handling, Observability) still applies.
