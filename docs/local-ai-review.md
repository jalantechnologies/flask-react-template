# Local AI Pre-Push Review

CI runs an AI code review on every pull request: it reads the diff, applies the
standards in `AGENTS.md`, and posts inline comments. That review is useful but it
runs after the push, and every run spends tokens against the project's shared
`ANTHROPIC_API_KEY` budget.

The local pre-push review moves that same review onto the engineer's machine,
before the push leaves the laptop. It uses whichever AI coding CLI the engineer
already runs (and that engineer's own subscription), so the work is done once,
locally, and the PR arrives already reviewed. Less back-and-forth on the PR, and
the project's API budget is no longer spent re-reviewing the same commits on each
push.

## How it works

A `pre-push` git hook (`.husky/pre-push`) runs `.husky/scripts/ai-review.sh`,
which:

1. Works out the exact range being pushed (the commits the remote does not yet
   have) from the refs git passes to the hook.
2. Detects the engineer's AI CLI on `PATH` — `claude`, then `codex`, then
   `cursor-agent`.
3. Launches that CLI interactively, seeded with `.husky/scripts/ai-review-prompt.md`,
   which points the agent at `AGENTS.md` and `CLAUDE.md` as the standard — the
   same source of truth CI uses.

The agent reviews the diff and, for each finding:

- **fixes it in place when it is 100% sure** the fix is correct, and
- **stops and asks the engineer when it is not** — ambiguous fixes, multiple valid
  approaches, anything it cannot verify. It never guesses.

It then re-reviews and repeats until a pass surfaces nothing new. All edits are
left in the working tree for the engineer to review and commit. The agent does
not commit, amend, or push.

## It is enabled by default, and never blocks you

The hook runs automatically once you have an AI CLI installed. It is advisory:
it never fails the push on its own, so a cancelled or crashed agent can never
wedge a push. It skips silently (and lets the push proceed) when:

- no supported AI CLI is on your `PATH`,
- there is no terminal to drive an interactive session (CI, scripts, GUI clients),
- you set `AI_REVIEW=0`.

## Knobs

| Variable        | Effect                                                                                                                                  |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `AI_REVIEW=0`   | Skip the review for this push.                                                                                                          |
| `AI_REVIEW_CMD` | Force a specific CLI command. Per-push: `AI_REVIEW_CMD=codex git push`. Persistent: `export AI_REVIEW_CMD=codex` in your shell profile. |

To bypass all git hooks for a single push, use `git push --no-verify`.

## Using a CLI that isn't auto-detected

If your AI CLI is not one of the detected three, set `AI_REVIEW_CMD` to its launch
command. The contract is simple: the command is invoked with the review prompt as
its final argument and must start an interactive session so it can ask you
questions. Add your tool to `.husky/scripts/ai-review.sh` if the team adopts it
widely.
