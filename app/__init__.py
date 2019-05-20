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

import os

from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

migrate = Migrate()
login = LoginManager()


def create_app():
    app = Flask('pste', static_folder=f'{BASE_DIR}/static')
    app.config.from_object('app.settings')

    try:
        app.config.from_object('app.settings.local')
    except ImportError:
        app.logger.error('pste is not configured. Copy app/settings/default.py to app/settings/local.py and edit it.')
        os._exit(1)

    if app.config['SENTRY_DSN']:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration

            sentry_sdk.init(dsn=app.config['SENTRY_DSN'], integrations=[FlaskIntegration()])
        except ImportError:
            app.logger.warn('SENTRY_ENABLED is True but sentry-sdk is not available. Sentry will not be used.')

    from app.models import db
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.views import register_blueprints
    register_blueprints(app)

    return app
