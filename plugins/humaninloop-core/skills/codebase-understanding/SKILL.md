---
name: codebase-understanding
description: Techniques for analyzing and comprehending code structure. Use when exploring unfamiliar codebases, understanding architecture, or mapping system components. Essential for onboarding, code review, and impact analysis.
---

# Codebase Understanding

## Purpose

Provide systematic techniques for analyzing, comprehending, and mapping codebases. These techniques help build mental models of unfamiliar systems and support informed decision-making about changes.

## Core Principles

1. **Top-Down Then Bottom-Up**: Start with structure, then dive into details
2. **Follow the Data**: Trace how data flows through the system
3. **Find the Boundaries**: Identify modules, layers, and interfaces
4. **Map the Patterns**: Recognize recurring architectural patterns
5. **Document Your Model**: Write down your understanding

## Exploration Strategy

### Level 1: Project Structure

Start with the bird's-eye view:

```
1. Read README, CONTRIBUTING, docs/
2. Examine directory structure
3. Identify entry points (main, index, app)
4. Note configuration files
5. Check package.json, Cargo.toml, etc. for dependencies
```

**Key Questions:**
- What's the project's purpose?
- What technologies does it use?
- How is code organized?

### Level 2: Architecture

Identify the system's shape:

| Pattern | Signals | Implications |
|---------|---------|--------------|
| **Layered** | controllers/, services/, repos/ | Clear separation, call downward |
| **Modular** | features/, modules/ with self-contained code | Feature-based organization |
| **Microservices** | Multiple package.json, docker-compose | Distributed system |
| **Monolith** | Single entry, shared everything | Simpler deployment, tighter coupling |

**Key Questions:**
- What are the main components?
- How do they communicate?
- Where are the boundaries?

### Level 3: Key Flows

Trace critical paths through the code:

```
1. Pick a user action (e.g., "user logs in")
2. Find the entry point (route, handler)
3. Follow the call chain
4. Note data transformations
5. Identify external calls (DB, APIs)
6. Document the flow
```

### Level 4: Deep Dives

For specific areas:

```
1. Read the code carefully
2. Check tests for expected behavior
3. Look at git history for evolution
4. Find related documentation
5. Identify edge cases and error handling
```

## Mapping Techniques

### Entity Map

Document the data model:

```markdown
## Entities

| Entity | Location | Key Fields | Relationships |
|--------|----------|------------|---------------|
| User | src/models/user.ts | id, email, role | has_many Posts |
| Post | src/models/post.ts | id, title, author_id | belongs_to User |
```

### Component Map

Document system components:

```markdown
## Components

| Component | Purpose | Interfaces | Dependencies |
|-----------|---------|------------|--------------|
| AuthService | Handle authentication | login(), logout() | UserRepo, TokenService |
| UserRepo | User data access | find(), create() | Database |
```

### Flow Map

Document key flows:

```markdown
## Login Flow

1. POST /login → AuthController.login()
2. AuthController → AuthService.authenticate(email, password)
3. AuthService → UserRepo.findByEmail(email)
4. AuthService → PasswordService.verify(password, hash)
5. AuthService → TokenService.generate(user)
6. AuthController → Response with token
```

## Pattern Recognition

### Common Patterns to Look For

| Pattern | How to Identify | What It Means |
|---------|-----------------|---------------|
| **Repository** | Classes ending in Repo/Repository | Data access abstraction |
| **Service** | Classes ending in Service | Business logic layer |
| **Controller** | Classes handling HTTP | Request/response handling |
| **Factory** | create(), build() methods | Object creation |
| **Middleware** | Functions in request chain | Cross-cutting concerns |
| **Event-driven** | emit(), on(), subscribe() | Decoupled communication |

### Conventions to Note

| Aspect | What to Look For |
|--------|------------------|
| **Naming** | camelCase, PascalCase, snake_case |
| **File structure** | By feature, by layer, hybrid |
| **Error handling** | Exceptions, Result types, error codes |
| **Async patterns** | Promises, async/await, callbacks |
| **Testing approach** | Unit, integration, e2e locations |

## Investigation Tools

### Search Strategies

| Goal | Approach |
|------|----------|
| Find entity definitions | Grep for `class Entity`, `interface Entity`, `type Entity` |
| Find API endpoints | Grep for route decorators, router definitions |
| Find usages | Grep for function/class name |
| Find patterns | Glob for `**/pattern/**` |
| Trace flow | LSP go-to-definition, find-references |

### Reading Order

When exploring a new area:

```
1. Interface/type definitions (contracts)
2. Tests (expected behavior)
3. Public methods (API)
4. Private methods (implementation)
5. Edge cases and error paths
```

## Documentation Pattern

### Codebase Overview Template

```markdown
# Codebase Overview: {project_name}

## Purpose
{What does this system do?}

## Technology Stack
- Language: {language}
- Framework: {framework}
- Database: {database}
- Key dependencies: {list}

## Architecture
{Diagram or description of main components}

## Directory Structure
{Key directories and their purposes}

## Key Flows
{List of important user journeys with entry points}

## Conventions
{Naming, file structure, error handling patterns}

## Entry Points
{Where to start reading for different concerns}
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Random wandering** | No systematic approach | Follow exploration levels |
| **Premature deep dive** | Miss the big picture | Top-down first |
| **Assumptions** | Guess instead of verify | Read the actual code |
| **No documentation** | Knowledge stays in your head | Write it down |
| **Ignoring tests** | Miss expected behavior | Tests are documentation |

## When to Use These Techniques

- Onboarding to a new codebase
- Preparing for a code review
- Assessing impact of changes
- Debugging unfamiliar code
- Planning refactoring work
- Knowledge transfer sessions
