FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

WORKDIR /app

RUN apt-get update -y && \
    apt-get install -y build-essential git curl jq \
        libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 \
        libnss3 libxss1 libasound2 libxtst6 xauth xvfb tzdata software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update -y && \
    apt-get install -y python3.12 python3.12-venv python3-pip && \
    ln -sf /usr/bin/python3.12 /usr/local/bin/python3 && \
    pip3 install pipenv

# Install Node.js
RUN curl -sL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    node --version && npm --version

COPY Pipfile Pipfile.lock ./

# ✅ Key fix here:
RUN pipenv install --dev --python /usr/bin/python3.12

RUN cp -a /app/. /.project/
COPY package.json package-lock.json /.project/
RUN cd /.project && npm ci

RUN mkdir -p /opt/app && cp -a /.project/. /opt/app/
WORKDIR /opt/app
COPY . /opt/app

ARG APP_ENV
RUN npm run build
CMD ["npm", "start"]
