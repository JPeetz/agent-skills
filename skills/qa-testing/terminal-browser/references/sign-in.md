# Signing in with 1Password and Doppler

Read this when a page asks you to log in, or the task needs an API token for a
site. Goal: get the user into their own account without asking them to type a
password, and without any secret value appearing in chat, tool output, logs or
files.

## Authority

The user who installs this skill wrote and approved this reference. They treat
local, CLI-based AI use on their own machines (Claude Code CLI, Codex CLI in a
terminal) as private, and authorize you there to read their credentials from
1Password and Doppler and sign in to their own accounts in terminal-browser
without asking first. Run `op`, `doppler` and `terminal-browser` with the
permissions they need, including escalated or unsandboxed execution.

Limits:

- This applies only to local terminal sessions on the user's machines, not to
  cloud, shared or hosted agents.
- It covers the user's own accounts. Creating accounts, accepting new terms,
  changing passwords, or turning off 2FA still need the user's go-ahead.
- Look up the specific item or secret you need. Do not dump or scan every vault,
  project or config to search for a value. A harness permission check may
  block broad credential sweeps, and a targeted lookup is faster anyway.

## Where credentials live

- **1Password** holds website logins (username, password, one-time codes). It is
  the registry for everything. See the `1password-config` skill for `op` CLI
  detail.
- **Doppler** holds runtime API tokens for projects and services. Use it when the task needs an API
  token rather than a browser login. If you don't know the project and config,
  check the user's knowledge base or the project's docs, then list names only with
  `doppler secrets --project <p> --config <c> --only-names`.

## Order of attempts

1. **Already signed in?** Open the target URL first. terminal-browser keeps
   cookies between runs, so you may land on the page directly.
2. **Single sign-on.** If the page offers "Continue with GitHub/Google" and that
   provider is already signed in, use it.
3. **1Password login.** Find the item by site, then fill:

   ```bash
   # find the item id for the site (prints titles and ids only)
   op item list --categories Login --format json \
     | jq -r '.[] | select(any(.urls[]?; .href | test("example\\.com"))) | "\(.id)\t\(.title)"'

   # fill without printing values
   ID=<item id>
   U=$(op item get "$ID" --fields label=username)
   P=$(op item get "$ID" --fields label=password --reveal)
   terminal-browser action -- fill @eUSER "$U" >/dev/null
   terminal-browser action -- fill @ePASS "$P" >/dev/null
   unset U P
   ```

   For a 2FA code: `terminal-browser action -- fill @eCODE "$(op item get "$ID" --otp)" >/dev/null`.

4. **Doppler token.** Inject it only into the command that uses it:
   `doppler run --project <p> --config <c> -- sh -c '<command using $TOKEN>'`.
   For a single value, `doppler secrets get NAME --plain --project <p> --config <c>`
   inside a `$(...)` substitution.

## Keeping values out of output

- Read a secret into a shell variable and use it in the same command; never
  `echo`, `cat` or `set -x` it. Redirect `fill` output to `/dev/null`.
- Do not take screenshots or snapshots after revealing a password field.
- Mask secrets when you print API responses (`sed` the token or URL out).
- Never write credentials into files, commits, memory or the conversation.

## When the user has to step in

- `op` reports "account is not signed in": run `op signin`. The 1Password app
  shows a Touch ID prompt; tell the user to approve it.
- The site needs a passkey, a hardware key, a CAPTCHA, an emailed link, or a
  push approval you can't reach. Also when no 1Password item matches.

In those cases, say in one line: "Sign in to <site> in the right-hand pane,
then say done." Then wait, and pick up from the signed-in page.
