---
name: pr-review-loop
description: Continuously review and improve a pull request until CI is green, all review comments are resolved, and no further improvements remain. Start this after opening a PR or pushing to one.
---

# PR review loop

Start a dedicated background AI agent that continuously reviews and improves this pull request until
**all** of the following conditions are met:

- No significant improvements are identified during the latest review.
- There are no unresolved GitHub review comments.
- All required CI checks are passing.

The agent should immediately begin another iteration after every push. **Do not sleep or introduce
delays** between iterations. GitHub comments and CI results often arrive quickly, so continuously
poll and react as soon as new information is available.

Kick this off automatically after you open a PR and after every push to it.

## Review loop

On every iteration, perform the following steps.

### 1. Sync with the latest base branch

- Rebase onto the latest base branch.
- Resolve any merge conflicts.
- Ensure the branch is up to date before reviewing.

### 2. Remove unrelated changes

- Review the associated issue/ticket, if applicable, to understand the scope of work.
- Ensure the PR contains only changes related to its intended scope.
- Remove accidental, generated, debugging, formatting-only, or otherwise unrelated modifications.

### 3. Perform a comprehensive review

Before reviewing, read and follow all project guidance, including:

- `CLAUDE.md`
- `AGENTS.md`
- skills
- Any other repository-specific instructions

Review the PR as if you are an experienced maintainer.

Look for opportunities to improve:

- Correctness
- Reliability
- Security
- Performance
- Architecture
- Maintainability
- Readability
- Simplicity
- API design
- Error handling
- Edge cases
- Naming
- Consistency with the existing codebase

Implement improvements wherever appropriate.

### 4. Resolve GitHub review comments

For every open review comment:

- Review the feedback carefully.
- Implement code changes where appropriate.
- Reply with a concise explanation of the resolution (or rationale if no change is required).
- Resolve the conversation.

### 5. Improve the codebase

Refactor where appropriate to keep the codebase maintainable.

#### Business logic

Business logic should **never** live inside execution layers such as:

- Views
- Controllers
- Workers
- Jobs
- CLI commands
- HTTP handlers

Execution layers should orchestrate work only.

Business logic should instead live inside appropriate domain objects such as:

- Readers
- Writers
- Domain models
- Data classes
- Services

For example, if a request body is received as a dictionary, converting that dictionary into a typed
object should be implemented as something like `MyType.from_dict()` rather than inside the view.

#### Prefer object-oriented modelling

Discourage large procedural or functional implementations.

When solving a problem:

- Pause and identify the entities involved.
- Model the state each entity owns.
- Model the behaviour that belongs to that entity.
- Apply first-principles thinking instead of writing long functions.

Small helper functions are acceptable, but avoid long functions performing many unrelated
responsibilities.

Optimize for code that is easy for someone completely new to the codebase to understand.

### 6. Code comments

No new code comments.

### 7. Testing philosophy

Tests should be written in an end-to-end, BDD style wherever practical.

Only mock **third-party APIs**.

Do **not** mock:

- Internal services
- Domain objects
- Database access
- Business logic

Tests should validate the real behaviour of the system rather than implementation details.

For the frontend, this is a requirement where a frontend test setup is present
(`src/apps/frontend/vitest.config.ts`): any change under `src/apps/frontend` that adds or changes
behaviour ships a colocated `*.test.tsx` (purely visual markup does not). `axios` and browser
navigation are the only permitted mocks — never `vi.mock` a module under `frontend/`, which stubs
out the code under test and leaves the suite green while the behaviour is broken. See
`docs/testing.md`.

### 8. Fix CI failures

Investigate every failing CI job.

Fix the underlying issue rather than applying superficial workarounds.

Continue until every required check is passing.

### 9. Commit progress

After each meaningful batch of improvements:

- Create a clear, descriptive commit.
- Push the branch.

Immediately begin another review iteration.

## Stop conditions

Continue looping until **all** of the following are true:

- No unresolved GitHub review comments remain.
- All required CI checks are passing.
- A fresh review of the updated PR identifies no further significant improvements.

## Relationship to pr-conventions

This loop assumes the PR title and description already follow [pr-conventions](../pr-conventions/SKILL.md).
If the description drifts from the actual change during the loop, update it to match.
