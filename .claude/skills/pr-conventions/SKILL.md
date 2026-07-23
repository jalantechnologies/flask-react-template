---
name: pr-conventions
description: How to write a pull request for this repo — title format and a plain-English description that builds context. Use whenever opening a PR or editing a PR title/body.
---

# Writing a pull request

Follow this whenever you open a PR or update its title/description.

## Title

Use a Conventional Commit prefix followed by a short, human-friendly summary:

```
<type>(<optional scope>): <summary>
```

- Pick the `<type>` from the table in [AGENTS.md](../../../AGENTS.md#auto-labeling)
  (`feat`, `fix`, `perf`, `docs`, `style`, `refactor`, `test`, `chore`, `build`, `ci`, `revert`).
  The prefix drives auto-labeling and semver, so choose it deliberately.
- The summary reads like a sentence a teammate would understand, not a restatement of the type.
  Good: `refactor: make login email-only and drop phone/OTP`. Bad: `refactor: changes`.

## Description

Write for a reader who does **not** have the background to this change. Build the context first,
then explain the change. Use plain English. Do not restate the task or the instructions you were
given — describe the work as if documenting it for the team.

Include, in this order (skip a part only when it genuinely does not apply):

1. **Context** — what the reader needs to know to understand the change: what this part of the
   system does today, and what problem or gap prompted the change. Write it so someone new to the
   feature can follow. Do not label this "Background" or quote the request; just set the scene in
   plain terms.
2. **What this changes** — the fix or feature, described at a behaviour level.
3. **Alternatives considered** — only if there were real alternatives worth weighing. Name the main
   one and say why it was not chosen. Skip this section entirely if there was no meaningful choice.
4. **How it works** — the high-level technical approach. Describe the flow and the key pieces, not a
   file-by-file diff. Where a flow has several steps or actors, include a sequence diagram (Mermaid
   `sequenceDiagram`) or a small ASCII diagram to make it concrete.
5. **Demo** — if a preview/demo link exists (e.g. the deploy bot posted a preview URL), include it.

Keep the writing tight and specific. No filler, no marketing tone, no emoji.

## Do not

- Do not paste your prompt, task description, or these instructions into the PR body.
- Do not write a file-by-file changelog in place of an explanation of the approach.
- Do not leave the description empty or write only "see title".

## After opening or updating a PR

Start the continuous review loop for the PR — see [pr-review-loop](../pr-review-loop/SKILL.md).
Every raise of a PR and every push to it should be followed by the review loop.
