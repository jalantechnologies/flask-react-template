import os
from pathlib import Path

SECRETS_DIR = Path("/opt/app/secrets")

def init_secrets_from_files():
    if not SECRETS_DIR.exists():
        return

    for file in SECRETS_DIR.iterdir():
        if file.is_file():
            env_name = file.name.upper()
            print(env_name)
            print(file.read_text().strip())

            os.environ[f'{env_name}'] = file.read_text().strip()
