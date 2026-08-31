# Conventional Commits Specification Reference

## Summary

The Conventional Commits specification is a lightweight convention on top of commit messages.
It provides an easy set of rules for creating an explicit commit history;
which makes it easier to write automated tools on top of.

## Specification

Commits MUST be prefixed with a type noun (feat, fix, etc.)
An optional scope MAY be added after type, enclosed in parentheses.
A colon and space MUST follow type (and optional scope).
A description MUST immediately follow the colon and space.

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Why Use Conventional Commits

- Automatically generating CHANGELOGs
- Automatically determining a semantic version bump
- Communicating the nature of changes to teammates, the public, and other stakeholders
- Triggering build and publish processes
- Making it easier for people to contribute to your projects

## FAQ

### How do I indicate a breaking change?
Add `!` before the colon, OR add `BREAKING CHANGE:` footer.
- `feat!: remove deprecated API`
- `feat(api)!: change user response format`
- Footer: `BREAKING CHANGE: The user response no longer includes the 'meta' field`

### What types are standard?
feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert

### Are types case-sensitive?
Yes. Always lowercase. `Feat` and `FEAT` are not valid.

### What about merge commits?
Merge commits (both GitHub PR merges and `git merge`) do not need to follow this format.
However, the commits being merged SHOULD be conventional.