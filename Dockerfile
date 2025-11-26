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

# Set PIPENV_VENV_IN_PROJECT early so virtualenv is created in project directory
# This ensures the virtualenv is accessible to both root and appuser
ENV PIPENV_VENV_IN_PROJECT=1

# Copy dependency files first for better layer caching
COPY Pipfile Pipfile.lock /app/
COPY package.json package-lock.json /app/

# Install Python dependencies once
RUN pipenv install --dev

# Install Node dependencies once
RUN npm ci

# Copy to final location (including .venv)
RUN mkdir -p /opt/app && cp -a /app/. /opt/app/

WORKDIR /opt/app

# Copy application code (preserves .venv since it's in .dockerignore)
COPY . /opt/app

# build arguments
ARG APP_ENV

RUN npm run build

# Create non-root user for security - use consistent UID/GID across environments
RUN groupadd -r -g 10001 app && \
    useradd -r -u 10001 -g 10001 -m appuser

# Create directories and set ownership for non-root user to write files
# chown -R appuser:app /opt/app covers .venv and all other files/directories
# Production uses readOnlyRootFilesystem, so .venv must be readable by appuser
RUN mkdir -p /opt/app/tmp /opt/app/logs /opt/app/output /home/appuser/.cache /app/output && \
    chown -R appuser:app /opt/app /home/appuser /app/output

# Switch to appuser (dependencies already installed as root above)
USER appuser

CMD [ "npm", "start" ]
