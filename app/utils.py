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
from pygments.lexers import guess_lexer

from app.models.file import File


def random_string(length):
    chars = ''.join(string.ascii_letters + string.digits)
    value = ''.join(random.choice(chars) for _ in range(length))
    return value


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{error}', category='error')


def generate_slug():
    length = 3

    while True:
        slug = random_string(length)
        if not File.query.filter_by(slug=slug).first():
            break
        length += 1

    return slug


def format_code(code):
    lexer = guess_lexer(code)
    return highlight(code, lexer, HtmlFormatter(linenos='table', anchorlinenos=True, lineanchors='line'))
