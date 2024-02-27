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

import click
import email_validator
from flask.cli import AppGroup

from pste.extensions import db
from pste.models.user import User

group = AppGroup("user", help="User management commands.")

DEFAULT_FG = "bright_green"
ERROR_FG = "bright_red"
PASSWORD_MIN_LEN = 6
TERM_WIDTH_MAX = 40


def validate_email(ctx, param, value):
    try:
        email_validator.validate_email(value, check_deliverability=False)
    except email_validator.EmailNotValidError:
        click.secho("Not a valid email address.", fg=ERROR_FG)
        value = click.prompt(param.prompt)
        return validate_email(ctx, param, value)
    return value


@group.command("create")
@click.option("--email", "-e", prompt=True, callback=validate_email)
@click.password_option()
@click.option("--admin", "-a", is_flag=True, prompt=True, default=False)
def user_create(email, password, admin):
    """Create user."""

    user = User()
    user.email = email.lower()
    user.is_admin = admin

    if User.query.filter_by(email=user.email).first() is not None:
        click.secho("Email is already in use.", fg=ERROR_FG, err=True)
        return

    if len(password) < PASSWORD_MIN_LEN:
        click.secho(
            f"Password must be at least {PASSWORD_MIN_LEN} characters long.",
            fg=ERROR_FG,
            err=True,
        )
        return

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    click.secho("User created.", fg=DEFAULT_FG)


@group.command("delete")
@click.argument("users", nargs=-1, required=True)
@click.confirmation_option(prompt="Confirm")
def user_delete(users):
    """Delete user(s)."""

    user_query = User.query.filter(User.email.in_(set(users))).all()
    for user in user_query:
        db.session.delete(user)
        click.secho(f"Deleted {user.email}", fg=DEFAULT_FG)

    db.session.commit()


@group.command("list")
def user_list():
    """List users."""

    users = User.query.all()
    if len(users) == 0:
        click.secho("No users registered!", fg=ERROR_FG, err=True)
        return

    term_width, _ = shutil.get_terminal_size()
    if term_width > TERM_WIDTH_MAX:
        term_width = TERM_WIDTH_MAX

    seperator = "".join("-" for _ in range(term_width))

    click.echo(click.style("Total: ", fg=DEFAULT_FG) + str(len(users)))
    if len(users) == 1:
        click.echo(seperator)

    for user in users:
        if len(users) > 1:
            click.echo(seperator)

        click.echo(click.style("ID: ", fg=DEFAULT_FG) + str(user.id))
        click.echo(click.style("Email: ", fg=DEFAULT_FG) + user.email)
        click.echo(click.style("Admin: ", fg=DEFAULT_FG) + str(user.is_admin))
        click.echo(
            click.style("Created: ", fg=DEFAULT_FG)
            + str(user.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        )
        click.echo(click.style("Uploads: ", fg=DEFAULT_FG) + str(user.file_count))
        click.echo(
            click.style("Disk usage: ", fg=DEFAULT_FG) + user.disk_usage(humanize=True)
        )

    if len(users) > 1:
        click.echo(seperator)
