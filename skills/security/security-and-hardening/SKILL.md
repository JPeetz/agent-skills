---
name: security-and-hardening
description: Use this skill when auditing code for vulnerabilities, handling user input, authentication, data storage, or external integrations. Hardens code against OWASP Top 10 with a three-tier boundary system, dependency auditing, data privacy, and LLM safety.
---

# Security and Hardening

## Overview

Security-first development practices for web applications. Treat every external input as hostile, every secret as sacred, and every authorization check as mandatory. Security isn't a phase — it's a constraint on every line of code that touches user data, authentication, or external systems.

## When to Use

- Building anything that accepts user input
- Implementing authentication or authorization
- Storing or transmitting sensitive data
- Integrating with external APIs or services
- Adding file uploads, webhooks, or callbacks
- Handling payment or PII data
- Building LLM/AI features (chatbots, summarizers, agents, RAG)

## Process: Threat Model First

Controls bolted on without a threat model are guesses. Before hardening, spend five minutes thinking like an attacker:

1. **Map the trust boundaries.** Where does untrusted data cross into your system? HTTP requests, form fields, file uploads, webhooks, third-party APIs, message queues, and LLM output.
2. **Name the assets.** What's worth stealing or breaking? Credentials, PII, payment data, admin actions.
3. **Run STRIDE over each boundary** — a quick lens, not a ceremony:

| Threat | Ask | Typical Mitigation |
|---|---|---|
| **S**poofing | Can someone impersonate a user/service? | Authentication, signature verification |
| **T**ampering | Can data be altered in transit or at rest? | Integrity checks, parameterized queries, HTTPS |
| **R**epudiation | Can an action be denied later? | Audit logging of security events |
| **I**nformation disclosure | Can data leak? | Encryption, field allowlists, generic errors |
| **D**enial of service | Can it be overwhelmed? | Rate limiting, input size caps, timeouts |
| **E**levation of privilege | Can a user gain rights they shouldn't? | Authorization checks, least privilege |

4. **Write abuse cases next to use cases.** For each feature, ask "how would I misuse this?" — then make that your first test.

## The Three-Tier Boundary System

### Always Do (No Exceptions)

