FROM ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update -y && \
  apt-get install build-essential -y && \
  apt-get install git -y && \
  apt-get install curl -y && \
  apt-get install jq -y 

RUN apt-get install -y libgtk2.0-0 libgtk-3-0 libgbm-dev \
  libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 \
  libxtst6 xauth xvfb tzdata software-properties-common

RUN add-apt-repository ppa:deadsnakes/ppa -y && \
  apt-get install python3.12 python3-pip -y && \
  pip install pipenv

RUN curl -sL https://deb.nodesource.com/setup_22.x -o nodesource_setup.sh && \
  bash nodesource_setup.sh && \
  cat /etc/apt/sources.list.d/nodesource.list

RUN apt-get install nodejs -y
RUN node --version && npm --version

# Copy dependency files first for better layer caching
COPY Pipfile Pipfile.lock /app/
COPY package.json package-lock.json /app/

# Install Python dependencies once
RUN pipenv install --dev

# Install Node dependencies once
RUN npm ci

# Copy to final location
RUN mkdir -p /opt/app && cp -a /app/. /opt/app/

WORKDIR /opt/app

# Set PIPENV_VENV_IN_PROJECT so virtualenv is created in project directory
# This ensures the virtualenv is accessible to both root and appuser
ENV PIPENV_VENV_IN_PROJECT=1

# Copy application code (overwrites with latest)
COPY . /opt/app

# build arguments
ARG APP_ENV

RUN npm run build

# Create non-root user for security - use consistent UID/GID across environments
# This matches Kubernetes production securityContext (runAsUser: 10001)
RUN groupadd -r -g 10001 app && \
    useradd -r -u 10001 -g 10001 -m appuser

# Create directories and set ownership for non-root user to write files
# Ensure .venv directory is accessible to appuser for production use
# Production uses readOnlyRootFilesystem, so .venv must be readable by appuser
RUN mkdir -p /opt/app/tmp /opt/app/logs /opt/app/output /home/appuser/.cache /app/output && \
    chown -R appuser:app /opt/app /home/appuser /app/output && \
    if [ -d "/opt/app/.venv" ]; then \
      chown -R appuser:app /opt/app/.venv && \
      chmod -R u+rX,go+rX /opt/app/.venv; \
    fi

# Verify .venv is functional before switching users
# This ensures production pods can use the venv immediately
RUN if [ -d "/opt/app/.venv" ]; then \
      /opt/app/.venv/bin/python -c "import gunicorn, flask, pymongo" && \
      echo "✓ Virtualenv verified - all critical dependencies available"; \
    fi

# Switch to appuser (dependencies already installed as root above)
# Production Kubernetes runs as this user (10001)
# Note: docker-compose.dev.yml overrides to root user for local development
USER appuser

CMD [ "npm", "start" ]
