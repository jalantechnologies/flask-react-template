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

### 1. With Docker Compose

```bash
# Build (optional) and start everything
docker compose -f docker-compose.dev.yml up --build
```

* The full stack (frontend, backend, MongoDB, Temporal, etc.) starts in hot‑reload mode.  
* Once the containers are healthy, your browser should open automatically at **http://localhost:3000**.  
  If it doesn’t, visit the URL manually.  

### 2. Locally (npm run serve)

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
* **Windows users:** run inside WSL or Git Bash for best results.

### Windows (WSL) Setup

Follow these steps to run the app on Windows using WSL (Windows Subsystem for Linux).

1. **Install WSL**
   - Open PowerShell as Administrator and run:

     ```powershell
     wsl --install
     ```

   - Restart your computer when prompted.

2. **Initial Ubuntu setup**
   - After restart, the first Ubuntu launch will initialize WSL and prompt you to create a Linux username and password.
   - If it doesn't initialize automatically, open the Start menu, search for "Ubuntu", and launch it to complete initialization.

3. **Open the project in VS Code**
   - Open the project folder in VS Code.

4. **Switch the VS Code terminal into Ubuntu (WSL)**
   - In the VS Code terminal, run:

     ```powershell
     wsl
     ```

   - If you have multiple distros (check with `wsl -l -v`), explicitly select Ubuntu:

     ```powershell
     wsl -d Ubuntu
     ```

   - You are now in the Ubuntu CLI inside your project folder.

5. **Install required packages (inside Ubuntu)**

   ```bash
   sudo apt update
   sudo apt install -y python3-pip
   sudo apt install -y pipenv
   sudo apt install -y jq
   ```

6. **Install project dependencies**

   ```bash
   npm install
   ```

7. **Install Python dependencies (development)**

   ```bash
   pipenv install --dev
   ```

8. **Activate Pipenv shell**

   ```bash
   pipenv shell
   ```

9. **Start dev mode with hot reload**

   ```bash
   npm run serve
   ```

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