- **Validate all external input** at the system boundary (API routes, form handlers)
- **Parameterize all database queries** — never concatenate user input into SQL
- **Encode output** to prevent XSS (use framework auto-escaping, don't bypass it)
- **Use HTTPS** for all external communication
- **Hash passwords** with bcrypt/scrypt/argon2 (never store plaintext)
- **Set security headers** (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
- **Use httpOnly, secure, sameSite cookies** for sessions
- **Run the package manager's native audit** against the committed lockfile before every release

### Ask First (Requires Human Approval)

- Adding new authentication flows or changing auth logic
- Storing new categories of sensitive data (PII, payment info)
- Adding new external service integrations
- Changing CORS configuration
- Adding file upload handlers
- Modifying rate limiting or throttling
- Granting elevated permissions or roles

### Never Do

- **Never commit secrets** to version control (API keys, passwords, tokens)
- **Never log sensitive data** (passwords, tokens, full credit card numbers)
- **Never trust client-side validation** as a security boundary
- **Never disable security headers** for convenience
- **Never use `eval()` or `innerHTML`** with user-provided data
- **Never store sessions in client-accessible storage** (localStorage for auth tokens)
- **Never expose stack traces** or internal error details to users

## Hardening Controls

### Injection, XSS, and Access Control

- Parameterize every query. Never build SQL, NoSQL, or shell commands from input strings.
- Encode output through the framework's auto-escaping. If raw HTML is unavoidable, sanitize with an allowlist sanitizer first.
- Check **authorization** on every request, not just authentication: the authenticated user must own, or be permitted on, the specific resource (IDOR).

### Authentication and Sessions

- Hash passwords with bcrypt (≥12 rounds), scrypt, or argon2.
- Session cookies are `httpOnly`, `secure`, and `sameSite: 'lax'` or `'strict'`.
- Session secrets come from the environment, never from code.

### Headers, CORS, and Responses

- Security headers on every response (helmet or the framework equivalent).
- CORS restricted to an explicit origin list from configuration. Never `*` with credentials.
- Strip sensitive fields before any response. Error bodies are generic; internals go to server logs only.

### Input Validation and Uploads

- Validate at the boundary with a schema: allowlisted shape, lengths, enums, formats.
- Uploads: allowlist MIME types, cap size, verify content (magic bytes) when it matters.

### Server-Side Fetches (SSRF)

Any URL the user influences — webhooks, import-from-URL, image proxies, link previews — can be aimed at internal services. Allowlist scheme and host, resolve all DNS records and reject any private or reserved address, and forbid redirects.

### Rate Limiting

Limit the API generally and auth endpoints strictly (~10 attempts per 15 minutes). Once more than one process serves traffic, back the limiter with a shared store.

### Secrets Management

Secrets come from the environment. `.env.example` is committed with placeholders; real `.env*` files are gitignored. A secret that reaches a remote is compromised the moment it lands: rotate it first, then purge history.

### Dependencies and Supply Chain

1. Find the installation boundary and manager. Corroborate the lockfile and CI; stop on disagreement.
2. Block dependency scripts before first execution. Bootstrap with scripts disabled.
3. Run the native audit before every release. Triage critical/high by reachability and fix availability.
4. Audits match known advisories only. They do not catch malicious or typosquatted packages.

### Personal Data and Privacy

- **Classify fields** as you add them (non-personal, PII, sensitive).
- **Collect only against a stated purpose.** "Might be useful later" is latent breach scope.
- **Set retention up front**, then actually delete — including backups, caches, and analytics copies.
- **Support data-subject rights** (GDPR, CCPA): export, correct, delete.
- **Consent gates collection and third-party sharing.**

### AI / LLM Features

- **Model output is untrusted input** — never into `eval`, SQL, a shell, `innerHTML`, or a file path.
- **Prompts can be hijacked** — untrusted text in the context carries instructions. The system prompt is not a security boundary.
- **Keep secrets and other tenants' data** out of the context window.
- **Scope tool permissions** and validate every tool argument.

## Review Checklist

Before sign-off:
- [ ] No secrets in source code or git history
- [ ] All user input validated at system boundaries
- [ ] Parameterized queries throughout
- [ ] Authentication and authorization checked on every protected endpoint
- [ ] Security headers present in response
- [ ] Error responses don't expose internal details
- [ ] Rate limiting active on auth endpoints
- [ ] No SSRF vectors through user-supplied URLs
- [ ] LLM output is validated and encoded before use (if AI features present)
- [ ] Personal data is classified, minimized, and has a retention limit
- [ ] Deletion and export requests work end-to-end
- [ ] Native dependency audit has no unmitigated critical/high findings

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "This is an internal tool, security doesn't matter" | Internal tools get compromised. Attackers target the weakest link. |
| "We'll add security later" | Security retrofitting is 10x harder than building it in. |
| "The framework handles security" | Frameworks provide tools, not guarantees. You still need to use them correctly. |
| "It's just a prototype" | Prototypes become production. Security habits from day one. |
| "Threat modeling is overkill here" | Five minutes of "how would I attack this?" prevents design flaws no control can patch later. |
| "It's just LLM output, it's only text" | That "text" can be a SQL statement, a script tag, or a shell command. |
| "The audit passed, so the dependency is safe" | Audits match known advisories. They don't detect newly malicious packages. |
| "Collect it now, we might need it later" | Data you don't hold can't be breached. "Might need it" is breach scope, not a purpose. |

## Red Flags

- User input passed directly to database queries, shell commands, or HTML rendering
- Secrets in source code or commit history
- API endpoints without authentication or authorization checks
- Missing CORS configuration or wildcard origins
- No rate limiting on authentication endpoints
- Stack traces or internal errors exposed to users
- Dependencies with known critical vulnerabilities
- Server fetches user-supplied URLs without an allowlist (SSRF)
- LLM output passed into query, DOM, shell, or eval
- Personal data collected with no stated purpose, retention limit, or deletion path