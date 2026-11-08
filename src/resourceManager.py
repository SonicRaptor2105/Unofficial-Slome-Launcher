import sys
from pathlib import Path
from typing import Union

def getResourcePath(relativePath: Union[str, Path]): #Check if the assets are local or if they're bundled into the
    try:
        basePath = Path(sys._MEIPASS)
    except:
        basePath = Path.cwd()
    return basePath / relativePath