#!/bin/sh

if test -d "$PATHS_STATIC/.webassets-cache"; then
    gosu "$APP_USER" flask assets clean
fi

gosu "$APP_USER" flask assets build
