# Git Bisect Guide

Use `git bisect` to find which commit introduced a bug — it performs a binary search over your commit history.

## Basic Workflow

```bash
# Start the bisect session
git bisect start

# Mark the current commit as bad (broken)
git bisect bad

# Mark a known-good commit
git bisect good <known-good-sha>

# Git checks out a midpoint commit — test it
# If the bug is present: git bisect bad
# If the bug is absent: git bisect good
# Repeat until the first bad commit is identified
```

## Automated Bisect

```bash
# Run a test script at each step automatically
git bisect run python -m pytest tests/test_foo.py -x
```

The script must exit 0 for "good" and non-0 for "bad" commits.

## Bisect Strategies

### Narrow the Range First

Before starting bisect, find the tightest possible range:

```bash
# Find when a file was last changed
git log --oneline src/suspected_file.py | head

# Find commits touching a specific function
git log -p -S "function_name" --oneline
```

### Skip Build Failures

If a midpoint commit doesn't compile, skip it:

```bash
git bisect skip  # Skip the current commit
```

Or skip known broken ranges:

```bash
git bisect skip <sha1>..<sha2>
```

### Visualize Progress

```bash
git bisect visualize  # Shows the remaining candidate commits
```

### Reset When Done

```bash
git bisect reset  # Returns to the original HEAD
```

## Common Pitfalls

| Pitfall | Solution |
|---|---|
| Bisecting across a merge commit | `git bisect --first-parent` to follow the mainline |
| Commit doesn't compile | Use `git bisect skip` |
| Bug exists on the "good" commit too | Pick an older good commit and restart |
| The bug is introduced by a merge, not a regular commit | Check merge commits' parents individually |
| Bisecting across non-sequential commits | Squash or rebase first, or use --first-parent |

## Bisecting Performance Regressions

```bash
# For performance regressions, use a timing script:
git bisect run ./benchmark_script.sh
# Where benchmark_script.sh runs the perf test and exits 0 if fast, 1 if slow
```

## Pre-Bisect Checklist

Before reaching for bisect, ensure you have:

- [ ] A reliable reproduction (the bug happens every time)
- [ ] A test or command that exits 0 for "works" and non-0 for "broken"
- [ ] A known-good commit that doesn't have the bug
- [ ] A bisect-friendly history (no thousands of un-squashed WIP commits)