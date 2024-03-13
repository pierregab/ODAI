from OpticalSystemManager_eyepieces import OpticalSystemManager_eyepieces
import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as scrolledtext
import sys
import threading
import pythoncom

data_from_ui = None

class PrintLogger:  # create file like object
    def __init__(self, textbox):  # pass reference to text widget
        self.textbox = textbox  # keep ref

    def write(self, text):
        self.textbox.configure(state="normal")  # make field editable
        self.textbox.insert("end", text)  # write text to textbox
        self.textbox.see("end")  # scroll to end
        self.textbox.configure(state="disabled")  # make field readonly

    def flush(self):  # needed for file like object
        pass


# Function to dynamically add a wavelength entry
def add_wavelength_entry():
    frame = ttk.Frame(wavelengths_container)
    frame.pack(padx=5, pady=5)

    entry = ttk.Entry(frame, width=20)
    entry.pack(side=tk.LEFT)

    remove_button = ttk.Button(frame, text="-", command=lambda frame=frame: frame.destroy())
    remove_button.pack(side=tk.LEFT)

    wavelength_entries.append((frame, entry))

# Function to dynamically add a field entry
def add_field_entry():
    frame = ttk.Frame(fields_container)
    frame.pack(padx=5, pady=5)

    entry1 = ttk.Entry(frame, width=10)
    entry1.pack(side=tk.LEFT)
    ttk.Label(frame, text=", ").pack(side=tk.LEFT)  # Visual separator
    entry2 = ttk.Entry(frame, width=10)
    entry2.pack(side=tk.LEFT)

    remove_button = ttk.Button(frame, text="-", command=lambda frame=frame: frame.destroy())
    remove_button.pack(side=tk.LEFT)

    field_entries.append((frame, entry1, entry2))

# Function to dynamically add a lens thickness step entry
def add_lens_thickness_step_entry():
    frame = ttk.Frame(lens_thickness_steps_container)
    frame.pack(padx=5, pady=5)

    entry = ttk.Entry(frame, width=20)
    entry.pack(side=tk.LEFT)

    remove_button = ttk.Button(frame, text="-", command=lambda frame=frame: frame.destroy())
    remove_button.pack(side=tk.LEFT)

    lens_thickness_steps_entries.append((frame, entry))

# Function to submit the data and setup the optical system
def submit():
    global data_from_ui
    try:
        data = {
            "wavelengths": [float(entry[1].get()) for entry in wavelength_entries],
            "fields": [(float(entry[1].get()), float(entry[2].get())) for entry in field_entries],
            "efl": float(efl_entry.get()),
            "epsilon": float(epsilon_entry.get()),
            "lens_thickness_steps": [float(entry[1].get()) for entry in lens_thickness_steps_entries],
            "air_distance_steps": list(map(int, air_distance_steps_entry.get().split(','))),
            "lens_thickness": float(lens_thickness_entry.get()),
            "base_material": base_material_entry.get(),
            "target_depth": int(target_depth_entry.get()),
            "base_file_path": base_file_path_entry.get(),
            "fd": float(fd_entry.get()),
            "starting_system": {
                "surface1": {
                    "radius": float(surface1_radius_entry.get()),
                    "lens_thickness": float(surface1_thickness_entry.get()),
                    "material": surface1_material_entry.get(),
                },
                "surface2": {
                    "radius": float(surface2_radius_entry.get()),
                    "lens_thickness": float(surface2_thickness_entry.get()),
                }
            }
        }
        data_from_ui = data
    except ValueError as e:
        print(f"Error in input data: {e}")
        return
    
   # Lancement des opérations de l'optical system manager dans un nouveau thread
    def manage_optical_system():
        pythoncom.CoInitialize()  # Initialise COM pour ce thread
        try:
            if data_from_ui:
                optical_system_manager = OpticalSystemManager_eyepieces()
                optical_system_manager.update_parameters_from_ui(data_from_ui)
                optical_system_manager.start_system()
                optical_system_manager.evolve_and_optimize()
                optical_system_manager.end_system()
                print("Session CodeV terminée.")
        except Exception as e:
            print(f"Une erreur est survenue : {e}")
        finally:
            pythoncom.CoUninitialize()  # Uninitialize COM pour ce thread
    
    # Création et démarrage du thread
    thread = threading.Thread(target=manage_optical_system)
    thread.start()

# Initialize PrintLogger and redirect stdout
def redirect_logging():
    logger = PrintLogger(console_text)
    sys.stdout = logger
    sys.stderr = logger

