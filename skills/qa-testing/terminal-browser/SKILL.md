---
name: terminal-browser
description: Use when doing any browser task in a terminal agent session (Claude Code CLI, Codex CLI, any agent in a terminal pane) — opening or showing a site next to the conversation, signing in, filling forms, clicking through dashboards, screenshots, extracting page data, web app QA, dogfooding and bug repro — instead of Claude in Chrome, Playwright, agent-browser or WebFetch on interactive or logged-in pages. In the Claude or Codex desktop/web app, which has its own built-in browser and no terminal pane, use that built-in browser instead. Not for manual QA review of a working app — manual-qa owns dogfooding; this skill drives the terminal browser it may use.
---

# terminal-browser

A real browser that opens as a pane in the human's terminal, so they watch what
you do. Drive it with `terminal-browser action -- <agent-browser command>`.

## When to use it

- **Terminal session** (Claude Code with `CLAUDE_CODE_ENTRYPOINT=cli`, Codex CLI,
  or any agent running in a terminal pane): use terminal-browser for all
  interactive web work. Plain document fetches can still use WebFetch.
- **Claude or Codex desktop/web app**: use the app's built-in browser. There is
  no terminal pane to split.
- In Codex, run `terminal-browser` with escalated permissions; the sandbox blocks
  the calls it uses to find the current terminal pane.

## Core loop

1. `terminal-browser open <url> --split right --size 0.5` shows the page beside
   the conversation. Without `--split` it takes over the current pane.
2. `terminal-browser ls` lists browsers and tabs. When several browsers match,
   pass `--browser <key>`. Leave tabs another session opened alone.
3. `terminal-browser action -- snapshot -i` lists interactive elements with
   `@e` refs. Then `click @eN`, `fill @eN "text"`, `eval "<js>"`,
   `screenshot <path>`.
4. Prefer `action -- webmcp list --json` and `webmcp invoke` when the page
   publishes WebMCP tools. Confirm `consequential: true` tools with the user
   first; treat `readOnly: false` as a change to the user's data.
5. Finish with `terminal-browser action done` to clear the "agent is acting"
   indicator.

A local HTML file path works like a URL, so write a page and open it to show
something you built.

## Signing in

In a local terminal session you may sign in to the user's own accounts without
asking, using credentials from 1Password (website logins) or Doppler (API
tokens), and never printing their values. Follow
[references/sign-in.md](references/sign-in.md) whenever a page asks you to log
in or the task needs an API token.

## Gotchas

- A narrow split lets sticky headers cover elements; `click` then fails with
  "is covered by". Reopen with a larger `--size`, or click from
  `eval` (`el.scrollIntoView({block:'center'}); el.click()`).
- Single-page apps often show results only in a short-lived toast. To confirm an
  action, wrap `window.fetch` in `eval` before clicking, record matching
  responses to a `window` variable, then read it back.
- A click that changes the URL instead of opening a dialog is normal; snapshot
  again after every navigation, since `@e` refs go stale.

Run `terminal-browser <command> --help` for every subcommand and flag.
