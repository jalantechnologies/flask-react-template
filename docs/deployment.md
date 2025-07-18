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

# Deployment Pipeline

Deployments are handled via **GitHub Actions** and [github-ci](https://github.com/jalantechnologies/github-ci).

- Preview deploys run per PR.
- Production deploys are triggered on merge to the main branch.
