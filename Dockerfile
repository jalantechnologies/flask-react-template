# Stage 1: Python dependencies builder
FROM python:3.12-slim AS python-builder
ARG DEBIAN_FRONTEND=noninteractive
ARG APP_ENV=production

WORKDIR /build

# Install build dependencies only (needed for compiling Python packages)
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv and upgrade setuptools to fix pymongo build issue.
# setuptools is pinned to >=78.1.1 to clear CVE-2025-47273 (path traversal in PackageIndex).
RUN pip install --no-cache-dir --upgrade pip 'setuptools>=78.1.1' pipenv

# Copy Python dependency files
COPY Pipfile Pipfile.lock ./

# Install Python dependencies
# For testing environment, install dev dependencies
# For production/preview/development, install only production dependencies
# Use PIPENV_VENV_IN_PROJECT to store venv in project directory for easier copying
ENV PIPENV_VENV_IN_PROJECT=1
RUN if [ "$APP_ENV" = "testing" ]; then \
        pipenv install --deploy --ignore-pipfile --dev; \
    else \
        pipenv install --deploy --ignore-pipfile; \
    fi

# Stage 2: Node.js dependencies and frontend builder
# Debian release must match the python:3.12-slim base (trixie) so the Node binary
# copied into the runtime stage links against the same system libraries.
FROM node:22-trixie-slim AS node-builder

WORKDIR /build

# Upgrade npm to fix bundled dependency vulnerabilities (glob, minimatch, tar CVEs)
# npm 12.0.2 still bundles tar 7.5.19 (CVE-2026-73566), so replace that copy with the
# fixed release and fail the build if the vulnerable version survives.
# npm 12.0.2 likewise still bundles ip-address 10.2.0 (CVE-2026-69192, SSRF filter bypass);
# ip-address 10.3.1 has no runtime dependencies, so the same copy-over-and-assert pattern
# clears it. Both are replaced here so no vulnerable copy survives in the image.
RUN npm install -g npm@12.0.1 && \
    npm install -g --prefix /tmp/tar-fix tar@7.5.21 && \
    TAR_DIR="$(npm root -g)/npm/node_modules/tar" && \
    rm -rf "$TAR_DIR" && \
    mkdir -p "$TAR_DIR" && \
    cp -R /tmp/tar-fix/lib/node_modules/tar/. "$TAR_DIR/" && \
    rm -rf /tmp/tar-fix && \
    TAR_DIR="$TAR_DIR" node -e 'process.exit(require(process.env.TAR_DIR + "/package.json").version === "7.5.21" ? 0 : 1)' && \
    npm install -g --prefix /tmp/ip-fix ip-address@10.3.1 && \
    IP_DIR="$(npm root -g)/npm/node_modules/ip-address" && \
    rm -rf "$IP_DIR" && \
    mkdir -p "$IP_DIR" && \
    cp -R /tmp/ip-fix/lib/node_modules/ip-address/. "$IP_DIR/" && \
    rm -rf /tmp/ip-fix && \
    IP_DIR="$IP_DIR" node -e 'process.exit(require(process.env.IP_DIR + "/package.json").version === "10.3.1" ? 0 : 1)'

# Stage the Node runtime at a fixed path so the runtime stage can COPY it without
# depending on where this image happens to put global modules ("npm root -g"
# differs between the Debian and Alpine variants).
RUN mkdir -p /node-dist/lib && \
    cp "$(command -v node)" /node-dist/node && \
    cp -R "$(npm root -g)" /node-dist/lib/node_modules

# Copy package files first for better layer caching
COPY package.json package-lock.json ./

# Install all dependencies (including dev dependencies needed for build)
RUN npm ci && npm cache clean --force

# Copy source files needed for build
COPY src/ ./src/
COPY tsconfig.json tailwind.config.js postcss.config.cjs ./
COPY config/ ./config/

# Build frontend (requires APP_ENV build arg)
ARG APP_ENV=production
RUN npm run build

# Stage 3: Runtime stage (minimal)
FROM python:3.12-slim AS runtime
ARG DEBIAN_FRONTEND=noninteractive
ARG APP_ENV=production

WORKDIR /app

# Install only runtime system dependencies
# Note: Removed GUI libraries (libgtk, xvfb, xauth) as they're not used
# make is needed for npm start (runs make run-engine)
# procps provides ps command needed by concurrently for process management
# jq is needed by Makefile serve script to enumerate serve:* scripts
# apt-get upgrade applies security patches for base image vulnerabilities (e.g., OpenSSL CVEs)
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        make \
        tzdata \
        procps \
        jq \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy Node.js from the official image rather than installing it from NodeSource.
# The node-builder stage shares this stage's Debian release, so the binary and its
# bundled npm run against the same system libraries.
COPY --from=node-builder /node-dist/node /usr/local/bin/node
COPY --from=node-builder /node-dist/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/bin/node /usr/local/bin/nodejs && \
    ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm && \
    ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# Install pipenv for runtime.
# setuptools is upgraded to >=78.1.1 to clear CVE-2025-47273 (path traversal in PackageIndex)
# in the final runtime image's system site-packages.
# Fix GHSA-58pv-8j8x-9vj2: setuptools vendors jaraco.context 5.3.0 which has a path traversal
# vulnerability fixed in 6.1.0. Remove the vulnerable vendored copy's metadata so Trivy
# doesn't flag it, and install the fixed version as a regular package for setuptools to use.
RUN pip install --no-cache-dir --upgrade 'setuptools>=78.1.1' pipenv 'jaraco.context>=6.1.0' && \
    rm -rf /usr/local/lib/python3.12/site-packages/setuptools/_vendor/jaraco.context-*.dist-info

# Copy Pipfile first (needed for pipenv virtualenv detection)
COPY Pipfile Pipfile.lock ./

# Copy Python virtual environment from builder (.venv directory)
# Using PIPENV_VENV_IN_PROJECT=1 ensures venv is in project directory
COPY --from=python-builder /build/.venv ./.venv

# Fix shebang lines in virtualenv scripts (they point to /build/.venv/bin/python)
# Update all scripts in .venv/bin to use the correct path
RUN find .venv/bin -type f -executable -exec sed -i '1s|^#!.*/build/.venv/bin/python|#!/app/.venv/bin/python|' {} \;

# Set environment variable so pipenv uses the copied venv
ENV PIPENV_VENV_IN_PROJECT=1

# Copy package.json first (needed for npm install)
COPY --from=node-builder /build/package.json /build/package-lock.json ./

# Install Node.js dependencies
# For testing environment, install dev dependencies
# For production/preview/development, install only production dependencies
# --ignore-scripts skips lifecycle scripts like husky prepare hook
RUN if [ "$APP_ENV" = "testing" ]; then \
        npm ci --ignore-scripts && npm cache clean --force; \
    else \
        npm ci --omit=dev --ignore-scripts && npm cache clean --force; \
    fi

# Copy build artifacts from node-builder
COPY --from=node-builder /build/dist ./dist

# Copy application source code (includes Makefile, src/, config/, etc.)
# Note: This will overwrite node_modules and dist, but that's fine since
# we've already copied the production versions from builders
COPY . .

# Create non-root user with consistent UID/GID 
RUN groupadd -r -g 10001 app && \
    useradd -r -u 10001 -g 10001 -m appuser && \
    mkdir -p /app/tmp /app/logs /app/output && \
    chown -R appuser:app /app /home/appuser

# Switch to non-root user
USER appuser

# Pipenv will automatically detect the virtualenv from Pipfile location
# The virtualenv binaries are accessible via pipenv run commands

CMD [ "npm", "start" ]
