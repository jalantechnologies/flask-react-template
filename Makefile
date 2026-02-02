run-lint:
	cd src/apps/backend && \
	pipenv run mypy --config-file mypy.ini . && \
	pipenv run pylint \
	  --disable=all \
	  --reports=no \
	  --enable=cyclic-import \
	  ./

run-format:
	cd src/apps/backend \
		&& pipenv run autoflake . -i \
		&& pipenv run isort . \
		&& pipenv run black .

run-format-tests:
	cd tests \
		&& pipenv run autoflake . -i \
		&& pipenv run isort . \
		&& pipenv run black .

run-vulture:
	cd src/apps/backend \
		&& pipenv run vulture

run-engine:
	cd src/apps/backend \
		&& pipenv run python --version \
		&& pipenv run gunicorn -c gunicorn_config.py --reload server:app

run-worker:
	cd src/apps/backend \
		&& pipenv run celery -A celery_app worker --loglevel=info --concurrency=4 --queues=critical,default,low -E

run-beat:
	cd src/apps/backend \
		&& pipenv run celery -A celery_app beat --loglevel=info

run-flower:
	cd src/apps/backend \
		&& pipenv run celery -A celery_app flower --port=5555


run-test:
	PYTHONPATH=src/apps/backend pipenv run pytest --disable-warnings -s -x -v --cov=src/apps/backend --cov-report=xml:/app/output/coverage.xml tests

run-engine-winx86:
	echo "This command is specifically for Windows platform \
	since gunicorn is not well supported by Windows OS"
	cd src/apps/backend \
		&& pipenv run waitress-serve --listen 127.0.0.1:8080 server:app

run-script:
	cd src/apps/backend && \
		PYTHONPATH=./ pipenv run python scripts/$(file).py

serve:
	@echo "Detected args: $(ARGS)"
	@SERVE_SCRIPTS=$$(jq -r '.scripts | to_entries[] | select(.key | startswith("serve:")) | .key' package.json | grep -v '^serve:$$'); \
	CMD_ARGS=$$(echo "$$SERVE_SCRIPTS" | xargs -I {} echo npm run {}); \
	echo "Running: $$CMD_ARGS"; \
	echo "$$CMD_ARGS" | xargs -I {} -P 0 sh -c "{}"