# Reset logging to default
def reset_logging():
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    root.title("Optical System Configuration Interface")

    wavelength_entries = []
    field_entries = []
    lens_thickness_steps_entries = []

    tab_control = ttk.Notebook(root)
    tab_environment = ttk.Frame(tab_control)
    tab_sp = ttk.Frame(tab_control)
    tab_tree = ttk.Frame(tab_control)
    tab_starting_system = ttk.Frame(tab_control)
    tab_console_output = ttk.Frame(tab_control)
    
    tab_control.add(tab_environment, text='Environment')
    tab_control.add(tab_sp, text='SP Parameters')
    tab_control.add(tab_tree, text='Tree')
    tab_control.add(tab_starting_system, text='Starting System')
    tab_control.add(tab_console_output, text='Console Output')
    tab_control.pack(expand=1, fill="both")

    # Environment tab
    env_frame = ttk.LabelFrame(tab_environment, text="Environment")
    env_frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Frame for wavelength entries
    wavelengths_frame = ttk.Frame(env_frame)
    wavelengths_frame.pack()
    ttk.Button(wavelengths_frame, text="+ Add Wavelength", command=add_wavelength_entry).pack()

    # Container for wavelength entries
    wavelengths_container = ttk.Frame(env_frame)
    wavelengths_container.pack()

    # Frame for field entries
    fields_frame = ttk.Frame(env_frame)
    fields_frame.pack()
    ttk.Button(fields_frame, text="+ Add Field", command=add_field_entry).pack()

    # Container for field entries
    fields_container = ttk.Frame(env_frame)
    fields_container.pack()

    # EFL entry
    ttk.Label(env_frame, text="EFL").pack()
    efl_entry = ttk.Entry(env_frame)
    efl_entry.pack()

    # Entrance fd
    ttk.Label(env_frame, text="fd").pack()
    fd_entry = ttk.Entry(env_frame)
    fd_entry.pack()

    # SP Parameters tab
    sp_frame = ttk.LabelFrame(tab_sp, text="SP Parameters")
    sp_frame.pack(expand=True, fill="both", padx=10, pady=10)

    ttk.Label(sp_frame, text="Epsilon").pack()
    epsilon_entry = ttk.Entry(sp_frame)
    epsilon_entry.pack()

    # Frame for lens thickness steps entries
    lens_thickness_steps_frame = ttk.Frame(sp_frame)
    lens_thickness_steps_frame.pack()
    ttk.Button(lens_thickness_steps_frame, text="+ Add Lens Thickness Step", command=add_lens_thickness_step_entry).pack()

    # Container for lens thickness steps entries
    lens_thickness_steps_container = ttk.Frame(sp_frame)
    lens_thickness_steps_container.pack()

    ttk.Label(sp_frame, text="Air Distance Steps").pack()
    air_distance_steps_entry = ttk.Entry(sp_frame)
    air_distance_steps_entry.pack()

    ttk.Label(sp_frame, text="Lens Thickness").pack()
    lens_thickness_entry = ttk.Entry(sp_frame)
    lens_thickness_entry.pack()

    ttk.Label(sp_frame, text="Base Material").pack()
    base_material_entry = ttk.Entry(sp_frame)
    base_material_entry.pack()

    # Tree tab
    tree_frame = ttk.LabelFrame(tab_tree, text="Tree")
    tree_frame.pack(expand=True, fill="both", padx=10, pady=10)

    ttk.Label(tree_frame, text="Target Depth").pack()
    target_depth_entry = ttk.Entry(tree_frame)
    target_depth_entry.pack()

    ttk.Label(tree_frame, text="Base File Path").pack()
    base_file_path_entry = ttk.Entry(tree_frame)
    base_file_path_entry.pack()

    # Starting System tab modifications
    starting_system_frame = ttk.LabelFrame(tab_starting_system, text="Starting System Parameters")
    starting_system_frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Surface 1 Parameters
    surface1_frame = ttk.Frame(starting_system_frame)
    surface1_frame.pack(fill="x", padx=5, pady=5)

    ttk.Label(surface1_frame, text="Surface 1 Radius:").pack(side=tk.LEFT)
    surface1_radius_entry = ttk.Entry(surface1_frame, width=10)
    surface1_radius_entry.pack(side=tk.LEFT)

    ttk.Label(surface1_frame, text="Lens Thickness:").pack(side=tk.LEFT)
    surface1_thickness_entry = ttk.Entry(surface1_frame, width=10)
    surface1_thickness_entry.pack(side=tk.LEFT)

    ttk.Label(surface1_frame, text="Base Material:").pack(side=tk.LEFT)
    surface1_material_entry = ttk.Entry(surface1_frame, width=10)
    surface1_material_entry.pack(side=tk.LEFT)

    # Surface 2 Parameters
    surface2_frame = ttk.Frame(starting_system_frame)
    surface2_frame.pack(fill="x", padx=5, pady=5)

    ttk.Label(surface2_frame, text="Surface 2 Radius:").pack(side=tk.LEFT)
    surface2_radius_entry = ttk.Entry(surface2_frame, width=10)
    surface2_radius_entry.pack(side=tk.LEFT)

    ttk.Label(surface2_frame, text="Lens Thickness:").pack(side=tk.LEFT)
    surface2_thickness_entry = ttk.Entry(surface2_frame, width=10)
    surface2_thickness_entry.pack(side=tk.LEFT)

     # Console Output tab
    console_output_frame = ttk.LabelFrame(tab_console_output, text="Console Output")
    console_output_frame.pack(expand=True, fill="both", padx=10, pady=10)

    console_text = scrolledtext.ScrolledText(console_output_frame, wrap=tk.WORD, width=40, height=10)
    console_text.pack(expand=True, fill="both")

    # Submit button
    submit_button = ttk.Button(root, text="Submit", command=submit)
    submit_button.pack(pady=10)

    redirect_logging()
    # Run the GUI
    root.mainloop()
