import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import threading
import subprocess
import sys

from pathlib import Path
import json

class App:
    """MatterGen-App"""

    def __init__(self):
        self.root = None

        self.base_dir = None
        self.config_path = None
        self.config = None

        # command for the mattergen-generate script
        self.generate_command = None

        # tk string variables
        self.tkVar_work_path = None
        self.tkVar_result_path = None
        self.tkVar_options_selected_model = None
        self.tkVar_diffusion_guidance_factor = None
        self.tkVar_num_batches = None
        self.tkVar_batch_size = None

        # tk elements
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

        # tk arrays
        self.tkLabelArray_property = []
        self.tkEntryArray_property = []
        self.tkVarArray_property = []
        
        self.number_of_avail_model_properties = 0
        self.has_avail_model_properties = False
        self.properties = None

        self.process = None
        self.thread = None

    def run(self):
        """
        Entry point of the app.
        """

        # check which os is running
        if sys.platform == "win32":
            # experimental (seems to work just fine)
            print("Running on Windows (experimental)")
            self.main()
        elif sys.platform == "linux":
            print("Running on Linux distribution.")
            self.main()
        else:
            print("Current platform: " + sys.platform)
            print("OS not supported.")

    def main(self):
        """main entry"""

        # set path of the configuration file
        self.base_dir = Path(__file__).resolve().parent 
        self.config_path = self.base_dir.parent / "mattergen-app" / "config.json"

        # load config file
        with open(self.config_path, "r") as f:
            self.config = json.load(f)

        # initialize window geometry
        self.root = tk.Tk()
        self.root.title("MatterGen-App")
        self.root.geometry(self.config["app-geometry"])

        def validate_positive_int(value):
            return value.isdigit() or value == ""
        
        def validate_positive_float(value):
            try:
                return float(value) > 0
            except ValueError:
                return False
        
        # gui elements: work path
        self.tkVar_work_path = tk.StringVar()
        self.tkVar_work_path.set(self.config["work-path"])
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

        # gui elements: result path
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

        # gui elements: internal available models
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

        # gui elements: properties to condition on
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

        # gui elements: basic sampling parameters
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

        # gui elements: run/start process
        self.tkLabel_Process = tk.Label(self.root, text="Run/Stop the process:", anchor="w")
        self.tkLabel_Process.pack(fill="x", padx=10, pady=(30,5))

        self.tkButton_Run = tk.Button(self.root, text="RUN")
        self.tkButton_Run.config(command=self.start_thread)
        self.tkButton_Run.pack(fill="x", padx=10, pady=(0,0))

        self.tkButton_Stop = tk.Button(self.root, text="STOP")
        self.tkButton_Stop.config(command=self.stop_shell_process)
        self.tkButton_Stop.pack(fill="x", padx=10, pady=(5,10))

        # configure and run app procedure
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def save_config(self):
        """save the config.json file
        """
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def create_command(self):
        """create the command string for the mattergen-generate script cli
        """
        if sys.platform == "win32":
            # mattergen-generate.exe has to be called directly from the environment
            self.generate_command = f"""cd "{self.config["work-path"]}"; .venv/Scripts/mattergen-generate.exe"""
            self.generate_command += f""" mattergen-generate --result-path="{self.config["result-path"]}" """
        elif sys.platform == "linux":
            self.generate_command = f"""source "{'' if self.config["work-path"]=='/' else self.config["work-path"] }/.venv/bin/activate" && """
            self.generate_command += f"""mattergen-generate --result-path="{self.config["result-path"]}" """

        # command parameter: internal model
        self.generate_command += f"""--pretrained-name={self.config["internal-model-selected"]} """

        # command parameter: batch size
        self.generate_command += f"""--batch_size={self.config["batch-size"]} """

        # command parameter: number of batches
        self.generate_command += f"""--num_batches={self.config["num-batches"]} """

        # command parameter: models to condition on
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

            # format: {"property1":"value1","property2":"value1", ... }
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

    def run_shell_process(self, command: str):
        """run the shell process

        Args:
            command (str): command to run on the corresponding shell
        """

        # run a process and invoke the command in powershell
        if sys.platform == "win32":
            self.process = subprocess.Popen(["powershell", "-c", command])

        # run a process and invoke the command in bash
        elif sys.platform == "linux":
            self.process = subprocess.Popen(["bash", "-c", command])

    def stop_shell_process(self):
        """stop the shell process
        """

        # kill the subprocess
        if sys.platform == "win32":
            if self.process and self.process.poll() is None:
                try:
                    subprocess.run(f"taskkill /F /T /PID {self.process.pid}", shell=True)
                    self.process.kill()
                    
                    print("Killed process.")
                except Exception:
                    pass
            else:
                print("No process running.")
        elif sys.platform == "linux":
            if self.process and self.process.poll() is None:
                self.process.kill()
                print("Killed process.")
            else:
                print("No process running.")

    def start_thread(self):
        """start a thread and run the shell process
        """
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

    def on_close(self):
        """protocol to apply when app window closes
        """

        # save window position and size of the app
        self.config["app-geometry"] = self.root.geometry()
        self.save_config()

        print("Exiting app.")

        # kill the process if running
        if sys.platform == "win32":
            if self.process and self.process.poll() is None:
                try:
                    subprocess.run(f"taskkill /F /T /PID {self.process.pid}", shell=True)
                    self.process.kill()
                    
                    print("Killed process.")
                except Exception:
                    pass
        elif sys.platform == "linux":
            if self.process and self.process.poll() is None:
                self.process.kill()
                print("Killed process.")

        self.root.destroy()

    def update_available_number_of_model_properties(self):
        """update the available number of properties from each model in the config.json file
                Example:    "chemical_system": ["chemical_system"]  -> 1 property
                            "dft_mag_density_hhi_score": [
                                "dft_mag_density",
                                "hhi_score"
                            ]                                       -> 2 properties

        """
        self.number_of_avail_model_properties = len(self.config["model-conditions"][self.tkVar_selected_model.get()])

        if self.number_of_avail_model_properties > 0:
            self.has_avail_model_properties = True
        else:
            self.has_avail_model_properties = False

    def update_properties_to_condition_on_gui_visibility(self):
        """toggle gui elements depending on current chosen model in the drop down menu
        and how many properties to condition on the model.
        """

        # destroy tk arrays
        for w in self.tkLabelArray_property:
            w.destroy()
        self.tkLabelArray_property.clear()

        for w in self.tkEntryArray_property:
            w.destroy()
        self.tkEntryArray_property.clear()
        self.tkVarArray_property.clear()

        # create tk elements and pack them in the right order and layout
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

            # pack first element to the tk diffusion_guidance_factor element
            self.tkLabelArray_property[0].pack(after=self.tkEntry_diffusion_guidance_factor, fill="x", padx=10, pady=(5,0))
            self.tkEntryArray_property[0].pack(after=self.tkLabelArray_property[0], fill="x", padx=10, pady=(0,10))

            # pack all other elements after that
            for i in range(self.number_of_avail_model_properties-1):
                self.tkLabelArray_property[i+1].pack(after=self.tkEntryArray_property[i], fill="x", padx=10, pady=(5,0))
                self.tkEntryArray_property[i+1].pack(after=self.tkLabelArray_property[i+1], fill="x", padx=10, pady=(0,10))

    def update_diffusion_guidance_factor_gui_visibility(self):
        """toggle diffusion_guidance_factor tk element depending on the chosen model from the dropdown menu
        """
        if self.has_avail_model_properties:
            self.tkLabel_diffusion_guidance_factor.pack(after=self.tkDropDownMenu_internalModels, fill="x", padx=10, pady=(5,0))
            self.tkEntry_diffusion_guidance_factor.pack(after=self.tkLabel_diffusion_guidance_factor, fill="x", padx=10, pady=(0,10))
        else:
            self.tkLabel_diffusion_guidance_factor.pack_forget()
            self.tkEntry_diffusion_guidance_factor.pack_forget()

    def tkDropDownMenu_internalModels_on_select(self, event):
        """dropdown menu event handler: on select

        Args:
            event (Any): event triggered on select
        """
        # set and save config
        self.config["internal-model-selected"] = self.tkVar_selected_model.get()
        self.save_config()

        # display properties to condition on depending on chosen model
        self.update_available_number_of_model_properties()
        self.update_diffusion_guidance_factor_gui_visibility()
        self.update_properties_to_condition_on_gui_visibility()

    def tkEntry_work_path_on_keyrelease(self, event):
        """work path entry field event handler: on keyrelease

        Args:
            event (Any): event triggered on keyrelease
        """
        # set and save config
        self.config["work-path"] = self.tkVar_work_path.get()
        self.save_config()

    def tkButton_work_path_command(self, *args):
        """command for pressing the button to choose the work path
        """
        path = filedialog.askdirectory()
        if path:  
            self.tkVar_work_path.set(path)
        else:
            self.tkVar_work_path.set("/tmp")
        
        self.config["work-path"] = self.tkVar_work_path.get()
        self.save_config()

    def tkEntry_result_path_on_keyrelease(self, event):
        """result path entry field event handler: on keyrelease

        Args:
            event (Any): event triggered on keyrelease
        """
        self.config["result-path"] = self.tkVar_result_path.get()
        self.save_config()

    def tkButton_result_path_command(self, *args):
        """command for pressing the button to choose the result path
        """
        path = filedialog.askdirectory()
        if path:  
            self.tkVar_result_path.set(path)
        else:
            self.tkVar_result_path.set((self.tkVar_work_path.get() + "/results"))
        
        self.config["result-path"] = self.tkVar_result_path.get()
        self.save_config()

    def tkEntry_diffusion_guidance_factor_on_keyrelease(self, event):
        """diffusion_guidance_factor entry field event handler: on keyrelease

        Args:
            event (Any): event triggered on keyrelease
        """
        self.save_config()

    def tkEntry_diffusion_guidance_factor_callback(self, *args):
        """diffusion_guidance_factor callback for input validation
        """
        value = self.tkVar_diffusion_guidance_factor.get()

        try: 
            if float(value) > 0:
                self.config["diffusion_guidance_factor"] = float(value)
        except ValueError:
            self.config["diffusion_guidance_factor"] = 1.0

        self.save_config

    def tkEntryArray_property_callback(self, i, *args):
        """property array callback for input validation
        """
        self.config[self.properties[i]] = self.tkVarArray_property[i].get()
        self.save_config()

    def tkEntryArray_property_on_keyrelease(self, event):
        """property array entry field event handler: on keyrelease

        Args:
            event (Any): event triggered on keyrelease
        """
        self.save_config()

    def tkEntry_num_batches_on_keyrelease(self, event):
        """number of batches entry field event handler: on keyrelease

        Args:
            event (Any): event triggered on keyrelease
        """
        self.save_config()

    def tkEntry_num_batches_callback(self, *args):
        """number of batches entry callback for input validation
        """
        value = self.tkVar_num_batches.get()

        if value.isdigit():
            self.config["num-batches"] = int(value)
            if int(value) == 0:
                self.config["num-batches"] = 1
        else:
            self.config["num-batches"] = 1

        self.save_config

    def tkEntry_batch_size_on_keyrelease(self, event):
        """batch size entry field event handler: on keyrelease

        Args:
            event (Any): event triggered on keyrelease
        """
        self.save_config()

    def tkEntry_batch_size_callback(self, *args):
        """batch size entry callback for input validation
        """
        value = self.tkVar_batch_size.get()

        if value.isdigit():
            self.config["batch-size"] = int(value)
            if int(value) == 0:
                self.config["batch-size"] = 1
        else:
            self.config["batch-size"] = 1

        self.save_config

# app entry point
if __name__ == "__main__":
    app = App()
    app.run()