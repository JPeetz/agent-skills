---
name: graphql-api-development
description: >
  AI-powered GraphQL API design, implementation, and optimization.
  Covers schema-first design, resolver architecture, query optimization
  with DataLoader for N+1 prevention, mutation patterns with idempotency,
  real-time subscriptions, Apollo Federation for distributed graphs,
  security hardening (depth limiting, rate limiting, authz), and
  production performance (persisted queries, caching, CDN integration).
  Primary keyword clusters: GraphQL schema design best practices, Apollo
  Federation subgraph patterns, DataLoader N+1 query optimization,
  GraphQL security depth limiting rate limiting, GraphQL persisted
  queries performance, GraphQL subscription real-time patterns, GraphQL
  error handling union types, GraphQL pagination relay cursor connection,
  GraphQL caching strategies production, GraphQL resolver architecture
  patterns. Designed for agentic platforms — Claude Code, Codex, Cursor,
  Gemini CLI, OpenClaw, GitHub Copilot, Windsurf, and OpenCode.
version: 1.0.0
author: Skill Foundry
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
  - opencode
tags:
  - graphql
  - api-design
  - apollo
  - schema
  - resolvers
  - federation
  - performance
  - security
  - dataloader
  - subscriptions
geo:
  primary_workflows:
    - schema_design
    - resolver_implementation
    - query_optimization
    - performance_tuning
    - security_hardening
    - federation_setup
    - subscription_architecture
  target_roles:
    - backend_developer
    - api_architect
    - platform_engineer
    - full_stack_developer
    - devops_engineer
  complexity_level: advanced
  prerequisite_knowledge:
    - graphql_type_system
    - node_js_or_server_runtime
    - database_query_patterns
    - api_design_principles
    - distributed_systems_basics
---

# GraphQL API Development Agent Skill

Design, implement, and optimize production-grade GraphQL APIs with a
schema-first approach. This skill equips an agent to build performant,
secure, and federated GraphQL services — not just lint a schema.

---

## Quick Reference

| Dimension | What to Check | Key Indicators |
|---|---|---|
| 🔵 Schema Design | Naming, types, pagination, errors | Verb-first mutations, Relay pagination, union errors |
| 🟠 Resolvers | Data loading, context, error handling | DataLoader usage, null propagation, partial errors |
| ⚡ Query Optimization | N+1 prevention, field selection, complexity | Batched loads, DataLoader per request, query cost |
| 🟣 Mutations | Input types, idempotency, atomicity | Single input arg, idempotency keys, thin resolvers |
| 📡 Subscriptions | Event sources, filtering, auth | AsyncIterator, `withFilter`, ws auth |
| 🏗️ Federation | Entity resolution, shared types, contracts | `@key` directives, reference resolvers, contract tags |
| 🔒 Security | Authz, depth limiting, rate limiting | Field-level auth, graphql-depth-limit, persist-authenticated |
| 🚀 Performance | Caching, persisted queries, CDN | APQ, `@cacheControl`, response compression |

**Severity Scale:**
- 🔴 **BLOCKER** — Must fix before production. SQL injection via resolvers,
  auth bypass, unbounded recursion, schema that returns secrets.
- 🟠 **MAJOR** — Should fix. N+1 on hot path, missing depth limit, no error
  handling on critical mutations, federation entity mismatch.
- 🟡 **MINOR** — Nice to fix. Deprecated field usage, inconsistent naming
  convention, missing description strings.
- ⚪ **NIT** — Optional. Field ordering preference, comment style, type name
  bikeshedding.

---

## When to Use This Skill

Activate when the user asks you to:

- "Design a GraphQL schema for..." / "Create a GraphQL API for..."
- "Review this GraphQL schema" / "Check my resolvers for N+1 queries"
- "Set up Apollo Federation" / "Convert my monolith to subgraphs"
- "Add subscriptions to my GraphQL API" / "Implement real-time updates with GraphQL"
- "Optimize my GraphQL performance" / "Add persisted queries"
- "Harden my GraphQL API" / "Add depth limiting and rate limiting"
- "Implement pagination in GraphQL" / "Add Relay-style cursor connections"
- "Design error handling for GraphQL" / "Use union types for errors"
- "Set up DataLoader" / "Fix N+1 queries in my resolvers"
- Any request combining "GraphQL" + design, review, optimize, secure, or implement

