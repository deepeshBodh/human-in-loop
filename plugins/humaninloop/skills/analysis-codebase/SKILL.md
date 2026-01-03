---
name: analysis-codebase
description: Analyze existing codebases for tech stack, conventions, entities, and patterns. Use when scanning projects for context, brownfield analysis, or when you see "tech stack", "codebase analysis", "existing code", "collision risk", "brownfield", or "project context".
---

# Analyzing Codebase

## Purpose

Systematically analyze existing codebases to extract structural information. Supports two modes:

1. **Context Mode**: Gather project characteristics to inform constitution authoring
2. **Brownfield Mode**: Extract entities, endpoints, and collision risks for planning

## Mode Selection

| Mode | When to Use | Output |
|------|-------------|--------|
| **Context** | Setting up constitution, understanding project DNA | Markdown report for humans |
| **Brownfield** | Planning new features against existing code | JSON inventory with collision risks |

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
- Team signals (test coverage, required approvals)
- Existing governance docs

**Output**: Project Context Report (markdown)

See [CONTEXT-GATHERING.md](CONTEXT-GATHERING.md) for detailed guidance.

## Mode: Brownfield Analysis

For planning - extract structural details for collision detection.

**What to Extract:**
- Entities with fields and relationships
- Endpoints with handlers
- Collision risks against proposed spec

**Output**: Codebase Inventory (JSON)

See [BROWNFIELD-ANALYSIS.md](BROWNFIELD-ANALYSIS.md) for detailed guidance.

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
- [ ] Existing governance docs checked
- [ ] Recommendations provided

**Brownfield Mode:**
- [ ] All entity directories scanned
- [ ] All route directories scanned
- [ ] Collision risks classified by severity

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Assuming framework** | Guessing without evidence | Verify with code patterns |
| **Missing directories** | Only checking standard paths | Projects vary, explore |
| **Over-extracting** | Analyzing every file | Focus on config and patterns |
| **Ignoring governance** | Missing existing decisions | Check README, CLAUDE.md, ADRs |
| **Inventing findings** | Documenting assumptions | Only report what's found |
