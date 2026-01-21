# Approved Domain Dependencies Registry

This template defines the format and initial list for approved domain layer dependencies. Projects using hexagonal architecture MAY allow these libraries in the domain layer without violating layer rules.

## Qualification Criteria

A library qualifies for domain layer usage when it meets BOTH criteria:

1. **Ubiquity (>80% adoption)**: The library is effectively a standard in its ecosystem
2. **Domain-relevance**: The library provides domain modeling capabilities (validation, value objects, type safety)

Libraries that handle I/O, network calls, or external system integration MUST NOT be approved for domain use.

---

## Registry by Language

### Python

| Library | Purpose | Rationale |
|---------|---------|-----------|
| `pydantic` | Data validation, settings management | De facto standard for Python data modeling; provides immutable models, validation, serialization without I/O |
| `attrs` | Class boilerplate reduction, immutability | Mature alternative to dataclasses with strict immutability support; no external dependencies |

### TypeScript

| Library | Purpose | Rationale |
|---------|---------|-----------|
| `zod` | Schema validation, type inference | Runtime validation with TypeScript type inference; no I/O, pure transformation |
| `decimal.js` | Precise decimal arithmetic | Financial/monetary calculations require precision beyond IEEE 754 floats |
| `uuid` | UUID generation and validation | Standard identifier format; pure computation, no I/O |

### Go

| Library | Purpose | Rationale |
|---------|---------|-----------|
| `go-playground/validator` | Struct validation | Most widely adopted Go validation library; declarative tag-based validation |
| `shopspring/decimal` | Precise decimal arithmetic | Arbitrary-precision decimals for financial calculations |
| `google/uuid` | UUID generation and validation | Google-maintained, widely adopted; pure computation |

### Rust

| Library | Purpose | Rationale |
|---------|---------|-----------|
| `serde` | Serialization framework | Ecosystem standard; derive macros only, no I/O in core |
| `rust_decimal` | Precise decimal arithmetic | Financial-grade decimal type; no external dependencies |
| `uuid` | UUID generation and validation | Standard identifier library; pure computation |

### Java/Kotlin

| Library | Purpose | Rationale |
|---------|---------|-----------|
| `jakarta.validation` | Bean validation | Java EE standard; annotation-based validation |
| `java.math.BigDecimal` | Precise decimal arithmetic | Standard library (included for completeness) |

---

## Addition Process

To add a library to this registry:

1. **Open PR** modifying this file
2. **Include rationale** demonstrating:
   - Ubiquity claim with evidence (download stats, ecosystem surveys)
   - Domain-relevance (no I/O, no external system coupling)
   - Comparison to alternatives considered
3. **Review** by constitution approvers
4. **Update linter configuration** to allow the new import

---

## Linter Enforcement

Projects SHOULD configure import linters to enforce domain layer restrictions:

| Stack | Tool | Configuration |
|-------|------|---------------|
| Python | `import-linter` | Contract with allowed modules list |
| TypeScript | ESLint `import/no-restricted-paths` | Allowlist in domain zone |
| Go | `go-cleanarch` | Custom allowed imports |
| Rust | `clippy` | Custom lint rules |

Example Python `import-linter` contract:

```toml
[tool.importlinter]
root_package = "myapp"

[[tool.importlinter.contracts]]
name = "Domain layer isolation"
type = "layers"
layers = ["domain", "application", "adapters", "infrastructure"]
containers = ["myapp"]

# Domain MAY import these approved libraries
[[tool.importlinter.contracts]]
name = "Approved domain dependencies"
type = "independence"
modules = ["myapp.domain"]
ignore_imports = ["pydantic", "attrs"]
```

---

## Version

This registry follows the constitution versioning policy. Changes to qualification criteria or removal of libraries require MINOR version bump. Adding new libraries requires PATCH version bump.
