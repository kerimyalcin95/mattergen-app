import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

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

        self.tkVar_work_path = None
        self.tkVar_result_path = None
        self.tkVar_options_selected_model = None
        self.tkVar_num_batches = None
        self.tkVar_batch_size = None

        self.process = None
        self.thread = None

    def run(self):

        # Load config file
        self.BASE_DIR = Path(__file__).resolve().parent 
        self.CONFIG_PATH = self.BASE_DIR.parent / "mattergen-app" / "config.json"

        with open(self.CONFIG_PATH, "r") as f:
            self.config = json.load(f)

        # Initialize window geometry
        self.root = tk.Tk()
        self.root.title("MatterGen-App")
        self.root.geometry(self.config["app-geometry"])

        if sys.platform == "win32":
        # experimental
            main_windows()
        elif sys.platform == "linux":
            print("Running on Linux distribution.")
        else:
            print("Current platform: " + sys.platform)
            print("OS not supported.")

        def validate_positive_int(value):
            return value.isdigit() or value == ""
        

        self.tkVar_work_path = tk.StringVar()
        self.tkVar_work_path.set(self.config["work-path-linux"])
        tkLabel_work_path = tk.Label(self.root, text="Path of the work directory:", anchor="w")
        tkLabel_work_path.pack(fill="x", padx=10, pady=(30, 0))

        self.tkEntry_work_path = tk.Entry(
            self.root,
            textvariable=self.tkVar_work_path)
        self.tkEntry_work_path.bind("<KeyRelease>", self.tkEntry_work_path_on_keyrelease)
        self.tkEntry_work_path.pack(fill="x", padx=10, pady=(0,2))

        tkButton_work_path = tk.Button(self.root, text="Browse")
        tkButton_work_path.config(command=self.tkButton_work_path_command)
        tkButton_work_path.pack(fill="x", padx=10, pady=(0,0))


        self.tkVar_result_path = tk.StringVar()
        self.tkVar_result_path.set(self.config["result-path"])
        tkLabel_result_path = tk.Label(self.root, text="Path of the result directory:", anchor="w")
        tkLabel_result_path.pack(fill="x", padx=10, pady=(10, 0))

        self.tkEntry_result_path = tk.Entry(
            self.root,
            textvariable=self.tkVar_result_path)
        self.tkEntry_result_path.bind("<KeyRelease>", self.tkEntry_result_path_on_keyrelease)
        self.tkEntry_result_path.pack(fill="x", padx=10, pady=(0,2))

        tkButton_result_path = tk.Button(self.root, text="Browse")
        tkButton_result_path.config(command=self.tkButton_result_path_command)
        tkButton_result_path.pack(fill="x", padx=10, pady=(0,0))


        tkLabel_internal_models = tk.Label(self.root, text="Available internal models:", anchor="w")
        tkLabel_internal_models.pack(fill="x", padx=10, pady=(30, 0))

        options_internal_models = self.config["internal-models"]
        self.tkVar_selected_model = tk.StringVar()
        self.tkVar_selected_model.set(self.config["internal-model-selected"])
        tkDropDownMenu_internalModels = ttk.Combobox(
            self.root,
            textvariable=self.tkVar_selected_model,
            values=options_internal_models,
            state="readonly"
        )
        tkDropDownMenu_internalModels.pack(fill="x", padx=10, pady=(0,10))
        tkDropDownMenu_internalModels.bind("<<ComboboxSelected>>", self.tkDropDownMenu_internalModels_on_select)


        tkLabel_num_batches = tk.Label(self.root, text="Number of batches:", anchor="w")
        tkLabel_num_batches.pack(fill="x", padx=10, pady=(10,0))

        self.tkVar_num_batches = tk.StringVar()
        self.tkVar_num_batches.set(self.config["num-batches"])
        self.tkVar_num_batches.trace_add("write", self.tkEntry_num_batches_callback)
        
        self.tkEntry_num_batches = tk.Entry(
            self.root,
            textvariable=self.tkVar_num_batches,
            validate="key",
            validatecommand=(self.root.register(validate_positive_int), "%P"))
        self.tkEntry_num_batches.bind("<KeyRelease>", self.tkEntry_num_batches_on_keyrelease)
        self.tkEntry_num_batches.pack(fill="x", padx=10, pady=(0,10))


        tkLabel_batch_size = tk.Label(self.root, text="Batch size:", anchor="w")
        tkLabel_batch_size.pack(fill="x", padx=10, pady=(0,0))

        self.tkVar_batch_size = tk.StringVar()
        self.tkVar_batch_size.set(self.config["batch-size"])
        self.tkVar_batch_size.trace_add("write", self.tkEntry_batch_size_callback)
        
        self.tkEntry_batch_size = tk.Entry(
            self.root,
            textvariable=self.tkVar_batch_size,
            validate="key",
            validatecommand=(self.root.register(validate_positive_int), "%P"))
        self.tkEntry_batch_size.bind("<KeyRelease>", self.tkEntry_batch_size_on_keyrelease)
        self.tkEntry_batch_size.pack(fill="x", padx=10, pady=(0,10))
        

        tkLabel_Process = tk.Label(self.root, text="Run/Stop the process:", anchor="w")
        tkLabel_Process.pack(fill="x", padx=10, pady=(30,5))

        tkButton_Run = tk.Button(self.root, text="RUN")
        tkButton_Run.config(command=self.start_thread)
        tkButton_Run.pack(fill="x", padx=10, pady=(0,0))

        tkButton_Stop = tk.Button(self.root, text="STOP")
        tkButton_Stop.config(command=self.stop_shell_process)
        tkButton_Stop.pack(fill="x", padx=10, pady=(5,10))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def save_config(self):
        with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def create_command(self):
        self.generate_command = f"""source {'' if self.config["work-path-linux"]=='/' else self.config["work-path-linux"] }/.venv/bin/activate && """
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

    # Safe window geometry (size, position) and kill the app
    def on_close(self):
        self.config["app-geometry"] = self.root.geometry()
        self.save_config()

        print("Exiting app.")
        # Hard kill in case process got stuck
        try:
            os.killpg(0, signal.SIGTERM)
        except Exception:
            pass

        self.root.destroy()

    def tkDropDownMenu_internalModels_on_select(self, event):
        self.config["internal-model-selected"] = self.tkVar_selected_model.get()
        self.save_config()

    def tkEntry_work_path_on_keyrelease(self, event):
        self.config["work-path-linux"] = self.tkVar_work_path.get()
        self.save_config()

    def tkButton_work_path_command(self, *args):
        path = filedialog.askdirectory()
        if path:  
            self.tkVar_work_path.set(path)
        else:
            self.tkVar_work_path.set("/tmp")
        
        self.config["work-path-linux"] = self.tkVar_work_path.get()
        self.save_config()

    def tkEntry_result_path_on_keyrelease(self, event):
        self.config["result-path"] = self.tkVar_result_path.get()
        self.save_config()

    def tkButton_result_path_command(self, *args):
        path = filedialog.askdirectory()
        if path:  
            self.tkVar_result_path.set(path)
        else:
            self.tkVar_result_path.set((self.tkVar_work_path.get() + "/results"))
        
        self.config["result-path"] = self.tkVar_result_path.get()
        self.save_config()

    def tkEntry_num_batches_on_keyrelease(self, event):
        self.save_config()

    def tkEntry_num_batches_callback(self, *args):
            value = self.tkVar_num_batches.get()

            if value.isdigit():
                self.config["num-batches"] = int(value)
                if int(value) == 0:
                    self.config["num-batches"] = 1
            else:
                self.config["num-batches"] = 1

            self.save_config

    def tkEntry_batch_size_on_keyrelease(self, event):
        self.save_config()

    def tkEntry_batch_size_callback(self, *args):
            value = self.tkVar_batch_size.get()

            if value.isdigit():
                self.config["batch-size"] = int(value)
                if int(value) == 0:
                    self.config["batch-size"] = 1
            else:
                self.config["batch-size"] = 1

            self.save_config

if __name__ == "__main__":
    app = App()
    app.run()