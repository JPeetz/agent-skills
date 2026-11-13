# Skill Patterns

Four shapes cover almost every skill. Pick by the structure of the work, not by preference.

## Simple / hub

**Shape:** one SKILL.md, a handful of sibling reference files, a tracks table linking them.

**Use when:** the job is a set of related-but-separable tasks, and the model should pick one based on what it sees — several input formats, several document types, several detectors.

**Structure:**

```text
skill/
├── SKILL.md          # routing table + shared rules
├── track-a.md
└── track-b.md
```

SKILL.md carries the shared constraints and a table: "if the input is X, read track-a". Each track is self-contained.

**Failure mode:** a hub with tracks that all get read anyway. If every task loads every track, it is one workflow with extra indirection.

## Workflow

**Shape:** numbered phases in SKILL.md, each with a clear exit condition, sometimes with references per phase.

**Use when:** order matters — the output of step 2 constrains step 3, and doing them out of order produces a wrong result that looks fine. Deployments, migrations, audits with a fixed sequence, multi-stage production pipelines.

**Structure:**

```text
skill/
├── SKILL.md          # Steps 1..n, each: action, exit condition
└── references/
    └── phase-3-details.md
```

Each step states what to do and how you know it is done. Shared rules (authorization, naming, output format) go near the top, once.

**Failure mode:** a workflow where no step depends on the previous one. That is a checklist, and a checklist should be rules-based instead — the model can then run only the relevant checks.

## Rules-based

**Shape:** a `rules/` folder, one concern per file, each rule individually addressable and citable.

**Use when:** the job is a sweep of independent checks against an artifact — lints, compliance audits, security reviews, style enforcement. The output is a report naming which rules passed.

**Structure:**

```text
skill/
├── SKILL.md          # how to run the sweep, how to report
└── rules/
    ├── _sections.md  # index and grouping
    ├── _template.md  # shape of a rule file
    └── 01-some-rule.md
```

Each rule file: id, what it checks, why it matters, pass/fail criteria, one example of a violation. Numbered filenames keep order stable and diffs readable.

**Failure mode:** rules that overlap, so one finding gets reported three times under three ids. One concern per file, and check for near-duplicates when adding.

## Mixed

**Shape:** a workflow in SKILL.md whose phases delegate to reference files, some of which are rules-based sweeps.

**Use when:** the real job has both a required order and a broad set of checks inside one phase — an incident review, a release process, a content pipeline.

**Failure mode:** the mixed pattern used to avoid choosing. If you cannot say which phases are ordered and which are free, the structure is not doing any work; default to workflow.

## Choosing

| Problem | Pattern |
|---------|---------|
| Several input types, each needing different handling | Simple / hub |
| Steps where getting the order wrong produces a wrong result | Workflow |
| Many independent checks producing a report | Rules-based |
| Ordered phases, one of which is a broad sweep | Mixed |
| A single short procedure with a few gotchas | None of these — plain SKILL.md |

## Before any of them

Check the collection for an existing owner of the job. A second skill with the same trigger is not a new capability; it is a routing coin-flip. Extend the owner, or add the new material as a reference file inside it.
