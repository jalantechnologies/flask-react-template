# Workflows

GitHub Actions workflow definitions for this template. For a plain-language walkthrough of what the
pull-request checks do and why, see [`docs/ci.md`](../../docs/ci.md).

| Workflow           | Trigger                         | What it does                                                                                                                                                     |
| ------------------ | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ci.yml`           | pull request                    | Runs the merge-gate checks: `lint`, `codereview`, `test-backend`, `test-frontend`, `sonarqube`, `scan`. A `changes` job skips the heavy checks on docs-only PRs. |
| `pr-labeler.yml`   | pull request (title)            | Validates the conventional-commit title and applies the `type:` / `semver:` labels. Lightweight — no checkout or dependency install.                             |
| `version-bump.yml` | pull request merged into `main` | Bumps the `package.json` version according to the merged PR's `semver:` label.                                                                                   |

## Matching CI work to the change

`ci.yml` cancels a superseded run when a newer commit is pushed to the same pull request
(`concurrency` with `cancel-in-progress`), and its `changes` job classifies each pull request as
documentation-only when every changed file is under `docs/` or is a `*.md` file. On a
documentation-only pull request the heavy checks (`test-backend`, `test-frontend`, `scan`,
`sonarqube`, `codereview`) are skipped via `needs: changes` + `if: needs.changes.outputs.doc_only ==
'false'`; `lint` and `pr-labeler` still run. See [`docs/ci.md`](../../docs/ci.md) for the full
rationale, including how products built from this template extend the same signal to skip their
preview deployment.

## Deployment

This template runs its checks in `ci.yml`; application deployment (preview and production) is handled
by the shared [`jalantechnologies/github-ci`](https://github.com/jalantechnologies/github-ci)
reusable workflows that products wire in. See [`docs/deployment.md`](../../docs/deployment.md).
