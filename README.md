# pste

![GitHub](https://img.shields.io/github/license/TheReverend403/pste?style=flat-square)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/TheReverend403/pste/build-docker-image.yml?branch=main&style=flat-square)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg?style=flat-square)](https://github.com/astral-sh/ruff)

Just a simple file hosting application inspired by the likes of pomf.se and teknik.io.

Very early alpha, 100% definitely not ready whatsoever for production use. Not even for a laugh.

[Demo (latest dev)](https://dev.pste.pw)

## Setting up the development environment

First, install [uv](https://docs.astral.sh/uv/getting-started/installation/).

```sh
git clone https://github.com/TheReverend403/pste
cd pste

uv sync --group dev
uv run pre-commit install

yarn install
```

## Running

```sh
mkdir config
cp pste/resources/config/settings.toml config/settings.toml # Edit settings.toml

echo FLASK_APP=pste\nFLASK_ENV=development > .flaskenv

uv run flask assets build
uv run flask db upgrade
uv run flask user create # Or use /auth/register

# Do not use this in production, use a WSGI server such as gunicorn with pste:create_app() as your entrypoint.
uv run flask run
```
