import logging
import pathlib
import sys
from types import TracebackType
from typing import Type

LOGGER = logging.getLogger("Slome Launcher")
LOGGER.setLevel(logging.ERROR)
fileHandler = logging.FileHandler(pathlib.Path.home() / "AppData" / "Roaming" / ".Unofficial Slome Launcher" / "crash.log", mode="w", encoding="utf-8", delay=True)
fileHandler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(message)s", datefmt="%d-%m-%Y %H:%M:%S",))
consoleHandler = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(fileHandler)
LOGGER.addHandler(consoleHandler)
LOGGER.propagate = False

def handleException(excType: Type[BaseException], excValue: BaseException, excTraceback: TracebackType):
    if issubclass(excType, KeyboardInterrupt):
        sys.__excepthook__(excType, excValue, excTraceback)
        return
    LOGGER.error("An unhandled exception occurred:", exc_info=(excType, excValue, excTraceback))