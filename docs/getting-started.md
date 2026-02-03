# Getting Started

## Prerequisites

| Dependency | Version | Notes                                                                   |
|------------|---------|-------------------------------------------------------------------------|
| **Python** | 3.11    | —                                                                       |
| **Node**   | 22.13.1 | [Download](https://nodejs.org/download/release/v22.13.1/)               |
| **MongoDB**| 8.x     | [Installation guide](https://www.mongodb.com/docs/manual/installation/) |
| **Redis**  | 7.x     | [Installation guide](https://redis.io/docs/install/install-redis/)     |

## Quickstart

This project can run either in **Docker** or **locally with Node**. Choose whichever fits your workflow.

---

# Running the App

### 1. With Docker Compose

```bash
# Build (optional) and start everything
docker compose -f docker-compose.dev.yml up --build
```

* The full stack (frontend, backend, MongoDB, Redis, Celery workers) starts in hot‑reload mode.
* Once the containers are healthy, your browser should open automatically at **http://localhost:3000**.
  If it doesn't, visit the URL manually.  

### 2. Locally (npm run serve)

```bash
# Install JS deps
npm install

# Install Python deps
pipenv install --dev

# Start Redis (in separate terminal)
redis-server

# Start dev servers (frontend + backend + workers)
npm run serve
```

* **Frontend:** http://localhost:3000
* **Backend:**  http://localhost:8080
* **MongoDB:**  `mongodb://localhost:27017`
* **Redis:**    `localhost:6379`
* Disable the auto‑opening browser tab by exporting `WEBPACK_DEV_DISABLE_OPEN=true`.
* **Windows users:** run inside WSL or Git Bash for best results.
* **Note:** `npm run serve` starts frontend, backend, Celery worker, Celery beat scheduler, and Flower dashboard.

---

# Scripts

| Script                 | Purpose                                                                  |
|------------------------|--------------------------------------------------------------------------|
| `npm install`          | Install JavaScript/TypeScript dependencies.                              |
| `pipenv install --dev` | Install Python dependencies.                                             |
| `npm run build`        | Production build (no hot reload).                                        |
| `npm start`            | Start the built app.                                                     |
| `npm run serve`        | Dev mode with hot reload (frontend, backend, workers, beat scheduler).   |
| `npm run serve:worker` | Start Celery worker only.                                                |
| `npm run serve:beat`   | Start Celery beat scheduler only.                                        |
| `npm run serve:flower` | Start Flower dashboard (worker monitoring UI at `localhost:5555`).       |
| `npm run lint`         | Lint all code.                                                           |
| `npm run fmt`          | Auto‑format code.                                                        |

---

# Bonus Tips

* **Hot Reload:** Both frontend and backend restart automatically on code changes.
* **Mongo CLI access:** connect with `mongodb://localhost:27017`.
* **Redis CLI access:** run `redis-cli` to connect to Redis.
* **Background Jobs:** Workers process async jobs automatically. See [Workers documentation](workers.md) for details.
* **Worker Monitoring:** Use Flower dashboard (`npm run serve:flower`) to monitor workers, tasks, and queues at `http://localhost:5555`.
