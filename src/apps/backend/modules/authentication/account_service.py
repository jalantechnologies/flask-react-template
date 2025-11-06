from src.apps.backend.modules.authentication.account_writer import AccountWriter
from src.apps.backend.modules.authentication.account_model import Account
from werkzeug.security import generate_password_hash

class AccountService:
    def _init_(self):
        self.account_writer = AccountWriter()
        # ... existing code ...
    
    def create_account(self, email: str, password: str, name: str, phone: str) -> Account:
        """
        Create a new user account
        
        Args:
            email: User's email address
            password: Plain text password (will be hashed)
            name: User's full name
            phone: User's phone number
            
        Returns:
            Account: Newly created account object
            
        Raises:
            ValueError: If account with email already exists
        """
        # Check if account already exists
        existing_account = self.account_reader.get_account_by_email(email)
        if existing_account:
            raise ValueError(f"Account with email {email} already exists")
        
        # Hash the password before storing
        hashed_password = generate_password_hash(password)
        
        # Create new account using AccountWriter
        new_account = self.account_writer.create_account(
            email=email,
            password=hashed_password,
            name=name,
            phone=phone
        )
        
        return new_account