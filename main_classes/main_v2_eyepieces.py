from OpticalSystemManager_eyepieces import OpticalSystemManager_eyepieces
import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as scrolledtext
import sys
import threading
import pythoncom
import os

data_from_ui = None
final_data = None

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
    try:
        # Construction du dictionnaire de données à partir de l'interface utilisateur
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
            "starting_depth": int(starting_depth_entry.get()),
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
        start_optimization_thread(data)  # Passe directement les données au thread d'optimisation
    except ValueError as e:
        print(f"Error in input data: {e}")

def start_optimization_thread(data):
    def manage_optical_system():
        global final_data
        pythoncom.CoInitialize()  # Initialise COM pour ce thread
        try:
            optical_system_manager = OpticalSystemManager_eyepieces()
            optical_system_manager.update_parameters_from_ui(data)  # Met à jour les paramètres avec les données de l'UI
            optical_system_manager.start_system()
            final_data=optical_system_manager.evolve_and_optimize()
            optical_system_manager.end_system()
            print("Session CodeV finished")
            # Utilise `root.after` pour planifier l'affichage des données dans l'UI sur le thread principal
            root.after(0, lambda: display_final_data_in_ui(final_data))
        except Exception as e:
            print(f"An error has occurred : {e}")
        finally:
            pythoncom.CoUninitialize()  # Désinitialise COM pour ce thread
    def display_final_data_in_ui(final_data):
        for system_data in final_data:
            tree.insert("", "end", values=(
                system_data['Node ID'], system_data['Parent ID'], system_data['Merit Function'],
                system_data['EFL'], system_data['SEQ File Path']
            ))
        update_seq_files_combobox()

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
    

def update_seq_files_combobox():
    # Extraire tous les chemins des fichiers .seq de la dernière colonne du TreeView
    seq_files = [tree.item(row)['values'][-1] for row in tree.get_children()]
    # Mettre à jour le combobox avec les noms de ces fichiers
    seq_combobox['values'] = seq_files
    if seq_files:
        seq_combobox.current(0)  # Sélectionnez le premier fichier par défaut, si la liste n'est pas vide

def open_selected_seq_file():
    selected_file_path = seq_combobox.get()
    if selected_file_path:
        try:
            os.startfile(selected_file_path)
        except Exception as e:
            print(f"Error opening file : {e}")
    else:
        print("No files selected")

def perform_action(action_name):
    selected_file = seq_combobox.get()
    if not selected_file:
        print("No files selected")
        return

    print(f"Action {action_name} selected for the file {selected_file}")
    # Ici, vous pouvez ajouter la logique spécifique à chaque action
    # Par exemple, appeler une fonction différente en fonction de action_name

def show_actions_window():
    actions_window = tk.Toplevel(root)
    actions_window.title("Select the actions")
    
    tk.Checkbutton(actions_window, text="Spot Diagram", variable=spot_diagram_var).pack(anchor='w')
    tk.Checkbutton(actions_window, text="MTF", variable=mtf_var).pack(anchor='w')
    tk.Checkbutton(actions_window, text="Spot Diameter", variable=spot_diameter_var).pack(anchor='w')
    
    tk.Button(actions_window, text="Apply", command=apply_actions).pack()

def apply_actions():
    selected_file = seq_combobox.get()
    if not selected_file:
        print("No file selected")
        return

    if spot_diagram_var.get():
        print(f"Spot Diagram selected for {selected_file}")
        # Logique pour Spot Diagram ici
    
    if mtf_var.get():
        print(f"MTF selected for {selected_file}")
        # Logique pour MTF ici
    
    if spot_diameter_var.get():
        print(f"Spot Diameter selected for {selected_file}")
        # Logique pour Spot Diameter ici


