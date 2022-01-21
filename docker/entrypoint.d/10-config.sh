#!/bin/sh

if ! test -f "$SETTINGS_FILE_FOR_DYNACONF"; then
    echo "Copying default settings.yml"
    cp -rau /app/pste/resources/config/settings.yml "$SETTINGS_FILE_FOR_DYNACONF"
fi
