import argparse
import logging
import sys
from src import *

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true", help="Turn on verbose logging")

LOGGER = logging.getLogger("Slome Launcher")
sys.excepthook = handleException

if __name__ == "__main__":
    args = parser.parse_args()
    if args.verbose:
        LOGGER.setLevel(logging.DEBUG)
    
    launcher = Launcher()
    launcher.mainloop()