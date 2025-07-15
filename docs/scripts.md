# One-Off Scripts

The application can run standalone Python scripts—useful for ad-hoc tasks, cron jobs, or data fixes.

---

## Directory Structure

```
src/
└─ apps/
   └─ backend/
      └─ scripts/
          sample_script.py   # ← your script lives here
```

---

## Writing a Script

Create a Python file under `src/apps/backend/scripts`, for example:

```python
# src/apps/backend/scripts/sample_script.py
from modules.logger.logger import Logger

def main():
    Logger.info(message="Running sample script")
    # your logic here
    Logger.info(message="Script finished")

if __name__ == "__main__":
    main()
```

---

## Running a Script

Use the npm helper:

```bash
npm run script --file=sample_script
```

* This bootstraps the Flask context so application settings and database models are available.  
* Omit the `.py` extension in `--file=`.  

---

## Typical Use-Cases

| Use-Case              | Example                                         |
|-----------------------|-------------------------------------------------|
| Data backfill         | Re-compute a derived column for historical rows |
| Maintenance / cleanup | Remove orphaned documents, trim log tables      |
| Cron-style jobs       | Generate weekly reports, send summary emails    |
| One-time migrations   | Copy data between services before a deploy      |
