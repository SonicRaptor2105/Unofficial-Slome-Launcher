import struct
import shutil
import pathlib
from src.helperMethods import getResourcePath
from src.constants import HOME, LOGGER

def _getBitness(exe: pathlib.Path):
    with open(exe, "rb") as f:
        f.seek(0x3C) #Go to byte 60
        pe = struct.unpack("<I", f.read(4))[0] #Get the header to check the bitness
        f.seek(pe + 4)
        machine = struct.unpack("<H", f.read(2))[0]
        if machine == 0x8664:
            return "x64"
        if machine == 0x014C:
            return "x86"
        raise ValueError(f"Unsupported exe architecture: {machine:#x}") #Error handling to prevent injecting the mod into invalid dirs

def install(exe: pathlib.Path):
    patcherDir = getResourcePath(pathlib.Path(__file__).resolve().parent.parent / "patcher")
    proxyDll = patcherDir / _getBitness(exe) / "winhttp.dll"
    patcherDll = patcherDir / "PersistentPathPatch.dll"
    ini = f"""[General
    enabled=true
    target_assembly={patcherDll}
    redirect_output_log=false
    ignore_disable_switch=false

    [UnityMono]
    dll_search_path_override=
    debug_enabled=false
    """
    shutil.copy2(proxyDll, exe.parent / "winhttp.dll")
    (exe.parent / "doorstop_config.ini").write_text(ini, encoding="utf-8") #Inject the ini

def cleanUp(version: pathlib.Path | None):
    if version: #If one file given
        (version / "doorstop_config.ini").unlink(missing_ok=True)
        (version / "winhttp.dll").unlink(missing_ok=True)
        (version / "saves").rmdir() #Unneeded empty folder
        LOGGER.debug(f"{version} cleaned")
        return
    for v in (HOME / "versions").iterdir(): #If all versions need cleanup
        if v.is_dir(): #Ignore exes
            cleanUp(v)