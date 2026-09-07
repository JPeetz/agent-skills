# Gate 4: Security Review — Vulnerabilities & LLM-App Risks

## Overview

This gate catches the systematic ways LLMs introduce security defects — distinct from general quality failures. Security review is not optional polish: a single injection or missing authorization check is worth more attacker leverage than every style nit in the file combined. Treat any code path that touches untrusted input, authentication, authorization, secrets, cryptography, file or network I/O, or third-party packages as in-scope and guilty until proven safe.

## The 27 Imperatives

### Untrusted Input and Injection
1. **All untrusted input is hostile until validated.** Validate against an allow-list (shape, type, range, enum) — never a deny-list. (CWE-20)
2. **Never build a query, command, or path by string concatenation with input.** Use parameterized queries, argument arrays, safe path-join with canonicalization. (CWE-89, CWE-78, CWE-22)
3. **Output is encoded for its sink.** HTML-encode for HTML, use framework auto-escaping. Never `dangerouslySetInnerHTML`, `|safe`, `v-html` on untrusted data. (CWE-79)
4. **No deserialization of untrusted data into live objects.** No `pickle`, `yaml.load` (use `safe_load`), Java/PHP native deserialization, or `eval`/`exec` on input. (CWE-502, CWE-94)
5. **Guard every outbound request built from input (SSRF).** A URL/host/webhook from input must be validated against an allow-list; must not reach internal addresses, `169.254.169.254`, or `localhost`. Pin resolved IP for DNS rebinding protection. (CWE-918, CWE-601)
6. **Bind request data to explicit fields.** Never spread a whole request body into a model. Allow-list writable fields per endpoint; privileged fields change only through code paths that authorize the change. (CWE-915)

### Authentication and Authorization
7. **Every protected action checks authorization server-side.** Never rely on hidden UI, client-side role flags, or "the caller wouldn't send that ID." Verify the current principal owns or may act on the specific resource. (CWE-862, CWE-639)
8. **Authentication is never rolled by hand when a vetted mechanism exists.** Passwords are hashed with argon2id/bcrypt/scrypt/PBKDF2. Tokens are verified with the library's verify (correct algorithm pinned, signature and expiry checked). (CWE-287, CWE-916)
9. **State-changing endpoints are CSRF-protected** when authenticated by cookies: framework CSRF middleware plus `SameSite` cookies. (CWE-352)
10. **Fail closed.** On any auth, validation, or crypto error, deny — do not fall through to allow. (OWASP A10:2025)

### Secrets and Cryptography
11. **No secrets in source.** No API keys, passwords, tokens, private keys, or connection strings as literals — in code, tests, samples, comments, or fixtures. Read from environment or a secrets manager. (CWE-798)
12. **Use standard crypto, correctly — never invent it.** Use AEAD (AES-GCM, ChaCha20-Poly1305) via the platform library. No ECB, no static IV, no reused nonce. (CWE-327)
13. **Randomness for security is cryptographic.** Tokens, session IDs, reset codes, salts use a CSPRNG (`secrets`, `crypto.randomBytes`, `SecureRandom`). Never `Math.random`, `rand()`, seeded PRNG. (CWE-338)
14. **Secrets are compared in constant time.** Tokens, MACs, signatures, OTPs use `compare_digest`/`timingSafeEqual`/`hash_equals`. Never `==`. (CWE-208)
15. **Transport and storage are encrypted by default.** HTTPS/TLS for everything over a network; no `verify=False`/disabled cert checks. Sensitive data encrypted at rest. (OWASP A04:2025)

### Exposure, Misconfiguration, and Limits
16. **Errors and logs leak nothing.** No stack traces, SQL, internal paths, or secrets in responses. No secrets, tokens, or raw passwords in logs. (CWE-209)
17. **No insecure defaults.** No `debug=True` in production, no wildcard CORS with credentials, no default/blank admin credentials. (OWASP A02:2025)
18. **Everything an outsider can trigger is bounded.** Request body and upload size caps, archive-extraction limits, pagination caps, timeouts, rate limits. Security decisions are atomic, not check-then-act. (CWE-770, CWE-362)

### Supply Chain
19. **Every new dependency is verified to exist and to be the right one before you import it.** Confirm exact spelling, real publisher, plausible age and downloads. AI-suggested names are a top slopsquatting vector. (USENIX Security '25)
20. **Pin and lock.** New dependencies are added through the lockfile, not hand-edited. Do not add a dependency with a known unpatched CVE. (OWASP A03:2025)
21. **No unvetted install/build scripts or remote `curl | sh`.** Treat postinstall scripts as third-party code execution. (OWASP A08)

### LLM Applications
22. **Model output is untrusted input.** Anything the model returns gets the same treatment as a request parameter before reaching SQL, shell, HTML, `eval`, a path, or a URL. (OWASP LLM05)
23. **The model's decision is not authorization.** Tools run with least privilege; authorization is checked inside the tool against the end user; irreversible actions need human confirmation. Agent loops, tokens, and per-user rates are capped. (LLM06, LLM10)
24. **Prompts hold no secrets and trust no content.** No keys, credentials, or sensitive PII in any prompt. Untrusted content enters prompts delimited as data, never as instructions. (LLM07, LLM01)

### AI-Specific Security Guardrails
25. **Plausible is not secure.** The model emits the pattern that looks like working code, which is frequently the insecure one (string-built SQL, `Math.random` token, disabled TLS). Re-derive the secure pattern from the rule. (Perry et al., CCS 2023)
26. **Never weaken security to make something pass.** Do not disable cert verification, loosen CORS, widen a permission, comment out an auth check, or add a secret to a fixture so a call passes. (Pearce et al., IEEE S&P 2022)
27. **Verify the import before you trust it — for existence and for safety.** Same as Rule 19 plus hallucinated-import detection. Check the lockfile and the registry, not your memory. (USENIX Security '25)

## Self-Check (Gate 4)
1. Walk imperatives 1–27 against your diff. Fix or flag every violation.
2. For every place untrusted input meets a query, command, path, HTML sink, deserializer, or outbound URL: is it parameterized/encoded/allow-listed?
3. For every protected action: authorization checked server-side? CSRF-protected? Request bodies bound to explicit fields?
4. Any secret, key, token, or password as a literal — including in tests, samples, comments, and prompts?
5. Any hand-rolled crypto, weak hash, disabled TLS, or `Math.random` for a security value?
6. Any new dependency you did not verify against the registry and add through the lockfile?
7. If LLM code: does model output reach a sink unencoded? Does any tool exceed the end user's permissions?
8. Did you disable, loosen, or comment out any security control? If yes, revert and solve properly.