import logging
import threading
import subprocess
import tkinter
import queue
import pathlib
from datetime import datetime

SLOMELOGFORMAT = logging.Formatter(fmt="%(message)s")

class GUIHandler(logging.Handler): #Handles the gui log messages
    def __init__(self, logQueue, logWindow):
        super().__init__()
        self.logQueue = logQueue
        self.logWindow = logWindow

    def emit(self, record):
        msg = self.format(record)
        self.logQueue.put(msg + "\n")
        if self.logWindow:
            try:
                self.logWindow.event_generate("<<NewLogMessage>>", when="tail")
            except Exception:
                pass



class InstanceLog(threading.Thread):
    def __init__(self, instance: subprocess.Popen[str], version: str, showLog: bool, root: tkinter.Tk):
        super().__init__()
        self.instance = instance
        self.version = version
        self.daemon = False #Allows the logger to continue running even if the launcher is

        self.logger = logging.getLogger(version)
        self.logger.setLevel(logging.DEBUG)
        filePath = pathlib.Path.home() / "AppData/Roaming" / ".Unofficial Slome Launcher" / "logs" / version
        filePath.mkdir(parents=True, exist_ok=True)
        fileHandler = logging.FileHandler(filePath / datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log"))
        fileHandler.setFormatter(SLOMELOGFORMAT)
        self.logger.addHandler(fileHandler)

        if showLog:
            logWindow, self.logBox = self.setupLoggerGUI(root) #If the user wants a visual logger
            self.logQueue = queue.Queue()
            guiHandler = GUIHandler(self.logQueue, logWindow) #Create a handler for the log gui
            guiHandler.setFormatter(SLOMELOGFORMAT)
            self.logger.addHandler(guiHandler)

        self.logger.debug("Warning this instance has been launched by SonicRaptor's launcher\nThis will cause minor game modifications that can lead to crashes\n\n\n")


    def run(self):
        for line in self.instance.stdout:
            self.logger.debug(line.rstrip())

    def setupLoggerGUI(self, root):
        logWindow = tkinter.Toplevel(root) #Spawn sub window
        logWindow.title(f"Slome {self.version} Log")
        logWindow.geometry("320x600")
        logBox = tkinter.Text(logWindow, wrap=tkinter.WORD)
        logBox.pack(expand=True, fill=tkinter.BOTH, padx=10, pady=10)
        logBox.config(state=tkinter.DISABLED) #Lock the logger
        logWindow.bind("<<NewLogMessage>>", lambda event: self.updateLoggerGUI()) #Stupid work around cause tkinter cant touch threads
        return logWindow, logBox #Return the object references

    def updateLoggerGUI(self):
        try:
            while True:
                line = self.logQueue.get_nowait()
                self.logBox.config(state=tkinter.NORMAL) #Unlock the logger
                self.logBox.insert(tkinter.END, line) #Post message
                self.logBox.see(tkinter.END) #Scroll to the bottom
                self.logBox.config(state=tkinter.DISABLED) #Lock the logger
        except queue.Empty: #Loops through all messages each call to ensure it doesn't get desynced
            pass