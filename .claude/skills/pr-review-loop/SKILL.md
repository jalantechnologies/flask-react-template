---
name: pr-review-loop
description: Continuously review and improve a pull request until CI is green, all review comments are resolved, and no further improvements remain. Start this after opening a PR or pushing to one.
---

# PR review loop

Start a dedicated background agent that continuously reviews and improves a pull request until
**all** stop conditions are met. Kick this off automatically after you open a PR and after every
push to it.

**Do not sleep or add delays between iterations.** GitHub comments and CI results arrive quickly;
poll and react as soon as new information is available. Begin the next iteration immediately after
each push.

## Stop conditions

Keep looping until **all** of these are true:

- A fresh review of the updated PR finds no further significant improvements.
- No unresolved GitHub review comments remain.
- All required CI checks are passing.

## Each iteration

### 1. Sync with the base branch

Rebase onto the latest base branch, resolve conflicts, and make sure the branch is up to date
before reviewing.

### 2. Remove unrelated changes

Read the linked issue (if any) to understand the intended scope. Keep the PR to that scope only.
Strip accidental, generated, debugging, or formatting-only changes that are not part of the PR's
purpose.

### 3. Comprehensive review

First read and follow all project guidance: `CLAUDE.md`, `AGENTS.md`, and any other repo-specific
instructions. Then review as an experienced maintainer, looking for improvements to: correctness,
reliability, security, performance, architecture, maintainability, readability, simplicity, API
design, error handling, edge cases, naming, and consistency with the existing codebase. Implement
improvements where appropriate.

### 4. Resolve review comments

For every open review comment: consider it carefully, make code changes where appropriate, reply
with a concise explanation of the resolution (or the rationale if no change is needed), and resolve
the conversation.

### 5. Keep the codebase clean

**Business logic never lives in execution layers** (views, controllers, workers, jobs, CLI
commands, HTTP handlers). Those orchestrate only. Business logic belongs in domain objects —
readers, writers, domain models, data classes, services. Example: turning a request-body dict into
a typed object is `MyType.from_dict()`, not inline in the view.

**Prefer object-oriented modelling** over large procedural or functional code. Identify the entities
involved, model the state each owns and the behaviour that belongs to it, and think from first
principles. Small helper functions are fine; long functions doing many unrelated things are not.
Optimize for code a newcomer can understand.

### 6. Comments

No new code comments. Code should be self-explanatory through naming and structure. Remove comments
that narrate what the next line does. (If a genuinely non-obvious invariant or workaround already
carries a "why" comment, leave it; but do not add new ones.)

### 7. Tests

Write end-to-end, BDD-style tests wherever practical. Mock **only third-party APIs**. Do not mock
internal services, domain objects, database access, or business logic. Tests validate real system
behaviour, not implementation details.

If a frontend test setup is present (`src/apps/frontend/vitest.config.ts`), any change under
`src/apps/frontend` that adds or changes behaviour ships a colocated `*.test.tsx` (purely visual
markup does not). `axios` and browser navigation are the only permitted mocks — never `vi.mock` a
module under `frontend/`, which stubs out the code under test and leaves the suite green while the
behaviour is broken. See `docs/testing.md`.

### 8. Fix CI

Investigate every failing CI job and fix the underlying cause, not a superficial workaround.
Continue until every required check passes.

### 9. Commit and continue

After each meaningful batch of improvements, make a clear, descriptive commit and push. Then begin
the next iteration immediately.

## Relationship to pr-conventions

This loop assumes the PR title and description already follow [pr-conventions](../pr-conventions/SKILL.md).
If the description drifts from the actual change during the loop, update it to match.
