# Skills

This project ships [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) skills under
`.claude/skills/`. A skill is a reusable, versioned prompt that lives with the codebase, so every
contributor runs the same workflow. Invoke one in Claude Code by typing `/<skill-name>` and passing any
arguments it expects.

## Available skills

| Skill                                                 | Invoke                             | What it does                                                    |
| ----------------------------------------------------- | ---------------------------------- | --------------------------------------------------------------- |
| [Self-Review](../.claude/skills/self-review/SKILL.md) | `/self-review <PR link or number>` | Reviews and improves a PR in a loop until it is ready to merge. |

## Self-Review

After raising a PR, run the skill and pass the PR link or number:

```
/self-review <PR link or number>
```

The agent reviews the PR, applies improvements, resolves review comments, and fixes CI, looping until no
significant improvements remain and every check is green. It never pushes to a base branch.
