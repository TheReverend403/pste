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

import click
from flask.cli import AppGroup
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import User


def validate_email(ctx, param, value):
    if not re.match(r'[^@]+@[^@]+\.[^@]+', value):
        click.secho('Not a valid email address.', fg='red')
        value = click.prompt(param.prompt)
        return validate_email(ctx, param, value)

    return value


group = AppGroup('user', help='User management commands.')


@group.command('create')
@click.option('--email', '-e', prompt=True, callback=validate_email)
@click.option('--password', '-p', prompt=True, hide_input=True, confirmation_prompt=True)
@click.option('--admin', '-a', is_flag=True, prompt=True, default=False)
def user_create(email, password, admin):
    """Create user."""

    user = User()
    user.email = email
    user.is_admin = admin
    user.set_password(password)
    user.generate_api_key()

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        click.secho('Email is already in use.', fg='red', err=True)
        return


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

    for user in users:
        click.secho(f'Invalid user: {user}', fg='red', err=True)

    db.session.commit()
