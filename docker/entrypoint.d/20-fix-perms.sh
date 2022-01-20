#!/bin/sh

if test -z "$PUID" && test -z "$PGID"; then
    echo "Neither PUID or PGID are set, skipping permission changes."
    exit 0
fi

if test -n "$PUID"; then
    echo "Changing UID of $APP_USER to $PUID"
    usermod -u "$PUID" "$APP_USER"
fi

if test -n "$PGID"; then
    echo "Changing GID of $APP_USER to $PGID"
    groupmod -g "$PGID" "$APP_USER"
fi

echo "Changing ownership of app files"
chown -R "$APP_USER:$APP_USER" /config /data /app /static
