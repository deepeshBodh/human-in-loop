# Brownfield Analysis Mode

Detailed guidance for extracting entities, endpoints, and collision risks for planning.

## Entity Detection Heuristics

### By Framework

| Framework | File Pattern | Code Pattern |
|-----------|--------------|--------------|
| SQLAlchemy | `models/*.py` | `class X(Base):`, `db.Model` |
| Django | `*/models.py` | `class X(models.Model):` |
| Prisma | `schema.prisma` | `model X {` |
| TypeORM | `entities/*.ts` | `@Entity()` |
| Mongoose | `models/*.js` | `mongoose.Schema`, `new Schema` |
| GORM | `*_model.go` | `type X struct`, `gorm.Model` |
| ActiveRecord | `app/models/*.rb` | `class X < ApplicationRecord` |

### Generic Detection

If framework not identified, search for:
- Files named `*model*.{ts,py,go,java,rb}`
- Files named `*entity*.{ts,py,go,java,rb}`
- Classes with database-like field patterns

## Endpoint Detection Heuristics

### By Framework

| Framework | File Pattern | Code Pattern |
|-----------|--------------|--------------|
| Express | `routes/*.ts` | `router.get()`, `app.post()` |
| FastAPI | `api/*.py` | `@router.get()`, `@app.post()` |
| Django | `urls.py` | `path()`, `url()` |
| Flask | `routes/*.py` | `@app.route()`, `@bp.route()` |
| Gin | `*_handler.go` | `r.GET()`, `r.POST()` |
| Rails | `routes.rb` | `get`, `post`, `resources` |
| Spring | `*Controller.java` | `@GetMapping`, `@PostMapping` |

### Generic Detection

If framework not identified, search for:
- HTTP method names: GET, POST, PUT, PATCH, DELETE
- URL path patterns: `/api/`, `/v1/`
- Router patterns: `route`, `path`, `endpoint`

## Collision Risk Assessment

### Entity Collision Types

| Type | Description | Risk | Action |
|------|-------------|------|--------|
| **Exact Match** | Same name, same fields | Low | Reuse existing |
| **Compatible Extend** | Same name, additive fields | Medium | Extend existing |
| **Semantic Match** | Different name, same concept | Medium | Clarify or map |
| **Conflict** | Same name, incompatible fields | High | Escalate |

### Endpoint Collision Types

| Type | Description | Risk | Action |
|------|-------------|------|--------|
| **Exact Match** | Same path + method | High | Escalate |
| **Path Conflict** | Same path, different method | Low | Compatible |
| **Resource Extension** | Same resource, new action | Low | Auto-extend |
| **Pattern Conflict** | Path pattern overlap | Medium | Review |

## Output Format: Codebase Inventory

```json
{
  "project_info": {
    "type": "node",
    "framework": "express",
    "orm": "prisma",
    "architecture_pattern": "monolith_layered"
  },
  "entities": [
    {
      "name": "User",
      "file_path": "src/models/user.ts",
      "line_number": 10,
      "fields": [
        {"name": "id", "type": "String", "required": true},
        {"name": "email", "type": "String", "required": true}
      ],
      "relationships": [
        {"type": "has_many", "target": "Task"}
      ]
    }
  ],
  "endpoints": [
    {
      "method": "GET",
      "path": "/api/users",
      "file_path": "src/routes/users.ts:25",
      "handler": "listUsers",
      "related_entity": "User"
    }
  ],
  "collision_risks": [
    {
      "type": "entity",
      "spec_item": "Session",
      "existing_item": "Session",
      "compatibility": "compatible_extend",
      "risk_level": "medium",
      "recommendation": "Extend existing Session with new fields"
    }
  ]
}
```

## Brownfield Status Markers

When documenting entities in data-model.md, use these markers:

| Marker | Meaning | Action |
|--------|---------|--------|
| `[NEW]` | No existing entity | Create from scratch |
| `[EXTENDS EXISTING]` | Existing entity, adding fields | Extend with migration |
| `[REUSES EXISTING]` | Existing entity, no changes | Reference directly |

Example:
```markdown
## User [EXTENDS EXISTING]

Extends existing `User` entity at `src/models/user.ts`.

**New Fields:**
- `lastLoginAt`: DateTime (optional)
- `preferences`: JSON (optional)
```

## Scanning Strategy

1. **Identify ORM first** - Determines where to look for entities
2. **Scan model directories** - Extract entity definitions
3. **Scan route directories** - Extract endpoint definitions
4. **Cross-reference** - Link endpoints to entities
5. **Compare with spec** - Generate collision risks
