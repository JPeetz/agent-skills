# Gate 3: Docs Review — Accuracy & Drift Detection

## Overview

This gate catches how LLMs produce documentation that sounds authoritative but is factually wrong. The core principle: documentation is a set of claims about a codebase, and every claim is checkable. AI agents document from memory of how APIs *usually* look, not from the code in front of them.

## The 10 Rules

### Accuracy — Must Fix

1. **Every referenced symbol must exist.** Every function, method, class, hook, CLI command, flag, endpoint, config key, env var, and file path mentioned in the docs gets verified against the actual source — by reading it, not recalling it. An unverifiable reference does not ship.

2. **Every code sample must work.** Imports resolve, APIs exist with the documented signatures (names, argument order, defaults, return shape), and the sample runs outside the author's machine — no hardcoded local paths, no real credentials, no implicit prior state.

3. **Document the code's actual behavior, not its intended behavior.** Read the implementation before describing it. Where code and comments disagree, the code is the truth — and flag the disagreement.

4. **No unverifiable claims.** Performance numbers, compatibility matrices, scale limits, and "production-ready" assertions require a source in the repository or they come out.

### Versioning and Drift — Should Fix

5. **Versions are explicit.** Features, flags, and behaviors state the version that introduced them. Prerequisites are pinned or ranged, never "latest". Deprecated items say so, with the replacement.

6. **A code change owes a docs change.** When editing code whose behavior is documented — rename, signature change, new default — update every doc surface that mentions it in the same change. Grep the docs for the old symbol before finishing.

### Substance — Should Fix

7. **No filler, no slop.** Delete: docstrings that paraphrase the signature, sections that restate their heading, marketing adjectives in technical prose ("powerful", "seamless", "blazingly fast"), and intro padding.

8. **Don't paraphrase upstream docs.** Link to external documentation instead of restating it. Document only your project's relationship to the external thing.

9. **Examples cover the failure path too.** A tutorial that only shows the happy path documents half the API. Show what the error looks like.

### Structure — Worth Noting

10. **Navigation tells the truth.** Headings describe their sections, the table of contents matches the actual headings, internal links and anchors resolve. No TODO stubs or "coming soon" sections in published docs.

## Self-Check (Gate 3)
1. List every symbol, flag, endpoint, config key, and path your docs mention. Did you verify each one against the source in this session — not from memory?
2. Would every code sample run on a clean machine? Did you check each import and signature?
3. Any number, compatibility claim, or superlative without a repo-verifiable source?
4. If this change touched code: did you grep all docs surfaces for the old names?
5. Any docstring that just restates the signature? Any section that restates its heading?
6. Do all internal links and anchors resolve?