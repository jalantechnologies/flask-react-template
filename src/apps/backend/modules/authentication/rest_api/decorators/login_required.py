from functools import wraps
from flask import request, jsonify, g

def login_required(f):
    """
    Decorator to protect routes that require authentication.
    Currently uses a mock user until JWT validation is implemented.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({
                "error": "AUTH_REQUIRED",
                "message": "Authorization header missing"
            }), 401
        
        if not auth_header.startswith("Bearer "):
            return jsonify({
                "error": "INVALID_AUTH_FORMAT",
                "message": "Expected format: Bearer <token>"
            }), 401
        
        # Extract JWT token (but not decoding yet)
        token = auth_header.split(" ")[1]
        if not token:
            return jsonify({
                "error": "TOKEN_MISSING",
                "message": "Bearer token not found"
            }), 401

        # ✅ Mock User (Replace with real JWT decoding later)
        class MockAccount:
            id = "mock-user-id-123"
            username = "test_user"
            email = "testuser@example.com"

        # Inject into request and Flask's global context
        request.account = MockAccount()
        g.current_user = MockAccount()

        return f(*args, **kwargs)

    return decorated_function
