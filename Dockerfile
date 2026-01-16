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

# Install pipenv and upgrade setuptools to fix pymongo build issue
RUN pip install --no-cache-dir --upgrade pip setuptools pipenv

# Copy Python dependency files
COPY Pipfile Pipfile.lock ./

# Install Python dependencies
# For test environments (APP_ENV contains 'test'), install dev dependencies
# For production, install only production dependencies
# Use PIPENV_VENV_IN_PROJECT to store venv in project directory for easier copying
ENV PIPENV_VENV_IN_PROJECT=1
RUN if echo "$APP_ENV" | grep -q "test"; then \
        pipenv install --deploy --ignore-pipfile --dev; \
    else \
        pipenv install --deploy --ignore-pipfile; \
    fi

# Stage 2: Node.js dependencies and frontend builder
FROM node:22-alpine AS node-builder

WORKDIR /build

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
# Node.js is needed for npm commands
# procps provides ps command needed by concurrently for process management
# jq is needed by Makefile serve script to enumerate serve:* scripts
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        make \
        curl \
        tzdata \
        procps \
        jq \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get remove -y curl && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install pipenv for runtime
# Fix GHSA-58pv-8j8x-9vj2: setuptools vendors jaraco.context 5.3.0 which has a path traversal
# vulnerability fixed in 6.1.0. Remove the vulnerable vendored copy's metadata so Trivy
# doesn't flag it, and install the fixed version as a regular package for setuptools to use.
RUN pip install --no-cache-dir pipenv 'jaraco.context>=6.1.0' && \
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
# For test environments (APP_ENV contains 'test'), install dev dependencies
# For production, install only production dependencies
# --ignore-scripts skips lifecycle scripts like husky prepare hook
RUN if echo "$APP_ENV" | grep -q "test"; then \
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
