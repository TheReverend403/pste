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

import click
from flask.cli import AppGroup

from app import db
from app.models import User

user_group = AppGroup('user')


@user_group.command('create')
@click.option('--email', '-e', prompt=True)
@click.option('--password', '-p', prompt=True, hide_input=True, confirmation_prompt=True)
@click.option('--admin', '-a', is_flag=True, prompt=True, default=False)
def create_user(email, password, admin):
    """Creates a new user."""

    user = User()
    user.email = email
    user.is_admin = admin
    user.set_password(password)
    user.generate_api_key()

    db.session.add(user)
    db.session.commit()

    click.echo('User created.')


@user_group.command('delete')
@click.option('--email', '-e', prompt=True)
@click.confirmation_option(prompt='Are you sure you want to delete this user?')
def delete_user(email):
    """Deletes a user."""

    user = User.query.filter_by(email=email).first()
    db.session.delete(user)
    db.session.commit()

    click.echo('User deleted.')


def init_app(app):
    app.cli.add_command(user_group)
