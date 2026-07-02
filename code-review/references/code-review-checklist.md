# Code Review Checklist

A comprehensive reference for systematic code review. Work through each
section when reviewing code. Not every item applies to every change — use
judgment.

---

## 1. Security

### 1.1 Injection Attacks
- [ ] SQL queries use parameterized statements / prepared statements (no string concatenation)
- [ ] OS command execution uses safe APIs (e.g., `subprocess.run` with list args, no `shell=True`)
- [ ] LDAP, XPath, XQuery use parameterized interfaces
- [ ] No dynamic code evaluation (`eval`, `exec`, `Function()` constructor) on untrusted input
- [ ] Template injection guarded (user input not passed directly to template engines)
- [ ] Regular expressions checked for ReDoS (no nested quantifiers on user input: `(a+)+$`)

### 1.2 Authentication & Session Management
- [ ] Authentication logic uses constant-time comparison (no early-exit string comparison)
- [ ] Password handling uses appropriate hashing (bcrypt, argon2, scrypt — never MD5/SHA-1/SHA-256 alone)
- [ ] Session tokens are cryptographically random (not `Math.random()` or `random.randrange()`)
- [ ] Session cookies set with HttpOnly, Secure, SameSite flags
- [ ] No authentication bypass paths (check every new endpoint/route)
- [ ] Multi-factor authentication changes reviewed carefully
- [ ] Password reset flows use time-limited, single-use tokens
- [ ] Rate limiting on login/2FA/reset endpoints

### 1.3 Authorization & Access Control
- [ ] Every new endpoint/action has authorization checks
- [ ] No reliance on client-side-only access control (e.g., hiding UI elements)
- [ ] Direct object references validated against ownership/entitlement
- [ ] Role/permission checks are server-side and not bypassable
- [ ] JWT tokens validated properly (signature, expiry, issuer, audience)
- [ ] No privilege escalation path through parameter manipulation

### 1.4 Data Protection
- [ ] Secrets: no hardcoded API keys, tokens, passwords, private keys, certificates
- [ ] PII/sensitive data not logged in plain text
- [ ] Sensitive data encrypted at rest (databases, backups)
- [ ] Data in transit uses TLS 1.2+ (no plain HTTP for sensitive endpoints)
- [ ] Debug endpoints/modes not exposed in production
- [ ] Error messages don't leak stack traces, DB schemas, or internal paths
- [ ] Sensitive headers stripped or masked in logs (Authorization, Cookie, Set-Cookie)

### 1.5 Input Validation & Output Encoding
- [ ] All user input validated: type, length, format, range, character set
- [ ] Input validated server-side even if validated client-side
- [ ] File uploads: type validated by content (magic bytes), not extension; size limits enforced
- [ ] Output encoded for the right context (HTML entity, JS encoding, URL encoding, CSS encoding)
- [ ] Content-Type headers set correctly; no MIME sniffing (`X-Content-Type-Options: nosniff`)

### 1.6 Cryptography
- [ ] No custom/homegrown cryptographic algorithms
- [ ] Adequate key sizes (RSA ≥2048, ECC ≥256, AES ≥128)
- [ ] No deprecated algorithms: MD5, SHA-1 (for security), DES, 3DES, RC4, RC2
- [ ] CBC mode with PKCS padding validated for padding oracle risk (use AEAD: GCM, ChaCha20-Poly1305)
- [ ] Random values from `secrets` module / `crypto.randomBytes` / `/dev/urandom` — NOT `Math.random()`
- [ ] IVs/nonces are unique and unpredictable (not hardcoded or reused)

### 1.7 File & Path Operations
- [ ] Path traversal prevented: user input sanitized, canonicalized, validated against base directory
- [ ] Zip slip prevented when extracting archives
- [ ] Deserialization: never use `pickle`, `yaml.load()`, `Marshal.load`, `unserialize()` on untrusted data
- [ ] XML parsing: disable external entities (XXE), disable DTD processing
- [ ] File permissions: least privilege on created files (no world-writable)

### 1.8 Dependency Security
- [ ] New dependencies reviewed for maintenance status, popularity, known vulnerabilities
- [ ] No dependency on abandoned/unmaintained packages
- [ ] Pinned versions (not ranges) for reproducible builds
- [ ] Supply chain: check for typosquatting, dependency confusion

