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
   - **preview** – Preview environment configuration.
   - **production** – Production environment configuration.

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
  regions:
    __name: 'DEMO_REGIONS'
    __format: 'list'
```

| Doppler Secret | Overrides Config Key     | Notes                                       |
| -------------- | ------------------------ | ------------------------------------------- |
| `MONGODB_URI`  | `mongodb.uri`            | String value                                |
| `DEMO_HOST`    | `demo.host`              | String value                                |
| `DEMO_PORT`    | `demo.port` (as number)  | Cast to number via `__format: number`       |
| `DEMO_REGIONS` | `demo.regions` (as list) | Comma separated, split via `__format: list` |

Supported `__format` values are `boolean`, `number`, and `list`. A `list` value is split on commas with
surrounding whitespace trimmed and empty entries dropped, so `a, b ,` becomes `['a', 'b']`.

_Empty or unset secrets are ignored and fallback to the value defined in the corresponding YAML config._

---

## Best Practices

- **Never** commit secrets to the repository.
- **production** secrets should be tightly controlled.
- Remove deprecated keys promptly to avoid confusion.
- If you add a new mapping in `custom-environment-variables.yml`, remember to create the matching secret in Doppler for every active environment.

---

## Required Secrets by Category

### Backend Authentication

Required in **every deployed environment** (preview, production). This key signs and verifies JWT access tokens. `default.yml` ships no value, so deployed environments resolve it only from this secret. Use a high-entropy random value that is unique per environment; the app refuses to boot when it is missing or left at a placeholder.

| Doppler Secret                     | Config Key                         | Description                                                |
| ---------------------------------- | ---------------------------------- | ---------------------------------------------------------- |
| `ACCOUNTS_TOKEN_SIGNING_KEY`       | `accounts.token_signing_key`       | High-entropy JWT signing key, unique per env               |
| `ACCOUNTS_TOKEN_VERIFICATION_KEYS` | `accounts.token_verification_keys` | Optional comma separated list of older keys still accepted |

#### Rotating the JWT signing key

Tokens are signed with `ACCOUNTS_TOKEN_SIGNING_KEY` only, but they are verified against that key plus
every key listed in `ACCOUNTS_TOKEN_VERIFICATION_KEYS`. That split is what makes rotation possible
without logging everyone out: tokens issued under the previous key keep working until they expire on
their own.

Rotate one environment at a time:

1. Generate a new high-entropy key, for example `openssl rand -base64 48`.
2. Set `ACCOUNTS_TOKEN_VERIFICATION_KEYS` to the key currently in `ACCOUNTS_TOKEN_SIGNING_KEY`. If the
   variable already holds keys from an earlier rotation, prepend the current one to the list.
3. Set `ACCOUNTS_TOKEN_SIGNING_KEY` to the new key.
4. Deploy. New logins are signed with the new key; existing sessions still verify against the old one.
5. Wait longer than `accounts.token_expiry_days` (one day by default) so every token signed with the old
   key has expired.
6. Remove the old key from `ACCOUNTS_TOKEN_VERIFICATION_KEYS` and deploy again.

Steps 2 and 3 belong in the same deploy. Swapping the signing key without first moving the old key into
the verification list invalidates every live session immediately.

Both variables are read at boot, so a running process keeps its old values until it restarts. The
verification list is a fallback for rotation, not a place to park keys permanently: a leaked key stays
usable for as long as it is listed, so complete step 6 rather than leaving the list to grow.

### Backend Datadog Logging

Required for backend log forwarding to Datadog (when `logger.transports` includes `'datadog'`):

| Doppler Secret      | Config Key          | Description                          |
| ------------------- | ------------------- | ------------------------------------ |
| `DATADOG_API_KEY`   | `datadog.api_key`   | Datadog API key for backend logging  |
| `DATADOG_SITE_NAME` | `datadog.site_name` | Datadog site (e.g., `datadoghq.com`) |
| `DATADOG_APP_NAME`  | `datadog.app_name`  | Application name in Datadog          |
| `DATADOG_LOG_LEVEL` | `datadog.log_level` | Log level (e.g., `info`, `debug`)    |

### Frontend Datadog RUM & Browser Logs

Required for frontend Real User Monitoring and browser log collection (when `public.datadog.enabled: 'true'`):

| Doppler Secret                       | Config Key                               | Description                                |
| ------------------------------------ | ---------------------------------------- | ------------------------------------------ |
| `DATADOG_CLIENT_TOKEN`               | `public.datadog.clientToken`             | Datadog client token for browser SDK       |
| `DATADOG_APPLICATION_ID`             | `public.datadog.applicationId`           | RUM application ID                         |
| `DATADOG_ENABLED`                    | `public.datadog.enabled`                 | Enable/disable frontend Datadog (`'true'`) |
| `DATADOG_ENV`                        | `public.datadog.env`                     | Environment name (e.g., `production`)      |
| `DATADOG_SERVICE`                    | `public.datadog.service`                 | Service name for frontend                  |
| `DATADOG_SESSION_SAMPLE_RATE`        | `public.datadog.sessionSampleRate`       | Session sampling rate (0-100)              |
| `DATADOG_SESSION_REPLAY_SAMPLE_RATE` | `public.datadog.sessionReplaySampleRate` | Session replay sampling rate (0-100)       |
| `DATADOG_SITE_NAME`                  | `public.datadog.site`                    | Datadog site (e.g., `us5.datadoghq.com`)   |

**Note:** Frontend public config is exposed at **runtime** via `/config.js` (see `serve_config` in `bin/blueprints.py`). Redeploy or restart the backend after changing these secrets so browsers receive the updated values.
