# Configuration

In the `config` directory, we maintain environment-specific YAML files to manage application configurations.

## Configuration Files

- **`custom-environment-variables.yml`** – Overrides values using environment variables.
- **`development.yml`** – Configuration for the development environment (default).
- **`testing.yml`** – Configuration for the testing environment (`APP_ENV` must be set to `testing`).
- **`preview.yml`** – Configuration for the preview environment (`APP_ENV` must be set to `preview`).
- **`production.yml`** – Configuration for the production environment (`APP_ENV` must be set to `production`).
- **`default.yml`** – Stores constant values that remain unchanged across deployments.

## Environment Selection

The configuration schema is loaded based on the `APP_ENV` value provided when starting the server:
```bash
APP_ENV=<environment_name>
```

## `default.yml` guidelines

- If a configuration value **varies across deployments**, set it to `null` in `default.yml` and define it in the respective environment-specific file.
- If a configuration value **remains the same across all deployments**, define it directly in `default.yml`.

## `.env` support

For injecting environment variables, you can add a `.env` file in the application root directory.

# Custom Environment Variables

Some deployment scenarios require environment variables for handling sensitive data or settings that should not be stored in the codebase.

To facilitate this, we use `custom-environment-variables.yml` to map environment variables to configuration keys.

## Example Mapping

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

### Behavior

- If the environment variable `MONGODB_URI` exists, it will override `mongodb.uri`.
- If `INSPECTLET_KEY` is present, it will override `inspectlet.key`.
- `DEMO_PORT` will be converted to a number before overriding `demo.port`.
- Empty environment variables are ignored and do not affect the configuration.

## Available `__format` Types

- `boolean`
- `number`

## Configuration Precedence

1. **Custom Environment Variables** (highest priority)
2. **Environment-Specific Configuration Files** (e.g., `development.yml`, `production.yml`)
3. **`default.yml`** (lowest priority, used as fallback)
