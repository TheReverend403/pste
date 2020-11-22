#  This file is part of pste.
#
#  pste is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  pste is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with pste.  If not, see <https://www.gnu.org/licenses/>.

import logging.config
import subprocess
from pathlib import Path

import sentry_sdk
import yaml
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from pste import extensions

BASE_DIR = Path(__file__).parent.absolute()
CONFIG_DIR = BASE_DIR.parent / "config"


try:
    PSTE_VERSION = (
        "pste " + subprocess.check_output(["git", "describe"]).decode("UTF-8").strip()
    )
except subprocess.CalledProcessError:
    # Not running from a git repo or git is not available.
    PSTE_VERSION = "pste"


def create_app():
    setup_logging()
    app = Flask(
        "pste",
        static_folder=str(BASE_DIR / "static"),
        template_folder=str(BASE_DIR / "templates"),
    )
    app.config.update(PSTE_VERSION=PSTE_VERSION, SQLALCHEMY_TRACK_MODIFICATIONS=False)
    app.logger.info(f"Running {PSTE_VERSION}")

    register_extensions(app)
    register_commands(app)
    register_blueprints(app)
    register_assets(app)
    return app


def register_commands(app):
    from pste import commands

    commands.init_app(app)
    app.logger.debug("Commands registered.")


def register_blueprints(app):
    from pste import views

    views.register_blueprints(app)
    app.logger.debug("Blueprints registered.")


def register_extensions(app):
    extensions.dynaconf.init_app(app)

    if "SENTRY_DSN" in app.config and app.config["SENTRY_DSN"] and not app.debug:
        sentry_sdk.init(
            dsn=app.config["SENTRY_DSN"],
            environment=app.config["ENV"],
            release=PSTE_VERSION.replace("pste ", ""),
            integrations=[FlaskIntegration(), SqlalchemyIntegration()],
        )

    extensions.db.init_app(app)
    extensions.migrate.init_app(app, extensions.db, directory=BASE_DIR / "migrations")
    extensions.login.init_app(app)
    extensions.csrf.init_app(app)
    extensions.assets.init_app(app)

    extensions.login.login_view = "auth.login"
    app.logger.debug("Extensions registered.")


def register_assets(app):
    with app.app_context():
        extensions.assets.directory = BASE_DIR / "static"
        extensions.assets.append_path(BASE_DIR / "assets")
        extensions.assets.auto_build = False

    extensions.assets.from_yaml(str(BASE_DIR / "assets" / "assets.yml"))
    app.logger.debug("Assets registered.")


def setup_logging(file: Path = CONFIG_DIR / "logging.yml"):
    try:
        logging.config.dictConfig(yaml.safe_load(file.read_text()))
    except FileNotFoundError:
        setup_logging(CONFIG_DIR / "default" / "logging.yml")
