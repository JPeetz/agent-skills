# GraphQL Patterns Reference

A comprehensive catalog of GraphQL design patterns, anti-patterns, and
production recipes. Use alongside the main SKILL.md for deep dives into
specific pattern families.

---

## 1. Schema Design Patterns

### 1.1 Naming Convention Reference

| Construct | Convention | Good Example | Bad Example |
|---|---|---|---|
| Object types | PascalCase, singular | `User`, `OrderItem` | `user`, `order_items` |
| Input types | PascalCase + `Input` | `CreateUserInput` | `UserCreateArgs` |
| Payload types | PascalCase + `Payload` | `CreateUserPayload` | `UserResponse` |
| Enum types | PascalCase | `OrderStatus` | `order_status_enum` |
| Enum values | UPPER_SNAKE_CASE | `PAYMENT_PENDING` | `PaymentPending`, `0` |
| Query fields | camelCase, noun | `currentUser`, `searchPosts` | `getUser`, `GET_POSTS` |
| Mutation fields | camelCase, verb+object | `createOrder`, `cancelSubscription` | `orderCreate`, `OrderCancel` |
| Interface types | PascalCase, adjective or noun | `Node`, `Timestamped` | `hasTimestamps` |
| Union types | PascalCase, descriptive | `SearchResult`, `PostMedia` | `post_or_page` |
| Scalar types | PascalCase | `DateTime`, `JSON`, `Email` | `dateTime`, `json_scalar` |
| Subscription fields | camelCase, event-past-tense | `messageSent`, `orderUpdated` | `newMessage`, `onOrderUpdate` |
| Directive names | camelCase | `@deprecated`, `@auth` | `@Deprecated`, `@RequiresAuth` |

### 1.2 Type Design Principles

**Prefer Specific Types Over Generic Wrappers:**

```graphql
# ✅ Specific, descriptive
type User {
  id: ID!
  name: String!
  email: Email!
  createdAt: DateTime!
}

# ❌ Generic wrapper hides the domain
type User {
  id: ID!
  attributes: JSON!
}
```

**Use Non-Null Semantically:**

```graphql
type Post {
  id: ID!           # Always present — good
  title: String!    # Always present — good
  author: User      # Might not be loaded yet — nullable is correct
  comments: [Comment!]!  # List always present, items always valid — good
}
```

Rule: `!` means "the field will NEVER be null when successfully resolved."
Use `!` on fields whose absence would be a bug, not a valid state.

**Scalar Over String for Semantic Types:**

```graphql
# ✅ Semantic scalars
scalar DateTime
scalar Email
scalar URL
scalar JSON
scalar PositiveInt

# ❌ String for everything — loses type safety
type User {
  email: String       # Is this an email? A username? A UUID?
  createdAt: String   # ISO 8601? Unix timestamp? What format?
  avatarUrl: String   # Relative path? Absolute URL? Base64 data?
}
```

**Interface for Polymorphism:**

```graphql
interface Content {
  id: ID!
  title: String!
  createdAt: DateTime!
}

type Article implements Content {
  id: ID!
  title: String!
  createdAt: DateTime!
  body: String!
  wordCount: Int!
}

type Video implements Content {
  id: ID!
  title: String!
  createdAt: DateTime!
  durationSeconds: Int!
  thumbnailUrl: URL!
}

type SearchResult {
  items: [Content!]!
  totalCount: Int!
}
```

### 1.3 Schema Evolution Patterns

**Additive Only — Never Remove Fields Directly:**

```graphql
type User {
  id: ID!

  """DEPRECATED: Use displayName instead. Will be removed 2027-01-01."""
  name: String!
    @deprecated(reason: "Use displayName instead. Will be removed 2027-01-01.")

  """The user's preferred display name, respecting locale."""
  displayName: String!
}
```

Deprecation checklist:
1. Add the new field
2. Mark the old field `@deprecated` with a reason and sunset date
3. Announce to consumers
4. Monitor usage via Apollo Studio or schema analytics
5. Remove after the sunset date (and after usage drops to zero)

**Versioning via Contracts (Federation):**

```graphql
# Public API contract
type Product @key(fields: "id") {
  id: ID!
  name: String!
  price: Money! @tag(name: "public")
  cost: Money! @tag(name: "internal") @inaccessible
}
```

### 1.4 Edge Cases & Nullability Traps

**The Non-Null List Trap:**

```graphql
type Query {
  # ❌ If any item in the DB is corrupted, the ENTIRE response fails
  users: [User!]!

  # ✅ null items are filtered out; list still resolves
  users: [User]!

  # ✅ The worst case: list is null but individual items never are
  users: [User!]

  # ✅ Most permissive: null list with null items — rarely correct
  users: [User]
}
```

