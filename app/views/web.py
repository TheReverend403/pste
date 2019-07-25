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

from flask import Blueprint, render_template, send_file, make_response
from flask_login import login_required

from app.models import File

blueprint = Blueprint('web', __name__)


@blueprint.route('/')
@login_required
def index():
    return render_template('main/index.html')


@blueprint.route('/f/<string:slug>')
def file(slug):
    file_instance = File.query.filter_by(slug=slug).first_or_404()

    response = make_response(send_file(file_instance.path()))
    response.headers['Content-Type'] = file_instance.response_mimetype()
    response.headers['Content-Disposition'] = f'inline; filename="{file_instance.name}"'
    return response
