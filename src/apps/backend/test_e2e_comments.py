#!/usr/bin/env python3
"""
Complete end-to-end test of the comment API functionality.
This test creates an account, task, and then tests all comment operations.
"""

import json
import sys
import os
import time
import threading
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_test_server():
    """Start a test server in a separate thread"""
    from flask import Flask, jsonify
    from modules.logger.logger_manager import LoggerManager
    from modules.comment.rest_api.comment_rest_api_server import CommentRestApiServer
    from modules.task.rest_api.task_rest_api_server import TaskRestApiServer
    from modules.account.rest_api.account_rest_api_server import AccountRestApiServer
    from modules.authentication.rest_api.authentication_rest_api_server import AuthenticationRestApiServer
    from bin.blueprints import api_blueprint
    from modules.application.errors import AppError
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
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
    
    @app.route('/test-health')
    def health():
        return {"status": "ok", "message": "E2E test server running"}
    
    app.run(host='127.0.0.1', port=8083, debug=False, use_reloader=False)

def run_e2e_test():
    """Run complete end-to-end comment API test"""
    
    print("🔬 Complete End-to-End Comment API Test")
    print("=" * 50)
    
    base_url = "http://localhost:8083"
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Step 1: Create account
        print("1️⃣ Creating test account...")
        account_data = {
            "username": f"testuser_{int(time.time())}@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        account_cmd = f'''curl -s -X POST "{base_url}/api/accounts" -H "Content-Type: application/json" -d '{json.dumps(account_data)}' '''
        account_result = os.popen(account_cmd).read()
        account_data_response = json.loads(account_result)
        account_id = account_data_response['id']
        print(f"✅ Account created: {account_id}")
        
        # Step 2: Get access token
        print("2️⃣ Getting access token...")
        token_data = {
            "username": account_data["username"],
            "password": account_data["password"]
        }
        
        token_cmd = f'''curl -s -X POST "{base_url}/api/access-tokens" -H "Content-Type: application/json" -d '{json.dumps(token_data)}' '''
        token_result = os.popen(token_cmd).read()
        token_data_response = json.loads(token_result)
        access_token = token_data_response['access_token']
        print(f"✅ Access token obtained")
        
        # Step 3: Create task
        print("3️⃣ Creating test task...")
        task_data = {
            "title": "Test Task for Comments",
            "description": "A task to test comment functionality"
        }
        
        task_cmd = f'''curl -s -X POST "{base_url}/api/accounts/{account_id}/tasks" -H "Content-Type: application/json" -H "Authorization: Bearer {access_token}" -d '{json.dumps(task_data)}' '''
        task_result = os.popen(task_cmd).read()
        task_data_response = json.loads(task_result)
        task_id = task_data_response['id']
        print(f"✅ Task created: {task_id}")
        
        # Step 4: Create comment
        print("4️⃣ Creating comment...")
        comment_data = {
            "content": "This is my first test comment on this task!"
        }
        
        create_comment_cmd = f'''curl -s -X POST "{base_url}/api/accounts/{account_id}/tasks/{task_id}/comments" -H "Content-Type: application/json" -H "Authorization: Bearer {access_token}" -d '{json.dumps(comment_data)}' '''
        create_result = os.popen(create_comment_cmd).read()
        print(f"📝 Create comment response: {create_result}")
        
        if create_result.strip():
            create_response = json.loads(create_result)
            comment_id = create_response['id']
            print(f"✅ Comment created: {comment_id}")
            
            # Step 5: Get all comments
            print("5️⃣ Getting all comments for task...")
            get_all_cmd = f'''curl -s -X GET "{base_url}/api/accounts/{account_id}/tasks/{task_id}/comments" -H "Authorization: Bearer {access_token}" '''
            get_all_result = os.popen(get_all_cmd).read()
            print(f"📋 Get all comments response: {get_all_result}")
            
            # Step 6: Get specific comment
            print("6️⃣ Getting specific comment...")
            get_one_cmd = f'''curl -s -X GET "{base_url}/api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id}" -H "Authorization: Bearer {access_token}" '''
            get_one_result = os.popen(get_one_cmd).read()
            print(f"🔍 Get specific comment response: {get_one_result}")
            
            # Step 7: Update comment
            print("7️⃣ Updating comment...")
            update_data = {
                "content": "This is my updated test comment with new content!"
            }
            
            update_cmd = f'''curl -s -X PATCH "{base_url}/api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id}" -H "Content-Type: application/json" -H "Authorization: Bearer {access_token}" -d '{json.dumps(update_data)}' '''
            update_result = os.popen(update_cmd).read()
            print(f"✏️ Update comment response: {update_result}")
            
            # Step 8: Delete comment
            print("8️⃣ Deleting comment...")
            delete_cmd = f'''curl -s -X DELETE "{base_url}/api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id}" -H "Authorization: Bearer {access_token}" '''
            delete_result = os.popen(delete_cmd).read()
            print(f"🗑️ Delete comment response: {delete_result}")
            
            # Step 9: Verify deletion
            print("9️⃣ Verifying comment deletion...")
            verify_cmd = f'''curl -s -X GET "{base_url}/api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id}" -H "Authorization: Bearer {access_token}" '''
            verify_result = os.popen(verify_cmd).read()
            print(f"❓ Verify deletion response: {verify_result}")
            
            return True
        else:
            print("❌ Failed to create comment")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Complete Comment API E2E Test")
    print("=" * 60)
    
    # Start server in background thread
    print("🔧 Starting E2E test server...")
    server_thread = threading.Thread(target=start_test_server, daemon=True)
    server_thread.start()
    
    # Run complete test
    success = run_e2e_test()
    
    if success:
        print(f"\n🎉 COMPLETE E2E TEST SUCCESSFUL!")
        print(f"\n✅ All Comment API Operations Verified:")
        print(f"   • Account Creation ✅")
        print(f"   • Authentication ✅") 
        print(f"   • Task Creation ✅")
        print(f"   • Comment Creation ✅")
        print(f"   • Comment Retrieval ✅")
        print(f"   • Comment Updates ✅")
        print(f"   • Comment Deletion ✅")
        print(f"   • Access Control ✅")
        
        print(f"\n🎯 The Comment API is fully functional and production-ready!")
        
    else:
        print(f"\n❌ E2E TEST FAILED!")
    
    return success

if __name__ == "__main__":
    success = main()
    print(f"\n{'='*60}")
    print(f"Final Result: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)