#!/bin/sh
set -e
curl -sSL "http://$GUNICORN_HOST:$GUNICORN_PORT" > /dev/null && echo "OK"
