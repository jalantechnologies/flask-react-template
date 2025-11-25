# fix: Resolve docker-compose dev environment issues and enable hot reload

## Description
This PR fixes critical issues preventing the docker-compose development environment from functioning properly. The changes resolve bind mount permission errors, enable hot reload for both frontend and backend, fix webpack-dev-server compatibility issues, and optimize container startup time. All changes maintain full compatibility with production Kubernetes deployments.

The primary issues addressed were:
- Bind mount permission conflicts when running as non-root user
- Empty `.venv` directory overwriting container's virtual environment
- webpack-dev-server v5.x compatibility issues causing build failures
- Slow container startup due to unnecessary dependency reinstalls

## Changes

### Dockerfile
- **Added `PIPENV_VENV_IN_PROJECT=1` environment variable**: Ensures virtualenv is created in the project directory (`/opt/app/.venv`) instead of user home, making it accessible to both root and appuser
- **Removed duplicate `pipenv install --dev` call**: Dependencies are now installed once as root before switching to appuser, eliminating redundant installation steps
- **Added `.venv` ownership and permissions**: Ensures appuser (UID 10001) can access the virtualenv in production Kubernetes deployments with `readOnlyRootFilesystem`
- **Added virtualenv verification step**: Validates that critical dependencies (gunicorn, flask, pymongo) are available before switching users, ensuring production pods can use the venv immediately
- **Fixed indentation**: Corrected `RUN curl` command indentation for consistency
- **Enhanced comments**: Added documentation explaining production vs development behavior

### docker-compose.dev.yml
- **Run as root user for local development**: Overrides Dockerfile's `USER appuser` to avoid bind mount permission issues while maintaining production security
- **Anonymous volume for `.venv`**: Prevents empty local `.venv` directory from overwriting the container's virtual environment
- **Optimized startup command**: Skips `npm install` and `pipenv install` when dependencies already exist, reducing container startup time from ~3-4 minutes to ~10-15 seconds on subsequent runs
- **Aligned working directory**: Set `working_dir` to `/opt/app` to match Dockerfile's `WORKDIR`
- **Updated volume mounts**: Mount local directory to `/opt/app` for hot reload, preserve `node_modules` and `.venv` in anonymous volumes

### Webpack Configuration
- **Reverted webpack-dev-server to v4.11.1**: Fixes `_assetEmittingPreviousFiles` validation error introduced in v5.2.2 (from PR #479)
- **Updated webpack.dev.js**: Added Docker-specific configuration (host: `0.0.0.0`, `allowedHosts: 'all'`, webSocketURL configuration) for proper hot reload in containers
- **Removed `output.clean` from base config**: Enabled only in production builds to prevent conflicts with webpack-dev-server

### .dockerignore
- **Added `.venv`, `venv`, `env`**: Prevents local Python virtual environments from being copied into build context
- **Added `data`, `logs`, `dist`**: Excludes runtime data directories and build artifacts from Docker build context

## Tests

### Manual test cases run

**Test Case 1: Docker Compose Development Environment**
1. Run `docker compose -f docker-compose.dev.yml up -d`
2. Verify all containers start successfully (app, app-db, temporal, temporal-db, temporal-ui)
3. Wait for services to initialize (~30 seconds)
4. Verify frontend is accessible at `http://localhost:3000` (returns HTML with webpack bundles)
5. Verify backend is running on port 8080 (server responds to requests)
6. Verify hot reload works by modifying a frontend file and observing webpack recompilation in logs
7. Verify hot reload works by modifying a backend Python file and observing gunicorn reload in logs
8. Stop containers with `docker compose -f docker-compose.dev.yml down`
9. Restart containers and verify startup is faster (~10-15 seconds vs ~3-4 minutes) due to dependency caching

**Expected Results:**
- All containers start without permission errors
- Frontend and backend are accessible
- Hot reload works for both frontend and backend changes
- Subsequent container starts are significantly faster
- No I/O errors or virtualenv access issues
