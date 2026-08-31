# Style Guides Reference

Concise style rules for common languages. Use these as a baseline when
performing code reviews. When a project has its own style config
(`.eslintrc`, `.prettierrc`, `pyproject.toml`, `golangci-lint`, etc.),
prefer the project's configuration.

---

## Python (PEP 8)

### Indentation
- 4 spaces per indentation level. Never tabs.
- Continuation lines: align with opening delimiter or use hanging indent (extra 4 spaces).

### Line Length
- Maximum 79 characters for code, 72 for docstrings/comments.
- Projects often extend to 88 (Black), 100, or 120 — check project config.

### Imports
- One import per line.
- Order: standard library → third-party → local application.
- Separate groups with a blank line.
- No wildcard imports (`from module import *`).

### Whitespace
- No trailing whitespace.
- Surround binary operators with single space.
- No space immediately inside parentheses, brackets, or braces.
- No space before comma/semicolon/colon, one space after.
- Function annotations: no space before colon, one space after.

### Naming
- `snake_case` for functions, variables, methods, modules.
- `PascalCase` for classes and exceptions.
- `UPPER_CASE` for constants.
- `_leading_underscore` for non-public methods/attributes.
- `__double_leading` for name mangling (avoid unless necessary).
- `__dunder__` for magic methods only.

### Blank Lines
- 2 blank lines before top-level functions and classes.
- 1 blank line before method definitions inside a class.
- Use blank lines sparingly inside functions to separate logical sections.

### Strings
- Consistent quote choice (single or double) throughout the file.
- Triple-quoted for docstrings. Use `"""` even if project uses `'`.
- Prefer f-strings over `.format()` and `%`-formatting.

### Comments
- Block comments: start with `# `, complete sentences, 72 char max.
- Inline comments: use sparingly, 2 spaces before `#`.
- Docstrings: triple-quoted, first line is summary, blank line, then details.

### Common Idioms
- Use `is` / `is not` for `None` comparisons. Never `== None`.
- Use `not` for boolean checks, not `== False`.
- Truthiness: `if seq:` not `if len(seq) > 0:`.
- Context managers (`with`) for resource management.
- List/dict/set comprehensions for simple cases; avoid nested comprehensions.
- Don't use mutable default arguments.

### Python Anti-patterns to Flag
- Bare `except:` clauses (at minimum `except Exception:`).
- `except:` followed by `pass`.
- Mutable default arguments (`def fn(items=[])`).
- `from module import *`.
- Global variables at module level.
- `type()` for type checking (use `isinstance()`).

---

## JavaScript

### Indentation
- 2 spaces (most common, especially with Prettier). Some projects use 4.

### Semicolons
- Project-dependent: either always or never (ASI). Be consistent.
- Prettier adds them; Standard/StandardX removes them.

### Quotes
- Single quotes preferred unless escaping needed. Prettier default: double.

### Naming
- `camelCase` for variables, functions, methods.
- `PascalCase` for classes, components, constructors.
- `UPPER_SNAKE_CASE` for true constants.
- No leading/trailing underscores (except `_` prefix for unused params convention).

### Variables
- Prefer `const` by default. Use `let` when reassignment is needed.
- Never `var` — it's function-scoped, hoisting is confusing.
- Declare variables at the top of their scope.
- One `const`/`let` per line is common; grouped destructuring is fine.

### Functions
- Prefer arrow functions for callbacks and short functions.
- Use regular functions for methods that need `this` binding.
- Default parameters over manual `||` checks.
- Rest parameters (`...args`) over `arguments` object.

### Objects & Arrays
- Use shorthand property/method syntax: `{ name }` not `{ name: name }`.
- Trailing commas in multiline (Prettier default).
- Destructuring for extracting multiple properties.
- Spread operator over `Object.assign`.

### Strings
- Template literals for string interpolation and multiline strings.
- Avoid unnecessary template literals for single strings.

### Comparisons
- `===` and `!==` — never `==` or `!=` (except `== null` for null-or-undefined check).
- Boolean conversion: `!!value` or `Boolean(value)`.

