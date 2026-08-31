# Changelog — Playwright E2E Testing Agent Skill

All notable changes to this skill package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-06-16

### Added
- Initial release of Playwright E2E Testing skill
- Complete test architecture and structure guidance with Page Object Model patterns
- Locator strategy priority hierarchy (getByRole → getByLabel → getByText → getByTestId)
- Anti-pattern catalog with concrete avoidance examples
- Authentication and session management with multi-profile auth setup
- Visual regression testing with element-level and full-page screenshot comparison
- Component testing support for React, Vue, Svelte via Playwright CT
- Mobile and device emulation testing with touch/gesture support
- Debugging checklist and flaky test detection methodology
- Auto-healing test patterns for resilient test suites
- CI/CD configuration for GitHub Actions, GitLab CI, CircleCI
- Accessibility testing via axe-core integration
- Performance testing with Lighthouse and Web Vitals
- Internationalization (i18n) and localization testing
- Security testing (XSS, CSRF, CSP, auth redirects)
- WebSocket and real-time application testing
- Electron and browser extension testing
- 8 eval cases covering critical, high, and medium priority paths
- 3 near-miss negative guards (Selenium, Cypress, unit tests)
- 3 reference documents: locator strategies, testing types matrix, CI/CD patterns
- 3 utility scripts: validate-playwright-setup.sh, generate-auth-profile.ts, flake-detector.sh
- Full SEO/GEO metadata with primary keywords and semantic clusters
- Cross-platform compatibility: Claude Code, Codex, Cursor, Gemini CLI, OpenClaw, Copilot, Windsurf, OpenCode, Kiro, Antigravity, Auggie

### Source
- Adapted and materially improved from currents-dev/playwright-best-practices-skill
- Added 7 additional testing domains (performance, i18n, security, WebSocket, Electron, extensions, debugging)
- Created complete eval suite with near-miss negatives
- Added executable scripts for setup validation, auth profiles, and flake detection
- Added comprehensive reference documentation