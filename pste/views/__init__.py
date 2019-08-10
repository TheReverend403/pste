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

from flask import render_template, request, jsonify

from pste.views.api import blueprint as api_blueprint
from pste.views.auth import blueprint as auth_blueprint
from pste.views.web import blueprint as web_blueprint


def register_blueprints(app):
    app.register_error_handler(404, page_not_found)
    app.register_blueprint(web_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(api_blueprint)


def page_not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Page not found'}), 404

    return render_template('errors/404.html', error=error, title='404'), 404
