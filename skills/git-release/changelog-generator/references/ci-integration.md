# CI Integration

How to run the two scripts in a pipeline. Both are stdlib-only, so a Python 3.9+ interpreter is the only requirement — no `pip install`, no lockfile, no cache to warm.

## Exit code contract

| Script | 0 | 1 | 2 |
|--------|---|---|---|
| `commit_linter.py` | clean, or warnings only | at least one violation (or any warning under `--strict`) | usage error, bad ref, unreadable input |
| `generate_changelog.py` | entry rendered / version printed | — | bad ref, bad date, duplicate version, missing `--update` target |

CI should treat `2` as a broken pipeline configuration, not a code defect: it means the range was wrong or the changelog state is unexpected.

## GitHub Actions: lint commits on every pull request

```yaml
name: commit-lint
on: pull_request

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0          # the range below needs the history
      - name: Lint commits
        run: |
          python3 scripts/commit_linter.py \
            --range "origin/${{ github.base_ref }}..HEAD" \
            --format text
```

`fetch-depth: 0` matters. The default shallow clone has no merge base, so `origin/main..HEAD` fails to resolve and the step exits 2 — which reads like a lint failure but is a checkout problem. If full history is too expensive, `fetch-depth: 50` is usually enough for a PR range.

For a PR that is already merged locally into the base branch, use `--range "${{ github.event.pull_request.base.sha }}..HEAD"` instead.

## GitHub Actions: attach notes to a release

```yaml
name: release
on:
  push:
    tags: ["v*"]

jobs:
  notes:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Render release notes
        run: |
          python3 scripts/generate_changelog.py \
            --from "$(git describe --tags --abbrev=0 "${GITHUB_REF_NAME}^")" \
            --to "$GITHUB_REF_NAME" \
            --version "${GITHUB_REF_NAME#v}" \
            --format markdown > notes.md
      - name: Publish
        env:
          GH_TOKEN: ${{ github.token }}
        run: gh release create "$GITHUB_REF_NAME" --notes-file notes.md
```

The `"${GITHUB_REF_NAME}^"` suffix is the part people get wrong: `git describe --tags --abbrev=0` on the tagged commit returns the tag you are releasing, so the range would be empty. Stepping back one commit first makes `--from` the *previous* release.

## GitHub Actions: fail the build when the changelog is stale

A release is not ready if `CHANGELOG.md` has no section for the version in the tag.

```yaml
      - name: Verify changelog covers this version
        run: |
          version="${GITHUB_REF_NAME#v}"
          grep -q "^## \[${version}\]" CHANGELOG.md \
            || { echo "CHANGELOG.md has no section for ${version}"; exit 1; }
```

## Computing the version in CI

```bash
next=$(python3 scripts/generate_changelog.py --from "$(git describe --tags --abbrev=0)" --next)
if [ "$next" = "no-release" ]; then
  echo "no releasable commits since the last tag; skipping"
  exit 0
fi
```

`--next` prints `no-release` when the range contains only `chore`/`test`/`ci` commits. Gate on that string before tagging — a job that tags unconditionally will produce empty patch releases.

To feed the bump into other tooling, ask for JSON:

```bash
python3 scripts/generate_changelog.py --from v1.4.0 --next --format json
# {"bump": "major", "current": "v1.4.0", "version": "2.0.0"}
```

## GitLab CI

```yaml
commit-lint:
  image: python:3.12-slim
  variables:
    GIT_DEPTH: "0"
  script:
    - python3 scripts/commit_linter.py --range "origin/$CI_MERGE_REQUEST_TARGET_BRANCH_NAME..HEAD"
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

GitLab shallow-clones by default too; `GIT_DEPTH: "0"` is the equivalent fix.

## pre-commit hook

Local enforcement catches the message at the moment it is written, which is cheaper than a failed CI run.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: conventional-commit-msg
        name: conventional commit message
        entry: python3 scripts/commit_linter.py
        language: system
        stages: [commit-msg]
        args: ["--input"]
        pass_filenames: true
```

With `pass_filenames: true`, pre-commit appends the message file path, which is exactly what `--input` expects. The hook reads the message file pre-commit writes — no `git log` call, so it works on the very first commit too.

## Shell hook alternative

```bash
# .git/hooks/commit-msg
#!/bin/sh
python3 scripts/commit_linter.py --input "$1" || {
  echo "Commit message rejected. See 'Conventional Commit Rules' in SKILL.md."
  exit 1
}
```

## Monorepo scoping

Filter the range to one package before generating, so each package changelog only claims its own changes:

```bash
git log --format='%s%n%b%n---COMMIT---' --no-merges \
  "$(git describe --tags --abbrev=0 --match 'pkg-a-v*')"..HEAD -- packages/a \
  | python3 scripts/generate_changelog.py --input - --version "$VERSION" --update packages/a/CHANGELOG.md
```

Tag per package (`pkg-a-v1.2.0`) rather than globally, otherwise the "most recent tag" default resolves to whichever package released last and the ranges overlap.

## JSON shape

Stable keys for downstream tooling — do not parse the Markdown when you need data:

```json
{
  "version": "2.0.0",
  "date": "2026-11-13",
  "bump": "major",
  "counts": {"Added": 1, "Changed": 1, "Fixed": 1},
  "breaking": [{"description": "drop the v1 tasks endpoint",
                "notes": ["clients must migrate to GET /v2/tasks."]}],
  "sections": {"Added": [{"type": "feat", "scope": "api",
                          "description": "add pagination", "breaking": false}]},
  "skipped": 2
}
```

`skipped` is the count of parsed commits whose type produces no section (`chore`, `test`, `ci`, `style`). A large `skipped` next to a small `sections` is normal — it means the history is mostly maintenance, not that parsing failed. Non-conventional messages and merge commits are dropped before that count and are not reported; use `commit_linter.py` to find them.

## Windows runners

Both scripts use `pathlib`-free `os.path` and write with explicit `utf-8` encoding, so `windows-latest` runners work without further configuration. Two practical notes:

- Invoke with `python` rather than `python3` on Windows runners; `python3` may not resolve depending on the image.
- Set `core.autocrlf=false` in the checkout step if you compare generated files against committed ones, or the CRLF conversion will show as a spurious diff. Both scripts normalize `\r\n` on input.
