# Managing Secrets with Doppler

We use **Doppler** as the single source of truth for sensitive configuration across environments.  
Secrets stored in Doppler are automatically injected into the app at runtime and mapped to configuration keys via `custom-environment-variables.yml`.

---

## Workflow

1. **Sign in to Doppler**  
   Log in at https://dashboard.doppler.com with the [Platform team's credentials](https://teams.microsoft.com/l/entity/1c256a65-83a6-4b5c-9ccf-78f8afb6f1e8/_djb2_msteams_prefix_384094637?context=%7B%22channelId%22%3A%2219%3A08e4a50edf634281a15e27fa7ca99fef%40thread.tacv2%22%7D&tenantId=79836b2a-53cc-4854-81b4-ba2d7c9f2726).

2. **Select the _flask-react-template_ project**  
   The `flask-react-template` project centralizes secrets for the full stack (frontend + backend).

3. **Choose an environment**
   - **preview** – Used by PR preview builds.
   - **production** – Live environment.

4. **Add or edit secrets**
   - Click **“Secrets”** → **“Add Secret”**.
   - Enter the key exactly as referenced in `custom-environment-variables.yml`.
   - Provide the value and save.

5. **Deploy**  
   The next deployment will pick up the new secret automatically.

---

## How Mapping Works

`custom-environment-variables.yml` maps a config path to an env-var name (the Doppler key).  
Example fragment:

```yaml
mongodb:
  uri: 'MONGODB_URI'

demo:
  host: 'DEMO_HOST'
  port:
    __name: 'DEMO_PORT'
    __format: 'number'
```

| Doppler Secret | Overrides Config Key    | Notes                                 |
| -------------- | ----------------------- | ------------------------------------- |
| `MONGODB_URI`  | `mongodb.uri`           | String value                          |
| `DEMO_HOST`    | `demo.host`             | String value                          |
| `DEMO_PORT`    | `demo.port` (as number) | Cast to number via `__format: number` |

_Empty or unset secrets are ignored and fallback to the value defined in the corresponding YAML config._

---

## Best Practices

- **Never** commit secrets to the repository.
- Use **preview** for testing; **production** secrets should be tightly controlled.
- Remove deprecated keys promptly to avoid confusion.
- If you add a new mapping in `custom-environment-variables.yml`, remember to create the matching secret in Doppler for every active environment.

---

## Required Secrets by Category

### Backend Datadog Logging

Required for backend log forwarding to Datadog (when `logger.transports` includes `'datadog'`):

| Doppler Secret       | Config Key           | Description                          |
| -------------------- | -------------------- | ------------------------------------ |
| `DATADOG_API_KEY`    | `datadog.api_key`    | Datadog API key for backend logging  |
| `DATADOG_SITE_NAME`  | `datadog.site_name`  | Datadog site (e.g., `datadoghq.com`) |
| `DATADOG_APP_NAME`   | `datadog.app_name`   | Application name in Datadog          |
| `DATADOG_LOG_LEVEL`  | `datadog.log_level`  | Log level (e.g., `info`, `debug`)    |

### Frontend Datadog RUM & Browser Logs

Required for frontend Real User Monitoring and browser log collection (when `public.datadog.enabled: 'true'`):

| Doppler Secret                       | Config Key                                | Description                                    |
| ------------------------------------ | ----------------------------------------- | ---------------------------------------------- |
| `DATADOG_CLIENT_TOKEN`               | `public.datadog.clientToken`              | Datadog client token for browser SDK           |
| `DATADOG_APPLICATION_ID`             | `public.datadog.applicationId`            | RUM application ID                             |
| `DATADOG_ENABLED`                    | `public.datadog.enabled`                  | Enable/disable frontend Datadog (`'true'`)     |
| `DATADOG_ENV`                        | `public.datadog.env`                      | Environment name (e.g., `production`)          |
| `DATADOG_SERVICE`                    | `public.datadog.service`                  | Service name for frontend                      |
| `DATADOG_SESSION_SAMPLE_RATE`        | `public.datadog.sessionSampleRate`        | Session sampling rate (0-100)                  |
| `DATADOG_SESSION_REPLAY_SAMPLE_RATE` | `public.datadog.sessionReplaySampleRate`  | Session replay sampling rate (0-100)           |
| `DATADOG_SITE_NAME`                  | `public.datadog.site`                     | Datadog site (e.g., `us5.datadoghq.com`)       |

**Note:** Frontend secrets are injected at **build time** via webpack's `DefinePlugin`. Changes require a rebuild and redeployment to take effect.
