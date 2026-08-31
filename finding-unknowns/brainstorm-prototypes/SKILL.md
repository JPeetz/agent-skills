---
name: finding-unknowns-brainstorm-prototypes
description: >-
  Use when the user can only recognize what they want by seeing
  it — generate several wildly different throwaway variations.
version: 1.0.0
author: Skill Foundry
license: MIT
platforms:
  - linux
  - macos
  - windows
metadata:
  tags:
    - finding-unknowns
    - prototyping
    - brainstorming
    - exploration
  related_skills:
    - finding-unknowns-reference-hunt
    - finding-unknowns-interview-me
    - technique-spike
  complexity_level: intermediate
---

# Brainstorm and Prototypes

The user has unknown knowns: criteria they can't verbalize but will recognize on sight. Finding those during prototyping is cheap; finding them mid-implementation is expensive, because small spec changes can mean drastically different code. Give them things to react to.

Original technique: *A Field Guide to Fable: Finding Your Unknowns* by Thariq Shihipar.

## Steps

1. Establish scope first: what is being decided (layout? approach? data model? tone?) and what is explicitly out of scope. One decision per round.
2. Produce 3-5 variations that are **wildly different, not shades of the same idea**. If two variations would get the same reaction, replace one.
3. Make them cheap and disposable:
   - Visual/UX → a single self-contained HTML file with fake data, no backend, no state.
   - Approaches → a one-screen sketch of each: the idea, what it optimizes for, its sharpest tradeoff.
   - Ranked lists → order from cheapest to most ambitious so the user can draw their line.
4. Label each variation with the belief it bets on ("this one assumes density beats whitespace"), so the user's reaction reveals the underlying criterion, not just a preference.
5. Collect reactions, then verbalize what was learned: "you consistently rejected X, which suggests the real requirement is Y." That sentence is the deliverable — it becomes part of the spec.

## Pitfalls

- **Premature convergence**: don't converge early to the variation you'd personally pick. The point is spanning the space.
- **Similar variations**: if two variations would get the same reaction, replace one. They must be wildly different.
- **Reframing needed**: if the user rejects all variations, that's signal the decision space was framed wrong. Reframe and rerun rather than generating more of the same.

## Verification

- [ ] Did you establish scope (what's being decided, what's out of scope)?
- [ ] Are the variations wildly different (not shades of the same idea)?
- [ ] Is each variation labeled with the belief it bets on?
- [ ] Did you verbalize what was learned from the reactions?

## Install

See the [finding-unknowns README](https://github.com/JPeetz/agent-skills/tree/main/finding-unknowns) for install instructions. Original source: [Neeeophytee/finding-unknowns-skills](https://github.com/Neeeophytee/finding-unknowns-skills).