**The Nested Non-Null Cascade:**

```graphql
type Query {
  # ❌ If post.author.profile.email throws, EVERYTHING fails
  post(id: ID!): Post!
}

type Post {
  author: User!     # Non-null — if author fails, Post fails
}

type User {
  profile: Profile! # Non-null — if profile fails, User fails
}

type Profile {
  email: String!    # Non-null — email fetch failure cascades to root
}
```

Mitigation:
1. Make the query field nullable: `post(id: ID!): Post`
2. Make nested resolvers nullable when data might not load: `author: User`
3. Return partial data with errors in the extensions payload

---

## 2. Resolver Patterns

### 2.1 DataLoader Pattern Catalog

**One-to-One:**

```typescript
const userLoader = new DataLoader(async (ids: readonly string[]) => {
  const users = await db.users.findByIds([...ids]);
  const userMap = new Map(users.map(u => [u.id, u]));
  return ids.map(id => userMap.get(id) || null);
});
```

**One-to-Many:**

```typescript
const postsByAuthorLoader = new DataLoader(async (authorIds: readonly string[]) => {
  const posts = await db.posts.findByAuthorIds([...authorIds]);
  const grouped = new Map<string, Post[]>();
  for (const post of posts) {
    const list = grouped.get(post.authorId) || [];
    list.push(post);
    grouped.set(post.authorId, list);
  }
  return authorIds.map(id => grouped.get(id) || []);
});
```

**Many-to-Many (Join Table):**

```typescript
const tagsByPostLoader = new DataLoader(async (postIds: readonly string[]) => {
  const rows = await db.postTags.findByPostIds([...postIds]);
  const tagIds = [...new Set(rows.map(r => r.tagId))];
  const tags = await db.tags.findByIds(tagIds);
  const tagMap = new Map(tags.map(t => [t.id, t]));

  const grouped = new Map<string, Tag[]>();
  for (const row of rows) {
    const list = grouped.get(row.postId) || [];
    const tag = tagMap.get(row.tagId);
    if (tag) list.push(tag);
    grouped.set(row.postId, list);
  }
  return postIds.map(id => grouped.get(id) || []);
});
```

**Conditional Batching:**

```typescript
const postLoader = new DataLoader(async (ids: readonly string[]) => {
  // Cache check first — DataLoader caches per-request, but you might
  // want a Redis cache layer here
  const posts = await db.posts.findByIds([...ids]);

  // Also pre-populate the user loader for the next resolver
  const authorIds = [...new Set(posts.map(p => p.authorId))];
  userLoader.primeMany(
    await db.users.findByIds(authorIds).then(users =>
      authorIds.map(id => users.find(u => u.id === id) || null)
    )
  );

  return ids.map(id => posts.find(p => p.id === id) || null);
});
```

**DataLoader Lifecycle:**

```typescript
// ✅ Correct — fresh per request
const server = new ApolloServer({
  schema,
  context: async ({ req }) => ({
    user: authenticate(req),
    loaders: {
      user: new DataLoader(batchUsers),
      post: new DataLoader(batchPosts),
    },
  }),
});

// ❌ Wrong — shared across ALL requests
const sharedLoaders = {
  user: new DataLoader(batchUsers),  // Never do this
};

const server = new ApolloServer({
  schema,
  context: () => ({ loaders: sharedLoaders }),
});
```

### 2.2 Resolver Composition

**Field-Level Authorization:**

```typescript
const resolvers = {
  User: {
    // Public field — everyone can see it
    username: (user) => user.username,

    // Semi-private — visible to self and admins
    email: (user, _, { currentUser }) => {
      if (currentUser?.id === user.id || currentUser?.isAdmin) {
        return user.email;
      }
      return null; // Silent field-level hide
    },

    // Fully private — never exposed to non-admins
    internalNotes: (user, _, { currentUser }) => {
      if (!currentUser?.isAdmin) {
        throw new ForbiddenError("Admin access required");
      }
      return user.internalNotes;
    },
  },
};
```

**Computed Fields:**

```typescript
const resolvers = {
  Post: {
    readingTime: (post) => {
      const wordsPerMinute = 200;
      const words = post.body.split(/\s+/).length;
      return Math.ceil(words / wordsPerMinute);
    },
    excerpt: (post, { maxLength = 200 }) => {
      if (post.body.length <= maxLength) return post.body;
      return post.body.slice(0, maxLength).replace(/\s+\S*$/, "") + "...";
    },
    isPopular: (post) => {
      return post.viewCount > 1000 || post.likeCount > 100;
    },
  },
};
```

