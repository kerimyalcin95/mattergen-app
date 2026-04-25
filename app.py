import tkinter as tk
from tkinter import ttk

import threading
import signal
import subprocess
import sys
import os
from pathlib import Path
import json

from app_windows import main_windows

class App:

    def __init__(self):
        self.root = None
        self.config = None
        self.generate_command = None
        self.BASE_DIR = None
        self.CONFIG_PATH = None
        self.selected_model = None
        self.process = None
        self.thread = None

    def run(self):
        self.root = tk.Tk()
        self.root.title("MatterGen-App")
        self.root.geometry("800x600")

        if sys.platform == "win32":
        # experimental
            main_windows()
        elif sys.platform == "linux":
            print("Running on Linux distribution.")
        else:
            print("Current platform: " + sys.platform)
            print("OS not supported.")

        # Load config file
        self.BASE_DIR = Path(__file__).resolve().parent 
        self.CONFIG_PATH = self.BASE_DIR.parent / "mattergen-app" / "config.json"

        with open(self.CONFIG_PATH, "r") as f:
            self.config = json.load(f)

        options_internalModels = self.config["internal-models"]
        selected_model = tk.StringVar()
        selected_model.set(self.config["internal-model-selected"])
        tkDropDownMenu_internalModels = ttk.Combobox(
            self.root,
            textvariable=selected_model,
            values=options_internalModels,
            state="readonly"
        )
        tkDropDownMenu_internalModels.pack()

        tkDropDownMenu_internalModels.bind("<<ComboboxSelected>>", self.tkDropDownMenu_internalModels_on_select)
        label = tk.Label(self.root, text="Generate crystal structures")
        label.pack()

        button = tk.Button(self.root, text="RUN")
        button.config(command=self.start_thread)
        button.pack()

        button = tk.Button(self.root, text="STOP")
        button.config(command=self.stop_shell_process)
        button.pack()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def save_config(self):
        with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def create_command(self):
        self.generate_command = f"""source /home/agx/mattergen-1.0.3/.venv/bin/activate && """
        self.generate_command += f"""mattergen-generate {self.config["result-path"]} """
        self.generate_command += f"""--pretrained-name={self.config["internal-model-selected"]} """
        self.generate_command += f"""--batch_size={self.config["batch-size"]} """
        self.generate_command += f"""--num_batches={self.config["num-batches"]} """

        print(self.generate_command)

    # Run mattergen CLI prompt
    def run_shell_process(self, command: str):
        #self.process = subprocess.run(["bash", "-c", command])
        self.process = subprocess.Popen(["bash", "-c", command])

    def stop_shell_process(self):
        if self.process and self.process.poll() is None:
            self.process.kill()
            print("Killed process.")
        else:
            print("No process running.")

    def start_thread(self):
        if self.process and self.process.poll() is None:
            print("Process already running.")
        else:
            print("Starting process.")
            self.create_command()
            self.thread = threading.Thread(
                target=self.run_shell_process,
                args=(self.generate_command,),
                daemon=True
            )
            self.thread.start()

    # Kills the entire process when closing window
    def on_close(self):
        try:
            os.killpg(0, signal.SIGTERM)
        except Exception:
            pass

        self.root.destroy()

    def tkDropDownMenu_internalModels_on_select(self, event):
        self.config["internal-model-selected"] = self.selected_model.get()
        self.save_config()

if __name__ == "__main__":
    app = App()
    app.run()