# syntax=docker/dockerfile:1

ARG DEBIAN_VERSION=bookworm
ARG PYTHON_VERSION=3.12
ARG NODE_VERSION=20

## Base
FROM python:${PYTHON_VERSION}-slim-${DEBIAN_VERSION} as python-base
ARG ARG_APP_USER=app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION="" \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" \
    NODE_MODULES="/opt/node" \
    S6_DOWNLOAD_PATH="/opt/s6" \
    SETTINGS_FILE_FOR_DYNACONF="/config/settings.yml" \
    GUNICORN_HOST="0.0.0.0" \
    GUNICORN_PORT=5000 \
    FLASK_APP="pste" \
    PATHS_STATIC="/static" \
    PATHS_DATA="/data" \
    S6_CMD_WAIT_FOR_SERVICES_MAXTIME=0 \
    S6_BEHAVIOUR_IF_STAGE2_FAILS=2 \
    APP_USER=$ARG_APP_USER

ENV PATHS_NODE_MODULES=$NODE_MODULES \
    PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"


FROM python-base as s6-base

RUN --mount=type=cache,target=/var/cache/apt,sharing=private \
    apt-get update && \
    apt-get install --no-install-recommends -y \
    xz-utils \
    && apt-get autoclean && rm -rf /var/lib/apt/lists/*

ARG S6_OVERLAY_VERSION="3.0.0.2"

ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch-${S6_OVERLAY_VERSION}.tar.xz /tmp
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64-${S6_OVERLAY_VERSION}.tar.xz /tmp
RUN mkdir -p "$S6_DOWNLOAD_PATH" && \
    tar -C "$S6_DOWNLOAD_PATH/" -Jxpf /tmp/s6-overlay-x86_64-${S6_OVERLAY_VERSION}.tar.xz && \
    tar -C "$S6_DOWNLOAD_PATH/" -Jxpf /tmp/s6-overlay-noarch-${S6_OVERLAY_VERSION}.tar.xz


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

# Install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python -

# Copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# Install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main


## JS builder
FROM node:${NODE_VERSION}-bullseye-slim as node-builder-base

ENV NODE_MODULES="/opt/node"
WORKDIR $NODE_MODULES

COPY yarn.lock package.json ./
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install


## Dev image
FROM python-base as development

RUN --mount=type=cache,target=/var/cache/apt,sharing=private \
    apt-get update && \
    apt-get install --no-install-recommends -y \
    libpq5 \
    libmagic1 \
    && apt-get autoclean && rm -rf /var/lib/apt/lists/*

WORKDIR $PYSETUP_PATH

COPY --from=python-builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY --from=python-builder-base $POETRY_HOME $POETRY_HOME
COPY --from=node-builder-base $NODE_MODULES/node_modules $NODE_MODULES/

RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root

COPY --from=s6-base $S6_DOWNLOAD_PATH /
COPY docker/rootfs /

RUN addgroup --gid 1000 --system $APP_USER && \
    adduser --uid 1000 --system --gid 1000 --no-create-home $APP_USER

WORKDIR /app

ENV FLASK_DEBUG=1 \
    FLASK_ENV="development"

VOLUME ["/static", "/config", "/data"]
EXPOSE 5000

ENTRYPOINT ["/init"]


## Production image
FROM python-base as production

RUN --mount=type=cache,target=/var/cache/apt,sharing=private \
    apt-get update && \
    apt-get install --no-install-recommends -y \
    curl \
    libpq5 \
    libmagic1 \
    && apt-get autoclean && rm -rf /var/lib/apt/lists/*

COPY --from=python-builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY --from=node-builder-base $NODE_MODULES/node_modules $NODE_MODULES/

COPY --from=s6-base $S6_DOWNLOAD_PATH /
COPY docker/rootfs /

RUN addgroup --gid 1000 --system $APP_USER && \
    adduser --uid 1000 --system --gid 1000 --no-create-home $APP_USER

WORKDIR /app

COPY --chown=$APP_USER:$APP_USER ./pste ./pste

ENV FLASK_ENV="production"

VOLUME ["/static", "/config", "/data"]
EXPOSE 5000

HEALTHCHECK --start-interval=1s --start-period=10s --interval=10s --timeout=5s CMD ["/docker-healthcheck.sh"]
ENTRYPOINT ["/init"]