### Async
- `async`/`await` over raw Promise chains.
- Always handle promise rejections (`.catch()` or `try/catch` with `await`).
- Don't mix `await` and `.then()` in the same logical block.

### Modules
- ES modules (`import`/`export`) over CommonJS (`require`/`module.exports`).
- Group imports: external → internal → styles.
- Named exports preferred over default exports (better IDE support).

### JavaScript Anti-patterns
- `var` anywhere.
- `==` comparisons (outside of deliberate `== null`).
- Unhandled promise rejections.
- Mutating function parameters.
- `eval()`.
- `new Array()` or `new Object()` (use literals).
- `for...in` on arrays (use `for...of` or `forEach`).

---

## TypeScript

All JavaScript rules apply, plus:

### Types
- Prefer `interface` over `type` for object shapes (more extensible).
- Use `type` for unions, intersections, and mapped types.
- Explicit return types on public/exported functions.
- No `any` — use `unknown` and narrow with type guards.
- Prefer `as` casts over angle-bracket syntax.

### Enums
- Prefer `const enum` or string union types over numeric enums.
- String enums are safer for serialization.

### Nullability
- Use `strictNullChecks`.
- Prefer `??` over `||` for null/undefined coalescing.
- Optional chaining: `obj?.prop?.nested`.

### Generics
- Single-letter names are acceptable when the purpose is obvious (`T`, `K`, `V`).
- Descriptive names for complex generics (`TItem`, `TResponse`).

### TypeScript Anti-patterns
- `any` — always flag as MINOR or MAJOR.
- `as any` casts — defeats type checking.
- `@ts-ignore` or `@ts-expect-error` without justification.
- Type assertions that can mask errors (`as unknown as TargetType`).
- Non-null assertions (`!`) without justification.

---

## Go

### Formatting
- Always run through `gofmt` or `goimports`. Non-negotiable.
- `gofumpt` is a stricter formatter — check if project uses it.

### Naming
- `MixedCaps` for exported identifiers (`ServeHTTP`).
- `mixedCaps` for unexported.
- Short, concise names: `i` for index, `r` for reader, `w` for writer.
- Acronyms are all caps or all lower: `HTTPServer`, `httpserver` (not `HttpServer`).
- Package names: lowercase, single word, no underscores.

### Error Handling
- Handle errors immediately; don't ignore with `_`.
- `if err != nil { return err }` is idiomatic.
- Wrap errors with context: `fmt.Errorf("doing X: %w", err)`.
- Sentinel errors: `var ErrNotFound = errors.New("not found")`.
- Custom error types with `Error()` method.

### Variables
- Short declaration `:=` inside functions.
- `var` for zero-value initialization or package-level.
- Zero values are useful; don't initialize unnecessarily.

### Control Flow
- No parentheses around `if` conditions.
- Opening brace on same line as `if`/`for`/`func`.
- Use `switch` for multiple if-else chains.
- Defer for cleanup (but be aware of defer-in-loop performance).

### Concurrency
- Don't communicate by sharing memory; share memory by communicating.
- Channels for coordination, mutexes for simple shared state.
- Always use `context.Context` for cancellation/timeout propagation.
- `sync.WaitGroup`, `errgroup.Group` for goroutine coordination.

### Packages
- Avoid package-level global state.
- Accept interfaces, return structs.
- Interface defined at consumer, not producer.

### Go Anti-patterns
- Ignoring errors with `_`.
- Panic in library code.
- Goroutine leaks (no cancellation/cleanup).
- `interface{}` everywhere (prefer specific types or generics in 1.18+).
- String concatenation in loops (use `strings.Builder`).
- Passing mutex by value (use pointer).

---

## Rust

### Formatting
- Always `rustfmt`. Non-negotiable.
- `cargo clippy` for linting.

### Naming
- `snake_case` for variables, functions, modules, crates.
- `PascalCase` for types, traits, enums (variants also PascalCase).
- `UPPER_SNAKE_CASE` for `const` and `static`.
- Constructor function: `new()` is convention.

