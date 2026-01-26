---
name: analysis-codebase
description: >
  This skill MUST be invoked when the user says "analyze codebase", "scan project",
  "detect tech stack", or "codebase analysis". SHOULD also invoke when user mentions
  "existing code", "collision risk", "brownfield", or "project context". Also used
  by plan-architect agents during discovery phase.
---

# Analyzing Codebase

## Overview

Systematically analyze existing codebases to extract structural information. Supports three modes: Context (project characteristics), Brownfield (entities and collision risks), and Setup-Brownfield (comprehensive analysis for `/humaninloop:setup`).

## When to Use

- Setting up constitution on existing codebase (brownfield projects)
- Planning new features against existing code
- Understanding tech stack before making changes
- Detecting collision risks for new entities or endpoints
- Running `/humaninloop:setup` on projects with existing code
- Gathering project context for governance decisions

## When NOT to Use

- **Greenfield projects**: No existing code to analyze; start with `humaninloop:authoring-constitution` directly
- **Single-file scripts**: No architectural patterns to extract
- **Documentation-only review**: Use standard file reading instead
- **Before project directory exists**: Nothing to analyze yet
- **When user provides complete context**: Skip analysis if user already documented tech stack and patterns

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Assuming framework | Guessing without evidence | Verify with code patterns |
| Missing directories | Only checking standard paths | Projects vary, explore |
| Over-extracting | Analyzing every file | Focus on config and patterns |
| Ignoring governance | Missing existing decisions | Check README, CLAUDE.md, ADRs |
| Inventing findings | Documenting assumptions | Only report what is found |

## Mode Selection

| Mode | When to Use | Output |
|------|-------------|--------|
| **Context** | Setting up constitution, understanding project DNA | Markdown report for humans |
| **Brownfield** | Planning new features against existing code | JSON inventory with collision risks |
| **Setup-Brownfield** | `/humaninloop:setup` on existing codebase | `codebase-analysis.md` with inventory + assessment |

## Project Type Detection

Identify project type from package manager files:

| File | Project Type |
|------|--------------|
| `package.json` | Node.js/JavaScript/TypeScript |
| `pyproject.toml` / `requirements.txt` | Python |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `pom.xml` / `build.gradle` | Java |
| `Gemfile` | Ruby |
| `pubspec.yaml` | Flutter/Dart |

## Framework Detection

### Web Frameworks

| Framework | Indicators |
|-----------|------------|
| **Express** | `express()`, `router.get()`, `app.use()` |
| **FastAPI** | `@app.get()`, `FastAPI()`, `APIRouter` |
| **Django** | `urls.py`, `views.py`, `models.py` pattern |
| **Flask** | `@app.route()`, `@bp.route()` |
| **Rails** | `routes.rb`, `app/models/`, `app/controllers/` |
| **Spring** | `@RestController`, `@GetMapping`, `@Entity` |
| **Gin/Echo** | `r.GET()`, `e.GET()` |

### ORM/Database Frameworks

| Framework | Indicators |
|-----------|------------|
| **Prisma** | `schema.prisma`, `@prisma/client` |
| **TypeORM** | `@Entity()`, `@Column()`, `DataSource` |
| **SQLAlchemy** | `Base`, `db.Model`, `Column()` |
| **Django ORM** | `models.Model`, `models.CharField` |
| **GORM** | `gorm.Model`, `db.AutoMigrate` |
| **Mongoose** | `mongoose.Schema`, `new Schema({` |
| **ActiveRecord** | `ApplicationRecord`, `has_many` |

## Architecture Pattern Recognition

| Pattern | Indicators |
|---------|------------|
| **Layered** | `src/models/`, `src/services/`, `src/controllers/` |
| **Feature-based** | `src/auth/`, `src/users/`, `src/tasks/` |
| **Microservices** | Multiple package files, docker compose |
| **Serverless** | `serverless.yml`, `lambda/`, `functions/` |
| **MVC** | `models/`, `views/`, `controllers/` |
| **Clean/Hexagonal** | `domain/`, `application/`, `infrastructure/` |

## Mode: Context Gathering