### Do NOT Activate For

Near-miss negatives — these mention GraphQL but are NOT design/implementation:

- **REST vs GraphQL comparison**: "Should I use GraphQL or REST?" — technology
  evaluation, not GraphQL development.
- **GraphQL client usage**: "How do I use useQuery in Apollo Client?" — client-side
  consumption, not API development.
- **Generic debugging**: "My GraphQL query returns null but the database has data"
  without schema/resolver context — debugging, not development.
- **Tooling questions**: "Which GraphQL IDE should I use?" / "How to set up
  GraphiQL?" — tool selection, not API design.
- **General Q&A about GraphQL concepts**: "What is a resolver?" / "How does
  introspection work?" — education, not implementation.
- **GraphQL migration without design**: "Move my REST endpoint to GraphQL" without
  schema design or resolver planning — migration planning, not API development.
- **GraphQL gateway/proxy setup without schema work**: "Set up Apollo Router" with
  no subgraph design — infrastructure, not API development.

When in doubt, ask: "Are you looking for schema design, resolver implementation,
or performance optimization for your GraphQL API?"

---

## Common Pitfalls & Anti-Patterns

### ❌ GraphQL Anti-Patterns

1. **N+1 Queries in Resolvers** — The most common GraphQL performance killer.
   Every resolver firing individual DB calls cascades into hundreds of queries.
   Always batch with DataLoader, not per-field queries.

2. **Over-fetching in Resolvers** — Resolvers returning all columns when the
   query only asks for `id` and `name`. Use field-aware database projections or
   parent-to-child delegation.

3. **Mutation Resolver as Business Logic Dump** — Thick mutation resolvers with
   validation, authorization, side effects, and notifications. Keep resolvers thin:
   validate → authorize → delegate to service layer → return result.

4. **String-Based Error Handling** — Returning `null` or magic strings for errors.
   Use typed error unions or the `errors` extensions payload so clients can
   pattern-match instead of string-parse.

5. **Monolithic Schema Before Federation** — Building one massive schema and
   then retrofitting federation. Design with federation from the start: define
   entity boundaries, `@key` fields, and subgraph ownership.

6. **No Depth or Complexity Limits** — Unbounded recursive queries can bring
   down a server. A single malicious query fetching `user.posts.author.posts.author`
   recursively is a DoS vector. Always set `graphql-depth-limit` or query cost
   analysis.

7. **Authentication in Resolvers, Not Middleware** — Checking `context.user`
   inline in every resolver bloats code. Extract auth to a GraphQL context
   function or a schema directive so resolvers receive an already-authenticated
   (or rejected) context.

8. **Subscription Leaks** — AsyncIterators that never clean up lead to memory
   pressure. Every subscription source must have a proper teardown in the
   `subscribe` function's return `{ unsubscribe }`.

9. **Hardcoded Field Selections in Business Logic** — Business code that
   assumes specific GraphQL selections (`if (info.fieldNodes...)`). Use
   attribute-based access patterns or GraphQL-aware ORMs instead.

10. **Ignoring the `extensions` Field** — The extensions field is the
    GraphQL protocol's extensibility point. Use it for tracing (Apollo Tracing),
    request IDs, deprecation warnings, and rate limit headers — don't invent
    custom envelopes.

### ✅ GraphQL Quality Checklist

Before claiming implementation complete, verify:

- [ ] Schema uses verb-first mutation naming (`createUser`, not `UserCreate`)
- [ ] All list fields are paginated (Relay Connection or simplified offset)
- [ ] Errors use typed unions, not loose strings
- [ ] Every resolver with a DB call uses DataLoader
- [ ] Depth limit and query cost analysis are configured
- [ ] Mutations accept a single input type argument
- [ ] Subscriptions have teardown/unsubscribe logic
- [ ] Authentication happens in context, not individual resolvers
- [ ] Federation entities have `@key` directives and reference resolvers
- [ ] Persisted queries are enabled for production builds
- [ ] All types and fields have `description` strings
- [ ] Deprecated fields use `@deprecated(reason: "...")` with a migration path

---

## Workflow

### Phase 1: Schema Design

Design the schema first — the schema is the contract. Resolvers implement it,
not the other way around.