**Recursive Resolvers:**

```graphql
type Category {
  id: ID!
  name: String!
  parent: Category
  children: [Category!]!
}
```

```typescript
const resolvers = {
  Category: {
    parent: (category, _, { loaders }) => {
      if (!category.parentId) return null;
      return loaders.category.load(category.parentId);
    },
    children: (category, _, { loaders }) => {
      return loaders.categoriesByParent.load(category.id);
    },
  },
};
```

**⚠️ Watch for infinite recursion.** A depth limit on the server is
insufficient if the data itself has circular references. Consider adding
a `maxDepth` argument or using `@skip`/`@include` patterns on the client.

### 2.3 Error Propagation Strategy

**The Rule of Nullability:**

GraphQL null-propagates errors upward through non-null fields. If a
`String!` field resolver throws, the error propagates to the nearest
nullable ancestor.

```
Post.author (User!)  ← throws here
  ↑
Post (Post)  ← this becomes null
  ↑
Query.post (Post)  ← and this becomes null
```

Design your nullability so that errors don't cascade further than necessary:

```graphql
type Query {
  # ✅ Error in post.author.email → post is still returned
  post(id: ID!): Post

  # ❌ Error in post.author.email → entire query fails
  post(id: ID!): Post!
}

type Post {
  # ✅ Error in author → post still returned, author is null
  author: User

  # ❌ Error in author → post becomes null
  author: User!
}
```

**Partial Data with Errors:**

GraphQL can return BOTH `data` AND `errors`:

```json
{
  "data": {
    "post": {
      "id": "42",
      "title": "Hello World",
      "author": null
    }
  },
  "errors": [
    {
      "message": "Failed to fetch author: connection timeout",
      "path": ["post", "author"],
      "extensions": {
        "code": "UPSTREAM_TIMEOUT",
        "retryable": true
      }
    }
  ]
}
```

---

## 3. Mutation Patterns

### 3.1 Input Type Design

**Single Input Argument (Always):**

```graphql
# ✅
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) { ... }
}

# ❌ Avoid
mutation CreatePost($title: String!, $body: String!) {
  createPost(title: $title, body: $body) { ... }
}
```

**Input Type Structure:**

```graphql
input CreatePostInput {
  """Required fields first"""
  title: String!
  body: String!

  """Optional fields with defaults"""
  tags: [String!] = []
  published: Boolean = false

  """Related entity references"""
  categoryId: ID!

  """Client-provided correlation for idempotency"""
  clientMutationId: String
}
```

**Nested Input Types:**

```graphql
input CreateOrderInput {
  customerId: ID!
  items: [OrderItemInput!]!
  shippingAddress: AddressInput!
  paymentMethod: PaymentMethodInput!
  idempotencyKey: String!
}

input OrderItemInput {
  productId: ID!
  quantity: PositiveInt!
  customizations: JSON
}
```

### 3.2 Idempotency Patterns

**Database-Level Idempotency:**

```typescript
async function createOrder(_, { input }, ctx) {
  const existing = await ctx.db.orders.findOne({
    idempotencyKey: input.idempotencyKey,
  });

  if (existing) {
    return { order: existing, errors: [] };
  }

  // Idempotency check + create in a transaction
  const order = await ctx.db.transaction(async (tx) => {
    const dup = await tx.orders.findOne({
      idempotencyKey: input.idempotencyKey,
    });
    if (dup) return dup;

    return tx.orders.create({
      ...validatedInput,
      idempotencyKey: input.idempotencyKey,
    });
  });

  return { order, errors: [] };
}
```

**Idempotency Key Generation:**

```typescript
// Client generates a UUID for each unique mutation attempt
const idempotencyKey = crypto.randomUUID();

// Store and retry with the same key on network failures
await client.mutate({
  mutation: CREATE_ORDER,
  variables: { input: { ...orderData, idempotencyKey } },
});
```

### 3.3 Transaction Patterns

**Multi-Entity Mutations:**

```typescript
async function checkoutCart(_, { input }, ctx) {
  return ctx.db.transaction(async (tx) => {
    // 1. Validate cart
    const cart = await tx.carts.findById(input.cartId);
    if (!cart || cart.items.length === 0) {
      return { order: null, errors: [{ __typename: "EmptyCartError", message: "..." }] };
    }

    // 2. Reserve inventory
    for (const item of cart.items) {
      const reserved = await tx.inventory.reserve(item.productId, item.quantity);
      if (!reserved) {
        return { order: null, errors: [{ __typename: "OutOfStockError", ... }] };
      }
    }

    // 3. Create order
    const order = await tx.orders.create({ ...cart, status: "CONFIRMED" });

    // 4. Clear cart
    await tx.carts.clear(input.cartId);

    return { order, errors: [] };
  });
}
```

