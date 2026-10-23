import tkinter
import pathlib
import zipfile
import subprocess
import datetime
import threading
import time
import queue
import psutil
import hashlib
import icoextract
import ctypes
import logging
from logHandler import handleException
from PIL import Image, ImageTk
VALIDSLOMEVERSIONS = ["Slome.exe", "survival project.exe", "SlomeSlomeSlomeSlome.exe"]
from aditionalDataClasses import *
from extractFromZip import *

LOGGER = logging.getLogger("Slome Launcher")

class Launcher(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.title("Unofficial Slome Launcher")
        self.geometry("800x550")
        self.iconbitmap("slomeIcon.ico") #TEMP

        self.thumbnails = list()
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        frame = tkinter.Frame(self, relief="solid", bd=2)
        frame.grid(row=0, column=1, rowspan=2, sticky="nsew")
        canvas = tkinter.Canvas(frame, highlightthickness=0)
        scrollbar = tkinter.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.instanceFrame = tkinter.Frame(canvas)
        self.instanceFrame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.instanceFrame, anchor="nw", tags="inner_window")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("inner_window", width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.instances = self.checkForInstances()
        self.running = PersistentProccessArrayList()
        self.running.validateAll()
        self.drawIntstances()
        for process in self.running.data: #Restore the monitor after the launcher is restarted if the process still exists
            LOGGER.debug(f"Resumed process with pid of {process.pid}")
            threading.Thread(target=self.monitorInstance, args=(process.pid,), daemon=True).start()
            self.showSubButtons(process.vid)

    def reportCallbackException(self, excType, excValue, excTraceback):
        handleException(excType, excValue, excTraceback)

    def drawIntstances(self):
        for instance in self.instances:
            vid = hashlib.md5(bytes(str(instance.name), encoding="utf-8")).hexdigest()
            rowFrame = tkinter.Frame(self.instanceFrame, name=vid, relief="raised")
            rowFrame.pack(fill="x", padx=5, pady=3)
            rowFrame.pack_propagate(False)
            rowFrame.config(height=60)
            
            if instance.is_dir(): #Only scrape .icos from unzipped instances
                slomePathEXE = instance / pathlib.Path(next(file for file in VALIDSLOMEVERSIONS if (instance / file).is_file())) #Grab the version
                extractor = icoextract.IconExtractor(slomePathEXE)
                data = extractor.get_icon(num=0)
                rawIcon = Image.open(data).resize((48,48))
            else:
                rawIcon = Image.open("slomeIcon.ico").resize((48,48)) #Just grab the built in icon as a fallback NEEDS TO BE REBOUND TO LOCAL BEFORE COMPILING TO EXE!!!!!
            icon = ImageTk.PhotoImage(rawIcon) #Tkinter accepts PIL files but not bytecode
            newInstanceButton = tkinter.Button(
                rowFrame,
                text=instance.name if instance.is_dir() else instance.stem, #Test to avoid cutting off folder names if they have a .
                image=icon,
                compound="left",
                anchor="w",
                relief="flat",
                padx=10,
                command=lambda p=instance, v=vid: self.launchVersion(filePath=p, vid=v, showLog=True) #Add the buttons and bind their local vars to prevent overwritting
            )
            newInstanceButton.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
            newInstanceButton.image = icon #Prevent the icon from getting killed by the gc

            tkinter.Button( #Add a close button for when the instance is running
                rowFrame,
                name="closeButton",
                text="X",
                relief="flat",
                bg="#ff4d4d",
                command=lambda v=vid: psutil.Process(self.running.find(vid=v).pid).kill() #Close the version instantly
            )
            tkinter.Button( #Add a log button for when the instance is running
                rowFrame,
                name="logButton",
                text="L",
                relief="flat",
                bg="#02FF0F",
                command=lambda v=vid: self.logGUI(pathlib.Path(self.running.find(vid=v).logPath)) #Open a new log instance
            )

    def checkForInstances(self):
        fp = pathlib.Path.home() / "AppData/Roaming" / ".Unofficial Slome Launcher" / "instances"
        if not fp.exists():
            fp.mkdir(parents=True) #First launch or instances folder missing
            return list() #No instances installed as folder was just created
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
                slomePathEXE = unzipFile(filePath) #Unzip the game first then run it

            logPath = pathlib.Path.home() / "AppData" / "Roaming" / ".Unofficial Slome Launcher" / "logs" / filePath.name / datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S.log")
            logPath.parent.mkdir(parents=True, exist_ok=True)
            with open(logPath, "w") as log:
                log.write("Warning this version has been launched through SonicRaptor's launcher.\nThis may potentially lead to crashes.\n\n\n")
            args = [
                "-logFile", str(logPath),
                "-logflush"
            ]
            instance = subprocess.Popen([slomePathEXE] + args) #Runs the instance with the above args and detaches it from the python process
            pid = instance.pid
            self.running.append(AdvProcessID(pid=pid, vid=vid, creation=psutil.Process(pid).create_time(), logPath=str(logPath))) #Push tracking data
            threading.Thread(target=self.monitorInstance, args=(pid,), daemon=True).start() #Starts a thread to watch for the end of the process to remove it from the active processes list
            LOGGER.debug(f"Launched version {filePath.name} with pid {pid}")
            self.showSubButtons(vid)
            if showLog:
                self.logGUI(logPath)
            
    def logGUI(self, logPath: pathlib.Path):
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

        logWindow.bind("<<NewLogLine>>", updateGUI) #Schedules a gui update for every new log found
        logWindow.protocol("WM_DELETE_WINDOW", onClose) #Close the thread upon the window closing
        listener = threading.Thread(target=readLog, args=(logPath,), daemon=True)
        listener.start()

    def monitorInstance(self, pid): #Removes any running instances instantly to avoid having to clean up later
        exitCode = psutil.Process(pid).wait()
        with open(pathlib.Path(self.running.find(pid=pid).logPath), "a") as f: #Log the exit code incase its force closed
            f.write(f"Process closed with code {exitCode}\x00")
        self.hideSubButtons(self.running.find(pid=pid).vid)
        self.running.remove(pid)

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