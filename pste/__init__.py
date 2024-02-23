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

import subprocess

import sentry_sdk
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from webassets import Bundle
from werkzeug.middleware.proxy_fix import ProxyFix

from pste import paths
from pste.extensions import assets, csrf, db, dynaconf, login, migrate

try:
    PSTE_VERSION = (
        "pste "
        + subprocess.check_output(["/usr/bin/git", "describe"]).decode("UTF-8").strip()  # noqa: S603
    )
except FileNotFoundError:
    # Not running from a git repo or git is not available.
    PSTE_VERSION = "pste"


def create_app():
    app = Flask(
        "pste",
        static_folder=str(paths.STATIC),
        template_folder=str(paths.TEMPLATES),
    )

    load_configuration(app)
    register_extensions(app)
    register_commands(app)
    register_blueprints(app)
    register_assets(app)

    if not app.debug and not app.testing:
        app.wsgi_app = ProxyFix(app.wsgi_app)

    return app


def register_commands(app):
    from pste import commands

    commands.init_app(app)
    app.logger.debug("Commands registered.")


def register_blueprints(app):
    from pste import views

    views.register_blueprints(app)
    app.logger.debug("Blueprints registered.")


def init_sentry(app):
    if (dsn := app.config.get("sentry_dsn")) and not (app.debug or app.testing):
        app.logger.info("Sentry enabled.")
        sentry_sdk.init(
            dsn=dsn,
            environment="production",
            release=PSTE_VERSION.replace("pste ", ""),
            integrations=[FlaskIntegration(), SqlalchemyIntegration()],
        )
    else:
        app.logger.debug("Sentry disabled.")


def load_configuration(app):
    dynaconf.init_app(app)
    app.config.update(
        PSTE_VERSION=PSTE_VERSION,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        DEBUG_TB_INTERCEPT_REDIRECTS=False,
        SESSION_USE_SIGNER=True,
        PERMANENT_SESSION_LIFETIME=604800,
    )


def register_extensions(app):
    init_sentry(app)
    db.init_app(app)
    migrate.init_app(app, db, directory=paths.BASE / "migrations")
    csrf.init_app(app)
    assets.init_app(app)
    login.init_app(app)

    app.config.update(SESSION_SQLALCHEMY=db)
    login.login_view = "auth.login"

    from pste.extensions import debugbar

    if app.debug and debugbar is not None:
        debugbar.init_app(app)

    app.logger.debug("Extensions registered.")


def register_assets(app):
    bundles = {
        "css-pygments": Bundle(
            "css/pygments.css",
            filters="cssmin",
            output="css/pygments-%(version)s.css",
        ),
        "css-dropzone": Bundle(
            f"{paths.NODE_MODULES}/dropzone/dist/dropzone.css",
            filters="cssmin",
            output="css/vendor/dropzone-%(version)s.css",
        ),
        "css-app": Bundle(
            "scss/app.scss",
            "css/starwars-glyphicons.css",
            filters="libsass,cssmin",
            output="css/app-%(version)s.css",
        ),
        "js-jquery": Bundle(
            f"{paths.NODE_MODULES}/jquery/dist/jquery.slim.js",
            filters="rjsmin",
            output="js/vendor/jquery-%(version)s.js",
        ),
        "js-popper": Bundle(
            f"{paths.NODE_MODULES}/popper.js/dist/umd/popper.js",
            filters="rjsmin",
            output="js/vendor/popper-%(version)s.js",
        ),
        "js-bootstrap": Bundle(
            f"{paths.NODE_MODULES}/bootstrap/dist/js/bootstrap.js",
            filters="rjsmin",
            output="js/vendor/bootstrap-%(version)s.js",
        ),
        "js-dropzone": Bundle(
            f"{paths.NODE_MODULES}/dropzone/dist/dropzone.js",
            filters="rjsmin",
            output="js/vendor/dropzone-%(version)s.js",
        ),
        "js-app": Bundle(
            "js/app.js",
            filters="rjsmin",
            output="js/app-%(version)s.js",
        ),
    }

    with app.app_context():
        assets.directory = app.static_folder
        assets.append_path(paths.ASSETS)

    for name, bundle in bundles.items():
        assets.register(name, bundle)

    app.logger.debug("Assets registered.")
