#!/bin/sh
gosu "$APP_USER" flask db upgrade
