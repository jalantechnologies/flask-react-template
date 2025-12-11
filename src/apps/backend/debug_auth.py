#!/usr/bin/env python3
"""
Debug the access token response to understand the issue.
"""

import json
import sys
import os
import time
import threading

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_auth():
    """Debug authentication flow"""
    
    print("🔍 Debugging Authentication Flow")
    print("=" * 40)
    
    from flask import Flask, jsonify
    from modules.logger.logger_manager import LoggerManager
    from modules.account.rest_api.account_rest_api_server import AccountRestApiServer
    from modules.authentication.rest_api.authentication_rest_api_server import AuthenticationRestApiServer
    from bin.blueprints import api_blueprint
    from modules.application.errors import AppError
    
    app = Flask(__name__)
    LoggerManager.mount_logger()
    
    # Register APIs
    auth_blueprint = AuthenticationRestApiServer.create()
    api_blueprint.register_blueprint(auth_blueprint)
    
    account_blueprint = AccountRestApiServer.create()
    api_blueprint.register_blueprint(account_blueprint)
    
    app.register_blueprint(api_blueprint)
    
    @app.errorhandler(AppError)
    def handle_error(exc: AppError):
        return jsonify({"message": exc.message, "code": exc.code}), exc.http_code or 500
    
    def start_server():
        app.run(host='127.0.0.1', port=8084, debug=False, use_reloader=False)
    
    # Start server
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(2)
    
    base_url = "http://localhost:8084"
    
    try:
        # Create account
        print("1️⃣ Creating account...")
        account_data = {
            "username": f"debug_{int(time.time())}@example.com",
            "password": "testpass123",
            "first_name": "Debug",
            "last_name": "User"
        }
        
        account_cmd = f'''curl -s -X POST "{base_url}/api/accounts" -H "Content-Type: application/json" -d '{json.dumps(account_data)}' '''
        account_result = os.popen(account_cmd).read()
        print(f"Account response: {account_result}")
        
        # Get token
        print("2️⃣ Getting access token...")
        token_data = {
            "username": account_data["username"],
            "password": account_data["password"]
        }
        
        token_cmd = f'''curl -s -X POST "{base_url}/api/access-tokens" -H "Content-Type: application/json" -d '{json.dumps(token_data)}' '''
        token_result = os.popen(token_cmd).read()
        print(f"Token response: {token_result}")
        
        # Parse token response
        if token_result.strip():
            try:
                token_json = json.loads(token_result)
                print(f"Token JSON keys: {list(token_json.keys())}")
                
                # Check different possible key names
                possible_keys = ['access_token', 'token', 'accessToken', 'jwt']
                for key in possible_keys:
                    if key in token_json:
                        print(f"✅ Found token with key '{key}': {token_json[key][:20]}...")
                        return True
                        
                print("❌ No token found in response")
                
            except json.JSONDecodeError:
                print("❌ Invalid JSON response")
        else:
            print("❌ Empty response")
            
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = debug_auth()
    print(f"\nDebug result: {'SUCCESS' if success else 'FAILED'}")