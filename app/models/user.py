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
import shutil

from passlib.hash import argon2
from sqlalchemy import func, event
from flask_login import UserMixin

from app import db, utils, login, BASE_DIR


@login.header_loader
def load_user_from_header(header):
    api_key = header.replace('Bearer ', '')
    return User.query.filter_by(api_key=api_key).first()


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


def generate_api_key():
    while True:
        key = utils.random_string(64)
        if not User.query.filter_by(api_key=key).first():
            break

    return key


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    api_key = db.Column(db.String(64), nullable=False, unique=True, default=generate_api_key)
    is_admin = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime(), nullable=False, server_default=func.now())
    files = db.relationship('File', backref='user', lazy=True)

    def set_password(self, password):
        self.password = argon2.hash(password)

    def check_password(self, password):
        return argon2.verify(password, self.password)

    def storage_directory(self):
        return f'{BASE_DIR}/storage/uploads/{self.id}'


def after_delete(mapper, connection, target):
    shutil.rmtree(target.storage_directory(), ignore_errors=True)


def after_insert(mapper, connection, target):
    os.makedirs(target.storage_directory(), exist_ok=True)


event.listen(User, 'after_delete', after_delete)
event.listen(User, 'after_insert', after_insert)
