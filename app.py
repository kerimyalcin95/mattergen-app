import tkinter as tk
import subprocess
from pathlib import Path

ps = subprocess.Popen(
    ["powershell", "-NoExit"],
    stdin=subprocess.PIPE,
    stdout=None,
    stderr=None,
    text=True,
    creationflags=subprocess.CREATE_NEW_CONSOLE
)



mattergen_path = r""
venv = r".\.venv\Scripts\activate"
commandPrompt = "cd " + mattergen_path + "; " + venv

root = tk.Tk()
root.title("MatterGen-App")
root.geometry("800x600")

label = tk.Label(root, text="mattergen-generate")
label.pack()

def shellProc():
    ps.stdin.write(r'cd "C:\Users\agx\LRZ Sync+Share\MatterGen-App\mattergen-master\mattergen-1.0.3"' + "\n")
    ps.stdin.write(r'.\.venv\Scripts\activate' + "\n")
    ps.stdin.write(r'mattergen-generate results\ --pretrained-name=mattergen_base --batch_size=1 --num_batches 1' + "\n")
    ps.stdin.flush()

button = tk.Button(root, text="Run")
button.config(command=shellProc)
button.pack()

root.mainloop()