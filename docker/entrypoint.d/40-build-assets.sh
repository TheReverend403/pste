#!/bin/sh

if test -d "$PATHS_STATIC/.webassets-cache"; then
    runuser -u "$APP_USER" -- flask assets clean
fi

runuser -u "$APP_USER" -- flask assets build