### 1.9 Configuration & Deployment
- [ ] No debug mode in production
- [ ] Security headers set (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
- [ ] CORS configured restrictively (not `Access-Control-Allow-Origin: *` with credentials)
- [ ] Default credentials changed; no hardcoded admin passwords
- [ ] CSRF protection on state-changing operations

---

## 2. Correctness & Logic

### 2.1 Core Logic
- [ ] Does the code do what it claims/intends to do?
- [ ] Edge cases handled: null/undefined/empty, zero, negative, very large values
- [ ] Boundary conditions correct (off-by-one in loops, array indices)
- [ ] Boolean logic correct (De Morgan's laws, operator precedence in conditions)
- [ ] No inverted conditions (`!=` where `==` intended, wrong comparison direction)
- [ ] Floating-point comparisons use epsilon/tolerance

### 2.2 Concurrency & Async
- [ ] No race conditions (shared mutable state accessed from multiple threads/goroutines)
- [ ] Proper synchronization (locks, channels, atomics) where needed
- [ ] No deadlock potential (consistent lock ordering)
- [ ] Async/await used correctly: no missing `await`, no fire-and-forget where result needed
- [ ] Event-loop blocking: no CPU-intensive or sync I/O on the event loop

### 2.3 Error Handling
- [ ] Errors are caught, not silently swallowed
- [ ] No empty `catch`/`except` blocks (or justified with comment)
- [ ] Error messages are useful and actionable
- [ ] No sensitive data leaked in error messages
- [ ] Transactions rolled back on failure
- [ ] Resource cleanup in `finally`/`defer`/context managers (files, connections, locks)
- [ ] Retry logic has backoff and max attempts

### 2.4 Data Integrity
- [ ] Null/undefined references checked before use
- [ ] Division by zero guarded
- [ ] Integer overflow/underflow considered (especially in C/C++/Rust unsafe)
- [ ] Type conversions are safe (no silent truncation or precision loss)
- [ ] Date/time handling uses proper timezone-aware APIs

---

## 3. Code Quality & Maintainability

### 3.1 Readability
- [ ] Variable/function/class names are descriptive and pronounceable
- [ ] No single-letter names except in tight scopes (loop index `i`, closure parameter `x`)
- [ ] No misleading names (e.g., `processData` that also sends emails)
- [ ] Functions do one thing (Single Responsibility)
- [ ] Complex expressions broken into named intermediate values
- [ ] Magic numbers replaced with named constants

### 3.2 Structure
- [ ] Functions are small (< ~50 lines; flag if >100)
- [ ] Classes/modules have coherent responsibility
- [ ] No deep nesting (>3-4 levels deep in conditionals/loops)
- [ ] Early returns used to reduce nesting (guard clauses)
- [ ] Cyclomatic complexity reasonable (< ~10 per function)
- [ ] No god objects or god functions

### 3.3 Duplication
- [ ] DRY: no copy-pasted code blocks
- [ ] Repeated patterns extracted into shared functions/utilities
- [ ] Configuration not duplicated across environments/files
- [ ] Rule of three: first time write it, second time copy it, third time refactor it

### 3.4 Comments & Documentation
- [ ] Comments explain *why*, not *what*
- [ ] No commented-out code (use version control instead)
- [ ] TODO/FIXME/HACK comments have ticket references and owners
- [ ] Public APIs have docstrings/JSDoc/documentation comments
- [ ] Complex algorithms have explanatory comments
- [ ] No misleading or outdated comments

### 3.5 Dead Code
- [ ] No unreachable code
- [ ] No unused imports, variables, functions, parameters
- [ ] No dead stores (assigned but never read)

---

## 4. Style Guide Compliance

### 4.1 General
- [ ] Consistent formatting throughout
- [ ] Line length within project standard (typically 80-120)
- [ ] Consistent brace/bracket style
- [ ] Consistent indentation (tabs vs spaces, width)
- [ ] Consistent quote style (single vs double)
- [ ] Imports organized and grouped (stdlib, third-party, local)

### 4.2 Language-Specific
- [ ] Python: PEP 8 compliance (see `style-guides.md`)
- [ ] JavaScript/TypeScript: project ESLint/Prettier config
- [ ] Go: `gofmt` / `goimports` compliant
- [ ] Rust: `rustfmt` compliant, no unnecessary `unsafe`
- [ ] Java: project checkstyle config
- [ ] See `references/style-guides.md` for detailed per-language rules

---

## 5. Architecture & Design

### 5.1 Architectural Fit
- [ ] Change fits the existing architectural patterns
- [ ] New patterns introduced intentionally, not accidentally
- [ ] Abstractions at the right level (not too thin, not too thick)
- [ ] No leaky abstractions exposing implementation details through interfaces

### 5.2 Coupling & Cohesion
- [ ] New code doesn't introduce tight coupling between unrelated modules
- [ ] Dependency direction follows architectural layering (no upward references)
- [ ] Circular dependencies avoided
- [ ] Interface segregation: clients shouldn't depend on methods they don't use

### 5.3 Database
- [ ] Schema changes are backward compatible (or have migration plan)
- [ ] Migrations have rollback plan
- [ ] No data loss in schema changes
- [ ] Indexes exist for new query patterns
- [ ] N+1 query problem avoided
- [ ] Appropriate use of transactions for multi-step operations

### 5.4 API Design
- [ ] API changes are backward compatible (or versioned)
- [ ] Consistent naming conventions with existing endpoints
- [ ] Appropriate HTTP methods and status codes
- [ ] Request/response schemas validated
- [ ] Pagination on list endpoints

---

## 6. Test Coverage

### 6.1 Test Presence
- [ ] Tests exist for new behavior
- [ ] Tests exist for bug fixes (regression tests)
- [ ] Happy path covered
- [ ] Edge cases covered (empty, null, boundary, error)
- [ ] Error conditions covered

### 6.2 Test Quality
- [ ] Tests are deterministic (no flakiness from time, random, network)
- [ ] Tests are independent (can run in any order)
- [ ] Tests are fast (< few seconds each)
- [ ] Test descriptions clearly state what is being tested
- [ ] Mocks/stubs used appropriately for external dependencies
- [ ] Not testing implementation details (test behavior, not internals)

### 6.3 Critical Paths
- [ ] Authentication/authorization flows tested
- [ ] Payment/transaction flows tested
- [ ] Data integrity operations tested
- [ ] Security-sensitive code has tests for failure modes

---

## 7. Performance

### 7.1 Algorithmic Efficiency
- [ ] Time complexity appropriate for expected input size
- [ ] No O(n²) or worse on unbounded inputs
- [ ] Appropriate data structures used (Map/Set for lookups, not Array.includes)
- [ ] No unnecessary copies/allocation of large data structures

### 7.2 Database Performance
- [ ] No N+1 query problems
- [ ] Queries use indexes (EXPLAIN plan reviewed for new queries)
- [ ] No SELECT * on large tables without need
- [ ] Appropriate batch operations (not one query per row)
- [ ] Connection pooling used properly

### 7.3 Memory
- [ ] No unbounded in-memory collections (streaming/batching for large datasets)
- [ ] No memory leaks (unclosed resources, growing caches, detached DOM nodes)
- [ ] Large objects released when no longer needed

### 7.4 Network & I/O
- [ ] No unnecessary API calls in loops
- [ ] Appropriate caching headers and strategies
- [ ] Asset sizes considered (large images, bundles, dependencies)
- [ ] Lazy loading where appropriate

---

## 8. Observability

### 8.1 Logging
- [ ] Important state transitions logged
- [ ] Errors logged with context (not just "something failed")
- [ ] Appropriate log levels used (DEBUG, INFO, WARN, ERROR)
- [ ] No sensitive data in logs
- [ ] Structured logging used (JSON) for machine parsing

### 8.2 Metrics & Monitoring
- [ ] Key operations instrumented (duration, error rate)
- [ ] Business metrics tracked if relevant
- [ ] Alerting thresholds considered for critical paths

### 8.3 Tracing
- [ ] Distributed tracing context propagated
- [ ] Correlation IDs / request IDs logged and returned

---

## 9. Documentation (User-Facing)

- [ ] Public API docs updated
- [ ] README updated if setup/configuration changed
- [ ] Changelog entry appropriate
- [ ] Breaking changes clearly documented with migration guide
- [ ] Environment variables / configuration changes documented