# syntax=docker/dockerfile:1

ARG DEBIAN_VERSION=bookworm
ARG PYTHON_VERSION=3.13
ARG NODE_VERSION=20

## Base
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-${DEBIAN_VERSION}-slim AS python-base

ARG META_VERSION
ARG META_VERSION_HASH
ARG META_SOURCE

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT="/venv" \
    META_VERSION="${META_VERSION}" \
    META_VERSION_HASH="${META_VERSION_HASH}" \
    META_SOURCE="${META_SOURCE}"

ENV PATH="${UV_PROJECT_ENVIRONMENT}/bin:${PATH}" \
    PYTHONPATH="/app:${PYTHONPATH}"

WORKDIR /app


## Python builder
FROM python-base AS python-builder-base

RUN --mount=type=cache,target=/var/cache/apt,sharing=private \
    apt-get update && \
    apt-get install --no-install-recommends -y \
    build-essential \
    libffi-dev \
    libpq-dev \
    && apt-get autoclean && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=README.md,target=README.md \
    --mount=type=bind,source=LICENSE,target=LICENSE \
    uv sync --frozen --no-install-project --no-dev


## JS builder
FROM node:${NODE_VERSION}-${DEBIAN_VERSION}-slim AS node-builder-base

WORKDIR /opt/node

COPY yarn.lock package.json ./
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install --frozen-lockfile --prod


## Base image
FROM python-base AS flask-base

RUN --mount=type=cache,target=/var/cache/apt,sharing=private \
    apt-get update && \
    apt-get install --no-install-recommends -y \
    libpq5 \
    curl \
    libmagic1 \
    && apt-get autoclean && rm -rf /var/lib/apt/lists/*

COPY --from=node-builder-base /opt/node /opt/node
COPY --from=python-builder-base ${UV_PROJECT_ENVIRONMENT} ${UV_PROJECT_ENVIRONMENT}
COPY docker/rootfs /
COPY pste ./pste
COPY alembic.ini .

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
FROM flask-base AS development

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=README.md,target=README.md \
    --mount=type=bind,source=LICENSE,target=LICENSE \
    uv sync --frozen --no-install-project --group dev

ENV ENV_FOR_DYNACONF=development \
    FLASK_ENV=development \
    FLASK_DEBUG=1 \
    GUNICORN_OPTS="--reload --reload-extra-file /config" \
    # Don't compile assets on startup as built-in autobuild is used in dev/testing environments.
    SKIP_ASSETS=true


## Production image
FROM flask-base AS production

ENV ENV_FOR_DYNACONF=production \
    FLASK_ENV=production

HEALTHCHECK --start-interval=1s --start-period=10s --interval=10s --timeout=5s CMD ["/docker-healthcheck.sh"]