### 3.4 Optimistic Concurrency

```graphql
input UpdatePostInput {
  id: ID!
  title: String
  body: String
  expectedVersion: Int!
}
```

```typescript
async function updatePost(_, { input }, ctx) {
  const result = await ctx.db.posts.updateOne(
    { id: input.id, version: input.expectedVersion },
    { $set: { ...input }, $inc: { version: 1 } },
  );

  if (result.matchedCount === 0) {
    return {
      post: null,
      errors: [{
        __typename: "ConflictError",
        message: "Post was modified by another request. Refresh and try again.",
      }],
    };
  }

  return { post: await ctx.loaders.post.load(input.id), errors: [] };
}
```

---

## 4. Subscription Patterns

### 4.1 Event Bus Architectures

**In-Memory PubSub (Development/Single Server):**

```typescript
import { PubSub } from "graphql-subscriptions";
const pubsub = new PubSub();

// Publishing
await pubsub.publish("MESSAGE_SENT", {
  messageSent: message,
  conversationId: message.conversationId,
});

// Subscribing
const resolvers = {
  Subscription: {
    messageSent: {
      subscribe: () => pubsub.asyncIterator(["MESSAGE_SENT"]),
    },
  },
};
```

**Redis PubSub (Production/Multi-Server):**

```typescript
import { RedisPubSub } from "graphql-redis-subscriptions";
import Redis from "ioredis";

const pubsub = new RedisPubSub({
  publisher: new Redis({ host: "redis" }),
  subscriber: new Redis({ host: "redis" }),
});
```

**Google Pub/Sub, Kafka, RabbitMQ:**

```typescript
import { PubSubEngine } from "graphql-subscriptions";

// Implement PubSubEngine interface for your message broker
class KafkaPubSub extends PubSubEngine {
  async publish(triggerName: string, payload: any): Promise<void> { ... }
  async subscribe(triggerName: string, onMessage: Function): Promise<number> { ... }
  async unsubscribe(subId: number): void { ... }
  asyncIterator<T>(triggers: string | string[]): AsyncIterator<T> { ... }
}
```

### 4.2 Filtering Patterns

**Basic withFilter:**

```typescript
const resolvers = {
  Subscription: {
    commentAdded: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(["COMMENT_ADDED"]),
        (payload, variables) => {
          return payload.commentAdded.postId === variables.postId;
        },
      ),
    },
  },
};
```

**Multi-Condition Filtering:**

```typescript
const resolvers = {
  Subscription: {
    orderUpdated: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(["ORDER_UPDATED"]),
        (payload, variables, context) => {
          const order = payload.orderUpdated;

          // Filter by order IDs if specified
          if (variables.orderIds?.length && !variables.orderIds.includes(order.id)) {
            return false;
          }

          // Filter by status transitions
          if (variables.statuses?.length && !variables.statuses.includes(order.status)) {
            return false;
          }

          // Authorization: only deliver if user owns the order
          if (order.userId !== context.user?.id && !context.user?.isAdmin) {
            return false;
          }

          return true;
        },
      ),
    },
  },
};
```

**Dynamic Topic Subscriptions:**

```typescript
const resolvers = {
  Subscription: {
    liveDocument: {
      subscribe: async (_, { documentId }, { user, db }) => {
        // Verify access before establishing the subscription
        const doc = await db.documents.findById(documentId);
        if (!doc || doc.ownerId !== user.id) {
          throw new ForbiddenError("Not authorized to watch this document");
        }

        // Dynamic topic based on document ID
        return pubsub.asyncIterator([`DOCUMENT:${documentId}`]);
      },
    },
  },
};
```

### 4.3 Cleanup & Resource Management

**AsyncIterator Cleanup:**

```typescript
const resolvers = {
  Subscription: {
    databaseChanges: {
      subscribe: async function* (_, { table }, { db }) {
        // Setup
        const listener = db.on("change", (change) => { ... });
        const interval = setInterval(() => { ... }, 1000);

        try {
          while (true) {
            // Yield events
            yield { databaseChanges: await getNextChange() };
          }
        } finally {
          // ALWAYS clean up, even if the client disconnects
          db.off("change", listener);
          clearInterval(interval);
        }
      },
    },
  },
};
```

**Return-Based Cleanup (graphql-subscriptions):**

