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
import os
import subprocess

import yaml
from dynaconf import FlaskDynaconf
from flask import Flask
from flask_assets import Environment
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


try:
    PSTE_VERSION = 'pste ' + subprocess.check_output(['git', 'describe']).decode('UTF-8').strip()
except subprocess.CalledProcessError:
    # Not running from a git repo or git is not available.
    PSTE_VERSION = 'pste'

db = SQLAlchemy()
migrate = Migrate(compare_type=True, directory=f'{BASE_DIR}/migrations')
login = LoginManager()
csrf = CSRFProtect()
assets = Environment()
dynaconf = FlaskDynaconf()


def create_app():
    setup_logging()
    app = Flask('pste', static_folder=f'{BASE_DIR}/static', template_folder=f'{BASE_DIR}/templates')
    app.config.update(PSTE_VERSION=PSTE_VERSION, SQLALCHEMY_TRACK_MODIFICATIONS=False)
    app.logger.info(f'Running {PSTE_VERSION}')

    register_extensions(app)
    register_commands(app)
    register_blueprints(app)
    register_assets(app)
    return app


def register_commands(app):
    from pste import commands
    commands.init_app(app)
    app.logger.debug('Commands registered.')


def register_blueprints(app):
    from pste import views
    views.register_blueprints(app)
    app.logger.debug('Blueprints registered.')


def register_extensions(app):
    dynaconf.init_app(app)

    if 'SENTRY_DSN' in app.config and app.config['SENTRY_DSN'] and not app.debug:
        try:
            import sentry_sdk
        except ImportError:
            app.logger.warn('SENTRY_DSN is set but the sentry-sdk library is not available. Sentry will not be used.')
        else:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

            sentry_sdk.init(
                dsn=app.config['SENTRY_DSN'],
                environment=app.config['ENV'],
                release=PSTE_VERSION.replace('pste ', ''),
                integrations=[FlaskIntegration(), SqlalchemyIntegration()])

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)

    login.login_view = 'auth.login'
    app.logger.debug('Extensions registered.')


def register_assets(app):
    assets.init_app(app)
    with app.app_context():
        assets.directory = f'{BASE_DIR}/static'
        assets.append_path(f'{BASE_DIR}/assets')
        assets.auto_build = False

    assets.from_yaml(f'{BASE_DIR}/assets/assets.yml')
    app.logger.debug('Assets registered.')


def setup_logging(file=f'{os.path.dirname(BASE_DIR)}/config/logging.yml'):
    try:
        with open(file, 'r') as fd:
            logging.config.dictConfig(yaml.safe_load(fd.read()))
    except FileNotFoundError:
        setup_logging(f'{os.path.dirname(BASE_DIR)}/config/default/logging.yml')
