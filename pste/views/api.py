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

import hashlib
import os
from pathlib import Path

import magic
from flask import Blueprint, current_app as app, jsonify, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from pste import csrf, db
from pste.forms.api import UploadForm
from pste.models.file import File
from pste.models.file import generate_slug

blueprint = Blueprint("api", __name__, url_prefix="/api")


@blueprint.route("<string:slug>", methods=["DELETE"])
@login_required
@csrf.exempt
def delete(slug):
    file = File.query.filter_by(user=current_user, slug=slug).first_or_404()
    db.session.delete(file)
    db.session.commit()
    return "", 204


@blueprint.route("list", methods=["GET"])
@login_required
def files():
    try:
        page = int(request.args.get("page", 0))
    except ValueError:
        page = 0

    file_query = File.query.filter_by(user=current_user)

    if page == 0:
        file_list = [file.to_dict() for file in file_query.all()]
    else:
        file_list = [
            file.to_dict() for file in file_query.paginate(page, 15, False).items
        ]

    return jsonify(file_list)


@blueprint.route("upload", methods=["POST"])
@login_required
@csrf.exempt
def upload():
    form = UploadForm(request.files)
    if not form.validate_on_submit():
        return {"errors": form.errors}

    fd = form.file.data

    fd.seek(0, os.SEEK_END)
    file_size = fd.tell()
    fd.seek(0)

    if (
        file_size + current_user.disk_usage() > current_user.quota()
        and not current_user.is_admin
    ):
        return {
            "errors": f"Storage limit reached ({current_user.quota(humanize=True)})"
        }

    file_contents = fd.read()
    fd.seek(0)

    file_hash = hashlib.sha256(file_contents).hexdigest()
    file_mimetype = magic.from_buffer(file_contents, mime=True)

    route_name = "web.file"
    extension = Path(fd.filename).suffix
    slug = generate_slug()
    if extension:
        slug = slug + extension

    existing_file = File.query.filter_by(user=current_user, file_hash=file_hash).first()
    if existing_file:
        existing_file.name = fd.filename
        db.session.commit()

        if existing_file.response_mimetype.startswith("text/"):
            route_name = "web.paste"

        return {"url": url_for(route_name, slug=existing_file.slug, _external=True)}

    file = File(user=current_user)
    file.name = fd.filename
    file.size = file_size
    file.file_hash = file_hash
    file.client_mimetype = fd.mimetype
    file.server_mimetype = file_mimetype
    file.slug = slug

    db.session.add(file)

    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        app.logger.error(exc)
        return {
            "errors": [
                "An error occured while processing your file. Try uploading again."
            ]
        }
    else:
        fd.save(file.path)

    if file.response_mimetype.startswith("text/"):
        route_name = "web.paste"

    return {"url": url_for(route_name, slug=file.slug, _external=True)}
