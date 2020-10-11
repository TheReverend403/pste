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

import random
import string

from flask import flash
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_for_mimetype, guess_lexer
from pygments.lexers.special import TextLexer
from pygments.util import ClassNotFound


def random_string(length):
    value = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )
    return value


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{error}", category="error")


def syntax_highlight(file):
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
