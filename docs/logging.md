# Logging

This document outlines the logging strategy for both backend and frontend applications, utilizing Datadog for log management and monitoring.

To view the logs, navigate to the [Datadog Logs Explorer](https://us5.datadoghq.com/logs).

## Configuration

### Backend Logging

Backend Datadog logging is controlled by the `logger.transports` configuration. When `'datadog'` is included in the transports list, logs are forwarded to Datadog.

**Required Doppler secrets:** See [Backend Datadog Logging](secrets.md#backend-datadog-logging) in the secrets documentation.

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
