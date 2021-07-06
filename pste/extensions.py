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

from dynaconf import Dynaconf, FlaskDynaconf
from flask_assets import Environment
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from pste.paths import CONFIG_DIR

db = SQLAlchemy()
migrate = Migrate(compare_type=True)
login = LoginManager()
csrf = CSRFProtect()
assets = Environment()
debugbar = DebugToolbarExtension()

dynaconf = FlaskDynaconf(
    dynaconf_instance=Dynaconf(
        settings_file=CONFIG_DIR / "config.yml",
        environments=False,
        envvar_prefix="PSTE",
        yaml_loader="safe_load",
    ),
)
