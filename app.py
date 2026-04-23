import tkinter as tk
import threading
import signal
import subprocess
import sys
import os
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

cmd = f"""
source /home/agx/mattergen-1.0.3/.venv/bin/activate &&
mattergen-generate {config["result-path"]} \
--pretrained-name=mattergen_base \
--batch_size={config["batch-size"]} \
--num_batches={config["num-batches"]}
"""

# Run mattergen CLI prompt
def shellProc():
    subprocess.run(["bash", "-c", cmd])

def start_thread():
    print("Starting thread.")
    thread = threading.Thread(target=shellProc)
    thread.start()

# Kills the entire process when closing window
def on_close():
    try:
        os.killpg(0, signal.SIGTERM)
    except Exception:
        pass

    root.destroy()

button = tk.Button(root, text="Run")
button.config(command=start_thread)
button.pack()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()