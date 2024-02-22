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
from pathlib import Path

from dynaconf import Dynaconf

BASE = Path(__file__).parent.absolute()
ASSETS = BASE / "assets"
TEMPLATES = BASE / "templates"
RESOURCES = BASE / "resources"

_paths_from_env = Dynaconf(envvar_prefix="PATHS")
NODE_MODULES = Path(_paths_from_env.get("NODE_MODULES", BASE.parent / "node_modules"))
STATIC = Path(_paths_from_env.get("STATIC", BASE.parent / "static"))
DATA = Path(_paths_from_env.get("DATA", BASE.parent / "data"))

for path in [STATIC, DATA]:
    path.mkdir(exist_ok=True)

shutil.copytree(str(ASSETS / "img"), str(STATIC / "img"), dirs_exist_ok=True)
shutil.copytree(str(ASSETS / "fonts"), str(STATIC / "fonts"), dirs_exist_ok=True)
