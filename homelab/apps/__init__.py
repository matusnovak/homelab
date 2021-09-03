import pkgutil
from typing import Dict, List
import homelab.apps as apps
from homelab.utils import App, Option

APPS: Dict[str, App] = {}
APPS_NAMES: List[str] = []

for importer, modname, ispkg in pkgutil.iter_modules(apps.__path__):
    module = __import__(f'homelab.apps.{modname}', fromlist="dummy")
    APPS[module.__name__.split('.')[-1]] = module.APP()

APPS_NAMES = APPS.keys()

APPS_OPTIONS: List[Option] = []

for _, app in APPS.items():
    APPS_OPTIONS.extend(app.options)
