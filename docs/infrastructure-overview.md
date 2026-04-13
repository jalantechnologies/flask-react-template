# Infrastructure Overview

This document gives a high-level picture of the infrastructure stack used by this template — what tools are in play, how the environments are structured, and how everything fits together. It is intended for developers joining the team or anyone bootstrapping a new project from this template.

For a full walkthrough, watch the video below.

[Watch: Infrastructure Tools Overview](https://www.loom.com/share/e27854a744884a6e83d12df43d948dff)

---

## Core Tools

| Tool               | Role                                                                     |
| ------------------ | ------------------------------------------------------------------------ |
| **Kubernetes**     | Container orchestration — runs all workloads across environments         |
| **Docker**         | Packages the application into a single image used for all environments   |
| **GitHub Actions** | CI/CD pipelines — runs tests, linting, and deploys on every PR and merge |
| **MongoDB**        | Primary database, shared across environments                             |
| **Redis**          | Message broker for Celery background workers                             |
| **Celery**         | Async task queue and scheduler (beat) for background jobs                |
| **Doppler**        | Secrets and environment variable management                              |
| **nginx ingress**  | Routes external traffic into the cluster                                 |
| **cert-manager**   | Automates SSL certificate issuance via Let's Encrypt                     |

---

## Deployment Environments

The template ships with three environments out of the box:

| Environment           | Trigger                        | URL Pattern                                 |
| --------------------- | ------------------------------ | ------------------------------------------- |
| **Preview (per PR)**  | Every pull request open/update | `<github_sha>.preview.platform.bettrhq.com` |
| **Permanent Preview** | Every merge to `main`          | `preview.<app>.<domain>`                    |
| **Production**        | Manual or on merge to `main`   | `<app>.<domain>`                            |

Each preview environment is **fully isolated** — its own WebApp pod, Worker pod, and Redis pod — and is torn down automatically when the PR is closed.

See [Deployment Architecture](deployment.md) for pod structure, worker scaling, and resource allocation details.

---

## CI/CD Pipeline

Every pull request triggers two independent workflow groups via **GitHub Actions**:

- **CI** — runs lint, SonarQube analysis, automated code review, and integration tests in parallel
- **CD** — builds the Docker image and deploys to the PR's preview environment (~3–4 min)

Merging to `main` triggers production and permanent-preview deployments automatically.

See [Deployment Architecture](deployment.md) for the full pipeline diagram and workflow descriptions.

---

## Secrets Management

All credentials (database URIs, API keys, third-party tokens) are stored and synced via **Doppler**. No secrets are committed to the repository. See [Secrets](secrets.md) for setup instructions.

---

## DNS & SSL

Each environment is served over HTTPS. DNS records must point to the cluster's nginx ingress LoadBalancer IP, and cert-manager handles certificate issuance automatically via ACME HTTP-01 challenges.

See [DNS Setup](dns-setup.md) for the required records and troubleshooting steps.

---

## Creating a New Project from the Template

The following video walks through how to bootstrap a new project using this template — from repository creation through first deployment.

[Watch: Creating a New Project from flask-react-template](https://www.loom.com/share/82771b5c1f2144039a737b61c9a81c45)

For the step-by-step written guide, see [Getting Started](getting-started.md).
