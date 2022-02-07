ARG ARG_PYTHON_VERSION=3.9
ARG ARG_NODE_VERSION=17
ARG ARG_POETRY_VERSION=1.1.12

## Base
FROM python:${ARG_PYTHON_VERSION}-slim as python-base

ARG ARG_APP_USER=app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=$ARG_POETRY_VERSION \
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

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        xz-utils

ARG S6_OVERLAY_VERSION="3.0.0.2"

ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch-${S6_OVERLAY_VERSION}.tar.xz /tmp
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64-${S6_OVERLAY_VERSION}.tar.xz /tmp
RUN mkdir -p "$S6_DOWNLOAD_PATH" && \
    tar -C "$S6_DOWNLOAD_PATH/" -Jxpf /tmp/s6-overlay-x86_64-${S6_OVERLAY_VERSION}.tar.xz && \
    tar -C "$S6_DOWNLOAD_PATH/" -Jxpf /tmp/s6-overlay-noarch-${S6_OVERLAY_VERSION}.tar.xz


## Python builder
FROM python-base as python-builder-base

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        curl \
        build-essential \
        libffi-dev \
        libpq-dev

# Install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python -

# Copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# Install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --no-dev


## JS builder
FROM node:${ARG_NODE_VERSION}-bullseye-slim as node-builder-base

ENV NODE_MODULES="/opt/node"
WORKDIR $NODE_MODULES

COPY yarn.lock package.json ./
RUN yarn install


## Dev image
FROM python-base as development

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        libpq5 \
        libmagic1

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR $PYSETUP_PATH

COPY --from=python-builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY --from=python-builder-base $POETRY_HOME $POETRY_HOME
COPY --from=node-builder-base $NODE_MODULES/node_modules $NODE_MODULES/

RUN poetry install

COPY --from=s6-base $S6_DOWNLOAD_PATH /
COPY docker/rootfs /

RUN addgroup --gid 1000 --system $APP_USER && \
    adduser --uid 1000 --system --gid 1000 --no-create-home $APP_USER

WORKDIR /app

ENV FLASK_ENV="development"

VOLUME ["/static", "/config", "/data"]
EXPOSE 5000

ENTRYPOINT ["/init"]


## Production image
FROM python-base as production

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        curl \
        libpq5 \
        libmagic1

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

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

HEALTHCHECK --interval=10s --timeout=5s CMD ["/bin/healthcheck"]
ENTRYPOINT ["/init"]
