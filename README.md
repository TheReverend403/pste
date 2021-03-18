# pste

[![License](https://img.shields.io/github/license/FoxDev/pste.svg)](https://www.gnu.org/licenses/gpl.txt)

Just a simple file hosting application inspired by the likes of pomf.se and teknik.io.

Very early alpha, 100% definitely not ready whatsoever for production use. Not even for a laugh.

[Demo (latest dev)](https://dev.pste.pw)

# Quick Installation (dev)

First, install [Poetry](https://poetry.eustace.io/).

```sh
git clone https://github.com/FoxDev/pste
cd pste
poetry install # optional features: poetry install --extras "mysql postgresql gunicorn sentry"
yarn install # or `npm install` if you're a caveman.
cp config/default/settings.yml config/settings.yml # Edit settings.yml
poetry shell

echo FLASK_APP=pste\nFLASK_ENV=development > .flaskenv

flask assets build
flask db upgrade
flask user create # Or use /auth/register

# Do not use this in production, use a WSGI server such as gunicorn with pste:create_app() as your entrypoint.
flask run
```
