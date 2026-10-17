import tkinter
import pathlib
import zipfile
import subprocess
import datetime
import threading
import time
import queue

VALIDSLOMEVERSIONS = ["Slome.exe", "survival project.exe", "SlomeSlomeSlomeSlome.exe"]


class Launcher(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.title("Unofficial Slome Launcher")
        self.geometry("800x550")

        self.instances = self.checkForInstances()
        self.drawIntstances()

    def drawIntstances(self):
        for instance in self.instances:
            x = tkinter.Button(self, text=instance.stem, command=lambda p=instance: self.launchVersion(p, showLog=True))
            x.pack()

    def checkForInstances(self):
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

    def launchVersion(self, filePath: pathlib.Path, showLog: bool = False): #Launches the selected version
        slomePathEXE = filePath / pathlib.Path(next(file for file in VALIDSLOMEVERSIONS if (filePath / file).is_file())) #Gets whatever version of the game is in the instance
        logPath = pathlib.Path.home() / "AppData/Roaming" / ".Unofficial Slome Launcher" / "logs" / filePath.name / datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
        logPath.parent.mkdir(parents=True, exist_ok=True)
        args = [
            "-logFile", str(logPath),
            "-logflush"
        ]
        instance = subprocess.Popen([slomePathEXE] + args)
        self.logGUI(logPath)

    def logGUI(self, logPath):
        logWindow = tkinter.Toplevel(self) #Spawn sub window
        logWindow.title(f"Slome log")
        logWindow.geometry("320x600")
        container = tkinter.Frame(logWindow)
        container.pack(expand=True, fill=tkinter.BOTH, padx=0, pady=0)
        scrollbar = tkinter.Scrollbar(container)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        logBox = tkinter.Text(container, wrap=tkinter.WORD, yscrollcommand=scrollbar.set)
        logBox.pack(expand=True, fill=tkinter.BOTH, padx=4, pady=0)
        logBox.config(state=tkinter.DISABLED) #Lock the logger
        scrollbar.config(command=logBox.yview)

        stopEvent = threading.Event() #Set a stop event for the sub thread so it can be rejoined on gui close
        logQueue = queue.Queue() #Queue log messages so they can be processed on the main thread

        def readLog(logPath):
            while not logPath.exists():
                if stopEvent.is_set():
                    return
                time.sleep(0.1)

            with open(logPath, "r", encoding="utf-8", errors="ignore") as f:
                while not stopEvent.is_set():
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    logQueue.put(line)
                    logWindow.event_generate("<<NewLogLine>>", when="tail") #Pass back onto the main thread

        def updateGUI(event=None):
            try:
                while True:
                    line = logQueue.get_nowait()
                    logBox.config(state=tkinter.NORMAL) #Unlock the logger
                    logBox.insert(tkinter.END, line) #Post message
                    logBox.see(tkinter.END) #Scroll to the bottom
                    logBox.config(state=tkinter.DISABLED) #Lock the logger
            except queue.Empty:
                pass

        def onClose():
            stopEvent.set()
            logWindow.destroy()

        logWindow.bind("<<NewLogLine>>", updateGUI) #Schedules a gui update for every new log found
        logWindow.protocol("WM_DELETE_WINDOW", onClose) #Close the thread upon the window closing
        listener = threading.Thread(target=readLog, args=(logPath,), daemon=True)
        listener.start()



if __name__ == "__main__":
    launcher = Launcher()
    launcher.mainloop()