#!/bin/sh
exec runuser -u "$APP_USER" -- "$@"
