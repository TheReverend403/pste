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

from environs import Env

PLAINTEXT_TYPES = [
    'txt', 'php', 'rb', 'sh', 'py',
    'conf', 'c', 'cpp', 'java', 'rs',
    'html', 'htm', 'js', 'xml', 'sql',
    'lua', 'cs', 'pl', 'md', 'ini',
    'shtml', 'yaml', 'cfg', 'go', 'fish',
    'yml', 'bash'
]

env = Env()
env.read_env()

APP_NAME = env.str('APP_NAME', 'pste')
SECRET_KEY = env.str('SECRET_KEY')
SQLALCHEMY_DATABASE_URI = env.str('DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False

ENABLE_REGISTRATION = env.bool('ENABLE_REGISTRATION', False)

with env.prefixed('MAIL_'):
    MAIL_SERVER = env.str('SERVER')
    MAIL_PORT = env.int('PORT')
    MAIL_USE_TLS = env.bool('USE_TLS')
    MAIL_USERNAME = env.str('USERNAME')
    MAIL_PASSWORD = env.str('PASSWORD')
    MAIL_DEFAULT_SENDER = env.str('FROM')

# Sentry
# https://sentry.io
SENTRY_DSN = env.str('SENTRY_DSN')