```typescript
const resolvers = {
  Subscription: {
    liveCursor: {
      subscribe: (_, { documentId }, { db }) => {
        const watcher = db.documents.watch(documentId);

        // graphql-subscriptions v2+ uses { [Symbol.asyncIterator], return }
        const iterator = {
          [Symbol.asyncIterator]() { return this; },
          async next() {
            const change = await watcher.nextChange();
            return { value: { liveCursor: change }, done: false };
          },
          async return() {
            await watcher.close(); // Client disconnected — clean up
            return { value: undefined, done: true };
          },
          async throw(error) {
            await watcher.close();
            throw error;
          },
        };

        return iterator;
      },
    },
  },
};
```

---

## 5. Federation Patterns

### 5.1 Entity Resolution Flow

```
Client Query:
  query {
    post(id: "42") {
      title
      author {         ← Cross-subgraph field
        name
        email
      }
    }
  }

Gateway → Posts Subgraph (_entities):
  { "representations": [{ "__typename": "User", "id": "4" }] }

Posts Subgraph → Gateway (resolved):
  { "_entities": [{ "__typename": "User", "id": "4", "posts": [...] }] }

Gateway → Users Subgraph (_entities):
  { "representations": [{ "__typename": "User", "id": "4" }] }

Users Subgraph → Gateway:
  { "_entities": [{ "__typename": "User", "id": "4", "name": "...", "email": "..." }] }
```

### 5.2 Directive Reference

| Directive | Purpose | Scope |
|---|---|---|
| `@key(fields: "id")` | Marks entity primary key for cross-subgraph resolution | OBJECT |
| `@shareable` | Allows field to be resolved by multiple subgraphs | FIELD_DEFINITION, OBJECT |
| `@requires(fields: "product { price }")` | Declares fields needed from another subgraph | FIELD_DEFINITION |
| `@external` | Field defined here, resolved by another subgraph | FIELD_DEFINITION |
| `@provides(fields: "name")` | This subgraph can resolve the listed fields | FIELD_DEFINITION |
| `@tag(name: "public")` | Labels fields/types for contract-based API surfaces | ALL |
| `@inaccessible` | Hides field/type from the composed public API | ALL |
| `@override(from: "subgraph")` | Migrates field resolution to this subgraph | FIELD_DEFINITION |
| `@interfaceObject` | Entity can be resolved as an interface | OBJECT |

### 5.3 Entity Design Patterns

**Value Object as Entity:**

```graphql
# Instead of duplicating address info in every subgraph:
type Address @key(fields: "id") {
  id: ID!
  street: String!
  city: String!
  country: String!
  postalCode: String!
}

type User @key(fields: "id") {
  id: ID!
  address: Address!  # Cross-subgraph reference
}
```

**Computed Fields via @requires:**

```graphql
# Products subgraph
type Product @key(fields: "id") {
  id: ID!
  name: String!
  price: Money!
}

# Reviews subgraph
type Review @key(fields: "id") {
  id: ID!
  product: Product!
  rating: Int!
  valueRating: Float @requires(fields: "product { price }")
  # valueRating resolver: rating / price — uses product.price from Products subgraph
}
```

**Field Migration via @override:**

```graphql
# Step 1: Define field in both subgraphs
# Users subgraph
type User @key(fields: "id") {
  id: ID!
  email: String! @shareable
}

# Notifications subgraph
type User @key(fields: "id") {
  id: ID!
  email: String! @shareable @override(from: "users")
  # Now Notifications subgraph resolves email
}
```

---

## 6. Security Patterns

### 6.1 Depth Limiting Configuration

```typescript
import depthLimit from "graphql-depth-limit";

// Conservative: max depth 5 (typical for simple CRUD APIs)
depthLimit(5)

// Moderate: max depth 7 (most production APIs)
depthLimit(7)

// Liberal: max depth 10 (complex nested queries)
depthLimit(10)
```

| API Style | Recommended Depth | Reasoning |
|---|---|---|
| Simple CRUD | 5 | User → posts → author → profile is depth 4 |
| Social/Content | 7 | User → posts → comments → author → posts requires depth 6 |
| E-commerce | 5 | Product → variants → reviews → author is depth 4 |
| Enterprise/Reporting | 10 | Deeply nested organizational hierarchies |

### 6.2 Query Cost Analysis

```typescript
import costAnalysis from "graphql-cost-analysis";

const costConfig = {
  maximumCost: 1000,
  defaultCost: 1,
  variables: {},
  complexityMap: {
    // Expensive operations
    search: 10,
    fullTextSearch: 20,
    topPosts: 2,

    // Multipliers for connection fields
    users: ({ args }) => (args.first || 20) * 2,
    posts: ({ args }) => (args.first || 20),
    comments: ({ args }) => (args.first || 20) * 0.5,
  },
};
```

