#!/bin/sh
runuser -u "$APP_USER" -- flask db upgrade