#### 1.1 Naming Conventions

| Construct | Convention | Example |
|---|---|---|
| Types | PascalCase, singular noun | `User`, `Post`, `Payment` |
| Query fields | camelCase, noun or noun phrase | `user(id:)`, `searchPosts` |
| Mutations | camelCase, verb + object | `createPost`, `cancelOrder` |
| Input types | PascalCase, suffixed with `Input` | `CreatePostInput`, `UserFilter` |
| Enum values | UPPER_SNAKE_CASE | `OrderStatus.PENDING`, `PAYMENT_FAILED` |
| Payload types | PascalCase, suffixed with `Payload` | `CreatePostPayload`, `LoginPayload` |
| Union errors | PascalCase, suffixed with `Error` | `ValidationError`, `NotFoundError` |

**Critical Rule:** Mutations MUST be verb-first. `postCreate` is wrong;
`createPost` is correct. This isn't style — it's a GraphQL spec expectation
that tooling (Apollo Studio, GraphiQL introspection) sorts on.

#### 1.2 Pagination Patterns

Always paginate list fields. Never return a bare `[User!]!`.

**Relay Cursor Connections (Preferred):**

```graphql
type Query {
  users(
    first: Int
    after: String
    last: Int
    before: String
    filter: UserFilter
  ): UserConnection!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  cursor: String!
  node: User!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

When to use Relay spec: public APIs, APIs consumed by multiple clients,
when you need stable cursor-based pagination, or when client uses Relay/Apollo
Client pagination helpers.

**Simplified Offset Pagination (Internal APIs):**

```graphql
type Query {
  users(limit: Int = 20, offset: Int = 0): UserPage!
}

type UserPage {
  items: [User!]!
  totalCount: Int!
  hasMore: Boolean!
}
```

When to use offset: internal/admin APIs, when clients need to jump to
arbitrary pages, or when data set is small and stable.

**Anti-pattern — Never:**

```graphql
# ❌ Unpaginated list — unbounded response, DoS risk
users: [User!]!
```

#### 1.3 Error Handling Patterns

Don't overload `null` to mean "error". Structure your errors.

**Typed Union Errors (Recommended):**

```graphql
type Mutation {
  createPost(input: CreatePostInput!): CreatePostPayload!
}

type CreatePostPayload {
  post: Post
  errors: [CreatePostError!]!
}

union CreatePostError = ValidationError | UnauthorizedError | RateLimitError

type ValidationError {
  message: String!
  field: String!
  code: String!
}

type UnauthorizedError {
  message: String!
}

type RateLimitError {
  message: String!
  retryAfterSeconds: Int!
}
```

Clients pattern-match on `__typename`:

```graphql
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    post {
      id
      title
    }
    errors {
      __typename
      ... on ValidationError { message field code }
      ... on RateLimitError { message retryAfterSeconds }
    }
  }
}
```

**Top-Level Errors (for partial failures):**

Use the standard GraphQL `errors` array for infrastructure errors (auth,
rate limit, internal server error). Use typed union errors for business
logic errors the client should handle.

**Anti-patterns:**

```graphql
# ❌ Magic null — was it not found? forbidden? deleted?
user(id: "1"): User

# ❌ Stringly-typed error — client must parse strings
type CreatePostPayload {
  post: Post
  error: String  # "VALIDATION_ERROR: title required"
}
```

#### 1.4 Schema Documentation

Every type and field MUST have a `description`:

```graphql
"""
A user account in the system. Users can create posts,
comment, and manage their profile.
"""
type User {
  """Unique identifier, stable across renames."""
  id: ID!

  """Display name shown on posts and comments."""
  name: String!

  """Set when the account was created. Immutable."""
  createdAt: DateTime!
}
```

Descriptions feed into GraphiQL, Apollo Studio, and codegen tools.
Undocumented schemas are tech debt.

### Phase 2: Resolver Architecture

#### 2.1 Resolver Signature

Every resolver receives `(parent, args, context, info)`:

```typescript
const resolvers = {
  Query: {
    user: async (_parent, { id }, context, info) => {
      // parent — result from parent resolver (null for root queries)
      // args   — GraphQL arguments ({ id: "42" })
      // context — per-request shared state (auth, loaders, db)
      // info    — AST, field name, return type, path
      return context.loaders.user.load(id);
    },
  },
};
```

#### 2.2 DataLoader & N+1 Prevention

The N+1 problem: resolving `posts.author` for 10 posts fires 11 queries
(1 for posts + 10 individual author queries). DataLoader coalesces the
10 author loads into a single `WHERE id IN (...)` query.

**Setup (per-request):**

```typescript
import DataLoader from "dataloader";

