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

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from flask import current_app as app
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_for_mimetype, guess_lexer
from pygments.lexers.special import TextLexer
from pygments.util import ClassNotFound
from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    String,
    Text,
    event,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pste import db
from pste.utils import random_string

if TYPE_CHECKING:
    from pste.models import User
else:
    User = "User"


def generate_slug() -> str:
    url_length = app.config.get("MIN_URL_LENGTH", 3)

    while True:
        slug = random_string(url_length, extra_chars="-_~")
        if File.query.filter_by(slug=slug).first() is None:
            return slug
        url_length += 1


class File(db.Model):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    client_mimetype: Mapped[str | None] = mapped_column(String(128))
    server_mimetype: Mapped[str | None] = mapped_column(String(128))
    slug: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    user: Mapped[User] = relationship(User, back_populates="files")

    @property
    def path(self) -> Path:
        return self.user.storage_directory / self.slug

    @property
    def response_mimetype(self) -> str:
        ext = self.path.suffix
        if (
            ext and ext.lstrip(".") in app.config.PLAINTEXT_TYPES
        ) or self.server_mimetype.startswith("text/"):
            return "text/plain"

        return self.server_mimetype

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "size": self.size,
            "server_mimetype": self.server_mimetype,
            "client_mimetype": self.client_mimetype,
            "slug": self.slug,
            "hash": self.file_hash,
            "created_at": self.created_at,
        }


def after_delete(mapper, connection, target: File):  # noqa: ARG001
    target.path.unlink(missing_ok=True)


event.listen(File, "after_delete", after_delete)


def syntax_highlight(file: File) -> str:
    code = file.path.read_text()
    try:
        lexer = get_lexer_for_mimetype(file.client_mimetype)
    except ClassNotFound:
        try:
            lexer = guess_lexer(code)
        except ClassNotFound:
            lexer = TextLexer()

    return highlight(
        code,
        lexer,
        HtmlFormatter(linenos="table", anchorlinenos=True, lineanchors="line"),
    )
