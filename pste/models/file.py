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
from pathlib import Path

from flask import current_app as app
from sqlalchemy import event, func

from pste.extensions import db
from pste.utils import random_string


def generate_slug() -> str:
    url_length = app.config.get("MIN_URL_LENGTH", 3)

    while True:
        slug = random_string(url_length, extra_chars="-_~")
        if File.query.filter_by(slug=slug).first() is None:
            return slug
        url_length += 1


class File(db.Model):
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    name = db.Column(db.String(255), nullable=False)
    size = db.Column(db.BigInteger, nullable=False)
    client_mimetype = db.Column(db.String(128))
    server_mimetype = db.Column(db.String(128))
    slug = db.Column(db.Text(), nullable=False, unique=True)
    file_hash = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False, server_default=func.now())

    @property
    def path(self) -> Path:
        return self.user.storage_directory / self.slug

    @property
    def response_mimetype(self):
        ext = self.path.suffix
        if (
            ext
            and ext.lstrip(".") in app.config["PLAINTEXT_TYPES"]
            or self.server_mimetype.startswith("text/")
        ):
            return "text/plain"

        return self.server_mimetype

    def to_dict(self):
        return {
            "name": self.name,
            "size": self.size,
            "server_mimetype": self.server_mimetype,
            "client_mimetype": self.client_mimetype,
            "slug": self.slug,
            "hash": self.file_hash,
            "created_at": self.created_at,
        }


def after_delete(mapper, connection, target: File):
    try:
        os.remove(target.path)
    except OSError:
        pass


event.listen(File, "after_delete", after_delete)
