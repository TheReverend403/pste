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

import click
from flask.cli import AppGroup

from pste import BASE_DIR, db
from pste.models import File

group = AppGroup('file', help='File management commands.')

DEFAULT_FG = 'bright_green'
ERROR_FG = 'bright_red'


@group.command('clean')
def file_clean():
    """Deletes any orphaned files from storage."""

    deleted_files = []
    for root, _, files in os.walk(f'{BASE_DIR}/storage/uploads', topdown=False):
        for name in files:
            if db.session.query(File.id).filter_by(slug=name).scalar() is None:
                os.remove(f'{root}/{name}')
                deleted_files.append(name)

    click.secho(f'Deleted {len(deleted_files)} orphaned file(s).', fg=DEFAULT_FG)
