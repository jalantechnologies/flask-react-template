---
name: self-review
description: >-
  Autonomously review and improve a pull request in a loop until no significant improvements
  remain, all GitHub review comments are resolved, and every CI check is green. Use after a
  PR is raised, when the user wants an agent to self-heal / polish it. Pass the PR link or number
  as an argument.
---

# Self-Review

Continuously review and improve the pull request passed as an argument (a PR link or number) until
**all** of these hold:

- A fresh review of the updated PR identifies no further significant improvements.
- No unresolved GitHub review comments remain.
- Every CI check on the PR is green.

Begin another iteration immediately after every push, and react as soon as new information lands. **Never
`sleep`-and-poll in a loop** — that burns API quota against CI jobs that take minutes. Block on the result
instead: `gh pr checks <pr> --watch` returns the moment the checks settle.

Use the `gh` CLI for every PR interaction (diff, comments, checks, runs). If no PR argument was given,
ask which PR to work on, or infer it from the current branch (`gh pr view`).

**A draft PR runs no CI** — every job is gated on `draft == false`, so no check ever reports and the CI stop
condition can never be met. Check `gh pr view <pr> --json isDraft` first; if it is a draft, ask the user to
run `gh pr ready <pr>`, or stop.

## Review loop

On every iteration, perform the following steps in order.

### 1. Sync with the latest base branch

- `git fetch origin main`. If `git rev-list --count HEAD..origin/main` is `0`, the branch is already current
  — do not rebase.
- Rebase only when behind **and** it matters: the PR conflicts (`gh pr view <pr> --json mergeable`), or CI
  fails for something `main` has since fixed. A rebase rewrites history — it forces a force-push and
  re-anchors every open review thread, so do not do it reflexively.
- On any conflict whose resolution is not unambiguous, `git rebase --abort` and hand back to the user with
  the conflicting files.

### 2. Remove unrelated changes

- Ensure the PR contains only changes related to its intended scope.
- Remove accidental, generated, debugging, formatting-only, or otherwise unrelated modifications.

### 3. Perform a comprehensive review

Before reviewing, read and follow all project guidance:

- `AGENTS.md` (root and any nested ones). The CI `codereview` gate treats `AGENTS.md` as the
  authoritative standard, so stay consistent with it.
- `CLAUDE.md` (root and any nested ones).
- Any other repository-specific instructions, including the relevant docs under `docs/`.

Review the PR as an experienced maintainer. Look for opportunities to improve: correctness, reliability,
security, performance, architecture, maintainability, readability, simplicity, API design, error handling,
edge cases, naming, and consistency with the existing codebase. Implement improvements wherever appropriate.

### 4. Resolve GitHub review comments

For every open review comment:

- Review the feedback carefully.
- Implement code changes where appropriate.
- Reply with a concise explanation of the resolution (or the rationale if no change is required).
- Resolve the conversation.

### 5. Improve the code the PR touches

Refactor to keep the codebase maintainable, but **only within the PR's existing footprint** — the lines and
files it already changes. Do not rename a shared helper, restructure a neighbouring module, or tidy a
function the PR never touched. Report such findings to the user at the end instead of fixing them.

Judge the code against the Review Guidelines in `AGENTS.md` — comments, naming, function size, layering,
encapsulation, reuse, module independence, business-logic placement, data access, and the frontend design
system.

### 6. Testing

Every behavioural change carries its tests, and a PR that only adds tests is still a PR that must pass them.
Follow the Testing Requirements in `AGENTS.md` — where tests live, the coverage target, BDD style, and the
rule that only third-party APIs may be mocked.

### 7. Fix CI failures

Wait for the run with `gh pr checks <pr> --watch`, then drill into failures with `gh run view`.
Fix the underlying issue rather than a superficial workaround. Continue until every check passes — treat them
all as blocking, whether or not branch protection currently enforces them. GitHub renders these as
`ci / <job>`; the CI jobs in this repo (`.github/workflows/ci.yml`) are:

- **`ci / lint`** — `npm run lint` (ESLint on TS, remark on markdown, `mypy` strict + a `pylint`
  cyclic-import check on Python) **and** `npm run fmt:check` (Prettier check + isort/black check). Format is
  folded into this one job; there is no separate `format` check.
- **`ci / test`** — integration tests in Docker via
  `docker compose -f docker-compose.test.yml up --exit-code-from app`. It reports coverage against the
  60/80 thresholds but does **not** fail on them (that step is `continue-on-error`), so a green `ci / test`
  is no proof coverage held — a failing test is what turns it red.
- **`ci / sonarqube`** — SonarQube quality gate (`needs: test`; consumes the coverage artifact). This is the
  check that can actually block on coverage.
- **`ci / codereview`** — the AI code-review gate (`anthropics/claude-code-action`, reading `AGENTS.md`).
  It fails when it posts inline findings, so address/resolve every finding it raises.
- **`ci / scan`** — Trivy (filesystem / IaC / Docker) and Checkov security scans; fails on HIGH/CRITICAL.

Reproduce failures locally before pushing with `npm run lint`, `npm run fmt:check`, and `make run-test`
(or `npm run test`).

### 8. Commit progress

After each meaningful batch of improvements:

- Create a clear, descriptive commit using Conventional Commits (`<type>: <subject>`).
- Push the PR's own feature branch. **Never push to `main`** (or any other base branch) — this loop
  only ever commits to and pushes the branch under review.
- After a rebase the push is a non-fast-forward: use `git push --force-with-lease`, never a bare `--force`.
  A rejection means someone else pushed — stop for the user instead of overriding it.

Then immediately begin another review iteration.

## Stop conditions

Continue looping until **all** of the following are true:

- No unresolved GitHub review comments remain.
- Every CI check on the PR is green.
- A fresh review of the updated PR identifies no further significant improvements.

Also stop and hand back to the user — with a short summary of what remains — if any of these trip,
so the loop can never spin forever: an iteration produces no new commit (nothing left to improve);
a change would revert or re-litigate an earlier iteration's work; the same check fails 3 times in a
row; a rebase conflict is not unambiguous or a `--force-with-lease` push is rejected (the branch is
contested); or you reach 10 iterations. When unsure whether an improvement is significant, prefer to stop.
