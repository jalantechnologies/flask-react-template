# Getting Started

## Prerequisites

| Dependency       | Version | Notes                                                                                                |
|------------------|---------|------------------------------------------------------------------------------------------------------|
| **Python**       | 3.11    | —                                                                                                    |
| **Node**         | 22.13.1 | [Download](https://nodejs.org/download/release/v22.13.1/)                                            |
| **MongoDB**      | 8.x     | [Installation guide](https://www.mongodb.com/docs/manual/installation/)                              |
| **Temporal CLI** | —       | Only required for distributed‑workflow support. Skip if you’ll run `npm run serve -- --no-temporal`. |

## Quickstart

This project can run either in **Docker** or **locally with Node**. Choose whichever fits your workflow.

---

# Running the App

1. **Install Docker Desktop**  
   [Official Installation Guide](https://docs.docker.com/desktop/install/windows-install/)

2. **Start Docker Desktop**  
   Wait until the **Docker Engine** is running — the whale icon in the system tray should indicate it’s active.

3. **Run the Application Stack**
   ```bash
   # start everything
   docker compose -f docker-compose.dev.yml up --build
   wait for 7-10 minutes to start all services 

   The full stack (frontend, backend, MongoDB, Temporal, etc.) starts in hot-reload mode.
   Once the containers are healthy, your browser should open automatically at http://localhost:3000.If it doesn’t, visit the URL manually.

### 2. Running on Linux (npm run serve)

```bash
# Install JS deps
npm install

# Install Python deps
pipenv install --dev

# Start dev servers (frontend + backend + Temporal)
npm run serve

# └─ Flags
#    --no-temporal   # skip starting Temporal service
# Example: npm run serve -- --no-temporal
```

* **Frontend:** http://localhost:3000  
* **Backend:**  http://localhost:8080  
* **MongoDB:**  `mongodb://localhost:27017`  
* Disable the auto‑opening browser tab by exporting `WEBPACK_DEV_DISABLE_OPEN=true`.  

---

# Scripts

| Script                 | Purpose                                                          |
|------------------------|------------------------------------------------------------------|
| `npm install`          | Install JavaScript/TypeScript dependencies.                      |
| `pipenv install --dev` | Install Python dependencies.                                     |
| `npm run build`        | Production build (no hot reload).                                |
| `npm start`            | Start the built app.                                             |
| `npm run serve`        | Dev mode with hot reload (plus Temporal unless `--no-temporal`). |
| `npm run lint`         | Lint all code.                                                   |
| `npm run fmt`          | Auto‑format code.                                                |

---

# Bonus Tips

* **Hot Reload:** Both frontend and backend restart automatically on code changes.  
* **Mongo CLI access:** connect with `mongodb://localhost:27017`.  
* **Temporal omitted?** Running `npm run serve -- --no-temporal` skips Temporal so you can develop without distributed workflows.

