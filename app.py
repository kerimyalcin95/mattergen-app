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
        self.tkVar_diffusion_guidance_factor = None
        self.tkVar_num_batches = None
        self.tkVar_batch_size = None

        self.tkLabel_work_path = None
        self.tkButton_work_path = None
        self.tkEntry_work_path = None
        self.tkLabel_result_path = None
        self.tkButton_result_path = None
        self.tkEntry_result_path = None
        self.tkLabel_internal_models = None
        self.tkDropDownMenu_internalModels = None
        self.tkLabel_diffusion_guidance_factor = None
        self.tkEntry_diffusion_guidance_factor = None
        self.tkLabel_num_batches = None
        self.tkEntry_num_batches = None
        self.tkLabel_batch_size = None
        self.tkEntry_batch_size = None
        self.tkLabel_Process = None
        self.tkButton_Run = None
        self.tkButton_Stop = None

        self.tkLabelArray_property = []
        self.tkEntryArray_property = []
        self.tkVarArray_property = []
        
        self.number_of_avail_model_properties = 0
        self.has_avail_model_properties = False
        self.properties = None

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
            print("Running on Windows (experimental)")
            main_windows()
        elif sys.platform == "linux":
            print("Running on Linux distribution.")
            self.main_linux()
        else:
            print("Current platform: " + sys.platform)
            print("OS not supported.")

    def main_linux(self):

        def validate_positive_int(value):
            return value.isdigit() or value == ""
        
        def validate_positive_float(value):
            try:
                return float(value) > 0
            except ValueError:
                return False
        

        self.tkVar_work_path = tk.StringVar()
        self.tkVar_work_path.set(self.config["work-path-linux"])
        self.tkLabel_work_path = tk.Label(self.root, text="Path of the work directory:", anchor="w")
        self.tkLabel_work_path.pack(fill="x", padx=10, pady=(30, 0))

        self.tkEntry_work_path = tk.Entry(
            self.root,
            textvariable=self.tkVar_work_path)
        self.tkEntry_work_path.bind("<KeyRelease>", self.tkEntry_work_path_on_keyrelease)
        self.tkEntry_work_path.pack(fill="x", padx=10, pady=(0,2))

        self.tkButton_work_path = tk.Button(self.root, text="Browse")
        self.tkButton_work_path.config(command=self.tkButton_work_path_command)
        self.tkButton_work_path.pack(fill="x", padx=10, pady=(0,0))


        self.tkVar_result_path = tk.StringVar()
        self.tkVar_result_path.set(self.config["result-path"])
        self.tkLabel_result_path = tk.Label(self.root, text="Path of the result directory:", anchor="w")
        self.tkLabel_result_path.pack(fill="x", padx=10, pady=(10, 0))

        self.tkEntry_result_path = tk.Entry(
            self.root,
            textvariable=self.tkVar_result_path)
        self.tkEntry_result_path.bind("<KeyRelease>", self.tkEntry_result_path_on_keyrelease)
        self.tkEntry_result_path.pack(fill="x", padx=10, pady=(0,2))

        self.tkButton_result_path = tk.Button(self.root, text="Browse")
        self.tkButton_result_path.config(command=self.tkButton_result_path_command)
        self.tkButton_result_path.pack(fill="x", padx=10, pady=(0,0))

        self.tkLabel_internal_models = tk.Label(self.root, text="Available internal models:", anchor="w")
        self.tkLabel_internal_models.pack(fill="x", padx=10, pady=(30, 0))

        options_internal_models = self.config["internal-models"]
        self.tkVar_selected_model = tk.StringVar()
        self.tkVar_selected_model.set(self.config["internal-model-selected"])
        self.tkDropDownMenu_internalModels = ttk.Combobox(
            self.root,
            textvariable=self.tkVar_selected_model,
            values=options_internal_models,
            state="readonly"
        )
        self.tkDropDownMenu_internalModels.pack(fill="x", padx=10, pady=(0,10))
        self.tkDropDownMenu_internalModels.bind("<<ComboboxSelected>>", self.tkDropDownMenu_internalModels_on_select)

        # Properties to conditions on
        self.tkLabel_diffusion_guidance_factor = tk.Label(self.root, text="diffusion_guidance_factor:", anchor="w")

        self.tkVar_diffusion_guidance_factor = tk.StringVar()
        self.tkVar_diffusion_guidance_factor.set(self.config["diffusion_guidance_factor"])
        self.tkVar_diffusion_guidance_factor.trace_add("write", self.tkEntry_diffusion_guidance_factor_callback)

        self.tkEntry_diffusion_guidance_factor = tk.Entry(
        self.root,
            textvariable=self.tkVar_diffusion_guidance_factor,
            #validate="key",
            #validatecommand=(self.root.register(validate_positive_float), "%P")
            )
        self.tkEntry_diffusion_guidance_factor.bind("<KeyRelease>", self.tkEntry_diffusion_guidance_factor_on_keyrelease)

        self.update_available_number_of_model_properties()

        self.update_diffusion_guidance_factor_gui_visibility()
        self.update_properties_to_condition_on_gui_visibility()

        # Basic sampling parameters
        self.tkLabel_num_batches = tk.Label(self.root, text="Number of batches:", anchor="w")
        self.tkLabel_num_batches.pack(fill="x", padx=10, pady=(0,0))

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


        self.tkLabel_batch_size = tk.Label(self.root, text="Batch size:", anchor="w")
        self.tkLabel_batch_size.pack(fill="x", padx=10, pady=(0,0))

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

        # Run/Start buttons
        self.tkLabel_Process = tk.Label(self.root, text="Run/Stop the process:", anchor="w")
        self.tkLabel_Process.pack(fill="x", padx=10, pady=(30,5))

        self.tkButton_Run = tk.Button(self.root, text="RUN")
        self.tkButton_Run.config(command=self.start_thread)
        self.tkButton_Run.pack(fill="x", padx=10, pady=(0,0))

        self.tkButton_Stop = tk.Button(self.root, text="STOP")
        self.tkButton_Stop.config(command=self.stop_shell_process)
        self.tkButton_Stop.pack(fill="x", padx=10, pady=(5,10))


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

        if self.has_avail_model_properties:

            def is_number(s: str) -> bool:
                try:
                    float(s)
                    return True
                except ValueError:
                    return False

            self.generate_command += f"""--diffusion_guidance_factor={self.config["diffusion_guidance_factor"]} """
            self.generate_command += f"""--properties_to_condition_on="""
            self.generate_command += "\"{"

            for i in range(self.number_of_avail_model_properties):
                if i > 0:
                    self.generate_command += ","

                self.generate_command += ("\'" + self.properties[i] + "\':")
                if is_number(self.config[self.properties[i]]):
                    self.generate_command += self.config[self.properties[i]]
                else:
                    self.generate_command += ("\'" + self.config[self.properties[i]] + "\'")

            self.generate_command += "}\""

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

    def update_available_number_of_model_properties(self):
        self.number_of_avail_model_properties = len(self.config["model-conditions"][self.tkVar_selected_model.get()])

        if self.number_of_avail_model_properties > 0:
            self.has_avail_model_properties = True
        else:
            self.has_avail_model_properties = False

    def update_properties_to_condition_on_gui_visibility(self):
        for w in self.tkLabelArray_property:
            w.destroy()
        self.tkLabelArray_property.clear()

        for w in self.tkEntryArray_property:
            w.destroy()
        self.tkEntryArray_property.clear()
        self.tkVarArray_property.clear()

        if self.has_avail_model_properties:
            self.properties = self.config["model-conditions"][self.tkVar_selected_model.get()]

            for i in range(self.number_of_avail_model_properties):
                self.tkLabelArray_property.append(tk.Label(self.root, text=self.properties[i]+":", anchor="w"))

                self.tkVarArray_property.append(tk.StringVar())
                self.tkVarArray_property[i].set(self.config[self.properties[i]])
                self.tkVarArray_property[i].trace_add(
                    "write",
                    lambda *args, i=i: self.tkEntryArray_property_callback(i, *args)
                )
                self.tkEntryArray_property.append(tk.Entry(
                    self.root,
                    textvariable=self.tkVarArray_property[i]
                ))
                self.tkEntryArray_property[i].bind("<KeyRelease>", self.tkEntryArray_property_on_keyrelease)

            self.tkLabelArray_property[0].pack(after=self.tkEntry_diffusion_guidance_factor, fill="x", padx=10, pady=(5,0))
            self.tkEntryArray_property[0].pack(after=self.tkLabelArray_property[0], fill="x", padx=10, pady=(0,10))

            for i in range(self.number_of_avail_model_properties-1):
                self.tkLabelArray_property[i+1].pack(after=self.tkEntryArray_property[i], fill="x", padx=10, pady=(5,0))
                self.tkEntryArray_property[i+1].pack(after=self.tkLabelArray_property[i+1], fill="x", padx=10, pady=(0,10))

    def update_diffusion_guidance_factor_gui_visibility(self):
        if self.has_avail_model_properties:
            self.tkLabel_diffusion_guidance_factor.pack(after=self.tkDropDownMenu_internalModels, fill="x", padx=10, pady=(5,0))
            self.tkEntry_diffusion_guidance_factor.pack(after=self.tkLabel_diffusion_guidance_factor, fill="x", padx=10, pady=(0,10))
        else:
            self.tkLabel_diffusion_guidance_factor.pack_forget()
            self.tkEntry_diffusion_guidance_factor.pack_forget()


    def tkDropDownMenu_internalModels_on_select(self, event):
        self.config["internal-model-selected"] = self.tkVar_selected_model.get()
        self.save_config()

        self.update_available_number_of_model_properties()
        self.update_diffusion_guidance_factor_gui_visibility()
        self.update_properties_to_condition_on_gui_visibility()

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

    def tkEntry_diffusion_guidance_factor_on_keyrelease(self, event):
        self.save_config()

    def tkEntry_diffusion_guidance_factor_callback(self, *args):
            value = self.tkVar_diffusion_guidance_factor.get()

            try: 
                if float(value) > 0:
                    self.config["diffusion_guidance_factor"] = float(value)
            except ValueError:
                self.config["diffusion_guidance_factor"] = 1.0

            self.save_config

    def tkEntryArray_property_callback(self, i, *args):
        self.config[self.properties[i]] = self.tkVarArray_property[i].get()
        self.save_config()

    def tkEntryArray_property_on_keyrelease(self, event):
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