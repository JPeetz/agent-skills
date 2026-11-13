---
name: open-source-license-compliance
description: "Use when vetting OSS licenses, compatibility, NOTICE, CI."
version: "1.0.0"
author: "@artisan"
license: "MIT"
category: compliance-legal
metadata:
  hermes:
    tags:
      - licensing
      - spdx
      - open-source
      - copyleft
      - sbom
      - attribution
      - supply-chain
      - compliance
    related_skills:
      - gdpr-dsgvo-expert
      - data-privacy-compliance
      - dependency-audit
      - third-party-project-assessment
platforms:
  - claude-code
  - openclaw
  - cursor
  - codex
  - opencode
  - gemini-cli
permissions:
  files:
    read: "audit-only: read dependency manifests, LICENSE files, and source headers to inventory licenses. No network egress, no package installation, no license-file rewriting without explicit user approval."
  caveat: >
    This skill produces engineering guidance, not legal advice. License compatibility
    findings are a technical first pass; distribution decisions, indemnities, and
    relicensing questions belong to counsel. Never state that a combination is
    "legally safe" — state what the licenses require and where the risk sits.
---

# Open Source License Compliance

> Every dependency you ship is someone else's contract. Read the terms before you distribute.

## Overview

License compliance fails in three predictable ways: nobody knows what is actually in the dependency tree, somebody assumes "it's on GitHub so it's free," and the obligation (attribution, source disclosure, notice propagation) is discovered after the release ships.

This skill covers the mechanical part — inventory, compatibility analysis, attribution output, CI enforcement — and is explicit about where the mechanical part ends. Determining whether your use is distribution, whether a plugin boundary is a derivative work, or whether a patent grant survives an acquisition is a legal question. Answer it with counsel, not with a scanner.

**Three rules that prevent most incidents:**

1. **No license is not "no restrictions."** Absent a license, default copyright applies — all rights reserved. You have no right to copy, modify, or redistribute.
2. **The obligation travels with the artifact.** You ship a container image or a compiled binary; the attribution requirement attaches to what you distribute, not to what you typed.
3. **A scanner reports, a human decides.** Tools give you identifiers and confidence scores. They do not know your distribution model, your linking, or your contracts.

## When to Use

- Before a first public release, a container image publish, or an on-prem delivery
- When adding a dependency whose license you have not read
- When integrating third-party code into a product you distribute (SaaS still counts for AGPL)
- When generating or refreshing a `NOTICE` / third-party notices file
- When a CI job must block new copyleft or unknown licenses
- When vendoring agent- or AI-generated code that came from an unverified source
- During due diligence: acquisition, OEM agreement, or a customer security questionnaire

**Do not use for:** interpreting a contract you signed with a vendor, patent litigation risk, or trademark questions. Different body of law, different specialist.

## License Classes

### Permissive

Grants broad rights; obligations are limited to preserving notices.

| SPDX ID | Obligations |
|---|---|
| `MIT` | Include copyright + permission notice in all copies or substantial portions |
| `BSD-2-Clause` | Same as MIT (copyright + conditions) |
| `BSD-3-Clause` | Adds: no endorsement using contributor names without permission |
| `Apache-2.0` | Keep `NOTICE` if present; state changes made; include a copy of the license; patent grant with termination on suit |
| `ISC` | Functionally MIT, shorter text |
| `0BSD` | No attribution required; closest thing to public domain with a warranty disclaimer |
| `Unlicense`, `CC0-1.0` | Public-domain dedication; some jurisdictions do not permit full dedication, so a fallback license clause matters |

Apache-2.0 is *not* interchangeable with MIT. The patent grant and the `NOTICE` propagation duty are real, additional obligations — and the patent grant is what makes Apache-2.0 incompatible with GPL-2.0-only.

### Weak Copyleft

Copyleft scope is bounded — by library boundary (LGPL), by file (MPL), by module (EPL, CDDL).

