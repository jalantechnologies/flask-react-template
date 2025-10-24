import logging
import os
from logging import LogRecord, StreamHandler

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.models import HTTPLog, HTTPLogItem

from modules.config.config_service import ConfigService


class DatadogHandler(StreamHandler):
    def __init__(self, ddsource: str) -> None:
        StreamHandler.__init__(self)
        self.ddsource = ddsource

    def __get_status(self, record: LogRecord) -> str:
        if record.levelno in [logging.NOTSET, logging.DEBUG, logging.INFO]:
            return "info"
        elif record.levelno in [logging.WARNING]:
            return "warn"
        else:
            return "error"

    def emit(self, record: LogRecord) -> None:
        msg = self.format(record)
        datadog_api_key = ConfigService[str].get_value(key="datadog.api_key")
        datadog_host = ConfigService[str].get_value(key="datadog.site_name")
        data_app_name = ConfigService[str].get_value(key="datadog.app_name")
        config = Configuration()
        config.api_key["apiKeyAuth"] = datadog_api_key
        config.server_variables["site"] = datadog_host
        config.debug = True
        with ApiClient(config) as api_client:
            api_instance = LogsApi(api_client)
            body = HTTPLog(
                [
                    HTTPLogItem(
                        ddsource=self.ddsource,
                        ddtags=f"env : {os.environ.get('APP_NAME')}",
                        hostname="",
                        message=msg,
                        service=data_app_name,
                        status=self.__get_status(record=record),
                    )
                ]
            )

            api_instance.submit_log(body)
