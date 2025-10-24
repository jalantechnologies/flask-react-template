/* eslint-disable no-console */
import { datadogLogs, LogsInitConfiguration } from '@datadog/browser-logs';
import {
  datadogRum,
  DefaultPrivacyLevel,
  RumInitConfiguration,
} from '@datadog/browser-rum';
import { reactPlugin } from '@datadog/browser-rum-react';

import getConfigValue from 'frontend/helpers/config';
import { DatadogUser } from 'frontend/types';

export class Logger {
  public static init() {
    if (this.isDatadogEnabled()) {
      this.initLogger();
      this.initRum();
    }
  }

  public static info(message: string, context?: Record<string, unknown>) {
    if (this.isDatadogEnabled()) {
      datadogLogs.logger.info(message, context);
    } else {
      console.info(message, context);
    }
  }

  public static warn(message: string, context?: Record<string, unknown>) {
    if (this.isDatadogEnabled()) {
      datadogLogs.logger.warn(message, context);
    } else {
      console.warn(message, context);
    }
  }

  public static error(message: string, context?: Record<string, unknown>) {
    if (this.isDatadogEnabled()) {
      datadogLogs.logger.error(message, context);
    } else {
      console.error(message, context);
    }
  }

  public static debug(message: string, context?: Record<string, unknown>) {
    if (this.isDatadogEnabled()) {
      datadogLogs.logger.debug(message, context);
    } else {
      console.debug(message, context);
    }
  }

  public static setRumUser(user: DatadogUser) {
    if (this.isDatadogEnabled()) {
      datadogRum.setUser(user);
    }
  }

  public static setLogAccount(user: DatadogUser) {
    if (this.isDatadogEnabled()) {
      datadogLogs.setAccount(user);
    }
  }

  private static isDatadogEnabled(): boolean {
    return getConfigValue('datadog.enabled') === 'true';
  }

  private static initLogger() {
    const datadogLogsConfig: LogsInitConfiguration = {
      clientToken: getConfigValue('datadog.clientToken') as string,
      site: getConfigValue('datadog.site') as RumInitConfiguration['site'],
      service: getConfigValue('datadog.service') as string,
      env: getConfigValue('datadog.env') as string,
      sessionSampleRate: parseInt(
        getConfigValue('datadog.sessionSampleRate') as string,
        10,
      ),
      forwardConsoleLogs: 'all',
    };

    datadogLogs.init(datadogLogsConfig);
  }

  private static initRum() {
    const dataDogConfig: RumInitConfiguration = {
      applicationId: getConfigValue('datadog.applicationId') as string,
      clientToken: getConfigValue('datadog.clientToken') as string,
      site: getConfigValue('datadog.site') as RumInitConfiguration['site'],
      service: getConfigValue('datadog.service') as string,
      env: getConfigValue('datadog.env') as string,
      sessionSampleRate: parseInt(
        getConfigValue('datadog.sessionSampleRate') as string,
        10,
      ),
      sessionReplaySampleRate: parseInt(
        getConfigValue('datadog.sessionReplaySampleRate') as string,
        10,
      ),
      defaultPrivacyLevel: DefaultPrivacyLevel.MASK_USER_INPUT,
      trackUserInteractions: true,
      trackResources: true,
      trackAnonymousUser: true,
      trackLongTasks: true,
      enablePrivacyForActionName: true,
      plugins: [reactPlugin({ router: true })],
      trackViewsManually: false,
    };

    datadogRum.init(dataDogConfig);
    datadogRum.startSessionReplayRecording();
  }
}
