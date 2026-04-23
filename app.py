import tkinter as tk
import subprocess
import sys
from pathlib import Path
import json

from app_windows import main_windows

if sys.platform == "win32":
    # experimental
    main_windows()
elif sys.platform == "linux":
    print("Running on Linux distribution.")
else:
    print("Current platform: " + sys.platform)
    print("OS not supported.")

root = tk.Tk()
root.title("MatterGen-App")
root.geometry("800x600")

# Load config file
BASE_DIR = Path(__file__).resolve().parent 
CONFIG_PATH = BASE_DIR.parent / "mattergen-app" / "config.json"

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

label = tk.Label(root, text="mattergen-generate")
label.pack()

# Run mattergen CLI prompt
def shellProc():
    ps.stdin.write(r'cd "' + config["work-path-linux"] + '"' + "\n")
    ps.stdin.write(r'.\.venv\Scripts\activate' + "\n")
    ps.stdin.write(r'mattergen-generate "' + config["result-path"] + '" --pretrained-name=mattergen_base --batch_size=' + str(config["batch-size"]) +  r' --num_batches=' + str(config["num-batches"]) + "\n")
    ps.stdin.flush()

# Closing the window kills all processes immediately
def on_close():
    try:
        subprocess.run(f"taskkill /F /T /PID {ps.pid}", shell=True)
    except Exception:
        pass
    root.destroy()

button = tk.Button(root, text="Run")
button.config(command=shellProc)
button.pack()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()