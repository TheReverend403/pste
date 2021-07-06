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
from pathlib import Path
from typing import Union

from flask import Request, current_app as app
from flask_login import UserMixin
from humanize import naturalsize
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    event,
    func,
)
from sqlalchemy.orm import relationship

from pste import utils
from pste.extensions import db, login
from pste.paths import BASE_DIR
from pste.security import hasher


@login.request_loader
def load_user_from_header(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header:
        api_key = auth_header.replace("Bearer ", "")
        return User.query.filter_by(api_key=api_key).first()


@login.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


def generate_api_key() -> str:
    while True:
        key = utils.random_string(64)
        if User.query.filter_by(api_key=key).first() is None:
            break

    return key


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False, server_default="")
    api_key = Column(String(64), nullable=False, unique=True, default=generate_api_key)
    is_admin = Column(Boolean, default=False)
    storage_quota = Column(BigInteger)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    files = relationship("File", back_populates="user", cascade="all,delete")

    def set_password(self, password: str):
        self.password = hasher.hash(password)

    def password_needs_update(self) -> bool:
        return hasher.needs_update(self.password)

    def check_password(self, password: str) -> bool:
        return hasher.verify(password, self.password)

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def storage_directory(self) -> Path:
        return BASE_DIR / "storage" / "uploads" / str(self.id)

    def disk_usage(self, humanize: bool = False) -> Union[int, str]:
        total = sum(file.size for file in self.files)
        if humanize:
            return naturalsize(total, gnu=True)
        return total

    def quota(self, humanize: bool = False) -> Union[int, str]:
        quota = self.storage_quota or app.config["USER_STORAGE_LIMIT"]
        if humanize:
            quota = naturalsize(quota, gnu=True)

        return quota


def after_delete(mapper, connection, target: User):
    shutil.rmtree(target.storage_directory, ignore_errors=True)


def after_insert(mapper, connection, target: User):
    os.makedirs(target.storage_directory, exist_ok=True)


event.listen(User, "after_delete", after_delete)
event.listen(User, "after_insert", after_insert)
