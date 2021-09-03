import pkgutil
import homelab.commands as commands

COMMAND_LIST = []

for importer, modname, ispkg in pkgutil.iter_modules(commands.__path__):
    module = __import__(f'homelab.commands.{modname}', fromlist="dummy")
    COMMAND_LIST.append(module)
