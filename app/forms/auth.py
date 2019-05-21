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

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import PasswordField, validators, BooleanField, SubmitField
from wtforms.fields.html5 import EmailField


class RegistrationForm(FlaskForm):
    email = EmailField('Email', [validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm password')
    recaptcha = RecaptchaField()


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[validators.Email()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')