function createLoaders(db) {
  return {
    user: new DataLoader(async (ids: readonly string[]) => {
      const users = await db.users.findByIds([...ids]);
      // MUST return in same order as input ids
      const userMap = new Map(users.map(u => [u.id, u]));
      return ids.map(id => userMap.get(id) || null);
    }),
    postsByAuthor: new DataLoader(async (authorIds: readonly string[]) => {
      const posts = await db.posts.findByAuthorIds([...authorIds]);
      const grouped = new Map<string, Post[]>();
      for (const post of posts) {
        const list = grouped.get(post.authorId) || [];
        list.push(post);
        grouped.set(post.authorId, list);
      }
      return authorIds.map(id => grouped.get(id) || []);
    }),
  };
}

// In Apollo Server context:
const server = new ApolloServer({
  schema,
  context: async ({ req }) => ({
    user: await authenticate(req),
    loaders: createLoaders(db),
  }),
});
```

**Critical DataLoader Rules:**

1. **Create new DataLoader instances per request** — Never reuse across
   requests. Caching across requests causes stale data and security leaks.
2. **Return arrays in the same order as input keys** — DataLoader matches
   by index. Wrong order = wrong data.
3. **Batch function must accept and return arrays** — Single-item batch
   functions defeat the purpose.
4. **Handle nulls for not-found** — Return `null` (not throw) for
   individual missing items so other items still resolve.
5. **Use `DataLoader` instance in context, not imported globally.**

#### 2.3 Resolver Chain Patterns

**Parent-to-Child Delegation:**

```typescript
const resolvers = {
  Query: {
    post: async (_, { id }, { loaders }) => loaders.post.load(id),
  },
  Post: {
    author: (post, _, { loaders }) => loaders.user.load(post.authorId),
    comments: (post, _, { loaders }) => loaders.commentsByPost.load(post.id),
  },
  Comment: {
    author: (comment, _, { loaders }) => loaders.user.load(comment.authorId),
  },
};
```

**Field-Level Authorization:**

```typescript
const resolvers = {
  User: {
    email: (user, _, { currentUser }) => {
      if (currentUser?.id !== user.id && !currentUser?.isAdmin) {
        return null; // Field-level hide, not error
      }
      return user.email;
    },
    ssn: (user, _, { currentUser }) => {
      throw new ForbiddenError("Insufficient permissions");
    },
  },
};
```

**Computed Fields with Args:**

```typescript
const resolvers = {
  Post: {
    excerpt: (post, { maxLength = 200 }) => {
      return post.body.length > maxLength
        ? post.body.slice(0, maxLength) + "..."
        : post.body;
    },
  },
};
```

#### 2.4 Error Propagation

GraphQL null-propagates: if a non-null field resolver throws, the error
bubbles up to the first nullable parent. Design your schema nullability
with this in mind:

```graphql
type Query {
  # ❌ If post.author.email throws, the entire query fails
  post(id: ID!): Post!

  # ✅ post.author.email can fail without killing the whole query
  post(id: ID!): Post
}
```

For partial data, return what you can + errors in the extensions payload.
GraphQL can return both `data` and `errors` simultaneously.

### Phase 3: Mutation Design

#### 3.1 Input Types

Every mutation MUST accept a single `input` argument of a dedicated input type:

```graphql
# ✅ Single input type
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) { ... }
}

