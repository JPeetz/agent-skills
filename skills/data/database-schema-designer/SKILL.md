---
name: database-schema-designer
description: >-
  Design production-ready database schemas for SQL and NoSQL databases.
  Covers normalization, indexing strategy, migration management with
  rollback safety, query optimization, and multi-tenant patterns.
  Supports PostgreSQL, MySQL, SQLite, MongoDB, and Vitess.
version: 1.0.0
platforms: [openclaw, claude, codex, cursor, gemini, copilot, opencode, windsurf]
author:
  name: Skill Foundry (Forge)
  source: PlanetScale Database Skills, Supabase Agent Skills, softaworks/agent-toolkit
license: MIT
risk_tier: L2
tags: [database, schema, sql, nosql, postgres, mysql, migration, optimization, design]
requires:
  binaries: []
---

# Database Schema Designer

Design production-ready database schemas with built-in best practices.
Covering SQL normalization, indexing strategy, migration management with
safe rollback patterns, query optimization, and multi-tenant architecture
patterns across PostgreSQL, MySQL, SQLite, MongoDB, and Vitess.

## When to Use This Skill

Use this skill when:
- Designing a new database schema from scratch
- Reviewing an existing schema for performance or correctness
- Planning a database migration with safe rollback
- Optimizing slow queries on a production database
- Converting between database engines (MySQL → PostgreSQL, etc.)
- Designing multi-tenant data architectures
- Any request like "design a schema for X", "review my database",
  "optimize this query", "create migrations", "normalize this table"

## Safety Rules (Risk Tier L2)

Database operations can be destructive. This skill enforces:

1. **Never DROP without backup** — Always generate backup commands first
2. **Always generate rollback** — Every migration includes verified reversal
3. **Test migrations on staging** — Never run directly on production
4. **Lock-aware design** — Schema changes must consider lock duration
5. **Data integrity first** — Validate before and after every migration
6. **No data loss** — Backfill before dropping columns, migrate before deleting

## Design Methodology

### Phase 1: Domain Modeling

Start with entities, not tables. Map the domain before writing DDL:

```
DOMAIN CANVAS:
├── Entities: What things exist? (User, Order, Product, Invoice)
├── Relationships: How do they connect? (one-to-many, many-to-many)
├── Attributes: What properties do they have?
├── Constraints: What must always be true?
├── Access Patterns: What queries will run most often?
└── Growth Projections: How many rows? At what rate?
```

### Phase 2: Schema Design — SQL

**Normalization checklist:**
- [ ] 1NF: Atomic columns, no repeating groups
- [ ] 2NF: No partial dependencies on composite keys
- [ ] 3NF: No transitive dependencies
- [ ] BCNF: Every determinant is a candidate key (when needed)
- [ ] Denormalize intentionally (document why, measure benefit)

**Example: E-Commerce Schema**

```sql
-- Users table (normalized, with soft delete)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ  -- soft delete
);
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;

-- Products with inventory tracking
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
    inventory_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_products_sku ON products(sku);

-- Orders with status state machine
CREATE TYPE order_status AS ENUM (
    'pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled'
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    status order_status NOT NULL DEFAULT 'pending',
    total_cents INTEGER NOT NULL DEFAULT 0,
    shipping_address JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status)
    WHERE status IN ('pending', 'processing');

-- Order items (many-to-many with quantities)
CREATE TABLE order_items (
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL,
    PRIMARY KEY (order_id, product_id)
);
```

### Phase 3: Indexing Strategy

**The Index Selection Algorithm:**

1. **WHERE clause columns** → Candidate for index
2. **JOIN columns** → Index foreign keys
3. **ORDER BY columns** → Consider composite with WHERE cols
4. **SELECT columns** → Consider covering indexes
5. **Cardinality check** → Don't index low-cardinality columns alone

**Index types by database:**

| Database | Index Types | When to Use |
|----------|-------------|-------------|
| PostgreSQL | B-tree (default), Hash, GiST, GIN, BRIN, SP-GiST | B-tree for equality/range; GIN for full-text/arrays; BRIN for large sequential data |
| MySQL/InnoDB | B-tree (clustered PK), Full-text, Spatial | B-tree for most cases; Full-text for text search |
| SQLite | B-tree (default) | All standard cases |
| MongoDB | Single-field, Compound, Multikey, Text, Geospatial, Hashed, TTL | Compound for common queries; TTL for expiring data |

