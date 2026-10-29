import zipfile
import pathlib
import json
import shutil
from src.constants import VALIDSLOMEVERSIONS

CACHEPATH = pathlib.Path.home() / "AppData" / "Roaming" / ".Unofficial Slome Launcher" / "temp" / "cache" / "latestLaunch"

def _getArchiveRoot(fileNames):
    filePaths = [pathlib.PurePosixPath(name) for name in fileNames if not name.endswith("/")]
    if not filePaths or any(len(path.parts) < 2 for path in filePaths):
        return None

    root = filePaths[0].parts[0]
    if all(path.parts[0] == root for path in filePaths):
        return root
    return None

def _compareHashDict(crc: dict, version: str): #Returns that need to be extracted
    hashDictPath = CACHEPATH / version / "hashDict.json"
    if not hashDictPath.exists(): #Nothings extracted or cache corrupted
        return crc
    with open(hashDictPath, "r") as f:
        hashDict = json.load(f)
    return dict(crc.items() - hashDict.items()) #Return the CRC with different values

def getHashDict(zipPath: pathlib.Path):
    hashDict = dict()
    with zipfile.ZipFile(zipPath, "r") as zf:
        archiveRoot = _getArchiveRoot(zf.namelist())
        for info in zf.infolist():
            if info.filename.endswith("/"): #Skip folders
                continue
            filePath = pathlib.PurePosixPath(info.filename)
            if archiveRoot is not None:
                filePath = filePath.relative_to(archiveRoot)
            filePath = filePath.as_posix()
            hashDict[f"{info.CRC:08x}"] = filePath #Saves the CRC and the filePath
    return hashDict

def _dumpHashDict(hashDict: dict, version):
    CACHEPATH.mkdir(parents=True, exist_ok=True)
    with open(CACHEPATH / version / "hashDict.json", "w") as f:
        json.dump(hashDict, f)

def unzipFile(zipPath: pathlib.Path):
    with zipfile.ZipFile(zipPath, "r") as zf:
        version = next(version for version in VALIDSLOMEVERSIONS if any(version in name for name in zf.namelist()))[:-4] #Check the version name
        archiveRoot = _getArchiveRoot(zf.namelist())
    hashDict = getHashDict(zipPath=zipPath) #Get the CRC of each file with its filePath
    dif = _compareHashDict(hashDict, version)
    if dif == {}:
        return CACHEPATH / version / f"{version}.exe" #Return the file path so it doesn't have to be constructed later
    pathlib.Path(CACHEPATH / version / "hashDict.json").unlink(missing_ok=True) #Delete the file to show that the extract has started
    filesToExtract = list(dif.values()) #File path of all the files ot be extracted
    with zipfile.ZipFile(zipPath, "r") as zf:
        for file in zf.namelist():
            if file.endswith("/"):
                continue
            filePath = pathlib.PurePosixPath(file)
            if archiveRoot is not None:
                filePath = filePath.relative_to(archiveRoot)
            filePath = filePath.as_posix()
            if filePath in filesToExtract:
                targetPath = CACHEPATH / version / filePath
                targetPath.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(file) as source, open(targetPath, "wb") as target: #Writes the file to a new destination rather than preserving its original file path
                    shutil.copyfileobj(source, target)
                filesToExtract.remove(filePath)
            if not filesToExtract: #If nothing else is needed
                break
    _dumpHashDict(hashDict, version) #Dump the hashDict only once the extract has been fully completed
    return CACHEPATH / version / f"{version}.exe"