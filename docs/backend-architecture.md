# Backend Architecture

> A **module** is a self-contained package of related functionality in our backend codebase. It encapsulates one domain concept (e.g., accounts, orders, payments) and exposes a clear interface for other parts of the system.

This document covers:
1. **Why** we structure code into modules and the benefits of our layout.
2. **What** each folder and file in a module does.
3. A **diagram** that shows how the layers interact at runtime.

Video explanation: [Backend Architecture Overview](https://www.loom.com/share/e51d50cd8bec4851a2a8718bdc6e34d5)

---

## 1. Why Modular Architecture?

- **Separation of Concerns**: Clearly divides HTTP routing, business logic, data access, and utilities into distinct layers.
- **Reusability**: Public-facing APIs (`account_service.py`, `types.py`) allow other modules to integrate without knowing internal details.
- **Testability**: Small, focused components (reader, writer, util) can be unit‑tested in isolation.
- **Consistency**: Applying the same pattern across modules speeds up onboarding and reduces cognitive load.
- **Scalability**: New features or entirely new domains can be added by copying the template and filling in domain specifics.

---

## 2. Concept & Layers Diagram

```mermaid
flowchart LR
  HTTP[HTTP Client / Flask Request]
  API[rest_api → AccountView]
  Service[account_service.py]
  Reader[internal/account_reader.py] & Writer[internal/account_writer.py]
  Repo[internal/store/account_repository.py]
  MongoDB[(MongoDB)]

  HTTP --> API --> Service --> Reader --> Repo --> MongoDB
  Service --> Writer --> Repo --> MongoDB
  Service --> AuthenticationService
  Service --> NotificationService
```

1. **HTTP Layer** (`rest_api/`): Routing and request/response handling.
2. **Service Layer**: Business logic, orchestration, calls to external services.
3. **Persistence Layer**: Reader/Writer + Repository + Model (MongoDB).
4. **Utilities & Types**: Shared helpers (utils) and data models (DTOs).

---

## 3. Typical Module Folder Structure

```
<module_name>/
├── <module_name>_service.py   # Public API for other modules
├── internal/                  # Implementation details (not imported externally)
│   ├── store/                 # DB model & repository
│   │   ├── *_model.py
│   │   └── *_repository.py
│   ├── *_reader.py            # Read operations
│   ├── *_writer.py            # Write operations
│   └── *_util.py              # Conversion, validation, common helpers
├── rest_api/                  # HTTP routes & handlers
│   ├── *_rest_api_server.py
│   ├── *_router.py
│   └── *_view.py
├── types.py                   # Data Transfer Objects (DTOs)
└── errors.py                  # Module-specific exception classes
```

> **Note**: Replace `<module_name>` and `*` with your module’s actual name.

---

## 4. Module Layout

> We will refer to the **account** module throughout this document to demonstrate each concept.

```
account/
├── account_service.py
├── internal/
│   ├── store/
│   │   ├── account_model.py
│   │   └── account_repository.py
│   ├── account_reader.py
│   ├── account_writer.py
│   └── account_util.py
├── rest_api/
│   ├── account_rest_api_server.py
│   ├── account_router.py
│   └── account_view.py
├── types.py
└── errors.py
```

### 4.1 `account_service.py`

- **Role**  
  - Exposes module‐wide operations as static methods, e.g. `create_account_by_username_and_password`, `reset_account_password`, `get_account_by_id`, `update_account_profile`, plus wiring into **AuthenticationService** (for OTP/password) and **NotificationService** (for preferences).
- **Imports**  
  ```python
  from modules.account.internal.account_reader import AccountReader
  from modules.account.internal.account_writer import AccountWriter
  from modules.account.types import (
      Account,
      CreateAccountByUsernameAndPasswordParams,
      ResetPasswordParams,
      UpdateAccountProfileParams,
      ...
  )
  from modules.authentication.authentication_service import AuthenticationService
  from modules.notification.notification_service import NotificationService
  ```
- **Example call**  
  ```python
  AccountService.create_account_by_username_and_password(
      params=CreateAccountByUsernameAndPasswordParams(username="alice", password="secret")
  )
  ```

---

## 5. Persistence Layer (`internal/store/`)

### 5.1 `account_model.py`

- A `@dataclass` extending `BaseModel`  
- Defines all Mongo fields (e.g. `first_name`, `hashed_password`, `phone_number`, `username`, `active`, `created_at`, `updated_at`)  
- `@staticmethod from_bson()` to validate & hydrate a model from raw BSON  
- `@staticmethod get_collection_name()` returns `"accounts"`

### 5.2 `account_repository.py`

- `class AccountRepository(ApplicationRepository)`  
- Provides:
  - `collection()` — the Mongo `Collection` object
  - `on_init_collection()` — sets up JSON-Schema validation (via `create_collection`) and any indexes  
- Central place for low-level DB concerns

---

## 6. I/O Helpers (`internal/`)

### 6.1 `account_reader.py`

- `class AccountReader:`  
  - High-level **read** methods, e.g.  
    - `get_account_by_id(params: AccountSearchByIdParams) -> Account`  
    - `get_account_by_phone_number(phone_number: PhoneNumber) -> Account`  
    - `get_account_by_username_and_password(params: AccountSearchParams) -> Account`  
  - Uses `AccountRepository.collection().find_one(...)`
  - Converts raw BSON → domain via `AccountUtil.convert_account_bson_to_account()`
  - Raises module-specific exceptions if not found or duplicates

### 6.2 `account_writer.py`

- `class AccountWriter:`  
  - High-level **write** methods, e.g.  
    - `create_account_by_username_and_password(params: CreateAccountByUsernameAndPasswordParams) -> Account`  
    - `create_or_update_account_notification_preferences(...) -> AccountNotificationPreferences`  
    - `update_account_profile(account_id: str, params: UpdateAccountProfileParams) -> Account`  
    - `reset_account_password(params: ResetPasswordParams) -> Account`  
  - Handles:
    - Phone-number validation via `phonenumbers.parse` & `is_valid_number`
    - Password hashing via `AccountUtil.hash_password()`
    - Mongo `insert_one` / `find_one_and_update`
    - Not-found errors (`AccountWithIdNotFoundError`)

### 6.3 `account_util.py`

- `class AccountUtil:`  
  - `hash_password(password: str) -> str`  
  - `compare_password(password: str, hashed_password: str) -> bool`  
  - `convert_account_bson_to_account(bson: dict) -> Account` (uses `AccountModel.from_bson`)

---

## 7. Shared Types & Errors

### 7.1 `types.py`

All of the data transfer objects (DTOs) are `@dataclass`es, for instance:
```python
@dataclass(frozen=True)
class CreateAccountByUsernameAndPasswordParams:
    username: str
    password: str

@dataclass(frozen=True)
class Account:
    id: str
    first_name: str
    last_name: str
    username: str
    phone_number: PhoneNumber
    hashed_password: str
```
Clients import these for type safety.

### 7.2 `errors.py`

Custom `AppError` subclasses, e.g.:
```python
class AccountWithUserNameExistsError(AppError): ...
class AccountWithPhoneNumberNotFoundError(AppError): ...
class AccountNotFoundError(AppError): ...
```
Each carries its own HTTP status code and error code from `AccountErrorCode` in `types.py`.

---

## 8. HTTP Layer (`rest_api/`)

### 8.1 `account_rest_api_server.py`

Bootstraps a Flask `Blueprint`:
```python
def create() -> Blueprint:
    bp = Blueprint("account", __name__)
    return AccountRouter.create_route(blueprint=bp)
```

### 8.2 `account_router.py`

Registers URL rules on the Blueprint:
```python
blueprint.add_url_rule("/accounts", view_func=AccountView.as_view("accounts"))
blueprint.add_url_rule("/accounts/<id>", view_func=AccountView.as_view("accounts_by_id"), methods=["GET", "PATCH"])
blueprint.add_url_rule(
    "/accounts/<account_id>/notification-preferences",
    view_func=AccountView.update_account_notification_preferences,
    methods=["PATCH"],
)
```

### 8.3 `account_view.py`

`class AccountView(MethodView):`
- Uses `flask.request` to parse JSON
- Marshals params into dataclasses (e.g. `CreateAccountByPhoneNumberParams(**request.json)`)
- Calls `AccountService.*`
- Returns `jsonify(asdict(result)), <status_code>`
- Raises `AccountBadRequestError` for missing/invalid inputs
