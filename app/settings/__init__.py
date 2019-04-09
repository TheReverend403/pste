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

"""
DON'T EDIT THIS FILE
Copy default.py to local.py and use that instead.
"""

DEBUG = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

USER_ENABLE_USERNAME = False
USER_CONFIRM_EMAIL_EXPIRATION = 7*24*3600  # 7 Days
USER_RESET_PASSWORD_EXPIRATION = 24*3600  # 1 Day
USER_INVITE_EXPIRATION = 7*24*3600  # 7 Days

USER_LOGIN_URL = '/user/login'
USER_LOGOUT_URL = '/user/logout'
USER_REGISTER_URL = '/user/register'
USER_CONFIRM_EMAIL_URL = '/user/confirm/<token>'
USER_EDIT_USER_PROFILE_URL = '/user/edit'
USER_EMAIL_ACTION_URL = '/user/email/<id>/<action>'
USER_RESEND_EMAIL_CONFIRMATION_URL = '/user/resend-email-confirmation'

SENTRY_DSN = ''
