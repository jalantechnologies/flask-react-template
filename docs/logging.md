# Logging

This document outlines the logging strategy for both backend and frontend applications.

The backend writes structured logs to stdout. The frontend reports to Datadog directly from the browser. To view collected logs, navigate to the [Datadog Logs Explorer](https://us5.datadoghq.com/logs).

## Configuration

### Backend Logging

The backend writes one JSON object per line to stdout and does nothing else. It does not open a connection to a log vendor, so logging costs the request path nothing.

Three settings control it, all under `logger` in `config/*.yml`:

| Config Key          | Default                | Description                                                                     |
| ------------------- | ---------------------- | ------------------------------------------------------------------------------- |
| `logger.level`      | `info`                 | Minimum level to emit. `development.yml` sets `debug`; deployed envs use `info` |
| `logger.service`    | `flask-react-template` | Service name stamped on every line                                              |
| `logger.transports` | `['console']`          | Where lines go. `console` (stdout) is the only transport                        |

Each line carries `timestamp`, `message`, `status`, `level`, `logger`, `service`, and `environment`, plus `error` when an exception is logged. Trace correlation ids (`dd.trace_id`, `dd.span_id`) are included when a tracer has put them on the record.

```json
{
  "timestamp": "2026-08-22T09:31:04.512331+00:00",
  "message": "Started background job",
  "status": "info",
  "level": "INFO",
  "logger": "modules.logger.internal.console_logger",
  "service": "flask-react-template",
  "environment": "production"
}
```

Gunicorn's access and error logs use the same formatter, so every line the container emits is one JSON object.

**Required Doppler secrets:** none. See [Backend Logging](secrets.md#backend-logging) for the optional overrides.

### Collecting backend logs

Getting these lines off the container is a deployment concern, not an application concern. The usual answer is an agent that tails container output and forwards it: the Datadog Agent with `containerCollectAll` enabled on the cluster, or any equivalent collector your platform provides. Configure it once per environment. Nothing in the application changes when you switch collectors.

This is the standard approach for containerised apps. The application stays fast and stays unaware of where its logs end up, and a log line is never lost because a vendor API was slow or down.

### Frontend Logging

Frontend Datadog RUM and browser logs are controlled by the `public.datadog.enabled` configuration flag. When set to `'true'`, the frontend initializes Datadog's browser SDK.

**Required Doppler secrets:** See [Frontend Datadog RUM & Browser Logs](secrets.md#frontend-datadog-rum--browser-logs) in the secrets documentation.

**Important:** Frontend public configuration (including Datadog RUM settings) is served at runtime from `/config.js` by the Flask app. After changing Doppler or environment values, redeploy the backend (or restart the process) so clients load the updated script; a separate frontend image rebuild is not required for `public` config changes.

## Backend Logging (Python)

Import the unified wrapper and log at the desired level:

```python
from modules.logger.logger import Logger

# Example usage
item_id = 123
payload = {"key": "value"}

Logger.info(message="Started background job")
Logger.debug(message=f"Payload received: {payload}")
Logger.error(message=f"Failed to process item {item_id}")
```

---

## Frontend Logging (JavaScript)

| Tool           | Purpose                               | Docs                                                                               |
| -------------- | ------------------------------------- | ---------------------------------------------------------------------------------- |
| Datadog Logger | Captures console & custom logs.       | [JS log collection ↗](https://docs.datadoghq.com/logs/log_collection/javascript/) |
| Datadog RUM    | Real-user monitoring & custom events. | [Browser RUM ↗](https://docs.datadoghq.com/real_user_monitoring/browser/)         |

### Usage Notes

- Both `console.*` and any custom logger integrations are forwarded to Datadog when logging is enabled.
- RUM auto-collects page views, errors, and performance metrics. Emit custom events for business-specific insights.

### Usage Example

```typescript jsx
import React, { useEffect } from 'react';
import { Logger } from './utils/logger';

Logger.init();

export default function App(): React.ReactElement {
  Logger.info("This is a logger info message");
  console.log("This is a console log"); // can also be captured by Datadog

  return (
    <div>
      <h1>Sample App</h1>
      {/* Your components go here */}
    </div>
  );
}
```
