import sys
import zipfile
import pathlib
import shutil
from typing import Union
from src.constants import VALIDSLOMEVERSIONS, HOME, LOGGER

def getResourcePath(relativePath: Union[str, pathlib.Path]): #Check if the assets are local or if they're bundled into the
    try:
        basePath = pathlib.Path(sys._MEIPASS)
    except:
        basePath = pathlib.Path.cwd()
    return basePath / relativePath

def checkForVersions():
    fp = HOME / "versions"
    if not fp.exists():
        fp.mkdir(parents=True) #First launch or versions folder missing
        return list() #No versions installed as folder was just created
    fileList = list(fp.iterdir())
    for file in fileList[:]: #Loop through the list and find any valid versions
        if file.is_dir():
            if any(x.name in VALIDSLOMEVERSIONS for x in file.iterdir()): #If the folder contains a Slome.exe file
                LOGGER.debug(f"Found Slome version at {file}")
                continue
        elif file.is_file() and file.suffix.lower() == ".zip":
            with zipfile.ZipFile(file, "r") as zf:
                if any(pathlib.PurePosixPath(name).name in VALIDSLOMEVERSIONS for name in zf.namelist()): #If the zip folder contains a Slome.exe file
                    LOGGER.debug(f"Found Slome version at {file}")
                    continue
        fileList.remove(file)
    return fileList #Returns all zips or folders with slome executables in them

def cleanCache():
    shutil.rmtree(HOME / "temp" / "cache", ignore_errors=True) #Delete the entire cache dir unless zip versions are currently in use