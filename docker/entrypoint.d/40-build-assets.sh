#!/bin/sh
runuser -u "$APP_USER" -- flask assets clean || true
runuser -u "$APP_USER" -- flask assets build