### 6.3 Rate Limiting Patterns

**Per-Operation Rate Limiting:**

```graphql
type Mutation {
  login(input: LoginInput!): LoginPayload!
    @rateLimit(limit: 5, duration: 60)     # 5 attempts per minute

  createPost(input: CreatePostInput!): CreatePostPayload!
    @rateLimit(limit: 30, duration: 60)    # 30 posts per minute

  sendMessage(input: SendMessageInput!): SendMessagePayload!
    @rateLimit(limit: 60, duration: 60)    # 60 messages per minute
}
```

**IP-Based vs Token-Based Rate Limiting:**

```typescript
const server = new ApolloServer({
  schema,
  plugins: [{
    async requestDidStart({ request, context }) {
      const key = context.user?.id || request.http.headers.get("x-forwarded-for") || "anonymous";
      // Use key for rate limit tracking
    },
  }],
});
```

### 6.4 Authentication Directives

```graphql
directive @auth(requires: Role = USER) on OBJECT | FIELD_DEFINITION

enum Role {
  ADMIN
  USER
  PUBLIC
}

type Query {
  me: User! @auth
  adminDashboard: DashboardData! @auth(requires: ADMIN)
  publicFeed: [Post!]! @auth(requires: PUBLIC)
}

type User @auth {
  id: ID!
  email: String! @auth(requires: ADMIN)
  ssn: String @auth(requires: ADMIN)
}
```

**Directive Implementation (graphql-tools):**

```typescript
import { mapSchema, getDirectives, MapperKind } from "@graphql-tools/utils";

function authDirective(schema) {
  return mapSchema(schema, {
    [MapperKind.OBJECT_FIELD]: (fieldConfig, fieldName, typeName) => {
      const directives = getDirectives(schema, fieldConfig);
      const authDirective = directives["auth"];
      if (authDirective) {
        const { resolve } = fieldConfig;
        const requiredRole = authDirective["requires"] || "USER";

        fieldConfig.resolve = async (source, args, context, info) => {
          if (!context.user && requiredRole !== "PUBLIC") {
            throw new AuthenticationError("Not authenticated");
          }
          if (requiredRole === "ADMIN" && !context.user?.isAdmin) {
            throw new ForbiddenError("Admin access required");
          }
          return resolve(source, args, context, info);
        };
      }
      return fieldConfig;
    },
  });
}
```

---

## 7. Performance Patterns

### 7.1 Caching Strategies

**Response Caching with Apollo Server:**

```typescript
import responseCachePlugin from "apollo-server-plugin-response-cache";

const server = new ApolloServer({
  plugins: [
    responseCachePlugin({
      sessionIdFromContext: (ctx) => {
        // Return null for public data (shared cache key)
        // Return user ID for private data (per-user cache key)
        return ctx.user?.id || null;
      },
      extraCacheKeyDataFromContext: (ctx) => {
        // Additional cache key segments
        return {
          locale: ctx.req.headers["accept-language"] || "en",
        };
      },
    }),
  ],
});
```

**Field-Level Cache Control:**

```graphql
enum CacheControlScope {
  PUBLIC
  PRIVATE
}

type Query {
  # Public data, cache 5 minutes — CDN can cache this
  topPosts: [Post!]! @cacheControl(maxAge: 300, scope: PUBLIC)

  # Private data, no cache — varies by user
  me: User @cacheControl(maxAge: 0, scope: PRIVATE)

  # Public but short-lived — 30 second CDN cache
  activeUsers: Int! @cacheControl(maxAge: 30, scope: PUBLIC)
}

type Post @cacheControl(maxAge: 600) {
  id: ID!
  title: String!
  body: String! @cacheControl(maxAge: 3600)  # Content rarely changes
  viewCount: Int! @cacheControl(maxAge: 30)   # Frequently updated
}
```

**Cache Invalidation via Mutations:**

```typescript
const resolvers = {
  Mutation: {
    updatePost: async (_, { input }, ctx) => {
      const post = await ctx.services.postService.update(input);
      // Invalidate related caches
      await ctx.cache.invalidate(`post:${post.id}`);
      await ctx.cache.invalidatePattern(`postsByAuthor:${post.authorId}:*`);
      return { post, errors: [] };
    },
  },
};
```

### 7.2 Persisted Queries (APQ)

**Full Setup:**