input CreatePostInput {
  title: String!
  body: String!
  tags: [String!]
  published: Boolean = false
}
```

**Why single input?**
- Evolvable: adding fields doesn't break the mutation signature
- Self-documenting: the input type describes the entire payload
- Client-friendly: single variable with nested fields vs flat positional args

**Anti-pattern:**

```graphql
# ❌ Multiple top-level args — fragile, not evolvable
createPost(title: String!, body: String!, tags: [String!]): Post!
```

#### 3.2 Idempotency Keys

For mutations that must not be duplicated (payments, orders, email sends),
accept an idempotency key:

```graphql
input ProcessPaymentInput {
  idempotencyKey: String!
  amount: Money!
  paymentMethodId: ID!
}
```

The resolver checks if the idempotencyKey has been seen:

```typescript
async function processPayment(_, { input }, { db, paymentService }) {
  const existing = await db.payments.findByKey(input.idempotencyKey);
  if (existing) return { payment: existing, errors: [] };

  // Process payment — if this fails and client retries with same key,
  // the above check prevents double-charge
  const payment = await paymentService.charge(input);
  await db.payments.create({ ...payment, idempotencyKey: input.idempotencyKey });
  return { payment, errors: [] };
}
```

#### 3.3 Mutation Response Pattern

Always return a payload type, never the entity directly:

```graphql
# ✅ Payload type — evolvable
type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}

type CreateUserPayload {
  user: User
  errors: [CreateUserError!]!
}

# ❌ Direct entity — no room for errors or metadata
type Mutation {
  createUser(input: CreateUserInput!): User!
}
```

#### 3.4 Thin Resolvers, Thick Services

Mutations are entry points. They should not contain business logic:

```typescript
// ✅ Thin resolver
const resolvers = {
  Mutation: {
    createPost: async (_, { input }, ctx) => {
      const validated = await ctx.services.postValidator.validate(input);
      await ctx.services.auth.assertCanCreatePost(ctx.user, validated);
      const post = await ctx.services.postService.create(validated);
      await ctx.services.eventBus.publish("post.created", { post });
      return { post, errors: [] };
    },
  },
};

// ❌ Thick resolver with inline logic
const resolvers = {
  Mutation: {
    createPost: async (_, { input }, ctx) => {
      if (!input.title || input.title.length < 3) { /* ... */ }
      if (!ctx.user) { /* ... */ }
      const slug = input.title.toLowerCase().replace(/\s+/g, "-");
      const existing = await ctx.db.posts.findOne({ slug });
      if (existing) { /* ... */ }
      // 50 more lines...
    },
  },
};
```

### Phase 4: Subscription Patterns

#### 4.1 Event-Driven Subscriptions

Use `PubSub` (or Redis-backed pub/sub in production) as an event bus:

```typescript
import { PubSub } from "graphql-subscriptions";

const pubsub = new PubSub();

const POST_CREATED = "POST_CREATED";

const resolvers = {
  Mutation: {
    createPost: async (_, { input }, ctx) => {
      const post = await ctx.services.postService.create(input);
      await pubsub.publish(POST_CREATED, { postCreated: post });
      return { post, errors: [] };
    },
  },
  Subscription: {
    postCreated: {
      subscribe: () => pubsub.asyncIterator([POST_CREATED]),
    },
  },
};
```

#### 4.2 Filtered Subscriptions

Use `withFilter` to only deliver events the subscriber cares about:

```typescript
import { withFilter } from "graphql-subscriptions";

const resolvers = {
  Subscription: {
    commentAdded: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(["COMMENT_ADDED"]),
        (payload, variables, context) => {
          // Only deliver if the comment is on the post the client watches
          return payload.commentAdded.postId === variables.postId;
        },
      ),
    },
  },
};
```

#### 4.3 Authentication on Subscriptions

WebSocket connections carry auth differently than HTTP:

```typescript
// Apollo Server 4 with graphql-ws:
const server = new ApolloServer({
  schema,
  plugins: [
    {
      async serverWillStart() {
        return {
          async drainServer() { pubsub.close(); },
        };
      },
    },
  ],
});

// In context function, handle WebSocket auth:
const context = async ({ req, connectionParams }) => {
  if (connectionParams) {
    // WebSocket connection
    const token = connectionParams.authorization || "";
    return { user: await verifyToken(token), loaders: createLoaders(db) };
  }
  // HTTP request
  const token = req.headers.authorization || "";
  return { user: await verifyToken(token), loaders: createLoaders(db) };
};
```

#### 4.4 Cleanup

Every subscription source needs a teardown:

```typescript
const resolvers = {
  Subscription: {
    liveCursor: {
      subscribe: async function* (_, { documentId }, { db }) {
        // Setup: watch database changes
        const watcher = await db.documents.watch(documentId);
        try {
          while (true) {
            const change = await watcher.nextChange();
            yield { liveCursor: change };
          }
        } finally {
          // Teardown: always clean up, even on disconnect
          await watcher.close();
        }
      },
    },
  },
};
```

### Phase 5: Apollo Federation

#### 5.1 Entity Definition

Define entities with `@key` directives:

```graphql
# Users subgraph
extend schema
  @link(url: "https://specs.apollo.dev/federation/v2.6")

