# Query Optimization — Profiling and Index Design

## Before Adding an Index

1. Get the **actual slow query** (from slow query log, APM, or `pg_stat_activity`)
2. Run `EXPLAIN (ANALYZE, BUFFERS, TIMING)` on it
3. Identify the bottleneck: sequential scan? Nested loop? Sort?
4. Check existing indexes with `\d table_name` (PostgreSQL) or `SHOW INDEX FROM table` (MySQL)

## Index Design Principles

- **Composite indexes** — order columns by cardinality (most selective first) unless range conditions change the order
- **Covering indexes** — include all columns the query needs (PostgreSQL `INCLUDE` clause)
- **Partial indexes** — `WHERE` clause on the index itself (e.g. `WHERE status = 'active'`)
- **Drop unused indexes** — they slow writes and bloat memory

## Example: N+1 Query Fix

**Before (N+1):**

```sql
-- Implicit: one query per order to get customer, one per order to get items
SELECT * FROM orders;
```

**After (eager join):**

```sql
SELECT o.id, o.total, c.name, i.product_id, i.quantity
FROM orders o
JOIN customers c ON c.id = o.customer_id
JOIN order_items i ON i.order_id = o.id
WHERE o.created_at > now() - interval '30 days';
```

## Example: Index Verification

```sql
-- Before
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE status = 'pending' AND created_at > now() - '1 day'::interval;

-- After adding index
CREATE INDEX idx_orders_status_created ON orders (status, created_at);

EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE status = 'pending' AND created_at > now() - '1 day'::interval;

-- Compare: rows examined, buffers hit, actual time
```