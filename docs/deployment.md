# Temporal Deployment

We deploy **Temporal** using a Kubernetes-native setup to enable scalable, isolated background job execution for both preview and production environments.

---

## Key Details

### Per PR (Preview) Deployment

Each pull request triggers a temporary, isolated environment with:

- **Two Pods**:
  1. **WebApp Pod** – Runs:
     - React frontend
     - Flask backend
  2. **Temporal Pod** – Runs:
     - `python-worker` (via `temporal_server.py`)
     - `temporal-server`
     - `temporal-ui` (dashboard)

This ensures every PR runs its own background job workers independently of other deployments.

### Database

- A **PostgresSQL** database is shared across preview environments.
- Production uses a **dedicated** database.
- All credentials are securely managed via [Doppler](https://www.doppler.com/).

### Access Control

| Service           | Access Scope            |
|-------------------|-------------------------|
| `temporal-server` | Internal-only           |
| `temporal-ui`     | Public (preview + prod) |

### Temporal Server Address Resolution

- The environment variable `TEMPORAL_SERVER_ADDRESS` is dynamically resolved:
  - If **set in Doppler** → it uses that.
  - If **not set** → fallback to PR-specific or production address.

---

## Architecture Diagram

```
                ┌─────────────────────────────┐
                │    GitHub PR (Preview URL)  │
                │   e.g., pr-123.example.com  │
                └─────────────┬───────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         │       Kubernetes Namespace (pr-123)     │
         └────────────────────┬────────────────────┘
                              |
                              │
                              │
                              │
   ┌────────────────────────────────────────────────────────────┐
   │                        Preview Pods                        │
   │                                                            │
   │            ┌───────────────────────────────┐               │
   │            │        WebApp Pod             │               │
   │            │  - React Frontend             │               │
   │            │  - Flask Backend              │               │
   │            └───────────────────────────────┘               │
   │                                                            │
   │      ┌──────────────────────────────────────────┐          │
   │      │         Temporal Services Pod            │          │
   │      │  -  python-worker (temporal_server.py)   │          │
   │      │  -  temporal-ui (Externally Exposed)     │          │
   │      │  -  temporal-server                      │          │
   │      └──────────────────────────────────────────┘          │
   │                                                            │
   └────────────────────────────────────────────────────────────┘
```

> Notes:
> - WebApp and Temporal services are separated for better scalability.
> - Docker networking is used for communication inside the Temporal pod.

📚 Learn more: [Temporal Deployment Docs](https://docs.temporal.io/application-development/foundations/deployment)

---

# CI/CD Pipeline

This project uses **GitHub Actions** for continuous integration and deployment on **Kubernetes**, using workflows defined in [github-ci](https://github.com/jalantechnologies/github-ci).

---

## CI/CD Pipeline Structure

When you open or update a pull request, CI and CD workflows run independently:

```mermaid
graph TB
    Start([PR Opened/Updated])

    Start --> CI[CI Workflow<br/>Code Quality & Testing]
    Start --> CD[CD Workflow<br/>Build & Deploy]

    CI --> Lint[ci/lint<br/>~30s]
    CI --> Sonar[ci/sonarqube<br/>~60s]
    CI --> Review[ci/review<br/>~90s]
    CI --> Test[ci/test<br/>~1 min]

    CD --> Deploy[cd/deploy<br/>~3-4 min<br/>builds + deploys]

    Lint --> End([Complete])
    Sonar --> End
    Review --> End
    Test --> End
    Deploy --> End

    style CI fill:#e1f5ff
    style CD fill:#fff4e1
    style Deploy fill:#d4edda
```

### CI Workflow (Code Quality & Testing)
All jobs run in parallel and independently:

1. **ci/lint** (~30s) - ESLint and Markdown checks for code style and potential errors
2. **ci/sonarqube** (~60s) - Code quality metrics, complexity, and code smells
3. **ci/review** (~90s) - Automated code review (placeholder for future AI-powered review)
4. **ci/test** (~1 min) - Integration tests using docker-compose

### CD Workflow (Build & Deploy)
Single job that builds Docker image and deploys:

1. **cd/deploy** (~3-4 min) - Builds Docker image and deploys to `{pr-name}.preview.platform.bettrhq.com`

**Note:** All CI checks are advisory and run independently. CD deploys regardless of CI status to enable fast iteration. Code merged to `main` should have passing CI checks from the PR.

---

## Deployment Workflows

### CD Workflows
- **cd** - Deploys preview environment for each PR (`cd/deploy`)
- **cd_production** - Deploys to production when code is merged to `main` (`cd_production/deploy`)
- **cd_permanent_preview** - Updates permanent preview when `main` changes (`cd_permanent_preview/deploy`)

### Cleanup Workflows
- **cleanup_pr** - Automatically removes preview environment when PR is closed

All credentials and secrets are securely managed via GitHub secrets and environment variables. Deployments use github-ci v3.2.5 reusable workflows for Docker image building and Kubernetes deployment.
