import argparse
import logging
import sys
from types import TracebackType
from typing import Type
from launcher import *

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true", help="Turn on verbose logging")
args = parser.parse_args()

LOGGER = logging.getLogger("Slome Launcher")
LOGGER.setLevel(logging.DEBUG if args.verbose else logging.ERROR)
fileHandler = logging.FileHandler(pathlib.Path.home() / "AppData" / "Roaming" / ".Unofficial Slome Launcher" / "crash.log", mode="w", encoding="utf-8", delay=True)
fileHandler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(message)s", datefmt="%d-%m-%Y %H:%M:%S",))
LOGGER.addHandler(fileHandler)
LOGGER.propagate = False

def handleException(excType: Type[BaseException], excValue: BaseException, excTraceback: TracebackType):
    if issubclass(excType, KeyboardInterrupt):
        sys.__excepthook__(excType, excValue, excTraceback)
        return
    LOGGER.error("An unhandled exception occurred:", exc_info=(excType, excValue, excTraceback))



if __name__ == "__main__":
    sys.excepthook = handleException
    launcher = Launcher()
    launcher.mainloop()