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

import re
import shutil

import click
from flask.cli import AppGroup
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import User

group = AppGroup('user', help='User management commands.')

DEFAULT_FG = 'bright_green'
ERROR_FG = 'bright_red'


def validate_email(ctx, param, value):
    if not re.match(r'[^@]+@[^@]+\.[^@]+', value):
        click.secho('Not a valid email address.', fg=ERROR_FG)
        value = click.prompt(param.prompt)
        return validate_email(ctx, param, value)

    return value


@group.command('create')
@click.option('--email', '-e', prompt=True, callback=validate_email)
@click.option('--password', '-p', prompt=True, hide_input=True, confirmation_prompt=True)
@click.option('--admin', '-a', is_flag=True, prompt=True, default=False)
def user_create(email, password, admin):
    """Create user."""

    user = User()
    user.email = email
    user.is_admin = admin

    if len(password) < 6:
        click.secho('Password must be at least 6 characters long.', fg=ERROR_FG, err=True)
        return

    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        click.secho('Email is already in use.', fg=ERROR_FG, err=True)
        return

    click.secho(f'User created.', fg=DEFAULT_FG)


@group.command('delete')
@click.argument('users', nargs=-1, required=True)
@click.confirmation_option(prompt='Confirm')
def user_delete(users):
    """Delete user(s)."""

    users = set(users)
    user_query = User.query.filter(User.email.in_(users)).all()
    for user in user_query:
        db.session.delete(user)
        users.remove(user.email)
        click.secho(f'Deleted user: {user.email}', fg=DEFAULT_FG)

    db.session.commit()

    # Any user left in `users` doesn't exist.
    if users:
        invalid_users = ', '.join(users)
        click.secho(f'Invalid users: {invalid_users}', fg=ERROR_FG, err=True)


@group.command('list')
def user_list():
    """List users."""

    users = User.query.all()
    if len(users) == 0:
        click.secho(f'No users registered!', fg=ERROR_FG, err=True)
        return

    term_width, _ = shutil.get_terminal_size()
    if term_width > 40:
        term_width = 40

    seperator = ''.join('-' for _ in range(term_width))

    click.echo(click.style('Total: ', fg=DEFAULT_FG) + str(len(users)))
    if len(users) == 1:
        click.echo(seperator)

    for user in users:
        if len(users) > 1:
            click.echo(seperator)

        click.echo(click.style('ID: ', fg=DEFAULT_FG) + str(user.id))
        click.echo(click.style('Email: ', fg=DEFAULT_FG) + user.email)
        click.echo(click.style('Admin: ', fg=DEFAULT_FG) + str(user.is_admin))
        click.echo(click.style('Created: ', fg=DEFAULT_FG) + str(user.created_at.strftime('%Y-%m-%d %H:%M:%S')))
        click.echo(click.style('Uploads: ', fg=DEFAULT_FG) + str(len(user.files)))
        click.echo(click.style('Disk usage: ', fg=DEFAULT_FG) + user.get_disk_usage(humanize=True))

    if len(users) > 1:
        click.echo(seperator)