For constitution authoring - gather broad project characteristics.

**What to Extract:**
- Tech stack with versions
- Linting/formatting conventions
- CI/CD quality gates
- Team signals (test coverage, required approvals, CODEOWNERS)
- Existing governance docs (CODEOWNERS, ADRs, CONTRIBUTING.md)

**Output**: Project Context Report (markdown)

See [references/CONTEXT-GATHERING.md](references/CONTEXT-GATHERING.md) for detailed guidance.

## Mode: Brownfield Analysis

For planning - extract structural details for collision detection.

**What to Extract:**
- Entities with fields and relationships
- Endpoints with handlers
- Collision risks against proposed spec

**Output**: Codebase Inventory (JSON)

See [references/BROWNFIELD-ANALYSIS.md](references/BROWNFIELD-ANALYSIS.md) for detailed guidance.

## Mode: Setup Brownfield

For `/humaninloop:setup` - comprehensive analysis combining Context + Brownfield with Essential Floor assessment.

**What to Extract:**
- Everything from Context mode (tech stack, conventions, architecture)
- Everything from Brownfield mode (entities, relationships)
- Essential Floor assessment (Security, Testing, Error Handling, Observability)
- Inconsistencies and strengths assessment

**Output**: `.humaninloop/memory/codebase-analysis.md` following `codebase-analysis-template.md`

### Essential Floor Analysis

Assess each of the four essential floor categories:

#### Security Assessment

| Check | How to Detect | Status Values |
|-------|---------------|---------------|
| Auth at boundaries | Middleware patterns (`authenticate`, `authorize`, `requireAuth`) | present/partial/absent |
| Secrets from env | `.env.example` exists, no hardcoded credentials in code | present/partial/absent |
| Input validation | Schema validation libraries, input checking patterns | present/partial/absent |

**Indicators to search:**
```bash
# Auth middleware
grep -r "authenticate\|authorize\|requireAuth\|isAuthenticated" src/ 2>/dev/null

# Environment variables
ls .env.example .env.sample 2>/dev/null
grep -r "process.env\|os.environ\|os.Getenv" src/ 2>/dev/null

# Validation
grep -r "zod\|yup\|joi\|pydantic\|validator" package.json pyproject.toml 2>/dev/null
```

#### Testing Assessment

| Check | How to Detect | Status Values |
|-------|---------------|---------------|
| Test framework configured | Config files (`jest.config.*`, `pytest.ini`, `vitest.config.*`) | present/partial/absent |
| Test files present | Files matching `*.test.*`, `*_test.*`, `test_*.*` | present/partial/absent |
| CI runs tests | Test commands in workflow files | present/partial/absent |

**Indicators to search:**
```bash
# Test config
ls jest.config.* vitest.config.* pytest.ini pyproject.toml 2>/dev/null

# Test files
find . -name "*.test.*" -o -name "*_test.*" -o -name "test_*.*" 2>/dev/null | head -5

# CI test commands
grep -r "npm test\|yarn test\|pytest\|go test" .github/workflows/ 2>/dev/null
```

#### Error Handling Assessment

| Check | How to Detect | Status Values |
|-------|---------------|---------------|
| Explicit error types | Custom error classes/types defined | present/partial/absent |
| Context preservation | Error messages include context, stack traces logged | present/partial/absent |
| Appropriate status codes | API responses use correct HTTP status codes | present/partial/absent |

**Indicators to search:**
```bash
# Custom errors
grep -r "class.*Error\|extends Error\|Exception" src/ 2>/dev/null | head -5

# Error logging
grep -r "error.*context\|error.*stack\|logger.error" src/ 2>/dev/null | head -3

# Status codes
grep -r "status(4\|status(5\|HttpStatus\|status_code" src/ 2>/dev/null | head -3
```

#### Observability Assessment

| Check | How to Detect | Status Values |
|-------|---------------|---------------|
| Structured logging | Logger config (winston, pino, structlog, logrus) | present/partial/absent |
| Correlation IDs | Request ID middleware, trace ID patterns | present/partial/absent |
| No PII in logs | Log sanitization, no email/password in log statements | present/partial/absent |

