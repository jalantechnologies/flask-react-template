from dotenv import load_dotenv
from flask import Flask, jsonify
from flask.typing import ResponseReturnValue
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from bin.blueprints import api_blueprint, img_assets_blueprint, react_blueprint
from modules.account.rest_api.account_rest_api_server import AccountRestApiServer
from modules.application.errors import AppError
from modules.application.worker_registry import WorkerRegistry
from modules.authentication.rest_api.authentication_rest_api_server import AuthenticationRestApiServer
from modules.config.config_service import ConfigService
from modules.logger.logger_manager import LoggerManager
from modules.task.rest_api.task_rest_api_server import TaskRestApiServer
from scripts.bootstrap_app import BootstrapApp

load_dotenv()

from datetime import datetime
from flask.json.provider import DefaultJSONProvider

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app = Flask(__name__)
app.json = CustomJSONProvider(app)
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Mount deps
LoggerManager.mount_logger()

# Run bootstrap tasks
with open("final_url_map.txt", "w") as f:
    f.write(str(app.url_map))
BootstrapApp().run()

# Initialize worker registry
WorkerRegistry.initialize()


# Apply ProxyFix to interpret `X-Forwarded` headers if enabled in configuration
# Visit: https://flask.palletsprojects.com/en/stable/deploying/proxy_fix/ for more information
if ConfigService.has_value("is_server_running_behind_proxy") and ConfigService[bool].get_value(
    "is_server_running_behind_proxy"
):
    app.wsgi_app = ProxyFix(app.wsgi_app)  # type: ignore

# Register authentication apis
authentication_blueprint = AuthenticationRestApiServer.create()
app.register_blueprint(authentication_blueprint, url_prefix="/api")

# Register accounts apis
account_blueprint = AccountRestApiServer.create()
app.register_blueprint(account_blueprint, url_prefix="/api")

# Register task apis
task_blueprint = TaskRestApiServer.create()
app.register_blueprint(task_blueprint, url_prefix="/api")

# Register comment apis
from modules.comment.rest_api.comment_rest_api_server import CommentRestApiServer
comment_blueprint = CommentRestApiServer.create()
app.register_blueprint(comment_blueprint, url_prefix="/api")

app.register_blueprint(api_blueprint)

# Register frontend elements
app.register_blueprint(img_assets_blueprint)
app.register_blueprint(react_blueprint)


@app.errorhandler(AppError)
def handle_error(exc: AppError) -> ResponseReturnValue:
    return jsonify({"message": exc.message, "code": exc.code}), exc.http_code or 500

@app.errorhandler(404)
def handle_404(e):
    from bin.blueprints import serve_react_home
    return serve_react_home("")
