# pste

![GitHub](https://img.shields.io/github/license/TheReverend403/pste?style=flat-square)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/TheReverend403/pste/build-docker-image.yml?branch=main&style=flat-square)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg?style=flat-square)](https://github.com/astral-sh/ruff)

Just a simple file hosting application inspired by the likes of pomf.se and teknik.io.

Very early alpha, 100% definitely not ready whatsoever for production use. Not even for a laugh.

[Demo (latest dev)](https://dev.pste.pw)

# Quick Installation (dev)

First, install [Poetry](https://poetry.eustace.io/).

```sh
git clone https://github.com/TheReverend403/pste
cd pste
poetry install
yarn install # or `npm install` if you're a caveman.
cp pste/resources/config/settings.toml config/settings.toml # Edit settings.toml
poetry shell

echo FLASK_APP=pste\nFLASK_ENV=development > .flaskenv

flask assets build
flask db upgrade
flask user create # Or use /auth/register

# Do not use this in production, use a WSGI server such as gunicorn with pste:create_app() as your entrypoint.
flask run
```
