import pathlib
import json
import psutil
from dataclasses import dataclass, asdict

@dataclass
class AdvProcessID:
    pid: int
    vid: str
    creation: int
    logPath: str

class PersistentProccessArrayList:
    def __init__(self):
        self.filePath = pathlib.Path.home() / "AppData" / "Roaming" / ".Unofficial Slome Launcher" / "temp" / "cache" / "processes.jsonl"
        self.data = list()
        self.load()

    def load(self):
        if self.filePath.exists():
            try:
                with open(self.filePath, "r") as f:
                    for process in f:
                        self.data.append(AdvProcessID(**json.loads(process))) #Automatically pass it back into AdvProcessID format
            except:
                self.data = list()

    def save(self):
        self.filePath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filePath, "w") as f:
            for process in self.data:
                f.write(json.dumps(asdict(process)) + "\n")

    def append(self, item):
        self.data.append(item)
        self.save()

    def remove(self, pid):
        item = next(process for process in self.data if process.pid == pid)
        self.data.remove(item)
        self.save()

    def validateAll(self): #Loop through all instances and see which are still running
        for process in self.data[:]:
            try:
                if not psutil.pid_exists(process.pid) or psutil.Process(process.pid).create_time() != process.creation:
                    self.remove(process.pid)
            except:
                self.remove(process.pid)

    def find(self, pid=None, vid=None): #Find a running instance by either its pid or vid
        if pid is not None:
            for process in self.data:
                if process.pid == pid:
                    return process
        elif vid is not None:
            for process in self.data:
                if process.vid == vid:
                    return process
        return None