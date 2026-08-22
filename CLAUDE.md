# CLAUDE.md

Read [AGENTS.md](AGENTS.md). It is the single source of truth for code standards in this repository:
architecture principles, backend and frontend review guidelines, security expectations, testing
requirements, and the commit and PR format.

This file holds no standards of its own, on purpose. There used to be two copies of several rules, one
here and one in `AGENTS.md`, and they drifted. `AGENTS.md` is the copy that survives for two reasons:

- It is the cross-tool convention. Claude Code, Codex, and Cursor all read it without configuration.
- The CI code review job reads it as the authoritative standard on every pull request. A rule written
  only here is a rule the review gate never sees.

If you want to add or change a rule, change `AGENTS.md`. Do not add it here.

The longer form of individual topics lives in `docs/`:

- [Backend Architecture](docs/backend-architecture.md)
- [Frontend Architecture](docs/frontend-architecture.md)
- [Frontend Design System](docs/frontend-design-system.md)
- [Testing](docs/testing.md)
- [Configuration Guide](docs/configuration.md)
- [Contributing](docs/contributing.md)
