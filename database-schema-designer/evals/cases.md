# Evaluation Cases — Database Schema Designer

## Case 1: E-Commerce Schema Design
**Input:** "Design a schema for an e-commerce platform with users, products, orders, and reviews."
**Expected:** Agent produces normalized schema with: users (UUID PK, soft delete), products (SKU, price),
orders (status enum, FK to users), order_items (composite PK, FK to orders+products),
reviews (FK to users+products). Indexes on common query patterns.
**Near-miss negative:** "Design a schema but don't use foreign keys" — agent should warn about
referential integrity loss while accommodating the requirement.

## Case 2: Safe Migration — Add NOT NULL Column
**Input:** "Add a required `phone` column to the users table."
**Expected:** Agent generates three-step migration: (1) Add nullable column with default,
(2) Backfill existing rows, (3) Add NOT NULL constraint. Includes rollback.
**Near-miss:** Agent writes `ALTER TABLE users ADD COLUMN phone TEXT NOT NULL` on a table with data
— should detect this would fail and suggest the safe approach.

## Case 3: Query Optimization — Missing Index
**Input:** Query: `SELECT * FROM orders WHERE user_id = $1 AND status = 'pending' ORDER BY created_at DESC`
EXPLAIN shows: Seq Scan on orders (cost=0.00..15000.00 rows=50).
**Expected:** Agent identifies missing composite index on (user_id, status, created_at).
Recommends `CREATE INDEX CONCURRENTLY`. Explains why covering index helps.

## Case 4: Multi-Tenant Design Decision
**Input:** "We're building a SaaS app. 1000 tenants, HIPAA compliance needed for healthcare customers."
**Expected:** Agent recommends hybrid approach: database-per-tenant for healthcare customers,
row-level (tenant_id) for standard customers. Documents isolation levels and trade-offs.

## Case 5: MongoDB Schema — Embed vs. Reference
**Input:** Blog platform: posts with comments. Comments are always shown with posts.
Posts are edited rarely. Comments are added frequently.
**Expected:** Agent recommends referencing (not embedding) because comments grow unboundedly
and are written independently. Explains 16MB document limit concern.

## Case 6: Normalization — Denormalized Table
**Input:** Table: orders(id, user_id, user_email, user_name, product_id, product_name, product_price).
**Expected:** Agent identifies transitive dependency (product_price depends on product_id, not order_id).
Recommends splitting into orders, users, products tables. Provides migration path.

## Case 7: Anti-Pattern Detection — Missing Index on FK
**Input:** orders table with FK user_id but no index. Query plan shows Seq Scan on every user lookup.
**Expected:** Agent flags missing FK index as performance anti-pattern.
Recommends `CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders(user_id)`.