```typescript
// Server
import responseCachePlugin from "apollo-server-plugin-response-cache";
import { InMemoryLRUCache } from "@apollo/utils.keyvaluecache";

const server = new ApolloServer({
  schema,
  plugins: [responseCachePlugin()],
  persistedQueries: {
    cache: new InMemoryLRUCache({ maxSize: 1000 }),
    ttl: 900, // 15 minutes
  },
});

// Client
import { createPersistedQueryLink } from "@apollo/client/link/persisted-queries";
import { sha256 } from "crypto-hash";

const link = createPersistedQueryLink({
  sha256,
  useGETForHashedQueries: true, // Enable CDN caching
}).concat(httpLink);
```

**Flow:**
```
1. Client sends: { extensions: { persistedQuery: { sha256Hash } } }
   (no query text — just the hash)
2. Server looks up hash in cache:
   a. Found → executes query, returns result
   b. Not found → returns error: PERSISTED_QUERY_NOT_FOUND
3. Client retries with: { query: "full text", extensions: { persistedQuery: { sha256Hash } } }
4. Server executes, caches hash→query mapping, returns result
5. Subsequent requests only send the hash
```

### 7.3 Defer & Stream (Incremental Delivery)

**@defer — Defer Slow Fields:**

```graphql
query PostPage($id: ID!) {
  post(id: $id) {
    title
    author { name }
    ... on Post @defer {
      body             # Large, delivered later
      comments {       # Slow (N+1 or DB-intensive), delivered later
        body
        author { name }
      }
    }
  }
}
```

Response stream:
```json
// Payload 1: Immediate
{ "data": { "post": { "title": "...", "author": { "name": "..." } } },
  "hasNext": true }

// Payload 2: Deferred
{ "incremental": [{ "data": { "body": "...", "comments": [...] },
                    "path": ["post"] }],
  "hasNext": false }
```

**@stream — Stream List Items:**

```graphql
query Feed {
  feed @stream(initialCount: 5) {
    items {
      title
      author { name }
    }
  }
}
```

### 7.4 Monitoring & Observability

**Apollo Tracing:**

```typescript
import { ApolloServerPluginInlineTrace } from "@apollo/server/plugin/inlineTrace";

const server = new ApolloServer({
  plugins: [
    ApolloServerPluginInlineTrace({
      includeErrors: { unmodified: true },
    }),
  ],
});
```

**Custom Tracing Hooks:**

```typescript
const server = new ApolloServer({
  plugins: [{
    async requestDidStart(ctx) {
      const start = Date.now();
      const operationName = ctx.request.operationName || "anonymous";

      return {
        async willSendResponse(ctx) {
          const duration = Date.now() - start;
          metrics.recordQueryDuration(operationName, duration);
          if (ctx.errors) {
            metrics.incrementErrorCount(operationName);
          }
        },
        async executionDidStart() {
          return {
            willResolveField({ source, args, context, info }) {
              const fieldStart = Date.now();
              return (error, result) => {
                const fieldDuration = Date.now() - fieldStart;
                if (fieldDuration > 100) {
                  logger.warn(`Slow field: ${info.parentType}.${info.fieldName} took ${fieldDuration}ms`);
                }
                metrics.recordFieldDuration(
                  `${info.parentType}.${info.fieldName}`,
                  fieldDuration,
                );
              };
            },
          };
        },
      };
    },
  },
}]);
```

---

## 8. Anti-Pattern Encyclopedia

### 8.1 Schema Anti-Patterns

| Anti-Pattern | Why It's Bad | Fix |
|---|---|---|
| `getX`, `fetchX`, `listX` query names | Imperative naming; GraphQL is declarative | `x`, `searchX`, `xById` |
| `XCreate`, `XUpdate` mutation names | Noun-first; breaks tooling expectations | `createX`, `updateX` |
| Exposing DB column names as GraphQL fields | Leaks implementation details | Map to domain names (`created_at` → `createdAt`) |
| `JSON` scalar for all unstructured data | Loses type safety and documentation | Use proper types with `@specifiedBy` URLs |
| `String` for IDs | No type validation | Use `ID` scalar |
| Multiple query/mutation root types | Ambiguous entry points | Single `Query` and `Mutation` types |
| PUT/DELETE/GET in operation names | REST-isms in GraphQL | Use domain-specific verbs |
| Every field is nullable | Clients must null-check everything | Use `!` where absence would be a bug |

### 8.2 Resolver Anti-Patterns