**Index anti-patterns:**
- Indexing every column "just in case" — wastes write performance
- Missing composite index leading column — index on (a, b) doesn't help queries on b alone
- Redundant indexes — index on (a, b) makes index on (a) redundant
- Unused indexes — audit with `pg_stat_user_indexes` or `sys.dm_db_index_usage_stats`

### Phase 4: Migration Design

**Migration file structure:**
```sql
-- migrations/001_add_user_preferences.sql
-- UP: Forward migration (what to apply)
-- DOWN: Rollback migration (how to undo)

-- UP MIGRATION
BEGIN;
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    theme TEXT NOT NULL DEFAULT 'light',
    notifications JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Backfill existing users with defaults
INSERT INTO user_preferences (user_id)
SELECT id FROM users
ON CONFLICT (user_id) DO NOTHING;
COMMIT;

-- DOWN MIGRATION
-- BEGIN;
-- DROP TABLE IF EXISTS user_preferences;
-- COMMIT;
```

**Safe migration rules:**

1. **Add columns** → Safe (nullable with default)
2. **Drop columns** → Three-step: stop writing → backfill → drop
3. **Rename columns** → Two-step: add new + dual-write → drop old
4. **Change type** → Add new column → backfill → switch reads → drop old
5. **Add NOT NULL** → Add with default → backfill nulls → add constraint
6. **Create index** → Use CONCURRENTLY (PostgreSQL) or ONLINE (MySQL 8+)
7. **Drop index** → Use CONCURRENTLY if available
8. **Add foreign key** → Validate existing data first, validate constraint

### Phase 5: Query Optimization

**The EXPLAIN-based optimization workflow:**

1. Run `EXPLAIN (ANALYZE, BUFFERS)` on the slow query
2. Identify the bottleneck: sequential scan? nested loop? sort?
3. Check if statistics are up to date: `ANALYZE table_name`
4. Consider: new index, query rewrite, schema change, or config tuning
5. Test and measure improvement (not just EXPLAIN cost, actual timing)

**Common optimization patterns:**

| Problem | Symptom | Fix |
|---------|---------|-----|
| Missing index | Seq Scan on large table | Add covering index for WHERE + JOIN + SELECT |
| N+1 queries | Many small queries | Use JOIN or batch load |
| Over-fetching | SELECT * on wide tables | Select only needed columns |
| Lock contention | UPDATE waiting on locks | Batch updates, use SKIP LOCKED |
| Statistics stale | Planner choosing wrong plan | ANALYZE table; adjust default_statistics_target |

### Phase 6: Multi-Tenant Architecture

| Pattern | Description | Best For | Trade-offs |
|---------|-------------|----------|------------|
| **Database per tenant** | Separate DB per customer | High security, compliance | Many connections, harder cross-tenant queries |
| **Schema per tenant** | Separate schema per customer | Medium security, shared DB | Easier backups, moderate isolation |
| **Row-level (shared)** | tenant_id column everywhere | Simplicity, shared resources | Weakest isolation, query complexity |
| **Hybrid** | Combine patterns by tier | Enterprise customers get isolation | Operational complexity |

## NoSQL Design Patterns

### MongoDB Schema Design

```javascript
// Denormalized by access pattern
db.products.insertOne({
  _id: ObjectId(),
  name: "Widget",
  price: 9.99,
  // Embedded reviews (accessed together)
  reviews: [
    { user: "alice", rating: 5, comment: "Great!" },
    { user: "bob", rating: 4, comment: "Good value" }
  ],
  // Reference pattern for frequently-updated data
  inventory_warehouse_id: ObjectId("...")
});
```

**MongoDB data modeling rules:**
- Embed for "contains" relationships (order → line items)
- Reference for "uses" relationships (order → product)
- Embed when data is read together, updated together
- Reference when data is shared across documents
- Size limit: documents must be under 16MB

### Key-Value (Redis) Design

```
# Session store with TTL
SETEX session:abc123 3600 '{"user_id": 42, "role": "admin"}'

# Rate limiting with sliding window
INCR rate:user:42
EXPIRE rate:user:42 60

# Leaderboard with sorted sets
ZADD leaderboard:weekly 1000 player:42 950 player:17
ZREVRANGE leaderboard:weekly 0 9 WITHSCORES
```

## Platform Notes

- **All platforms:** This skill provides declarative knowledge — the agent
  applies patterns using its existing database tools and query capabilities.
- **Risk tier L2:** Schema design is read-heavy during design phases.
  Migration execution requires human approval gates.
- **Database-specific tools:** The skill supports SQL command generation but
  defers to the agent's MCP or native database tools for actual execution.
