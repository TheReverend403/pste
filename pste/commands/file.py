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

import click
from flask.cli import AppGroup

from pste import paths
from pste.extensions import db
from pste.models.file import File

group = AppGroup("file", help="File management commands.")

DEFAULT_FG = "bright_green"
ERROR_FG = "bright_red"


@group.command("clean")
def file_clean():
    """Deletes any orphaned files from data."""

    deleted_files = 0
    for root, _, files in os.walk(f"{paths.DATA}/uploads", topdown=False):
        for name in files:
            if File.query.filter_by(slug=name).first() is None:
                Path(f"{root}/{name}").unlink()
                deleted_files += 1

    click.secho(f"Deleted {deleted_files} orphaned file(s).", fg=DEFAULT_FG)


@group.command("delete")
@click.argument("files", nargs=-1, required=True)
@click.confirmation_option(prompt="Confirm")
def file_delete(files):
    """Delete file(s)."""

    file_query = File.query.filter(File.slug.in_(set(files))).all()
    for file in file_query:
        db.session.delete(file)
        click.secho(f"Deleted {file.slug}", fg=DEFAULT_FG)

    db.session.commit()
