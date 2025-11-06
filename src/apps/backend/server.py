from dotenv import load_dotenv
from flask import Flask, jsonify
from flask.typing import ResponseReturnValue
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from modules.comment.rest_api.comment_rest_api_server import CommentRestApiServer
from bin.blueprints import api_blueprint, img_assets_blueprint, react_blueprint
from modules.account.rest_api.account_rest_api_server import AccountRestApiServer
from modules.application.application_service import ApplicationService
from modules.application.errors import AppError, WorkerClientConnectionError
from modules.authentication.rest_api.authentication_rest_api_server import AuthenticationRestApiServer
from modules.config.config_service import ConfigService
from modules.logger.logger_manager import LoggerManager
from modules.task.rest_api.task_rest_api_server import TaskRestApiServer
from scripts.bootstrap_app import BootstrapApp

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Mount logger
LoggerManager.mount_logger()

# Run bootstrap tasks
BootstrapApp().run()

# Connect to Temporal Server
try:
    # Uncomment this when Temporal is running
    # ApplicationService.connect_temporal_server()
    # ApplicationService.schedule_worker_as_cron(cls=HealthCheckWorker, cron_schedule="*/10 * * * *")
    pass

except WorkerClientConnectionError as e:
    pass

# Apply ProxyFix if behind proxy
if ConfigService.has_value("is_server_running_behind_proxy") and ConfigService[bool].get_value("is_server_running_behind_proxy"):
    app.wsgi_app = ProxyFix(app.wsgi_app)  # type: ignore

# Register APIs
authentication_blueprint = AuthenticationRestApiServer.create()
api_blueprint.register_blueprint(authentication_blueprint)

account_blueprint = AccountRestApiServer.create()
api_blueprint.register_blueprint(account_blueprint)

task_blueprint = TaskRestApiServer.create()
api_blueprint.register_blueprint(task_blueprint)

comment_blueprint = CommentRestApiServer.create()
api_blueprint.register_blueprint(comment_blueprint)

app.register_blueprint(api_blueprint)

# Register frontend
app.register_blueprint(img_assets_blueprint)
app.register_blueprint(react_blueprint)

# Global Error Handler
@app.errorhandler(AppError)
def handle_error(exc: AppError) -> ResponseReturnValue:
    return jsonify({"message": exc.message, "code": exc.code}), exc.http_code or 500


if __name__ == "__main__":
    print("🚀 Flask server running on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