| SPDX ID | Scope | Practical consequence |
|---|---|---|
| `LGPL-2.1-only`, `LGPL-3.0-only` | The library itself | You may link proprietary code dynamically; you must allow relinking (ship the LGPL library's source and permit replacement). Static linking pulls the whole work into LGPL scope. |
| `MPL-2.0` | Files originating from the MPL project | Your new files stay yours; modified MPL files must be published. Ship the source of those files. |
| `EPL-2.0` | Module/plugin boundary | Similar to MPL in spirit, different in drafting; check the "commercial distribution" definition |
| `CDDL-1.0` | File-level | Incompatible with GPL — do not mix in one work |

Weak copyleft is where teams get surprised: a *modified* MPL file in a private fork still owes its source when you distribute the binary. An *unmodified* one owes attribution and the license text.

### Strong Copyleft

The whole derivative work must be licensed under the same terms when distributed.

| SPDX ID | Trigger | Notes |
|---|---|---|
| `GPL-2.0-only` | Distribution of a derivative work | Source of the whole work; no additional restrictions |
| `GPL-3.0-only` | Distribution | Adds anti-tivoization, patent grant, installation information |
| `AGPL-3.0-only` | **Network use** (≥ §13) | Offering the software as a service counts as distribution. SaaS is in scope. |
| `EUPL-1.2` | Distribution | Strong copyleft with an explicit compatibility list (can combine into GPL-2.0+, AGPL, MPL, LGPL, OSL) |

GPL-2.0-only and GPL-3.0-only are mutually incompatible as a *combination* in one work. Code under one cannot be merged with code under the other unless the "or later" option is available and exercised.

### Proprietary / Source-Available

Not open source, whatever the repository visibility.

- `LicenseRef-*` — for anything non-standard; SPDX requires the prefix
- Business Source License (`BUSL-1.1`), Elastic License 2.0, SSPL, Commons Clause, PolyForm
- "All rights reserved," missing license file, or a README saying "free to use" with no grant

Source-available means you can read it. It does not mean you can ship it, and several of these licenses restrict offering the software as a service — precisely the thing a SaaS product does.

### SPDX Identifiers

Always use SPDX identifiers, in SPDX expression syntax, in machine-readable fields:

```
MIT
Apache-2.0
GPL-2.0-only          # not "GPL-2.0" (deprecated, ambiguous)
GPL-2.0-or-later
MIT OR Apache-2.0     # dual license — pick one at distribution time
MIT AND BSD-3-Clause  # both obligations apply
GPL-2.0-only WITH Classpath-exception-2.0
LicenseRef-Acme-Proprietary-1.0
```

Rules: `OR` means you choose; `AND` means you satisfy both; `WITH` attaches an exception that can materially change the obligation (Classpath and GCC runtime exceptions remove the copyleft reach over linking). Deprecated bare identifiers (`GPL-2.0`, `GPL-3.0`, `LGPL-2.1`) are ambiguous about the "or later" option — resolve them against the actual license text, not the identifier.

## Compatibility Matrix

Read this as "may I combine these into one work and distribute?"

| Inbound license | Into MIT/BSD | Into Apache-2.0 | Into GPL-2.0-only | Into GPL-3.0 | Into AGPL-3.0 | Into MPL-2.0 file |
|---|---|---|---|---|---|---|
| MIT | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| BSD-2/3-Clause | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Apache-2.0 | ✅ | ✅ | ❌ **patent clause** | ✅ | ✅ | ✅ |
| MPL-2.0 | ✅ (file stays MPL) | ✅ | ✅ via §3.3 (→ GPL-2.0-or-later) | ✅ | ✅ | ✅ |
| LGPL-2.1/3.0 | ⚠️ dynamic only | ⚠️ dynamic only | ⚠️ 2.1 upgradeable, 3.0 no | ✅ via upgrade right | ✅ | ❌ |
| GPL-2.0-only | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| GPL-3.0-only | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| AGPL-3.0-only | ❌ | ❌ | ❌ | ⚠️ (AGPL wins) | ✅ | ❌ |
| Proprietary | ⚠️ case-by-case | ⚠️ | ❌ | ❌ | ❌ | ❌ |

The three cells that cause the most real-world work:

**Apache-2.0 into GPL-2.0-only — incompatible.** GPLv2 §6 forbids imposing further restrictions on recipients. Apache-2.0's patent-termination clause and its indemnity/warranty language are treated as exactly that. The combination is not distributable. Fix: use the GPL-3.0 build of the dependency, drop it, or isolate it behind a process boundary — and get counsel to bless the boundary argument.

**MPL-2.0 into GPL family — allowed.** MPL-2.0 §3.3 offers a secondary-license option and GPL-2.0-or-later, LGPL-2.1-or-later, LGPL-3.0-or-later, GPL-3.0-or-later, and AGPL-3.0-or-later are on the list. This disappears if the file carries the "Incompatible With Secondary Licenses" notice — check the header, not the SPDX ID.

**AGPL-3.0 in a SaaS.** You do not "distribute" a binary, but §13 requires offering the Corresponding Source to anyone interacting with it over a network. A modified AGPL component behind your API endpoint obligates you to publish that component's source to your users. Running it unmodified still requires making the source available to them; the obligation is narrower but not zero.

### Linking Boundaries

The derivative-work question is legal, but the technical facts drive it:

- **Dynamic linking / separate process** — weaker copyleft reach; the LGPL is explicitly designed for this, the GPL is not.
- **Static linking / same address space** — strongest copyleft reach.
- **Subprocess + IPC (sidecar, CLI, RPC)** — usually treated as separate works; document the boundary (process, socket, serialization format) because you may need to defend it.
- **Header-only or template inclusion** — generally inside the same work.
- **Plugins loaded at runtime by a GPL host** — a plugin using the host's internal APIs is commonly treated as a derivative; a plugin speaking a documented external protocol usually is not.

Record the boundary in writing at the time you make the call. Reconstructing it two years later in a diligence conversation is how deals die.

## Transitive Scan Recipe

You cannot inventory licenses from `package.json` alone. Scan the resolved tree and the vendored code.

### 1. Manifest-level fast pass

```bash
# Node — resolved tree, not declared ranges
npx license-checker-rseidelsohn --production --json > licenses-npm.json

# Python — installed environment, including transitive deps
pip-licenses --format=json --with-license-file --with-urls > licenses-pip.json

# Go
go-licenses report ./... > licenses-go.csv

# Rust
cargo deny list > licenses-cargo.txt

# Java/Maven
mvn license:aggregate-add-third-party
```

These read metadata. Metadata lies — packages misdeclare, dual-license, or ship vendored copies of other code. Verify with a file-level scan.

### 2. File-level scan — ScanCode Toolkit

```bash
pipx install scancode-toolkit
scancode --license --copyright --package \
  --json-pp scancode.json \
  --license-score 90 \
  ./vendor ./node_modules
```

ScanCode matches license text against a corpus and reports `score` and `matched_rule`. Use `--license-score 90` to filter noise, and always inspect anything below 100 by hand. It also extracts copyright statements, which is what you need for attribution output.

### 3. Identification — licensee

```bash
gem install licensee
licensee detect .                    # what is this project's license?
licensee diff LICENSE other/LICENSE  # how does it differ from the canonical text?
```

Licensee is the engine GitHub uses for its license badge. It reports a confidence score and the closest match, which is exactly what you want for a repo that *modified* the GPL text (a common and legally meaningful event — a modified license is not that license).

### 4. Orchestration — ORT (OSS Review Toolkit)

For a real product with many ecosystems:

```bash
ort analyze -i . -o out
ort scan -i out/analyzer-result.yml -o out
ort report -i out/scan-result.yml -o out/reports -f NoticeTemplate,SpdxDocument,CycloneDX
```

ORT handles analyzer (dependency resolution per package manager), scanner (ScanCode under the hood), curations (`.ort.yml` for correcting bad metadata), policy rules (`rules.kts`), and reporters including a NOTICE template and SPDX/CycloneDX SBOMs. Use curations for any package whose manifest license is wrong — with a comment explaining why, so the correction is auditable.

### 5. Reconcile

Diff manifest metadata against the file scan. Every disagreement is a finding:

| Disagreement | Meaning |
|---|---|
| Manifest says MIT, files say GPL-3.0 | Vendored GPL code inside an MIT package — the real risk |
| Manifest says MIT, ScanCode finds no license | License file missing; treat as unresolved |
| Manifest full of `UNKNOWN` | No metadata; inspect the package manually |
| Multiple licenses, no expression | Dual-licensed but undeclared — read the README and license files |

## Unknown and Missing Licenses

The default is **all rights reserved**. This is not a conservative reading; it is the actual legal position under the Berne Convention. A public repository with no `LICENSE` file grants you nothing beyond viewing it.

Handling procedure:

1. **Search exhaustively before concluding.** `LICENSE`, `LICENSE.md`, `LICENSE.txt`, `COPYING`, `COPYRIGHT`, `NOTICE`, `UNLICENSE`, `.license` sidecars, README "License" sections, `package.json` `license` field, source-file headers, the project website, the package registry page.
2. **Classify as `NOASSERTION`** (SPDX's term for "I found something but cannot identify it") rather than guessing. `UNKNOWN` means nothing found; `NOASSERTION` means found but unidentifiable. Both block distribution by default.
3. **Escalate to the maintainer in writing** if the dependency matters. An issue asking "what license is this under?" answered in public is a usable record; a Slack guess is not. Archive the response.
4. **If unlicensed code is already vendored, remove it** or obtain a written grant. Do not proceed on the theory that nobody will notice; the obligation is what matters, not the enforcement probability.
5. **Never infer a license from language, registry, or popularity.** "Everyone uses it" is not a grant. A permissive license on a *different* package by the same author does not transfer.
6. **Public-domain claims need evidence.** `CC0-1.0` and `Unlicense` are dedications, not licenses; check the jurisdiction permits the dedication, and note that some corporate policies forbid relying on them regardless.

For a dependency you cannot resolve and cannot replace, document the decision as an accepted risk with an owner and a review date. An undocumented unknown is the finding; a documented one is a business decision.

## Attribution Output

What you owe depends on what you ship and where.

### NOTICE file (Apache-2.0 §4(d))

Apache-2.0 requires that a `NOTICE` file, if the distribution contains one, be included in a readable form and that its attribution notices not be modified. Aggregate, don't overwrite:

```
MyProduct 4.2.0
Copyright 2026 Acme GmbH

This product includes software developed at:
  The Apache Software Foundation (https://www.apache.org/)

--------------------------------------------------------------------------------
fast-json 2.1.0
Copyright 2023 Example Authors
Licensed under the Apache License, Version 2.0
--------------------------------------------------------------------------------
```

### Third-party notices (everything else)

For non-Apache permissive licenses, the obligation is to reproduce the copyright notice and permission text. One file, generated, sorted, and never hand-edited:

```
THIRD-PARTY NOTICES

foo-lib 1.4.2 — MIT
Copyright (c) 2021 Jane Doe

Permission is hereby granted, free of charge, ... [full text]

bar-util 0.9.0 — BSD-3-Clause
Copyright (c) 2020 Bar Contributors

Redistribution and use in source and binary forms, ... [full text]
```

Rules that make generated notices defensible:

- **Generate from the resolved dependency graph**, not from the direct-dependency list. Transitive dependencies are the majority of obligations.
- **Include the full license text**, not a link. A URL is not a copy of the notice, and it breaks when the project moves.
- **Regenerate in CI on every release** and fail the build if the committed file differs from a fresh generation. Stale notices are the most common audit finding.
- **Deduplicate by (package, version, license)** but keep every distinct copyright line — ScanCode finds multiple holders per package.
- **Ship it where the user can find it**: repo root, distribution tarball, container image `/usr/share/doc/<pkg>/copyright`, and an in-app "Licenses" screen for desktop and mobile.

### SBOM

Produce SPDX or CycloneDX alongside the notices. An SBOM is what lets a customer's scanner answer the question without emailing you, and it is increasingly a contractual requirement (`SPDX-2.3`, `CycloneDX 1.6`). ORT and ScanCode both emit them; `syft` is a fast one-shot if you only need the inventory.

## Redistribution Rules

> Engineering guidance, not legal advice. These are the mechanics of satisfying obligations; whether an obligation applies at all is a legal question.

1. **Distribution is the trigger.** Giving a copy to another legal entity — customer, container registry, app store, on-prem install — is distribution. Internal use inside one entity generally is not. AGPL changes this for network use.
2. **Source offer must be valid.** GPL requires either shipping the source alongside or a written offer valid for three years. "It's on our GitHub" works only if the exact corresponding source for that binary is there and stays there.
3. **Corresponding source is not just your files.** It includes build scripts, interface definition files, and the scripts used to control compilation and installation for GPL-3.0.
4. **Do not add restrictions.** You may not add terms that restrict recipients' GPL rights — this includes some EULAs, DRM/anti-tamper terms (GPLv3), and field-of-use limits.
5. **Keep changes marked.** Apache-2.0 §4(b) and MPL-2.0 §3.1 both require modified files to carry prominent notices of the change. A one-line header is enough.
6. **Version the obligation.** Notice obligations attach to the artifact you shipped. A customer on v2.1 is owed the notices for v2.1's dependency set, not v4.0's.
7. **Removing a dependency does not retroactively fix a shipped release.** Rotate the artifacts, or document the exposure.

## CI Policy Gate

Automate the mechanical decision; leave exceptions to humans with names attached.

### Policy shape

```yaml
# .license-policy.yml
allowed:
  - MIT
  - BSD-2-Clause
  - BSD-3-Clause
  - ISC
  - Apache-2.0
  - 0BSD
  - MPL-2.0
  - Unlicense

# Requires review, does not auto-fail
review:
  - LGPL-2.1-only
  - LGPL-3.0-only
  - EPL-2.0

denied:
  - GPL-2.0-only
  - GPL-3.0-only
  - AGPL-3.0-only
  - SSPL-1.0
  - BUSL-1.1
  - UNKNOWN
  - NOASSERTION

# Waivers expire. Always.
waivers:
  - package: legacy-pdf-lib@2.3.1
    license: GPL-3.0-only
    reason: "Isolated sidecar process; boundary reviewed 2026-09"
    owner: "@artisan"
    expires: 2027-03-31
```

### Enforcement

```bash
# Fail on anything not explicitly allowed, including the transitive tree
npx license-checker-rseidelsohn --production --onlyAllow \
  "MIT;ISC;BSD-2-Clause;BSD-3-Clause;Apache-2.0;0BSD;MPL-2.0" \
  --excludePackages "legacy-pdf-lib@2.3.1"
```

Gate rules that hold up:

- **Fail the build, don't warn.** A warning in a build log is not a gate.
- **Evaluate the lockfile, not the manifest.** Ranges resolve differently tomorrow.
- **Fail closed on `UNKNOWN`/`NOASSERTION`.** A dependency you cannot identify is a new risk, and new risks should require a human.
- **Diff against the base branch.** A repo with 40 pre-existing copyleft dependencies should not block every PR; fail when the *set* grows. Baseline the debt, then fail on new additions.
- **Waivers carry an owner and an expiry.** Unowned, never-expiring exceptions accumulate until the gate is theatre. An expired waiver is a build failure.
- **Run on a schedule, not only on PRs.** A transitive dependency can change license in a patch release — rare, real, and invisible to a PR-only gate.

## AI-Generated and Agent-Vendored Code

The provenance problem: an agent writes code, nobody records where the pattern came from, and eighteen months later the provenance question is unanswerable.

**Facts to work from:**

- Copyright in AI output is unsettled and jurisdiction-dependent. In several jurisdictions purely machine-generated material may not be copyrightable at all — which means you may not be able to grant a license over it, and a downstream user may not be able to rely on one.
- Model terms vary on whether output is assignable and whether it carries indemnity. Read them; they are contracts.
- An agent reproducing a recognizable block from a copyleft project is a licensing event regardless of how it arrived in your repo. "The model wrote it" is not a defense — the obligation attaches to the code.
- Vendored code pulled from a URL during an agent run has a license (or doesn't), and it is not your license.

**Provenance record** — one entry per non-trivial generated or vendored block:

```json
{
  "path": "src/parsers/csv.ts",
  "origin": "ai-generated",
  "model": "vendor/model-id",
  "generated_at": "2026-11-13T14:02:11Z",
  "prompt_hash": "sha256:9f2c...",
  "human_reviewed_by": "@artisan",
  "reviewed_at": "2026-11-13",
  "similarity_check": "scancode --license on the diff; no matches",
  "license": "MIT",
  "notes": "Algorithm rewritten from spec, no source consulted"
}
```

**Rules:**

1. **Record at creation, not at audit.** The record is cheap when the context is live and impossible to reconstruct later.
2. **Scan generated code for license text and recognizable headers.** Run the same ScanCode pass over new files; a copied `SPDX-License-Identifier` header or a verbatim function with an attribution comment is a signal.
3. **Keep prompts and inputs out of the repo; keep hashes.** Prompt text can contain customer data; the hash is what you need for reproducibility.
4. **A human reviews and owns every generated block.** Attribution of authorship to a model is not a control; review is.
5. **Never claim a license you cannot grant.** If the code is machine-generated and not copyrightable in your jurisdiction, your `LICENSE` covers the surrounding work; say so in the provenance record rather than asserting ownership.
6. **Vendored-from-a-URL code gets the upstream license, whatever the agent said.** Check the source, record the SPDX ID, comply with the obligations.

## Pitfalls

| Pitfall | Why it bites | Do this |
|---|---|---|
| "No LICENSE file means public domain" | Default copyright applies; you have no grant | Treat as all rights reserved; `NOASSERTION`, escalate |
| Reading only direct dependencies | Most obligations are transitive | Scan the resolved tree and vendored paths |
| Trusting `package.json` license fields | Packages misdeclare, vendored, or dual-license | Reconcile with a file-level ScanCode pass |
| Assuming SaaS avoids GPL | AGPL §13 covers network use | Check for AGPL in the server-side tree specifically |
| Treating Apache-2.0 as MIT-like | `NOTICE` propagation + patent termination | Include the NOTICE; review patent-clause interactions |
| Combining Apache-2.0 into GPL-2.0-only | §6 forbids additional restrictions | Switch to the GPL-3.0 dependency, drop it, or isolate with counsel sign-off |
| Copying a license text and editing it | A modified license is not that license | Use the canonical text verbatim; add clarification elsewhere |
| Linking metadata to a license by name | "BSD" is three different licenses | Resolve the SPDX ID; check `-Clause` count |
| Hand-maintaining the notices file | It drifts on the first dependency bump | Generate from the graph; fail CI on diffs |
| Ignoring the `WITH` exception | Classpath/GCC exceptions change copyleft reach materially | Parse the full SPDX expression, not just the license |
| Gate that only runs on PRs | Transitive license changes land silently | Add a scheduled scan of the resolved tree |
| Waivers that never expire | Exceptions outlive their justification | Owner + expiry; expired = failure |
| Deleting an AGPL package before release | The shipped artifact already carries the obligation | Rotate artifacts or document the exposure |

## References

- `references/sources.md` — primary sources: SPDX license list, REUSE spec, licensee, ScanCode, ORT, choosealicense
- `evals/evals.json` — evaluation scenarios

## Verification Checklist

- [ ] Dependency inventory produced from the resolved tree, not declared ranges
- [ ] File-level scan run over vendored and package directories; disagreements reconciled
- [ ] Every license mapped to an SPDX identifier, including `OR`/`AND`/`WITH` structure
- [ ] Every `UNKNOWN`/`NOASSERTION` resolved, replaced, or documented as accepted risk with an owner
- [ ] Compatibility checked for each inbound license against your outbound license
- [ ] Copyleft components: source offer valid, and corresponding source actually available
- [ ] Dynamic/static linking boundary documented where it carries the compliance argument
- [ ] `NOTICE` aggregated (Apache-2.0 §4(d)) and third-party notices generated with full texts
- [ ] Notices shipped in every artifact form: tarball, container image, in-app screen
- [ ] SBOM (SPDX or CycloneDX) generated and attached to the release
- [ ] CI gate fails on denied and unknown licenses, baselined against the base branch
- [ ] Every waiver has an owner and an unexpired date
- [ ] AI-generated and vendored code has a provenance record and a named human reviewer
- [ ] Findings reviewed by counsel before any statement about legal safety

This skill provides engineering guidance, not legal advice. Compatibility tables describe what the license texts say; they do not determine whether your specific use creates a derivative work or a distribution. Route final determinations to counsel.
