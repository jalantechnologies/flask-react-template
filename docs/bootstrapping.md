## App Bootstrapping Script

The project includes a generic bootstrapping script to automate one-time setup tasks, such as seeding a test user or initial data.

### Purpose
- Runs one-time bootstrapping tasks when the app first boots up (e.g., seeding a test user, initial data, etc.).
- Extensible: add more bootstrapping tasks as needed.

### Location
```
src/apps/backend/scripts/bootstrap_app.py
```

### How It Runs
- On startup, if the environment is `development` or `preview`, the backend runs all tasks defined in `bootstrap_app.py` **if enabled by config**.
- Each task (such as seeding a test user) is implemented as a function and called from `run_bootstrap_tasks()`.
- The script is extensible—add more bootstrapping tasks as needed.

### Configuration
- Controlled by the `BOOTSTRAP_APP` config key (see `config/development.yml`, `config/preview.yml`, or your environment variables).
- If `BOOTSTRAP_APP: true`, the script runs on startup; if `false`, it is skipped.

### How to Run Manually
You can run the script directly for ad-hoc bootstrapping:

```bash
cd src/apps/backend && pipenv run python scripts/bootstrap_app.py
```

### Example Use-Case
- **Seeding a test user account** if `account.create_test_user_account` is enabled in config and the user does not already exist.
- Credentials are read from `account.test_user` in your environment config.

#### Example Config
```yaml

account:
  create_test_user_account: true
  test_user:
    first_name: "Dev"
    last_name: "User"
    username: "dev@example.com"
    password: "devpassword"
```

---
