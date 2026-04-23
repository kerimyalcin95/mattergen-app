import tkinter as tk
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

matter_generate_cmd = r'mattergen-generate "' + config["result-path"] + '" --pretrained-name=mattergen_base --batch_size=' + str(config["batch-size"]) +  r' --num_batches=' + str(config["num-batches"])

cmd = """
source /home/agx/mattergen-1.0.3/.venv/bin/activate &&
mattergen-generate /home/agx/output \
--pretrained-name=mattergen_base \
--batch_size=4 \
--num_batches=2
"""

subprocess.run(["bash", "-c", cmd])

# Run mattergen CLI prompt
def shellProc():
    os.chdir(config["work-path-linux"])
    print("Changed working directory to: " + os.getcwd())
    os.system("./.venv/bin/" + matter_generate_cmd)

# Closing the window kills all processes immediately

button = tk.Button(root, text="Run")
button.config(command=shellProc)
button.pack()

root.mainloop()