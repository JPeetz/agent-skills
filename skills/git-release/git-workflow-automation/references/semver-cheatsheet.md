# Semantic Versioning Cheatsheet

## SemVer 2.0.0

Given a version number MAJOR.MINOR.PATCH:

- **MAJOR** version when you make incompatible API changes
- **MINOR** version when you add functionality in a backward compatible manner
- **PATCH** version when you make backward compatible bug fixes

Additional labels for pre-release and build metadata are available as extensions to the MAJOR.MINOR.PATCH format.

## Mapping Conventional Commits to SemVer

| Commit Type | Bump | Example |
|-------------|------|---------|
| `feat` | MINOR | 1.2.3 → 1.3.0 |
| `fix` | PATCH | 1.2.3 → 1.2.4 |
| `perf` | PATCH | 1.2.3 → 1.2.4 |
| `BREAKING CHANGE` / `!` | MAJOR | 1.2.3 → 2.0.0 |
| `docs`, `style`, `refactor`, `test`, `ci`, `chore` | NONE | No bump |
| `build` | PATCH* | *only if dependency change is user-facing |

## Pre-release Versions

```
1.0.0-alpha
1.0.0-alpha.1
1.0.0-beta.2
1.0.0-rc.1
```

## Build Metadata

```
1.0.0+20130313144700
1.0.0-beta+exp.sha.5114f85
```

## Precedence Rules (highest to lowest)

1. MAJOR.MINOR.PATCH (no pre-release)
2. MAJOR.MINOR.PATCH-rc.N
3. MAJOR.MINOR.PATCH-beta.N
4. MAJOR.MINOR.PATCH-alpha.N
5. Numeric identifiers compared numerically
6. Alphanumeric identifiers compared lexically

## Zero Version (0.y.z)

Initial development: anything may change at any time.
The public API should not be considered stable.
0.1.0 → 0.2.0 can include breaking changes without MAJOR bump.