### Ownership & Borrowing
- Prefer borrows over owned values when possible.
- Use references (`&T`, `&mut T`) rather than cloning.
- Derive `Clone` sparingly; prefer borrow-based APIs.
- Explicit lifetime annotations only when compiler requires them.

### Error Handling
- `Result<T, E>` over panics; `unwrap()`/`expect()` only in tests or when truly infallible.
- Custom error types with `thiserror` or manual `Display`/`Error` impl.
- `anyhow` for application code; `thiserror` for libraries.
- `?` operator for propagation.

### Types
- Derive common traits: `Debug`, `Clone`, `PartialEq`, `Eq`, `Hash`.
- Newtype pattern for type safety: `struct UserId(u64)` not bare `u64`.
- Prefer `enum` over `bool` parameters for clarity.
- Use `Option<T>` over nullable/null.

### Concurrency
- `Send` + `Sync` for thread safety (compiler enforced).
- `Arc<Mutex<T>>` or `Arc<RwLock<T>>` for shared mutable state.
- Channels from `std::sync::mpsc` or `tokio::sync`.
- Prefer message passing with channels over shared state.

### Unsafe Rust
- Every `unsafe` block must have a SAFETY comment explaining invariants.
- Minimize `unsafe` surface area.
- Prefer safe abstractions from `std` or well-audited crates.

### Rust Anti-patterns
- Excessive `clone()` instead of borrowing.
- `unwrap()` in production code.
- `unsafe` without safety documentation.
- Giant `match` arms (extract into functions).
- Unconstrained generic parameters.
- Deref polymorphism abuse (implementing `Deref` for non-smart-pointer types).

---

## Java

### Formatting
- 4 spaces indentation. No tabs.
- Opening brace on same line (K&R style).
- Line width: 100-120 characters.

### Naming
- `PascalCase` for classes, interfaces, enums.
- `camelCase` for methods, variables, parameters.
- `UPPER_SNAKE_CASE` for `static final` constants.
- Package names: all lowercase, reverse domain.

### Structure
- One public class per file (filename matches class name).
- Members in order: static fields → instance fields → constructors → methods.
- Public methods before private methods.

### Best Practices
- Use `Optional` for nullable return types (not for fields or parameters).
- Streams API for declarative data processing (but keep simple — no monster chains).
- Records for data carriers (Java 14+).
- `var` for local variables when type is obvious from right-hand side (Java 10+).
- Try-with-resources for `AutoCloseable` resources.

### Java Anti-patterns
- Returning `null` instead of `Optional` for optional values.
- Raw types (use generics).
- Catching `Exception` broadly (be specific).
- `String` concatenation in loops (use `StringBuilder`).
- Public fields (except in records/DTOs).
- `static` mutable state.

---

## General Cross-Language Rules

These apply regardless of language:

### Naming
- Names should reveal intent. `d` tells me nothing; `daysSinceLastLogin` does.
- No abbreviations unless universally understood in the domain (`id`, `url`, `http`).
- Boolean names: `isActive`, `hasPermission`, `canEdit`, `shouldRetry`.
- Collection names are plural: `users`, `activeSessions`.

### Function Design
- Functions do one thing. If you need "and" in the name, split it.
- No boolean parameters that change behavior entirely (`render(true)`). Use two functions or an enum.
- Avoid output parameters (mutate arguments). Return a result instead.
- Limit parameters to ~4 max. Use an options object or struct beyond that.

### Commenting
- Don't comment what the code says. Comment why it says it.
- Remove commented-out code. Git remembers.
- TODO comments need a ticket reference and owner: `// TODO(#1234): Add retry logic — jane`.
- Update comments when code changes. Outdated comments are worse than no comments.

### Error Messages
- Be specific: "Failed to connect to payment service after 3 retries" not "Error".
- Include context: what was being attempted, with what inputs (sanitized).
- No exclamation marks in production error messages.

### Logging
- INFO: significant lifecycle events (server started, config loaded, migration complete).
- WARN: unexpected but handled (retry succeeded, fallback used, quota at 80%).
- ERROR: operation failed, needs attention (payment failed, DB unreachable, crash).
- DEBUG: detailed diagnostic info for developers.
- Never log PII, secrets, or full request bodies.