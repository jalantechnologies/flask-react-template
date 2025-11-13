from dotenv import load_dotenv
from flask import Flask, jsonify
from flask.typing import ResponseReturnValue
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from bin.blueprints import api_blueprint, img_assets_blueprint, react_blueprint
from modules.account.rest_api.account_rest_api_server import AccountRestApiServer
from modules.application.application_service import ApplicationService
from modules.application.errors import AppError, WorkerClientConnectionError
from modules.application.workers.health_check_worker import HealthCheckWorker
from modules.authentication.rest_api.authentication_rest_api_server import AuthenticationRestApiServer
from modules.config.config_service import ConfigService
from modules.logger.logger import Logger
from modules.logger.logger_manager import LoggerManager
from modules.task.rest_api.task_rest_api_server import TaskRestApiServer
from scripts.bootstrap_app import BootstrapApp

load_dotenv()

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Mount deps
LoggerManager.mount_logger()

# Run bootstrap tasks
BootstrapApp().run()

# Connect to Temporal Server
try:
    ApplicationService.connect_temporal_server()

    # Start the health check worker
    # In production, it is optional to run this worker
    ApplicationService.schedule_worker_as_cron(cls=HealthCheckWorker, cron_schedule="*/10 * * * *")

except WorkerClientConnectionError as e:
    Logger.critical(message=e.message)


# Apply ProxyFix to interpret `X-Forwarded` headers if enabled in configuration
# Visit: https://flask.palletsprojects.com/en/stable/deploying/proxy_fix/ for more information
if ConfigService.has_value("is_server_running_behind_proxy") and ConfigService[bool].get_value(
    "is_server_running_behind_proxy"
):
    app.wsgi_app = ProxyFix(app.wsgi_app)  # type: ignore

# Register authentication apis
authentication_blueprint = AuthenticationRestApiServer.create()
api_blueprint.register_blueprint(authentication_blueprint)

# Register accounts apis
account_blueprint = AccountRestApiServer.create()
api_blueprint.register_blueprint(account_blueprint)

# Register task apis
task_blueprint = TaskRestApiServer.create()
api_blueprint.register_blueprint(task_blueprint)

app.register_blueprint(api_blueprint)

# Register frontend elements
app.register_blueprint(img_assets_blueprint)
app.register_blueprint(react_blueprint)


@app.errorhandler(AppError)
def handle_error(exc: AppError) -> ResponseReturnValue:
    return jsonify({"message": exc.message, "code": exc.code}), exc.http_code or 500