**Indicators to search:**
```bash
# Logger config
grep -r "winston\|pino\|structlog\|logrus\|zap" package.json pyproject.toml go.mod 2>/dev/null

# Correlation IDs
grep -r "requestId\|correlationId\|traceId\|x-request-id" src/ 2>/dev/null | head -3

# PII check (negative - should NOT find these in logs)
grep -r "logger.*email\|logger.*password\|log.*password" src/ 2>/dev/null
```

### Setup-Brownfield Quality Checklist

Before finalizing setup-brownfield analysis:

- [ ] Project identity complete (name, language, framework, entry points)
- [ ] Directory structure documented with purposes
- [ ] Architecture pattern identified with evidence
- [ ] Naming conventions documented (files, variables, functions, classes)
- [ ] All four Essential Floor categories assessed
- [ ] Domain entities extracted with relationships
- [ ] External dependencies documented
- [ ] Strengths to preserve identified (minimum 2-3)
- [ ] Inconsistencies documented with severity
- [ ] Recommendations provided for constitution focus

## Detection Script

Run the automated detection script for fast, deterministic stack identification:

```bash
bash scripts/detect-stack.sh /path/to/project
```

**Output:**
```json
{
  "project_type": "nodejs",
  "package_manager": "npm",
  "frameworks": ["express"],
  "orms": ["prisma"],
  "architecture": ["feature-based"],
  "ci_cd": ["github-actions"],
  "files_found": {...}
}
```

The script detects:
- **Project type**: nodejs, python, go, rust, java, ruby, flutter, elixir
- **Package manager**: npm, yarn, pnpm, pip, poetry, cargo, etc.
- **Frameworks**: express, fastapi, django, nextjs, gin, rails, spring-boot, etc.
- **ORMs**: prisma, typeorm, sqlalchemy, mongoose, gorm, activerecord, etc.
- **Architecture**: clean-architecture, mvc, layered, feature-based, serverless, microservices
- **CI/CD**: github-actions, gitlab-ci, jenkins, circleci, etc.

**Usage pattern:**
1. Run script first for deterministic baseline
2. Use script output to guide deeper LLM analysis
3. Script findings are ground truth; LLM adds nuance

## Manual Detection Commands

For cases where script detection is insufficient:

```bash
# Tech stack detection
cat package.json | jq '{name, engines, dependencies}'
cat pyproject.toml
cat .tool-versions .nvmrc .python-version 2>/dev/null

# Architecture detection
ls -d src/domain src/application src/features 2>/dev/null

# CI/CD detection
ls .github/workflows/*.yml .gitlab-ci.yml 2>/dev/null

# Governance detection
ls CODEOWNERS .github/CODEOWNERS docs/CODEOWNERS 2>/dev/null
cat CODEOWNERS 2>/dev/null | head -20

# Test structure
ls -d test/ tests/ spec/ __tests__/ 2>/dev/null
```

## Quality Checklist

Before finalizing analysis:

**Both Modes:**
- [ ] Project type and framework correctly identified
- [ ] Architecture pattern documented
- [ ] File paths cited for all findings

**Context Mode:**
- [ ] Existing linting/formatting config extracted
- [ ] CI quality gates analyzed
- [ ] Existing governance docs checked (CODEOWNERS, ADRs, CONTRIBUTING.md)
- [ ] Approvers identified (from CODEOWNERS or team structure)
- [ ] Recommendations provided

**Brownfield Mode:**
- [ ] All entity directories scanned
- [ ] All route directories scanned
- [ ] Collision risks classified by severity

**Setup-Brownfield Mode:**
- [ ] All Context Mode checks completed
- [ ] All four Essential Floor categories assessed
- [ ] Strengths and inconsistencies documented
- [ ] Output written to `.humaninloop/memory/codebase-analysis.md`

## Related Skills

- **For brownfield constitutions**: **REQUIRED:** Use humaninloop:brownfield-constitution after analysis
- **For greenfield projects**: **OPTIONAL:** Use humaninloop:authoring-constitution directly
- **For validation**: **OPTIONAL:** Use humaninloop:validation-constitution after constitution creation
