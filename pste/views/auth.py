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

from flask import (
    Blueprint,
    abort,
    current_app as app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from pste.extensions import db
from pste.forms.auth import LoginForm, RegistrationForm
from pste.models import User
from pste.utils import flash_errors

blueprint = Blueprint("auth", __name__, url_prefix="/auth")


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("web.index"))

    form = LoginForm(request.form)

    if request.method == "GET":
        return render_template("auth/login.html", title="Sign in", form=form)

    if not form.validate_on_submit():
        flash_errors(form)
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=form.email.data.lower()).first()

    if user is None or not user.check_password(form.password.data):
        flash("Invalid email or password.", category="error")
        return redirect(url_for("auth.login"))

    # Upgrade from uPste imported passwords, or update if hash parameters have changed.
    if user.password_needs_update():
        user.set_password(form.password.data)
        db.session.commit()

    login_user(user, remember=True)

    next_page = request.args.get("next")
    if not next_page or url_parse(next_page).netloc != "":
        next_page = url_for("web.index")

    return redirect(next_page)


@blueprint.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect(url_for("web.index"))


@blueprint.route("/register", methods=["GET", "POST"])
def register():
    if not app.config["ENABLE_REGISTRATION"]:
        abort(404)

    if current_user.is_authenticated:
        return redirect(url_for("web.index"))

    form = RegistrationForm(request.form)
    if request.method == "GET":
        return render_template("auth/register.html", title="Register", form=form)

    if not form.validate_on_submit():
        flash_errors(form)
        return redirect(url_for("auth.register"))

    email = form.email.data.lower()
    if User.query.filter_by(email=email).first() is not None:
        flash("Email is already in use.", "error")
        return redirect(url_for("auth.register"))

    user = User()
    user.email = email
    user.set_password(form.password.data)

    db.session.add(user)
    db.session.commit()

    login_user(user)
    return redirect(url_for("auth.login"))