type User @key(fields: "id") {
  id: ID!
  username: String!
  email: String! @shareable
}

# Posts subgraph
type User @key(fields: "id") {
  id: ID!
  posts: [Post!]!
}

type Post @key(fields: "id") {
  id: ID!
  title: String!
  authorId: ID!  # Only stored in Posts subgraph
  author: User!
}
```

#### 5.2 Reference Resolvers

Provide reference resolvers for each entity:

```typescript
// Posts subgraph
const resolvers = {
  User: {
    __resolveReference: async ({ id }, { loaders }) => {
      // Fetch the fields this subgraph contributes for the User entity
      return loaders.userById.load(id);
    },
    posts: (user, _, { loaders }) => {
      return loaders.postsByAuthor.load(user.id);
    },
  },
  Post: {
    __resolveReference: async ({ id }, { loaders }) => {
      return loaders.post.load(id);
    },
    author: (post, _, { loaders }) => {
      return { __typename: "User", id: post.authorId };
      // The gateway will resolve User fields from other subgraphs
    },
  },
};
```

#### 5.3 Federation Best Practices

- **Each subgraph owns its data.** The Posts subgraph stores `Post` data;
  the Users subgraph stores `User` data. Don't duplicate data across subgraphs.
- **Use `@shareable` for fields defined in multiple subgraphs.**
- **Keep `@key` fields simple.** Composite keys (`@key(fields: "orgId userId")`)
  are fine but avoid deeply nested keys.
- **`@requires` for cross-subgraph data needs:**

```graphql
type Product @key(fields: "id") {
  id: ID!
  price: Float  # stored in Products subgraph
}

type Review @key(fields: "id") {
  id: ID!
  product: Product!
  priceAtReview: Float @requires(fields: "product { price }")
}
```

- **Use contracts (`@tag`, `@inaccessible`) to version public vs internal APIs.**
- **Test `_entities` queries directly** — they're the gateway's query API.

### Phase 6: Security Hardening

#### 6.1 Depth Limiting

Prevent recursive query DoS attacks:

```bash
npm install graphql-depth-limit
```

```typescript
import depthLimit from "graphql-depth-limit";

const server = new ApolloServer({
  schema,
  validationRules: [depthLimit(7)], // Max 7 levels of nesting
});
```

A depth limit of 7 allows:
```graphql
query {                    # depth 0
  user {                   # depth 1
    posts {                # depth 2
      author {             # depth 3
        posts {            # depth 4
          author {         # depth 5
            posts {        # depth 6
              author {     # depth 7
                name       # depth 8 — REJECTED
              }
            }
          }
        }
      }
    }
  }
}
```

#### 6.2 Query Cost Analysis

Depth limiting isn't enough — a shallow but wide query can still be
expensive:

```graphql
# Depth 3, but fetches A LOT of data:
query HeavyQuery {
  users(first: 100) {
    posts(first: 50) {
      comments(first: 50) {
        body  # 100 × 50 × 50 = 250,000 nodes
      }
    }
  }
}
```

Use query cost analysis:

```bash
npm install graphql-cost-analysis
```

```typescript
import costAnalysis from "graphql-cost-analysis";

const server = new ApolloServer({
  schema,
  validationRules: [
    depthLimit(7),
    costAnalysis({
      maximumCost: 1000,
      defaultCost: 1,
      variables: {}, // Pass request variables
    }),
  ],
});
```

**Cost multipliers** — adjust per type:

```graphql
type Query {
  user(id: ID!): User                           # cost: 1
  users(first: Int, after: String): UserConnection # cost: first × complexity
  search(query: String!): [SearchResult!]!      # cost: 10 (expensive)
}
```

#### 6.3 Rate Limiting

Rate limiting should be per-operation, not just per-endpoint:

```typescript
import { createRateLimitDirective } from "graphql-rate-limit";

