import tkinter
import pathlib
import subprocess
import datetime
import threading
import time
import queue
import psutil
import hashlib
import icoextract
import ctypes
import os
from PIL import Image, ImageTk
from src.logHandler import handleException
from src.aditionalDataClasses import *
from src.extractFromZip import unzipFile
from src.modInjector import install
from src.constants import VALIDSLOMEVERSIONS, HOME, LOGGER
from src.helperMethods import getResourcePath, checkForVersions

class Launcher(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.title("Unofficial Slome Launcher")
        self.geometry("800x550")
        self.minsize(600, 300)
        self.iconbitmap(default=getResourcePath(r"assets\slomeIcon.ico"))
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=5)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        #Versions box
        versionFrame = tkinter.Frame(self, relief="solid", bd=2)
        versionFrame.grid(row=1, column=1, rowspan=2, sticky="nsew")
        statusBox = tkinter.Frame(versionFrame, height=30, relief="solid", bd=2)
        statusBox.pack(side="bottom", fill="x")
        statusBox.pack_propagate(False)
        self.statusLabel = tkinter.Label(statusBox, text="", fg="black")
        self.statusLabel.pack(side="left", padx=8)
        canvas = tkinter.Canvas(versionFrame, highlightthickness=0)
        scrollbar = tkinter.Scrollbar(versionFrame, orient="vertical", command=canvas.yview)
        self.instanceFrame = tkinter.Frame(canvas)
        self.instanceFrame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.instanceFrame, anchor="nw", tags="inner_window")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("inner_window", width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        #Version info box
        self.inspectedVersion = None
        self.statusFrame = tkinter.Frame(self, relief="solid", bd=2, width=160)
        self.statusFrame.grid(row=1, column=0, rowspan=2, sticky="nsew")
        self.statusFrame.pack_propagate(False)

        self.versions = checkForVersions()
        self.statusLabel.config(text=f"Ready | {len(self.versions)} versions found")
        self.running = PersistentProccessArrayList()
        self.running.validateAll()
        self.loggers = dict()
        self.drawIntstances()
        for process in self.running.data: #Restore the monitor after the launcher is restarted if the process still exists
            LOGGER.debug(f"Resumed process with pid of {process.pid}")
            threading.Thread(target=self.monitorInstance, args=(process.pid,), daemon=True).start()
            self.showSubButtons(process.vid)

    def report_callback_exception(self, excType, excValue, excTraceback): #Override the built in tkinter error handler
        handleException(excType, excValue, excTraceback)

    def drawIntstances(self):
        for version in self.versions:
            vid = hashlib.md5(bytes(str(version.name), encoding="utf-8")).hexdigest()
            rowFrame = tkinter.Frame(self.instanceFrame, name=vid, relief="raised")
            rowFrame.pack(fill="x", padx=5, pady=3)
            rowFrame.pack_propagate(False)
            rowFrame.config(height=60)
            
            if version.is_dir(): #Only scrape .icos from unzipped versions
                slomePathEXE = version / pathlib.Path(next(file for file in VALIDSLOMEVERSIONS if (version / file).is_file())) #Grab the version
                extractor = icoextract.IconExtractor(slomePathEXE)
                data = extractor.get_icon(num=0)
                rawIcon = Image.open(data).resize((48,48))
            else:
                rawIcon = Image.open(getResourcePath(r"assets\slomeIcon.ico")).resize((48,48)) #Just grab the built in icon as a fallback NEEDS TO BE REBOUND TO LOCAL BEFORE COMPILING TO EXE!!!!!
            icon = ImageTk.PhotoImage(rawIcon) #Tkinter accepts PIL files but not bytecode
            newVersionButton = tkinter.Button(
                rowFrame,
                text=version.name if version.is_dir() else version.stem, #Test to avoid cutting off folder names if they have a .
                image=icon,
                compound="left",
                anchor="w",
                relief="flat",
                padx=10,
                command=lambda t=rawIcon, v=version, i=vid: self.showVersionInfo(t, v, i)
            )
            newVersionButton.bind("<Double-Button-1>", lambda e, p=version, v=vid: self.launchVersion(filePath=p, vid=v, showLog=True)) #Allow the button to open versions and bind their local vars to prevent overwritting
            newVersionButton.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
            newVersionButton.image = icon #Prevent the icon from getting killed by the gc

            tkinter.Button( #Add a close button for when the version is running
                rowFrame,
                name="closeButton",
                text="X",
                relief="flat",
                bg="#ff4d4d",
                command=lambda v=vid: psutil.Process(self.running.find(vid=v).pid).kill() #Close the version instantly
            )
            tkinter.Button( #Add a log button for when the version is running
                rowFrame,
                name="logButton",
                text="L",
                relief="flat",
                bg="#02FF0F",
                command=lambda v=vid: self.logGUI(pathlib.Path(self.running.find(vid=v).logPath)) #Open a new log version
            )

    def launchVersion(self, filePath: pathlib.Path, vid: str, showLog: bool = False): #Launches the selected version
        running = self.running.find(vid=vid)
        if running: #If the versions running already
            def _searchForProcess(hwnd, extra): #Searches for the process and fullscreens it
                if ctypes.windll.user32.IsWindowVisible(hwnd): #Scan only visible processes not background tasks
                    targetPid = ctypes.c_ulong()
                    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(targetPid)) #Get the process id of the currently selected task
                    if targetPid.value == running.pid: #If its the instance
                        ctypes.windll.user32.ShowWindow(hwnd, 9) #Restores the program
                        ctypes.windll.user32.SetForegroundWindow(hwnd) #Brings the process into the foreground
                        return False  #Stop searching
                return True
            ctypes.windll.user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(_searchForProcess), 0) #Start the search for the instance using ctypes

        else: #If its not running
            if filePath.is_dir():
                slomePathEXE = filePath / pathlib.Path(next(file for file in VALIDSLOMEVERSIONS if (filePath / file).is_file())) #Gets whatever version of the game is in the instance
            else:
                self.statusLabel.config(text=f"Extracting {filePath.name}...")
                slomePathEXE = unzipFile(filePath) #Unzip the game first then run it
            self.statusLabel.config(text=f"Launching {filePath.name}...")
            logPath = HOME / "instances" / filePath.name / datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S.log")
            logPath.parent.mkdir(parents=True, exist_ok=True)
            args = [
                "-logFile", str(logPath),
                "-logflush"
            ]
            dataDir = HOME / "instances" / filePath.name
            dataDir.mkdir(parents=True, exist_ok=True)
            env = os.environ.copy()

            try:
                install(slomePathEXE) #Install the PersistentPathPatch
                env["DOORSTOP_ENABLED"] = "1" #Activate the patch
                env["DOORSTOP_TARGET_ASSEMBLY"] = str(getResourcePath(pathlib.Path("patcher") / "PersistentPathPatch.dll"))
                env["UNITY_DATA_OVERRIDE"] = str(dataDir)
                LOGGER.debug(f"PersistentPathPatch injection successful for {filePath.name}")
            except Exception as e:
                LOGGER.error(f"Failed to inject PersistentPathPatch for {filePath.name}\n{e}\nLaunching normally.")

            instance = subprocess.Popen([slomePathEXE] + args, env=env, cwd=filePath.parent) #Runs the instance with the above args and detaches it from the python process
            pid = instance.pid
            self.running.append(AdvProcessID(pid=pid, vid=vid, creation=psutil.Process(pid).create_time(), logPath=str(logPath))) #Push tracking data
            threading.Thread(target=self.monitorInstance, args=(pid,), daemon=True).start() #Starts a thread to watch for the end of the process to remove it from the active processes list
            LOGGER.debug(f"Launched version {filePath.name} with pid {pid}")
            self.statusLabel.config(text=f"Launched {filePath.name}")
            self.showSubButtons(vid)
            if showLog:
                self.logGUI(logPath)
            self.showVersionInfo(**self.inspectedVersion) #Reload the version info in case it needs to be updated

    def logGUI(self, logPath: pathlib.Path):
        existingLogger = self.loggers.get(logPath, None)
        if existingLogger:
            existingLogger.attributes("-topmost", True) #Pull to front
            existingLogger.attributes("-topmost", False) #Allow other windows to cover it again
            return
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

        self.loggers[logPath] = logWindow #Save to a dict so it can be restored if requested

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
                    if "\x00" in line: #Version has been closed
                        stopEvent.set()
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
            del self.loggers[logPath] #Remove from the dict

        logWindow.bind("<<NewLogLine>>", updateGUI) #Schedules a gui update for every new log found
        logWindow.protocol("WM_DELETE_WINDOW", onClose) #Close the thread upon the window closing
        listener = threading.Thread(target=readLog, args=(logPath,), daemon=True)
        listener.start()

    def monitorInstance(self, pid): #Removes any running versions instantly to avoid having to clean up later
        exitCode = psutil.Process(pid).wait()
        with open(pathlib.Path(self.running.find(pid=pid).logPath), "a") as f: #Log the exit code incase its force closed
            f.write(f"Process closed with code {exitCode}\x00")
        self.hideSubButtons(self.running.find(pid=pid).vid)
        self.running.remove(pid)
        self.showVersionInfo(**self.inspectedVersion) #Reload the version info in case it needs to be updated

    def showSubButtons(self, vid):
        for child in self.instanceFrame.winfo_children(): #Search the instance pannel for the specific instance
            if child.winfo_name() == vid:
                for subChild in child.winfo_children():
                    if subChild.winfo_name() == "logButton": #Show the log button
                        subChild.place(relx=1.0, x=-26, y=4, anchor="ne", width=18, height=18)
                    elif subChild.winfo_name() == "closeButton": #Show the close button
                        subChild.place(relx=1.0, x=-4, y=4, anchor="ne", width=18, height=18)

    def hideSubButtons(self, vid): #Hide the close and log button
        for child in self.instanceFrame.winfo_children(): #Search the instance pannel for the specific instance
            if child.winfo_name() == vid:
                for subChild in child.winfo_children():
                    if subChild.winfo_name() == "logButton" or subChild.winfo_name() == "closeButton":
                        subChild.place_forget()

    def showVersionInfo(self, thumbnail: Image, versionPath: str, vid: str): #Show info about the selected version
        self.inspectedVersion = locals().copy() #Save the last inspected version without the self reference
        self.inspectedVersion.pop("self", None)
        for child in self.statusFrame.winfo_children(): #Prevent versions from stacking
            child.destroy()
        thumbnail = thumbnail.resize((80, 80), Image.Resampling.NEAREST) #Use nearest to ensure hard edges
        photo = ImageTk.PhotoImage(thumbnail)
        img = tkinter.Label(self.statusFrame, image=photo)
        img.image = photo
        img.pack(pady=10)
        title = tkinter.Label(self.statusFrame, text=versionPath.name if versionPath.is_dir() else versionPath.stem, wraplength=90, justify="center")
        title.pack()
        running = self.running.find(vid=vid)
        if running: #Add a close button for when the version is running
            controlBtn = tkinter.Button(
                self.statusFrame,
                text="Close",
                relief="flat",
                bg="#ff4d4d",
                command=lambda: psutil.Process(running.pid).kill() #Close the version instantly
            )
        else: #Add a start button if the version is not running already
            controlBtn = tkinter.Button(
                self.statusFrame,
                text="Run",
                relief="flat",
                bg="#00ff37",
                command=lambda p=versionPath, v=vid: self.launchVersion(filePath=p, vid=v, showLog=True)
            )
        controlBtn.pack()
        savesFolder = HOME / "instances" / versionPath.name
        savesFolder.mkdir(parents=True, exist_ok=True) #Ensure it exists
        saveFolderBtn = tkinter.Button(
            self.statusFrame,
            text="Saves Folder",
            relief="flat",
            command=lambda: os.startfile(savesFolder)
        )
        saveFolderBtn.pack()