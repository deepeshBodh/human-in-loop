# Relationship Patterns

Reference documentation for modeling entity relationships including cardinality, join entities, and documentation formats.

## Relationship Types

| Type | Cardinality | Example |
|------|-------------|---------|
| **One-to-One** | 1:1 | User <-> Profile |
| **One-to-Many** | 1:N | User <-> Tasks |
| **Many-to-Many** | N:M | Users <-> Projects |

## One-to-Many (1:N) Pattern

The most common relationship type. One entity owns many of another.

### Documentation Format

```markdown
### User -> Tasks (1:N)

| Aspect | Value |
|--------|-------|
| **Type** | One-to-Many |
| **From** | User (one) |
| **To** | Task (many) |
| **Foreign Key** | task.userId |
| **Required** | Task requires User |
| **On Delete** | Cascade (delete tasks) |
```

### Common 1:N Examples

| Parent | Child | Foreign Key | On Delete |
|--------|-------|-------------|-----------|
| User | Task | task.userId | Cascade |
| User | Comment | comment.authorId | Cascade |
| Project | Task | task.projectId | Cascade |
| Category | Product | product.categoryId | Set Null |
| Folder | Document | document.folderId | Set Null |

## Many-to-Many (N:M) Pattern

Requires a join entity to represent the relationship.

### Documentation Format

```markdown
### Users <-> Projects (N:M)

| Aspect | Value |
|--------|-------|
| **Type** | Many-to-Many |
| **From** | User |
| **To** | Project |
| **Join Entity** | ProjectMember |
| **Additional Fields** | role, joinedAt |
```

### Join Entity Definition

```markdown
## Entity: ProjectMember [NEW]

> Join entity for User-Project relationship.

### Attributes

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| id | UUID | Yes | auto | Unique identifier |
| userId | Reference(User) | Yes | - | Member user |
| projectId | Reference(Project) | Yes | - | Project |
| role | Enum[owner,admin,member,viewer] | Yes | member | Member role |
| joinedAt | Timestamp | Yes | auto | When user joined |

### Constraints

- Unique: (userId, projectId) - user can join project once
```

### Common N:M Examples

| Entity A | Entity B | Join Entity | Additional Fields |
|----------|----------|-------------|-------------------|
| User | Project | ProjectMember | role, joinedAt |
| User | Group | GroupMembership | role, addedBy |
| Student | Course | Enrollment | enrolledAt, grade |
| Product | Category | ProductCategory | sortOrder |
| Tag | Article | ArticleTag | addedAt |

## One-to-One (1:1) Pattern

Used for optional extensions or large attribute groups.

### Documentation Format

```markdown
### User <-> Profile (1:1)

| Aspect | Value |
|--------|-------|
| **Type** | One-to-One |
| **From** | User |
| **To** | Profile |
| **Foreign Key** | profile.userId (unique) |
| **Required** | Profile optional for User |
| **On Delete** | Cascade |
```

### When to Use 1:1

| Scenario | Example |
|----------|---------|
| **Optional extension** | User <-> Profile (not all users have profile) |
| **Large data separation** | Product <-> ProductDetails |
| **Inherited entity** | Account <-> CompanyAccount |
| **Access control** | User <-> UserCredentials |

## Self-Referential Relationships

When an entity relates to itself.

### Tree Structure (1:N Self-Reference)

```markdown
### Category -> Subcategories (1:N Self)

| Aspect | Value |
|--------|-------|
| **Type** | One-to-Many (Self) |
| **Entity** | Category |
| **Foreign Key** | category.parentId |
| **Required** | No (root categories have no parent) |
| **On Delete** | Cascade or Set Null |
```

### Graph Structure (N:M Self-Reference)

```markdown
### User <-> User Follows (N:M Self)

| Aspect | Value |
|--------|-------|
| **Type** | Many-to-Many (Self) |
| **Entity** | User |
| **Join Entity** | UserFollow |
| **Fields** | followerId, followingId, createdAt |
```

## Relationship Diagram Notation

### Text-Based Diagram Format

```markdown
## Entity Relationships

```
User ──1:N──▶ Task (owns)
User ──1:N──▶ Session (has)
User ◀──N:M──▶ Project (via ProjectMember)
Task ──N:1──▶ Project (belongs to)
Category ──1:N──▶ Category (parent-child)
```
```

### Symbol Reference

| Symbol | Meaning |
|--------|---------|
| `──1:N──▶` | One-to-many (arrow points to many) |
| `──N:1──▶` | Many-to-one (arrow points to one) |
| `◀──N:M──▶` | Many-to-many (bidirectional) |
| `──1:1──▶` | One-to-one |
| `(via Entity)` | Join entity for N:M |
| `(verb)` | Relationship description |

## Delete Behavior

| Behavior | Description | Use When |
|----------|-------------|----------|
| **Cascade** | Delete related records | Child meaningless without parent |
| **Set Null** | Set FK to null | Child can exist independently |
| **Restrict** | Prevent delete | Must explicitly handle children first |
| **No Action** | Database default | Similar to Restrict |

## Relationship Attributes Table

Document relationships in entity definitions:

```markdown
### Relationships

| Relationship | Type | Target | Description |
|--------------|------|--------|-------------|
| owner | N:1 | User | Task owner |
| project | N:1 | Project | Parent project |
| comments | 1:N | Comment | Task comments |
| assignees | N:M | User | Assigned users (via TaskAssignment) |
```

## Validation Checklist

- [ ] Every Reference type has relationship documented
- [ ] Cardinality is explicit (1:1, 1:N, N:M)
- [ ] Foreign key location is specified
- [ ] Delete behavior is documented
- [ ] N:M relationships have join entity defined
- [ ] Join entities have necessary additional fields
- [ ] Self-referential relationships are clearly marked
- [ ] Diagram matches relationship documentation