| Anti-Pattern | Why It's Bad | Fix |
|---|---|---|
| DB call in every field resolver | N+1 queries | DataLoader batching |
| Throwing instead of returning null | Entire query fails for one missing field | Return null, add to errors array |
| Parsing `info.fieldNodes` for projection | Couples resolver to query shape | Use ORM features or separate projection logic |
| `context` as a global singleton | No request isolation | Fresh context per request |
| Synchronous I/O in event loops | Blocks the server | Always async resolvers |
| Resolver returning raw ORM objects | Over-fetching, security leaks | Map to DTOs/explicit fields |
| Logging at DEBUG in every resolver | Noise drowns signal | Log at appropriate levels; use tracing spans |

### 8.3 Security Anti-Patterns

| Anti-Pattern | Why It's Bad | Fix |
|---|---|---|
| Introspection enabled in production | Schema leak; attack surface | Gate or disable |
| No depth limit | Recursive query DoS | `depthLimit(N)` |
| No cost analysis | Wide queries bypass depth limit | `costAnalysis()` |
| Auth check after data fetch | Unauthorized data still loaded | Check auth BEFORE DB calls |
| Secrets in resolver code | Credential leak | Environment variables / vault |
| Raw error forwarding | Stack trace leak | Map to typed GraphQL errors |
| Server-side rendering of user input | XSS | Output-encode all user content |

---

## 9. Testing Patterns

### 9.1 Schema Testing

```typescript
import { makeExecutableSchema } from "@graphql-tools/schema";
import { graphql } from "graphql";

describe("Schema", () => {
  it("should reject queries beyond depth limit", async () => {
    const deepQuery = `
      query {
        user(id: "1") {
          posts { author { posts { author { posts { author { name } } } } } }
        }
      }
    `;
    const result = await graphql({ schema, source: deepQuery });
    expect(result.errors[0].message).toMatch(/depth/i);
  });

  it("should require authentication on admin fields", async () => {
    const query = `{ adminDashboard { stats } }`;
    const result = await graphql({ schema, source: query, contextValue: { user: null } });
    expect(result.errors[0].extensions.code).toBe("UNAUTHENTICATED");
  });
});
```

### 9.2 Resolver Testing

```typescript
describe("Post resolvers", () => {
  it("creates a post with valid input", async () => {
    const result = await graphql({
      schema,
      source: `mutation CreatePost($input: CreatePostInput!) {
        createPost(input: $input) { post { id title } errors { __typename } }
      }`,
      variableValues: {
        input: { title: "Test", body: "Content", categoryId: "1" },
      },
      contextValue: { user: testUser, loaders: createTestLoaders() },
    });

    expect(result.data.createPost.post.title).toBe("Test");
    expect(result.data.createPost.errors).toHaveLength(0);
  });
});
```

### 9.3 DataLoader Testing

```typescript
describe("User DataLoader", () => {
  it("batches multiple loads into a single DB call", async () => {
    const findByIds = jest.fn().mockResolvedValue([{ id: "1" }, { id: "2" }]);
    const loader = new DataLoader((ids) => findByIds([...ids]));

    const [user1, user2] = await Promise.all([
      loader.load("1"),
      loader.load("2"),
    ]);

    expect(findByIds).toHaveBeenCalledTimes(1);
    expect(findByIds).toHaveBeenCalledWith(["1", "2"]);
    expect(user1.id).toBe("1");
    expect(user2.id).toBe("2");
  });
});
```

---

## 10. Production Checklist

Before deploying a GraphQL API to production, verify:

### Schema Quality
- [ ] All types and fields have descriptions
- [ ] All mutations use verb-first naming
- [ ] All list fields are paginated
- [ ] Errors use typed unions, not strings
- [ ] Non-null used semantically (not everywhere)
- [ ] Deprecated fields have reasons and migration paths

### Performance
- [ ] DataLoader instances created per-request
- [ ] Persisted queries enabled (APQ)
- [ ] Cache control directives on appropriate fields
- [ ] Response caching plugin configured
- [ ] No N+1 queries on hot paths
- [ ] Query depth limit configured
- [ ] Query cost analysis configured

### Security
- [ ] Authentication in context, not resolvers
- [ ] Authorization on all mutations and sensitive fields
- [ ] Rate limiting on auth and expensive operations
- [ ] Introspection gated in production
- [ ] No hardcoded secrets
- [ ] Error messages don't leak internals

### Observability
- [ ] Apollo Tracing or OpenTelemetry enabled
- [ ] Slow resolver alerting configured
- [ ] Error rate monitoring
- [ ] DataLoader batch size metrics
- [ ] Subscription connection metrics

### Federation (if applicable)
- [ ] Every entity has a @key directive
- [ ] Every entity has __resolveReference implemented
- [ ] _service and _entities queries present
- [ ] @shareable fields coordinated across teams
- [ ] No circular @key reference chains
- [ ] Rover schema checks in CI/CD pipeline