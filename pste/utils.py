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
from flask_wtf import FlaskForm


def random_string(length: int, extra_chars: str = "") -> str:
    value = "".join(
        random.choice(string.ascii_letters + string.digits + extra_chars)
        for _ in range(length)
    )
    return value


def flash_errors(form: FlaskForm):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, category="error")
