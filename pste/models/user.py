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

import shutil
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from flask import Request
from flask import current_app as app
from flask_login import UserMixin
from humanize import naturalsize
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    String,
    event,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pste import paths, utils
from pste.extensions import db, login
from pste.security import hasher

if TYPE_CHECKING:
    from pste.models import File
else:
    File = "File"


@login.request_loader
def load_user_from_header(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header:
        api_key = auth_header.replace("Bearer ", "")
        return User.query.filter_by(api_key=api_key).first()
    return None


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

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    password: Mapped[str] = mapped_column(
        String(255), nullable=False, server_default=""
    )
    api_key: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, default=generate_api_key
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    storage_quota: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    files = relationship(File, back_populates="user", cascade="all,delete")

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
        return paths.DATA / "uploads" / str(self.id)

    def disk_usage(self, humanize: bool = False) -> int | str:
        total = sum(file.size for file in self.files)
        if humanize:
            return naturalsize(total, gnu=True)
        return total

    def quota(self, humanize: bool = False) -> int | str:
        quota = self.storage_quota or app.config.USER_STORAGE_LIMIT
        if humanize:
            quota = naturalsize(quota, gnu=True)

        return quota


def after_delete(mapper, connection, target: User):  # noqa: ARG001
    shutil.rmtree(target.storage_directory, ignore_errors=True)


def after_insert(mapper, connection, target: User):  # noqa: ARG001
    Path(target.storage_directory).mkdir(parents=True, exist_ok=True)


event.listen(User, "after_delete", after_delete)
event.listen(User, "after_insert", after_insert)
