#!/bin/sh
set -eu

curl -sSL "http://${GUNICORN_HOST}:${GUNICORN_PORT}" > /dev/null && echo "OK"
