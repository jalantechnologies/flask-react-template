# Flask React Template

Boilerplate project for Flask, React & MongoDB based projects. This README documents the steps necessary to get the application up and running, and various components of the application.

| Build Status                                                                                                                                                                                                                         | Code Coverage                                                                                                                                                                                                                                                                                                                                      |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![Production Deploy](https://github.com/jalantechnologies/flask-react-template/actions/workflows/production.yml/badge.svg?branch=main)](https://github.com/jalantechnologies/flask-react-template/actions/workflows/production.yml) | [![Coverage](https://sonarqube.platform.bettrhq.com/api/project_badges/measure?project=jalantechnologies_better-ai_4d429ede-a26b-4480-9e6f-05f558f39224&metric=coverage&token=sqb_6fda79e9305a120b0f1d921b86aaafbdde4f10f2)](https://sonarqube.platform.bettrhq.com/dashboard?id=jalantechnologies_better-ai_4d429ede-a26b-4480-9e6f-05f558f39224) |

### Environments & URLs

This project has three deployment environments that everyone can access:

- **Production**
  - The live app for end users.
  - Web App URL: [https://flask-react-template.platform.bettrhq.com](https://flask-react-template.platform.bettrhq.com)

- **Preview (per PR)**
  - A temporary environment for testing the latest changes in each PR
  - A unique URL is generated for every pull request (e.g. `https://<github_sha>.preview.platform.bettrhq.com`).

- **Permanent Preview**
  - Always reflects the latest `main` branch.
  - Useful for ongoing testing of the integrated codebase.
  - URL: [https://preview.flask-react-template.platform.bettrhq.com](https://preview.flask-react-template.platform.bettrhq.com)

## Documentation Directory

- [Getting Started](docs/getting-started.md)
- [Backend Architecture](docs/backend-architecture.md)
- [Frontend Architecture](docs/frontend-architecture.md)
- [Infrastructure Overview](docs/infrastructure-overview.md)
- [Logging](docs/logging.md)
- [Configuration](docs/configuration.md)
- [Secrets](docs/secrets.md)
- [Bootstrapping](docs/bootstrapping.md)
- [Scripts](docs/scripts.md)
- [Code Formatting](docs/code-formatting.md)
- [Workers](docs/workers.md)

- [CI/CD](docs/deployment.md)
- [DNS Setup](docs/dns-setup.md)
- [Running Scripts in Production](docs/running-scripts-in-production.md)

## Best Practices

Once you have familiarized yourself with the documentation, head over to the [Engineering Handbook](https://github.com/jalantechnologies/handbook/blob/main/engineering/index.md) to learn about the best practices we follow at Better Software.

PS: Before you start working on the application, these [three git settings](https://spin.atomicobject.com/git-configurations-default/) are a must-have!
