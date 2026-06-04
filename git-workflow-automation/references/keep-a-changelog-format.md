# Keep a Changelog Format Reference

## Guiding Principles

- Changelogs are for humans, not machines
- There should be an entry for every single version
- The same types of changes should be grouped
- Versions and sections should be linkable
- The latest version comes first
- The release date of each version is displayed

## Standard Sections

```markdown
## [VERSION] — YYYY-MM-DD

### Added
for new features

### Changed
for changes in existing functionality

### Deprecated
for soon-to-be removed features

### Removed
for now removed features

### Fixed
for any bug fixes

### Security
in case of vulnerabilities
```

## How to Keep a Good Changelog

1. **Write for humans.** Don't just paste git log. Translate technical commit messages into user-facing language.
2. **One entry per version.** Don't stack multiple releases under one heading.
3. **Link to diffs.** `[1.2.0]: https://github.com/user/repo/compare/v1.1.0...v1.2.0`
4. **Don't list refactors, style changes, or internal-only changes.** Users don't care about renamed variables.
5. **Don't use "various bug fixes and improvements".** Be specific.
6. **Sort by importance.** Most impactful changes first in each section.
7. **Date format: YYYY-MM-DD.** ISO 8601, always.

## Example

```markdown
## [1.2.0] — 2024-06-15

### Added
- Dark mode support with system preference detection
- CSV export for all report types
- Bulk user import via admin panel

### Changed
- Dashboard loads 3x faster with server-side pagination
- Email notifications now use brand templates

### Fixed
- Login redirect loop when session expires mid-form
- Date picker showing wrong timezone for UTC+X users

### Security
- Rate limiting on login endpoint (5 attempts per minute)
- XSS sanitization on user-generated content
```

## Version Links (at bottom of file)

```markdown
[1.2.0]: https://github.com/user/repo/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/user/repo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```