def initialize_default_values():
    # Default Wavelengths
    default_wavelengths = [486.1327, 546.074, 587.5618, 632.2, 657.2722]
    for wavelength in default_wavelengths:
        add_wavelength_entry()
        wavelength_entries[-1][1].insert(0, str(wavelength))

    # Default Fields
    default_fields = [(0, 3), (0, 6), (0, 35)]
    for field in default_fields:
        add_field_entry()
        field_entries[-1][1].insert(0, str(field[0]))
        field_entries[-1][2].insert(0, str(field[1]))

    # EFL, fd, and other singular entries
    efl_entry.insert(0, "1")
    fd_entry.insert(0, "5")

    # SP Parameters
    epsilon_entry.insert(0, "0.5")
    lens_thickness_entry.insert(0, "0.2")
    air_distance_steps_entry.insert(0, "0")
    base_material_entry.insert(0, "NBK7_SCHOTT")
    
    # Default Lens Thickness Steps
    default_lens_thickness_steps = [0.05, 0.1, 0.15, 0.4]
    for step in default_lens_thickness_steps:
        add_lens_thickness_step_entry()
        lens_thickness_steps_entries[-1][1].insert(0, str(step))

    # Other defaults
    starting_depth_entry.insert(0, "0")
    target_depth_entry.insert(0, "1")
    base_file_path_entry.insert(0, "C:/CVUSER")
    
    # Starting System Parameters
    surface1_radius_entry.insert(0, "59.33336")
    surface1_thickness_entry.insert(0, "0.2")
    surface1_material_entry.insert(0, "NBK7_SCHOTT")
    surface2_radius_entry.insert(0, "-391.44174")
    surface2_thickness_entry.insert(0, "97.703035")



if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    root.title("Optical System Configuration Interface")

    spot_diagram_var = tk.IntVar()
    mtf_var = tk.IntVar()
    spot_diameter_var = tk.IntVar()
    
    wavelength_entries = []
    field_entries = []
    lens_thickness_steps_entries = []

    tab_control = ttk.Notebook(root)
    tab_environment = ttk.Frame(tab_control)
    tab_sp = ttk.Frame(tab_control)
    tab_tree = ttk.Frame(tab_control)
    tab_starting_system = ttk.Frame(tab_control)
    tab_console_output = ttk.Frame(tab_control)
    tab_output=ttk.Frame(tab_control)
    
    tab_control.add(tab_environment, text='Environment')
    tab_control.add(tab_sp, text='SP Parameters')
    tab_control.add(tab_tree, text='Tree')
    tab_control.add(tab_starting_system, text='Starting System')
    tab_control.add(tab_console_output, text='Console Output')
    tab_control.add(tab_output,text='Output')
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

    ttk.Label(tree_frame, text="Starting Depth").pack()
    starting_depth_entry = ttk.Entry(tree_frame)
    starting_depth_entry.pack()
   
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
    
    # Output tab
    output_frame = ttk.LabelFrame(tab_output, text="Optimization Results")
    output_frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Create a Treeview widget for tab_output
    tree = ttk.Treeview(output_frame)
    tree["columns"] = ("Node ID", "Parent ID", "Merit Function", "EFL", "SEQ File Path")
    tree.configure(show='headings')
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")
       

    tree.pack(expand=True, fill="both")
    
    # Créez un frame pour le combobox et le placez-le sous le treeview
    seq_combobox_frame = ttk.Frame(output_frame)
    seq_combobox_frame.pack(fill='x', expand=False, padx=10, pady=5)

    # Créez le combobox pour sélectionner un fichier .seq
    seq_combobox = ttk.Combobox(seq_combobox_frame, state="readonly", width=50)
    seq_combobox.pack(side=tk.LEFT, padx=5, pady=5)

    # Vous pouvez ajouter un bouton à côté du combobox si nécessaire, par exemple, pour ouvrir le fichier .seq sélectionné
    open_seq_file_button = ttk.Button(seq_combobox_frame, text="Open", command=open_selected_seq_file)
    open_seq_file_button.pack(side=tk.LEFT, padx=5)
    
    # Ouvrir actions lorsque cliquées
    actions_button = ttk.Button(seq_combobox_frame, text="Actions", command=show_actions_window)
    actions_button.pack(side=tk.LEFT, padx=5)

    # Call the function to initialize default values
    initialize_default_values()

    # Submit button
    submit_button = ttk.Button(root, text="Submit", command=submit)
    submit_button.pack(pady=10)

    redirect_logging()
    # Run the GUI
    root.mainloop()
