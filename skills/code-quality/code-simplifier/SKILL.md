---
name: code-simplifier
description: Simplify, clean up, or tidy code without changing its behavior — especially recently modified code being reviewed for clarity and consistency before it lands.
---

# Code simplifier

**Simplification** changes how code reads, never what it does: the same inputs
produce the same outputs, side effects, and errors after every edit. Readable
and explicit beats compact.

## Steps

1. **Scope the target.** Default to the recently modified code (the working
   diff, or the range the user names); widen only when asked. Done when the
   files and line ranges are listed.
2. **Read the project's conventions** in `AGENTS.md` / `CLAUDE.md` and the
   neighbouring code: imports, naming, types, error handling, framework
   patterns. Done when each convention that touches the target is noted.
3. **Simplify, one concern per edit,** applying every rule below to every
   listed range. Done when each rule has been checked against each range.
4. **Prove behavior held.** Run the tests that cover the target; when none
   exist, trace each changed path by hand and say so. Done when the proof is
   in the report.
5. **Report** the edits that changed structure (a function extracted, a
   branch flattened) with the proof from step 4; renames and formatting go
   unlisted.

## Rules

- **Flatten**: early returns over nested conditionals; `if`/`else` or
  `switch` over nested ternaries.
- **Name the steps**: a long chain becomes named intermediates.
- **Inline the trivial**: a one-line wrapper around a built-in check becomes
  the check.
- **Consolidate**: related logic sits together under one name; a comment that
  restates the code goes.
- **Proportion**: one concern per function. An edit that merges concerns, or
  trades readability for fewer lines, is not a simplification.

## Patterns

### Nested ternaries → explicit branches

```typescript
// before
const status = isLoading ? 'loading' : hasError ? 'error' : isComplete ? 'complete' : 'idle';

// after
function getStatus(isLoading: boolean, hasError: boolean, isComplete: boolean): string {
  if (isLoading) return 'loading';
  if (hasError) return 'error';
  if (isComplete) return 'complete';
  return 'idle';
}
```

### Compact chains → named steps

```typescript
// before
const result = arr.filter(x => x > 0).map(x => x * 2).reduce((a, b) => a + b, 0);

// after
const positiveNumbers = arr.filter(x => x > 0);
const doubled = positiveNumbers.map(x => x * 2);
const sum = doubled.reduce((a, b) => a + b, 0);
```

### Trivial wrappers → direct checks

```typescript
// before
function isNotEmpty(arr: unknown[]): boolean { return arr.length > 0; }
if (isNotEmpty(items)) { ... }

// after
if (items.length > 0) { ... }
```
