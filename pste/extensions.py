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

from importlib.util import find_spec

from dynaconf import FlaskDynaconf
from flask_assets import Environment
from flask_login import LoginManager
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from pste import config

dynaconf = FlaskDynaconf(dynaconf_instance=config.dynaconf)
db = SQLAlchemy()
session = Session()
login = LoginManager()
csrf = CSRFProtect()
assets = Environment()
debugbar = None

if find_spec("flask_debugtoolbar"):
    from flask_debugtoolbar import DebugToolbarExtension

    debugbar = DebugToolbarExtension()
