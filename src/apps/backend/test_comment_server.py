#!/usr/bin/env python3
"""
Simple test script to verify comment API functionality without Temporal.
"""

import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from flask import Flask
    from modules.logger.logger_manager import LoggerManager
    from modules.comment.rest_api.comment_rest_api_server import CommentRestApiServer
    from modules.task.rest_api.task_rest_api_server import TaskRestApiServer
    from modules.account.rest_api.account_rest_api_server import AccountRestApiServer
    from modules.authentication.rest_api.authentication_rest_api_server import AuthenticationRestApiServer
    from bin.blueprints import api_blueprint
    from modules.application.errors import AppError
    from flask import jsonify
    
    # Simple Flask app setup
    app = Flask(__name__)
    
    # Mount logger
    LoggerManager.mount_logger()
    
    # Register APIs
    auth_blueprint = AuthenticationRestApiServer.create()
    api_blueprint.register_blueprint(auth_blueprint)
    
    account_blueprint = AccountRestApiServer.create()
    api_blueprint.register_blueprint(account_blueprint)
    
    task_blueprint = TaskRestApiServer.create()
    api_blueprint.register_blueprint(task_blueprint)
    
    comment_blueprint = CommentRestApiServer.create()
    api_blueprint.register_blueprint(comment_blueprint)
    
    app.register_blueprint(api_blueprint)
    
    @app.errorhandler(AppError)
    def handle_error(exc: AppError):
        return jsonify({"message": exc.message, "code": exc.code}), exc.http_code or 500
    
    @app.route('/health')
    def health():
        return {"status": "ok", "message": "Comment API test server running"}
    
    print("🚀 Starting Comment API test server on http://localhost:8081")
    print("📋 Available endpoints:")
    print("   Health: GET http://localhost:8081/health")
    print("   Auth: POST http://localhost:8081/api/access-tokens")
    print("   Accounts: POST http://localhost:8081/api/accounts")
    print("   Tasks: GET/POST/PATCH/DELETE http://localhost:8081/api/accounts/{id}/tasks")
    print("   Comments: GET/POST/PATCH/DELETE http://localhost:8081/api/accounts/{id}/tasks/{id}/comments")
    
    app.run(host='127.0.0.1', port=8081, debug=True)