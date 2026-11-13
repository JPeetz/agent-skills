# Primary Sources

Authoritative references for license identification, expression, and obligation
analysis. Prefer these over blog posts and license "explainers" — most of the
public commentary on copyleft scope is either wrong or jurisdiction-specific.

## License text and identifiers

| Source | What it is for |
|---|---|
| [SPDX License List](https://spdx.org/licenses/) | Canonical identifier for every license; the only list to cite. Check whether an ID is deprecated before using it. |
| [SPDX License Expressions](https://spdx.github.io/spdx-spec/v2.3/SPDX-license-expressions/) | Grammar for `OR`, `AND`, `WITH`, `+`, and `LicenseRef-`. Read this before writing an expression into a manifest. |
| [SPDX Specification](https://spdx.github.io/spdx-spec/) | The SBOM format itself: fields, document structure, `NOASSERTION` / `NONE` semantics. |
| [choosealicense.com](https://choosealicense.com) | Plain-language comparison of the common licenses and their permissions/conditions/limitations, plus the "appendix" of non-recommended licenses. |
| [OSI Approved Licenses](https://opensource.org/licenses) | Whether a license is actually open source by the OSI definition. Source-available licenses are not on this list. |
| [FSF License List](https://www.gnu.org/licenses/license-list.html) | Free-license classification, and the FSF's compatibility commentary — particularly for GPL interactions. |
| [GNU GPL FAQ](https://www.gnu.org/licenses/gpl-faq.html) | The FSF's own answers on linking, aggregation, plugins, and AGPL network use. Opinionated, but it is the license steward's opinion. |
| [Apache-2.0 text](https://www.apache.org/licenses/LICENSE-2.0) | §4 obligations (notices, change marking) and §3 patent grant/termination. |
| [MPL-2.0 text](https://www.mozilla.org/en-US/MPL/2.0/) | §3.1 source-form distribution, §3.3 secondary licenses, and the "Incompatible With Secondary Licenses" notice. |
| [AGPL-3.0 text](https://www.gnu.org/licenses/agpl-3.0.html) | §13 remote network interaction — the provision that puts SaaS in scope. |

## Machine-readable licensing practice

| Source | What it is for |
|---|---|
| [REUSE Specification](https://reuse.software/spec/) | Per-file licensing: `SPDX-FileCopyrightText` + `SPDX-License-Identifier` headers, `.license` sidecar files, the `LICENSES/` directory, and why DEP5 is deprecated. |
| [REUSE tool](https://github.com/fsfe/reuse-tool) | `reuse lint` and `reuse annotate` — the fastest way to make a repo machine-readable, and a good CI check. |
| [SPDX best practices](https://spdx.github.io/spdx-spec/v2.3/using-SPDX-short-identifiers-in-source-files/) | How to write identifiers in source headers. |

## Tooling

| Source | What it is for |
|---|---|
| [licensee](https://github.com/licensee/licensee) | License identification with confidence scores and text diffs. The engine behind GitHub's license badge. Ruby gem. |
| [ScanCode Toolkit](https://github.com/nexB/scancode-toolkit) | File-level license and copyright detection with match scores and matched rules. Also extracts holders for attribution output. |
| [OSS Review Toolkit](https://github.com/oss-review-toolkit/ort) | Analyzer/scanner/advisor/reporter pipeline. Curations in `.ort.yml`, policy rules in `rules.kts`, NOTICE and SBOM reporters. |
| [ORT documentation](https://oss-review-toolkit.org/ort/) | Config file reference and the rule DSL. |
| [CycloneDX](https://cyclonedx.org/) | Alternative SBOM format; more common in AppSec and container tooling than SPDX. |
| [syft](https://github.com/anchore/syft) | Fast one-shot SBOM generation across container images and filesystems. |
| [cargo-deny](https://github.com/EmbarkStudios/cargo-deny) | Rust license/ban/source policy in one config — a good model for what a policy gate should look like. |
| [license-checker-rseidelsohn](https://github.com/RSeidelsohn/license-checker-rseidelsohn) | Maintained fork of `license-checker`; `--onlyAllow` and `--excludePackages` cover most npm gates. |
| [pip-licenses](https://github.com/raimon49/pip-licenses) | Python license inventory from the installed environment. |

## Compatibility and obligation analysis

| Source | What it is for |
|---|---|
| [GNU license compatibility notes](https://www.gnu.org/licenses/license-compatibility.html) | The FSF's compatibility determinations, including why Apache-2.0 is incompatible with GPLv2. |
| [Apache Foundation licensing how-to](https://www.apache.org/legal/resolved.html) | Apache's own inbound/outbound matrix — useful because it is written for a project that must accept contributions under many licenses. |
| [SPDX license compatibility (FEEDS)](https://github.com/spdx/spdx-spec/tree/development/v2.3) | Machine-readable relationship data, where available. Fragmented; verify against license text. |
| [European Commission JLA](https://joinup.ec.europa.eu/collection/eupl/joinup-licensing-assistant) | Interactive compatibility checker, useful for EUPL and cross-license questions. |

## Reading notes

- **The license steward's FAQ is evidence, not law.** The FSF's position on
  plugin boundaries is influential and widely followed, but it is one party's
  interpretation. Courts decide the rest.
- **A modified license text is a different license.** `licensee diff` against
  the canonical text before assuming an identifier applies. Vendors routinely
  append "Commons Clause"-style restrictions to Apache-2.0.
- **Deprecated identifiers hide the "or later" question.** `GPL-2.0` is
  ambiguous by design; `GPL-2.0-only` and `GPL-2.0-or-later` are not. Resolve
  against the actual grant, not the metadata.
- **Nothing here is legal advice.** These are sources to reason from and to hand
  to counsel, not substitute conclusions.