const { rateLimitDirectiveTypeDefs, rateLimitDirectiveTransformer } =
  createRateLimitDirective();

// Apply rate limit to specific fields:
const typeDefs = gql`
  ${rateLimitDirectiveTypeDefs}

  type Mutation {
    login(input: LoginInput!): LoginPayload! @rateLimit(limit: 5, duration: 60)
    createPost(input: CreatePostInput!): CreatePostPayload! @rateLimit(limit: 30, duration: 60)
  }
`;
```

#### 6.4 Authentication & Authorization

**Pattern: Schema Directives for Auth:**

```graphql
directive @auth(requires: Role = USER) on OBJECT | FIELD_DEFINITION

enum Role {
  ADMIN
  USER
  PUBLIC
}

type Query {
  me: User! @auth
  users: [User!]! @auth(requires: ADMIN)
  publicPosts: [Post!]! @auth(requires: PUBLIC)
}
```

Implement as a directive transformer or check in context:

```typescript
const context = async ({ req }) => {
  const token = req.headers.authorization?.replace("Bearer ", "") || "";
  let user = null;
  if (token) {
    try { user = await verifyToken(token); } catch { /* unauthenticated */ }
  }
  return { user, loaders: createLoaders(db) };
};

// In resolvers:
function assertAuthenticated(ctx) {
  if (!ctx.user) throw new AuthenticationError("You must be logged in");
}

function assertAuthorized(ctx, requiredRole) {
  assertAuthenticated(ctx);
  if (!ctx.user.roles.includes(requiredRole)) {
    throw new ForbiddenError(`Requires role: ${requiredRole}`);
  }
}
```

#### 6.5 Introspection Control

Disable introspection in production or gate it:

```typescript
const server = new ApolloServer({
  schema,
  introspection: process.env.ALLOW_INTROSPECTION === "true",
  // Or gate behind auth:
  // introspection: true,
  // plugins: [{
  //   async requestDidStart({ request }) { ... }
  // }]
});
```

### Phase 7: Performance Optimization

#### 7.1 Persisted Queries

Automatic Persisted Queries (APQ) reduce bandwidth and improve cacheability:

```typescript
import { createPersistedQueryLink } from "@apollo/client/link/persisted-queries";

// Client side:
const link = createPersistedQueryLink({
  sha256,
  useGETForHashedQueries: true,
}).concat(httpLink);

// Server side:
import responseCachePlugin from "apollo-server-plugin-response-cache";

const server = new ApolloServer({
  schema,
  plugins: [
    responseCachePlugin({
      sessionIdFromContext: (ctx) => ctx.user?.id || null,
      // Private data varies by user; public data can be fully cached
    }),
  ],
  persistedQueries: {
    cache: new PrefixingKeyValueCache(
      new InMemoryLRUCache({ maxSize: 1000 }),
      "apq:"
    ),
    ttl: 900, // 15 minutes
  },
});
```

**CDN Integration:** With `useGETForHashedQueries: true`, persisted queries are
sent as GET requests, making them cachable by standard CDNs and edge caches.

#### 7.2 Field-Level Caching

Use `@cacheControl` directives:

```graphql
type Query {
  user(id: ID!): User @cacheControl(maxAge: 60)
  topPosts: [Post!]! @cacheControl(maxAge: 300, scope: PUBLIC)
  me: User @cacheControl(maxAge: 0, scope: PRIVATE)
}

type Post @cacheControl(maxAge: 600) {
  id: ID!
  title: String!
  body: String! @cacheControl(maxAge: 3600)
  viewCount: Int! @cacheControl(maxAge: 30)
}
```

#### 7.3 Response Compression

```typescript
import compression from "compression";
import express from "express";

const app = express();
app.use(compression()); // gzip/brotli for all responses
```

#### 7.4 Batching & Defer/Stream

**`@defer`** (experimental) for incremental delivery:

```graphql
query {
  post(id: "42") {
    title       # Delivered immediately
    author { name }
    ... on Post @defer {
      body      # Delivered in a later payload
      comments {
        body
        author { name }
      }
    }
  }
}
```

Enable with Apollo Server 4:

```typescript
import { ApolloServer } from "@apollo/server";
import { buildSubgraphSchema } from "@apollo/subgraph";

