#!/bin/sh
set -eu

if [ -z "$(find "${ROOT_PATH_FOR_DYNACONF}" -type f -mindepth 1 -maxdepth 1)" ]; then
    echo "Copying default settings.yml to ${ROOT_PATH_FOR_DYNACONF}"
    cp -au "${FLASK_APP}/resources/config/settings.yml" "${ROOT_PATH_FOR_DYNACONF}"
fi

if [ "${SKIP_MIGRATIONS:-false}" = "false" ]; then
    flask db migrate
else
    echo "Skipping migrations due to SKIP_MIGRATIONS=${SKIP_MIGRATIONS}"
fi

if [ "${SKIP_ASSETS:-false}" = "false" ]; then
    if [ -d "${CFG_PATHS__STATIC}/.webassets-cache" ]; then
        flask assets clean
    fi
    flask assets build
else
    echo "Skipping assets due to SKIP_ASSETS=${SKIP_ASSETS}"
fi

# shellcheck disable=SC2086
exec gunicorn "${FLASK_APP}:create_app()" --worker-class gevent --bind "${GUNICORN_HOST}:${GUNICORN_PORT}" ${GUNICORN_OPTS:-}
