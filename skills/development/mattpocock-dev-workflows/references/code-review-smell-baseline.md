# Code Review Smell Baseline

These are the Fowler code smells from *Refactoring* (ch.3) that apply in
every code review, even when the repo documents no coding standards.

## Rules

- **The repo overrides.** A documented repo standard always wins; where it
  endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible
  Feature Envy"), never a hard violation.
- **Skip anything tooling already enforces** (linters, formatters, type
  checkers).

## The Smells

### Mysterious Name
A function, variable, or type whose name doesn't reveal what it does or
holds. → Rename it; if no honest name comes, the design's murky.

### Duplicated Code
The same logic shape appears in more than one hunk or file in the change.
→ Extract the shared shape, call it from both.

### Feature Envy
A method that reaches into another object's data more than its own.
→ Move the method onto the data it envies.

### Data Clumps
The same few fields or params keep travelling together (a type wanting to
be born). → Bundle them into one type, pass that.

### Primitive Obsession
A primitive or string standing in for a domain concept that deserves its
own type. → Give the concept its own small type.

### Repeated Switches
The same `switch`/`if`-cascade on the same type recurs across the change.
→ Replace with polymorphism, or one map both sites share.

### Shotgun Surgery
One logical change forces scattered edits across many files in the diff.
→ Gather what changes together into one module.

### Divergent Change
One file or module is edited for several unrelated reasons.
→ Split so each module changes for one reason.

### Speculative Generality
Abstraction, parameters, or hooks added for needs the spec doesn't have.
→ Delete it; inline back until a real need shows.

### Message Chains
Long `a.b().c().d()` navigation the caller shouldn't depend on.
→ Hide the walk behind one method on the first object.

### Middle Man
A class or function that mostly just delegates onward.
→ Cut it, call the real target direct.

### Refused Bequest
A subclass or implementer that ignores or overrides most of what it
inherits. → Drop the inheritance, use composition.