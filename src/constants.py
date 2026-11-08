from pathlib import Path

VALIDSLOMEVERSIONS = ["Slome.exe", "survival project.exe", "SlomeSlomeSlomeSlome.exe"]
HOME = Path.home() / "AppData" / "Roaming" / ".Unofficial Slome Launcher"

HOME.mkdir(parents=True, exist_ok=True)