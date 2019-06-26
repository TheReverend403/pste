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

from sqlalchemy import func, event

from app import db


class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    name = db.Column(db.String(255), nullable=False)
    size = db.Column(db.BigInteger, nullable=False)
    client_mimetype = db.Column(db.String(32), nullable=False)
    server_mimetype = db.Column(db.String(32), nullable=False)
    slug = db.Column(db.String(32), nullable=False, unique=True)
    file_hash = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False, server_default=func.now())

    def path(self):
        return f'{self.user.storage_directory()}/{self.slug}'

    def response_mimetype(self):
        # TODO: Implement sending of certain file types as text/plain.
        return self.server_mimetype


def after_delete(mapper, connection, target):
    try:
        os.remove(target.path())
    except OSError:
        pass


event.listen(File, 'after_delete', after_delete)
