# syntax=docker/dockerfile:1

ARG DEBIAN_VERSION=bookworm
ARG PYTHON_VERSION=3.12
ARG NODE_VERSION=20

## Base
FROM python:${PYTHON_VERSION}-slim-${DEBIAN_VERSION} as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    # Latest
    POETRY_VERSION="" \
    VIRTUAL_ENV="/venv"

ENV PATH="${POETRY_HOME}/bin:${VIRTUAL_ENV}/bin:${PATH}" \
    PYTHONPATH="/app:${PYTHONPATH}"

RUN python -m venv "${VIRTUAL_ENV}"

WORKDIR /app


## Python builder
FROM python-base as python-builder-base

RUN --mount=type=cache,target=/var/cache/apt,sharing=private \
    apt-get update && \
    apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    libffi-dev \
    libpq-dev \
    && apt-get autoclean && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python3 -

COPY poetry.lock pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main


## JS builder
FROM node:${NODE_VERSION}-${DEBIAN_VERSION}-slim as node-builder-base

WORKDIR /opt/node

COPY yarn.lock package.json ./
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install


## Base image
FROM python-base as flask-base

RUN --mount=type=cache,target=/var/cache/apt,sharing=private \
    apt-get update && \
    apt-get install --no-install-recommends -y \
    libpq5 \
    curl \
    libmagic1 \
    && apt-get autoclean && rm -rf /var/lib/apt/lists/*

COPY --from=node-builder-base /opt/node /opt/node
COPY --from=python-builder-base ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY docker/rootfs /
COPY pste ./pste

ENV ROOT_PATH_FOR_DYNACONF="/config" \
    GUNICORN_HOST="0.0.0.0" \
    GUNICORN_PORT=5000 \
    FLASK_APP="pste" \
    CFG_PATHS__STATIC="/data/static" \
    CFG_PATHS__DATA="/data" \
    CFG_PATHS__NODE_MODULES="/opt/node/node_modules"

VOLUME ["/config", "/data"]
EXPOSE 5000

ENTRYPOINT ["/docker-entrypoint.sh"]


## Dev image
FROM flask-base as development

COPY --from=python-builder-base ${POETRY_HOME} ${POETRY_HOME}
COPY poetry.lock pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root

ENV ENV_FOR_DYNACONF=development \
    FLASK_ENV=development \
    FLASK_DEBUG=1 \
    GUNICORN_OPTS="--reload --reload-extra-file /config" \
    # Don't compile assets on startup as built-in autobuild is used in dev/testing environments.
    SKIP_ASSETS=true


## Production image
FROM flask-base as production

ENV ENV_FOR_DYNACONF=production \
    FLASK_ENV=production

HEALTHCHECK --start-interval=1s --start-period=10s --interval=10s --timeout=5s CMD ["/docker-healthcheck.sh"]
