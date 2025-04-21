import importlib
import pkgutil

def load_all_processors():
    for _, modname, _ in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{__name__}.{modname}")