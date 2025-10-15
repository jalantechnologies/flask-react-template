# Contributing

This guide explains how to contribute safely to this repository with secure workflow approval processes.

## External Contributors

For security reasons, workflows for external contributors require approval:

1. Fork the repository
2. Create your feature branch
3. Open a pull request
4. Wait for maintainer to add `approved-contributor` label
5. The workflow will automatically run after approval

## For Maintainers

### Approving External PRs

Avoid adding the 'approved-contributor' label if the PR modifies build or deployment secrets.

1. Review the code changes carefully
2. Check for suspicious workflow modifications
3. If safe, add label: 'approved-contributor'
4. Workflows will then run

### Security Guidelines

- Never approve PRs that modify `.github/workflows/` without thorough review
- External PRs cannot access secrets by default
- Team member PRs work automatically
- All workflows have explicit minimal permissions
