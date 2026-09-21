# Code Simplification — Language and Tool Patterns

## TypeScript / JavaScript

| Pattern | Before (complex) | After (simplified) |
|---------|------------------|---------------------|
| Early return over nested if | `if (x) { if (y) { return z } return null }` | `if (!x || !y) return null; return z` |
| Guard clause chain | `if (a) { if (b) { if (c) { doWork() } } }` | `if (!a || !b || !c) return; doWork()` |
| Boolean flag parameter | `processOrder(order, true, false, 'rush')` | Expose as `OrderOptions` object or split into named functions |
| Array method over loop | `for (let i = 0; i < items.length; i++) { ... }` | `items.map(...)`, `items.filter(...)` |
| Ternary to if/return | `return cond ? val1 : val2` (short) — keep | `return cond ? deeplyNested(cond) ? ...` — break into if blocks |

## Python

| Pattern | Before (complex) | After (simplified) |
|---------|------------------|---------------------|
| Dict lookup with default | `if key in d: return d[key] else: return default` | `return d.get(key, default)` |
| Guard clause | `def f(): if cond: ... long body ...` | `def f(): if not cond: return; ... long body ...` |
| Combined condition | `if a and b and not c and d:` | Extract intent as named variable `is_ready = a and b and not c and d` |
| Comprehension over loop | `result = []; for x in items: result.append(x.foo)` | `result = [x.foo for x in items]` |
| Context manager | `f = open(path); ...; f.close()` | `with open(path) as f: ...` |

## React

| Pattern | Before (complex) | After (simplified) |
|---------|------------------|---------------------|
| Conditional rendering | `{condition ? <Component /> : null}` | `{condition && <Component />}` |
| Extracted callback | `onClick={() => doSomething(id)}` in JSX | Move to stable callback if re-render is a concern |
| Derived state over effect | `useEffect(() => setFullName(first + ' ' + last), [first, last])` | `const fullName = first + ' ' + last` (computed during render) |

## Go

| Pattern | Before (complex) | After (simplified) |
|---------|------------------|---------------------|
| Error guard | `if err != nil { return err }` — keep (Go idiom) | Do NOT collapse errors: Go's explicit error handling is intentional |
| Map check | `if v, ok := m[key]; ok { return v } else { return fallback }` | `if v, ok := m[key]; ok { return v }; return fallback` |
| Switch over if-else chain | `if x == 1 { ... } else if x == 2 { ... } else if x == 3 { ... }` | `switch x { case 1: ... case 2: ... case 3: ... }` |

## When NOT to Apply These Patterns

- **Performance hot spots**: Array methods and list comprehensions have allocation costs. In inner loops, sometimes `for` is the right call.
- **Frameworks with conventions**: If the project standard is `if/else` because consistency matters, don't switch to ternaries just because they're shorter.
- **Generated/boilerplate code**: Tools generate verbose but predictable patterns. Simplifying them removes the predictability without adding value.
- **Public API surface**: Changing function signatures or return types to simplify internals breaks consumers.

---

## Tools That Help (Not Replace)

These tools automate the mechanical parts of simplification but can't judge intent:

| Tool | Scope | Limitation |
|------|-------|------------|
| Prettier / Ruff / gofmt | Formatting | Style only, no structural changes |
| ESLint `complexity` rule | Cyclomatic complexity reporting | Flags problems, doesn't fix them |
| `sonarlint` | Code smell detection | Can produce false positives on domain-specific complexity |
| JSCPD / PMD-CPD | Duplication detection | Finds duplicates, doesn't decide which to extract |
| `pyflakes` | Dead code detection | Conservative — doesn't catch unreachable paths in conditional logic |
| Codemod / jscodeshift | Automated large-scale changes | Only for deterministic, pattern-matched transformations |

Use the skill's judgment layer — the above tools are your assistants, not your replacement.