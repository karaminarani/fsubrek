import os
from importlib import import_module

from bot.utils.logger import Logger

_dir = os.path.join(os.path.dirname(__file__))


def loadplugin():
    for file in os.listdir(_dir):
        filepath = os.path.join(_dir, file)
        if (
            file.endswith('.py')
            and os.path.isfile(filepath)
            and file != '__init__.py'
        ):
            module = file[:-3]
            try:
                import_module(
                    f'.{module}',
                    package=__name__,
                )
                Logger.info(
                    f'{module.title()} Plugin Imported',
                )
            except ImportError:
                Logger.warning(
                    f'{module.title()} Plugin Failed',
                )