const server = new ApolloServer({
  schema: buildSubgraphSchema({ typeDefs, resolvers }),
  // @defer support is built-in for federated schemas
});
```

#### 7.5 Monitoring & Tracing

```typescript
import { ApolloServerPluginInlineTrace } from "@apollo/server/plugin/inlineTrace";

const server = new ApolloServer({
  schema,
  plugins: [
    ApolloServerPluginInlineTrace({
      includeErrors: { unmodified: true },
    }),
  ],
});
```

Key metrics to track:
- Resolver execution time by field
- DataLoader batch sizes (are they actually batching?)
- Query parse/validation time vs execution time
- Error rate by operation
- Subscription connection churn

---

## Safety Rules

**ABSOLUTE RULES — never violate these:**

1. **Never expose internal database IDs as the node identifier** in Relay
   patterns. Use opaque, globally unique IDs (base64-encoded `TypeName:UUID`).
   Database IDs leak information about table sizes and insertion rate.

2. **Never disable introspection in a way that breaks developer tooling**
   without providing an alternative. If you gate introspection, document how
   authenticated developers can access the schema.

3. **Never return raw database errors to clients.** Always map to typed
   GraphQL errors. Stack traces and SQL errors in production responses are
   information leaks.

4. **Never create circular references in federation `@key` chains.**
   A → B → A entity resolution will cause infinite loops in the gateway.

5. **Never use `@shareable` without coordination across subgraph teams.**
   A `@shareable` field with conflicting resolvers across subgraphs creates
   nondeterministic behavior.

6. **Never deploy without depth/cost limits.** An unprotected GraphQL
   endpoint is a DoS vector. Minimum: depth limit = 7, maximum cost = 1000.

7. **Never pass raw `req.body` or unvalidated variables to resolvers.**
   GraphQL argument coercion handles type validation, but business validation
   must be explicit.

8. **Never share DataLoader instances across requests.** This causes data
   leaking between users and stale cache hits.

---

## Platform Compatibility Notes

| Platform | Notes |
|---|---|
| **Claude Code** | Excellent for schema design iteration and resolver patterns. Use terminal access for `npx graphql-codegen` and schema composition. |
| **Codex (OpenAI)** | Strong at generating resolver implementations from schema definitions. Good at spotting N+1 patterns. |
| **Cursor** | Can read multiple schema/resolver files simultaneously. Ideal for cross-subgraph entity resolution validation. |
| **Gemini CLI** | Large context window aids full-schema review. Good for analyzing complex federated schemas end-to-end. |
| **OpenClaw** | Access to exec for running `rover subgraph check` and `graphql-inspector`. Use for CI/CD pipeline integration. |
| **GitHub Copilot** | Inline suggestions excel at resolver boilerplate and DataLoader patterns. Less effective at cross-file architectural review. |
| **Windsurf** | Multi-file workspace awareness helps with subgraph boundaries and entity cross-references. |
| **OpenCode** | Terminal-native: use for `graphql-codegen` setup, `rover` CLI operations, and schema composition in CI. |

### Platform-Specific Adjustments

- **If `rover` CLI is unavailable**: manually validate Federation directives
  and `_service { sdl }` output for each subgraph.
- **If `graphql-codegen` is unavailable**: manually verify TypeScript types
  against schema. Flag type mismatches as MAJOR findings.
- **If introspection is disabled**: rely on schema SDL files. Verify that
  SDL files are in version control and match deployed schemas.
- **For Discord/Slack delivery**: use bullet lists, not tables. Split
  schema reviews across multiple messages if >10 findings.

---

## References

- `references/graphql-patterns.md` — Comprehensive GraphQL patterns and anti-patterns reference
- GraphQL Spec (October 2021): https://spec.graphql.org/
- Apollo Federation Docs: https://www.apollographql.com/docs/federation/
- DataLoader: https://github.com/graphql/dataloader
- graphql-depth-limit: https://www.npmjs.com/package/graphql-depth-limit
- graphql-cost-analysis: https://www.npmjs.com/package/graphql-cost-analysis
- Apollo Server Security: https://www.apollographql.com/docs/apollo-server/security/
- Relay Pagination Spec: https://relay.dev/graphql/connections.htm
- graphql-rate-limit: https://www.npmjs.com/package/graphql-rate-limit