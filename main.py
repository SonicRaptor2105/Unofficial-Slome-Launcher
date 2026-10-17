import tkinter
import pathlib
import zipfile
import subprocess
import logManager
import logging

VALIDSLOMEVERSIONS = ["Slome.exe", "survival project.exe", "SlomeSlomeSlomeSlome.exe"]


class Launcher:
    def __init__(self):
        self.root = _instantiateWindow()
        self.instances = _checkForInstances()
        self._drawIntstances()

    def _drawIntstances(self):
        for instance in self.instances:
            x = tkinter.Button(self.root, text=instance.stem)
            x.pack()

def _checkForInstances():
    fp = pathlib.Path.home() / "AppData/Roaming" / ".Unofficial Slome Launcher" / "instances"
    if not fp.exists():
        fp.mkdir(parents=True) #First launch or instances folder missing
        return list() #No instances installed as folder was just created
    fileList = list(fp.iterdir())
    for file in fileList[:]: #Loop through the list and find any valid versions
        if file.is_dir():
            if any(x.name in VALIDSLOMEVERSIONS for x in file.iterdir()): #If the folder contains a Slome.exe file
                continue
        elif file.is_file() and file.suffix.lower() == ".zip":
            with zipfile.ZipFile(file, "r") as zf:
                if any(pathlib.PurePosixPath(name).name in VALIDSLOMEVERSIONS for name in zf.namelist()): #If the zip folder contains a Slome.exe file
                    continue
        fileList.remove(file)
    return fileList #Returns all zips or folders with slome executables in them

def launchVersion(filePath: pathlib.Path, root: tkinter.tk, showLog: bool = False): #Launches the selected version
    path = filePath / pathlib.Path(next(file for file in VALIDSLOMEVERSIONS if (filePath / file).is_file())) #Gets whatever version of the game is in the instance
    instance = subprocess.Popen([path, "-logFile", "-"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    logManager.InstanceLog(instance=instance, version=filePath.name, showLog=showLog, root=root).start()



def _instantiateWindow():
    root = tkinter.Tk()
    root.title("Unofficial Slome Launcher")
    root.geometry("800x550")
    return root




if __name__ == "__main__":
    x = Launcher()
    launchVersion(x.instances[0], root=x.root, showLog=True)
    x.root.mainloop()