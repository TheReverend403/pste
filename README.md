# pste

[![License](https://img.shields.io/github/license/FoxDev/pste.svg)](https://www.gnu.org/licenses/gpl.txt)
[![Keybase PGP](https://img.shields.io/keybase/pgp/TheReverend403.svg)](https://keybase.io/thereverend403)

Just a simple file hosting application inspired by the likes of pomf.se and teknik.io.

Very early alpha, 100% definitely not ready whatsoever for production use. Not even for a laugh.

[Demo (latest dev)](https://dev.pste.pw)

# Quick Installation (dev)

```sh
git clone https://github.com/FoxDev/pste
cd pste
pipenv install
cp .env.default .env # Edit .env
pipenv shell
flask db upgrade
flask user create # Or use /auth/register
flask run # Do not use this in production, use a WSGI server with app:create_app() as your entrypoint.
```
