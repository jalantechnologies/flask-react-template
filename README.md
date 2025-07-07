# Boilerplate - FRM

Boilerplate project for Flask, React & MongoDB based projects. This README documents the steps necessary to get your
application up and running.

## Badge Reports

| Build Status | Code Coverage |
| ------------ | ------------- |
| [![Production Deploy](https://github.com/jalantechnologies/rflask-boilerplate/actions/workflows/production_on_push.yml/badge.svg?branch=main)](https://github.com/jalantechnologies/rflask-boilerplate/actions/workflows/production_on_push.yml) | [![Code Coverage](https://sonarqube.platform.jalantechnologies.com/api/project_badges/measure?project=jalantechnologies_rflask-boilerplate&metric=coverage&token=a4dd71c68afbb8da4b7ed1026329bf0933298f79)](https://sonarqube.platform.jalantechnologies.com/dashboard?id=jalantechnologies_rflask-boilerplate) |

## Table of Contents

- [Boilerplate - FRM](#boilerplate---frm)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
  - [Frontend Logging](#frontend-logging)
  - [Configuration](#configuration)
  - [Custom Environment Variables](#custom-environment-variables)
  - [Scripts](#scripts)
  - [Workers](#workers)
  - [Temporal Deployment](#temporal-deployment)
  - [Deployment](#deployment)

## Getting Started

**Quickstart:**

- This project supports running the application with all the required dependencies using `docker compose`.
- Install [docker](https://docs.docker.com/engine/install/).
- Run `docker compose -f docker-compose.dev.yml up` (Add `--build` to force rebuild when new dependencies have been
  added).
- The application should open up automatically. If it doesn't, go to `http://localhost:3000`.
- Make required changes for development. Both backend and frontend should hot reload, and server restart is not
  required.

**Bonus:**

- On running `serve`, the frontend server is at `http://localhost:3000`.
- On running `serve`, the backend server is at `http://localhost:8080`.
- To connect to MongoDB server using a client, use `mongodb://localhost:27017`.

**Pre Requirements:**

- Python (v3.11)
- Node (v22.13.1) - [Download](https://nodejs.org/download/release/v22.13.1/)
- MongoDB (v5) - [Download](https://www.mongodb.com/docs/manual/installation/)
- Temporal CLI - [Download](https://learn.temporal.io/getting_started/typescript/dev_environment/#set-up-a-local-temporal-service-for-development-with-temporal-cli)  
  _Note: Temporal CLI is only required if you intend to use distributed workflows. If you run `npm run serve -- --no-temporal`, you can skip installing Temporal CLI, but distributed workflow features will not be available._

**Scripts:**

- Install dependencies - `npm install`
- Install Python dependencies - `pipenv install --dev`
- Build Project - `npm run build`
- Start Application (without HotReload) - `npm start`
- Start Application (with HotReload enabled) - `npm run serve`
  - To disable opening up the browser automatically, set `WEBPACK_DEV_DISABLE_OPEN` to `true`.
  - To disable starting the Temporal server, use the flag `-- --no-temporal` (e.g., `npm run serve -- --no-temporal`).
  - **Note for Windows users:** You will need to use either [WSL (Windows Subsystem for Linux)](https://learn.microsoft.com/en-us/windows/wsl/install) or Git Bash to run this command successfully.
- Lint Check - `npm run lint`
- Format Code - `npm run fmt`

## Frontend Logging

For frontend logging, we use **Datadog Logger** ([docs](https://docs.datadoghq.com/logs/log_collection/javascript/)) and **Datadog RUM** (Real User Monitoring) ([docs](https://docs.datadoghq.com/real_user_monitoring/browser/)). Both are critical for monitoring and observability.

- **Datadog Logger**: Captures and forwards frontend logs to Datadog. See the [JavaScript log collection documentation](https://docs.datadoghq.com/logs/log_collection/javascript/) for setup and usage.
- **Datadog RUM**: Automatically collects basic metrics (such as page views, errors, and performance data) and can also be used to send custom events for advanced monitoring. Refer to the [Browser RUM documentation](https://docs.datadoghq.com/real_user_monitoring/browser/) for more details.

**Usage Notes:**

- Both `console` and `Logger` methods are integrated to send logs to Datadog if logging is enabled.
- Datadog RUM is set up to automatically collect essential metrics, but you can also use it to send custom events as needed for your application.

## Configuration

In the `config` directory, we maintain environment-specific YAML files to manage application configurations.

### Configuration Files

- **`custom-environment-variables.yml`** – Overrides values using environment variables.
- **`development.yml`** – Configuration for the development environment (default).
- **`testing.yml`** – Configuration for the testing environment (`APP_ENV` must be set to `testing`).
- **`preview.yml`** – Configuration for the preview environment (`APP_ENV` must be set to `preview`).
- **`production.yml`** – Configuration for the production environment (`APP_ENV` must be set to `production`).
- **`default.yml`** – Stores constant values that remain unchanged across deployments.

### Environment Selection

The configuration schema is loaded based on the `APP_ENV` value provided when starting the server:
`APP_ENV=<environment_name>`

### `default.yml` Guidelines

- If a configuration value **varies across deployments**, set it to `null` in `default.yml` and define it in the respective environment-specific file.
- If a configuration value **remains the same across all deployments**, define it directly in `default.yml`.

### `.env` Support

For injecting environment variables, you can add a `.env` file in the application root directory.

## Custom Environment Variables

Some deployment scenarios require environment variables for handling sensitive data or settings that should not be stored in the codebase.

To facilitate this, we use `custom-environment-variables.yml` to map environment variables to configuration keys.

### Example Mapping:

```yaml
mongodb:
  uri: 'MONGODB_URI'

inspectlet:
  key: 'INSPECTLET_KEY'

demo:
  host: 'DEMO_HOST'
  port:
    __name: 'DEMO_PORT'
    __format: 'number'
```

#### Behavior:

- If the environment variable `MONGODB_URI` exists, it will override `mongodb.uri`.
- If `INSPECTLET_KEY` is present, it will override `inspectlet.key`.
- `DEMO_PORT` will be converted to a number before overriding `demo.port`.
- Empty environment variables are ignored and do not affect the configuration.

### Available `__format` Types:

- `boolean`
- `number`

### Configuration Precedence:

1. **Custom Environment Variables** (highest priority)
2. **Environment-Specific Configuration Files** (e.g., `development.yml`, `production.yml`)
3. **`default.yml`** (lowest priority, used as fallback)

**UI Config:**

In case of need of config values at client-side, this will make an internal request to the backend server to get the
desired config schema in the form of JSON.

## Scripts

This application also supports running one off scripts. Helpful during development or running cron jobs.

Steps:

- Create a python file under - `src/apps/backend/scripts` (ex - `my-script.py`)
- Run the script using npm - `npm run script --file=example_worker_script`

## Test User Account for Development & Preview

To improve developer experience, this boilerplate can automatically create a test user account on app startup in development and preview environments. This allows you to log in immediately without manual setup.

**How it works:**
- On startup, if the environment is `development` or `preview`, the backend checks config for the `account.create_test_user_account` flag.
- If enabled and the test user does not already exist, it creates a user with credentials from config.

**Default credentials:**
- Development: `dev@example.com` / `devpassword`
- Preview: `preview@example.com` / `previewpassword`
- (You can change these in `config/development.yml` and `config/preview.yml`)

**To disable:**
- Set `account.create_test_user_account: false` in your environment's config file.

**To customize:**
- Edit the `account.test_user` section in your config file to set your own test user credentials.

**Production:**
- This feature is disabled by default in production and will not run unless explicitly enabled in config.

## Code Formatting

To ensure consistent code style across the project, both backend and test Python files are automatically formatted using autoflake, isort, and black.

- To format all Python files (backend and tests), run:
  ```sh
  npm run fmt:py
  ```
- Pre-commit hooks (via lint-staged) will also auto-format any staged Python files before commit.

Test files have their own formatting configuration in `tests/pyproject.toml`.

For JavaScript/TypeScript files, Prettier is used and can be run with:
  ```sh
  npm run fmt:ts
  ```

## Github Badges Configuration
This project displays GitHub badges for SonarQube code coverage and the `production_on_push` workflow status, both referencing the `main` branch of the [`rflask-boilerplate`](https://github.com/jalantechnologies/rflask-boilerplate) repository. If you fork or host this project in a different GitHub repository, update the badge URLs to point to your repository to ensure accurate status and coverage reporting.

## Workers

This application supports queuing workers from the web application which are run independent of the web server by [Temporal](https://temporal.io/).

You can define workers in any module, preferably in a `/workers` directory. A worker needs to inherit from [`BaseWorker`](src/apps/backend/modules/application/types.py) and have a `run()` method.
You can use the `HealthCheckWorker` inside the `application` module as a reference.

```python
from typing import Any
from modules.application.types import BaseWorker
class ExampleWorker(BaseWorker):
    async def execute(self, *args: Any) -> None:
        # Your worker logic here
        ...

    async def run(self, *args: Any) -> None:
        await super().run(*args)
```

Optionally, you can specify the following parameters in the worker class:

1. `max_execution_time_in_seconds` - The time in seconds to wait for the worker to finish its execution. If the worker does not finish within this time, it will be cancelled.
2. `max_retries` - The maximum number of times the worker will be retried in case of failure. If the worker fails more than this number of times, it will be marked as failed and will not be retried again.

Once a worker is defined, it needs to be imported in the [`temporal_config.py`](src/apps/backend/temporal_config.py) and added to the `WORKERS` list.

Hereafter, the system will take care of registering the worker with the Temporal server.

The `ApplicationService` exposes various methods to interact with the workers:

- `get_worker_by_id` - Get a worker by its ID
- `run_worker_immediately` - Run a one-off worker immediately
- `schedule_worker_as_cron` - Schedule a worker to run as a cron job (you need to pass a cron expression in the `cron_schedule` parameter, e.g., `*/10 * * * *` for every 10 minutes)
- `cancel_worker` - Cancel a worker by its ID; please remember that cancellation will ONLY work when you explicitly handle the `asyncio.CancelledError` exception in your worker's `run()` method
- `terminate_worker` - Terminate a worker immediately by its ID

NOTE: Please refer to the [Temporal Python SDK documentation](https://docs.temporal.io/develop/python/cancellation) for detailed information on cancellation vs termination.

## Temporal Deployment

We deploy Temporal in a Kubernetes-native architecture to support scalable background task processing.

### Key Details:

- **Per Preview Deployment**:

  - Each PR spawns **two pods**:
    - **WebApp Pod** – Runs the React frontend and Flask backend.
    - **Temporal Pod** – Runs:
      - `python-worker` (executes `temporal_server.py`)
      - `temporal-server`
      - `temporal-ui`
  - This ensures isolated, independent processing environments for each PR.

- **Database**:

  - A single PostgreSQL instance is used across all deployments.
  - **Preview pods** share one database.
  - **Production** uses a dedicated database.
  - All database config is managed securely using [Doppler](https://www.doppler.com/).

- **Access**:

  - `temporal-server` is internal-only (cluster-only access).
  - `temporal-ui` is exposed externally for both preview and production.

- **Server Address Resolution**:
  - `TEMPORAL_SERVER_ADDRESS` is injected from Doppler or resolved dynamically:
    - If set in Doppler → uses that value.
    - If not set → uses PR-specific (for preview) or production address.

### Architecture Diagram:

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
   │      │         Temporal Services Pod            |          │
   │      │  -  python-worker (temporal_server.py)   |          |
   │      │  -  temporal-ui (Externally Exposed)     │          │
   │      │  -  temporal-server                      │          │
   │      └──────────────────────────────────────────┘          │
   │                                                            │
   └────────────────────────────────────────────────────────────┘
```

Notes:

- WebApp and Temporal pods run in parallel.
- Internal Docker networking is used for inter-container communication in the Temporal Pod.

```

📚 More info: [Temporal Deployment Docs](https://docs.temporal.io/application-development/foundations/deployment)

## Deployment

This project deploys on Kubernetes via GitHub Actions using workflows defined in [GitHub CI](https://github.com/jalantechnologies/github-ci).

```
