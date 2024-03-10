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

from pathlib import Path

from pste import config

BASE = Path(__file__).parent.absolute()

# Needs to be loaded outside the flask extension as these are needed before we have an app context.
__config = config.dynaconf

ASSETS = Path(__config.get("paths.assets", BASE / "assets"))
TEMPLATES = Path(__config.get("paths.templates", BASE / "templates"))
RESOURCES = Path(__config.get("paths.resources", BASE / "resources"))
DATA = Path(__config.get("paths.data", BASE.parent / "data"))
UPLOADS = Path(__config.get("paths.uploads", DATA / "uploads"))
STATIC = Path(__config.get("paths.static", DATA / "static"))
NODE_MODULES = Path(__config.get("paths.node_modules", BASE.parent / "node_modules"))
