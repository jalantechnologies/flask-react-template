from flask import request, jsonify
from flask.views import MethodView

from modules.account.account_service import AccountService
from modules.account.types import (
    CreateAccountByEmailAndPasswordParams,
    PhoneNumber,
    AccountSearchParams,
)


class SignupView(MethodView):
    """Handle user signup with email and password"""

    def post(self):
        """
        POST /api/auth/signup
        
        Expected Request Body:
        {
            "email": "user@example.com",
            "password": "Password123",
            "name": "John Doe",
            "phone": "9999999999"
        }
        """
        data = request.get_json() or {}

        email = data.get("email")
        password = data.get("password")
        name = data.get("name", "")
        phone = data.get("phone", "")

        # Validate required fields
        if not all([email, password]):
            return jsonify({"message": "Email and password are required"}), 400

        try:
            # Split full name
            name_parts = name.split(" ", 1) if name else ["", ""]
            first_name = name_parts[0] if len(name_parts) > 0 else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            # Optional phone number
            phone_number = None
            if phone:
                phone_number = PhoneNumber(country_code="+91", phone_number=phone)

            # Build params object
            params = CreateAccountByEmailAndPasswordParams(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
            )

            # Create account
            account = AccountService.create_account_by_email_and_password(params=params)

            return jsonify({
                "message": "Account created successfully",
                "account": {
                    "id": account.id,
                    "email": email,
                    "name": f"{account.first_name} {account.last_name}".strip(),
                    "username": account.username
                }
            }), 201

        except ValueError as e:
            return jsonify({"message": str(e)}), 409  # Conflict (existing user)

        except Exception as e:
            return jsonify({"message": f"Error creating account: {str(e)}"}), 500


class LoginView(MethodView):
    """Handle user login with email and password"""

    def post(self):
        """
        POST /api/auth/login
        
        Expected Request Body:
        {
            "email": "user@example.com",
            "password": "Password123"
        }
        """
        data = request.get_json() or {}

        email = data.get("email")
        password = data.get("password")

        if not all([email, password]):
            return jsonify({"message": "Email and password are required"}), 400

        try:
            # Build request params
            params = AccountSearchParams(
                username=email,  # Login via email
                password=password
            )

            # Validate account and password
            account = AccountService.get_account_by_username_and_password(params=params)

            # ✅ Import here to avoid circular import
            from modules.authentication.authentication_service import AuthenticationService

            # Generate JWT token
            access_token = AuthenticationService.create_access_token_by_username_and_password(
                account=account
            )

            return jsonify({
                "message": "Login successful",
                "access_token": access_token.token,
                "account": {
                    "id": account.id,
                    "email": email,
                    "username": account.username,
                    "name": f"{account.first_name} {account.last_name}".strip()
                }
            }), 200

        except Exception as e:
            return jsonify({"message": f"Login failed: {str(e)}"}), 401