# Codebase Design Glossary (Expanded)

Use these terms exactly. Consistent language is the whole point.

## Core Terms

| Term | Definition | Avoid |
|------|-----------|-------|
| Module | Anything with an interface and an implementation. Deliberately scale-agnostic: a function, class, package, or tier-spanning slice. | unit, component, service |
| Interface | Everything a caller must know to use the module correctly: the type signature, but also invariants, ordering constraints, error modes, required configuration, and performance characteristics. | API, signature (too narrow) |
| Implementation | What's inside a module, its body of code. Distinct from **Adapter**: a thing can be a small adapter with a large implementation (a Postgres repo) or a large adapter with a small implementation (an in-memory fake). Reach for "adapter" when the seam is the topic; "implementation" otherwise. | — |
| Depth | Leverage at the interface. The amount of behaviour a caller (or test) can exercise per unit of interface they have to learn. A module is **deep** when a large amount of behaviour sits behind a small interface, **shallow** when the interface is nearly as complex as the implementation. | — |
| Seam (Michael Feathers) | A place where you can alter behaviour without editing in that place; the *location* at which a module's interface lives. Where to put the seam is its own design decision, distinct from what goes behind it. | boundary (overloaded with DDD's bounded context) |
| Adapter | A concrete thing that satisfies an interface at a seam. Describes *role* (what slot it fills), not substance (what's inside). | — |
| Leverage | What callers get from depth. More capability per unit of interface they learn. One implementation pays back across N call sites and M tests. | — |
| Locality | What maintainers get from depth. Change, bugs, knowledge, and verification concentrate in one place rather than spreading across callers. Fix once, fixed everywhere. | — |

## Relationships

- A **Module** has exactly one **Interface** (the surface it presents to
  callers and tests).
- **Depth** is a property of a **Module**, measured against its
  **Interface**.
- A **Seam** is where a **Module**'s **Interface** lives.
- An **Adapter** sits at a **Seam** and satisfies the **Interface**.
- **Depth** produces **Leverage** for callers and **Locality** for
  maintainers.

## Rejected framings

- **Depth as ratio of implementation-lines to interface-lines**
  (Ousterhout): rewards padding the implementation. We use
  depth-as-leverage instead.
- **"Interface" as the TypeScript `interface` keyword or a class's public
  methods**: too narrow: interface here includes every fact a caller must
  know.
- **"Boundary"**: overloaded with DDD's bounded context. Say **seam** or
  **interface**.