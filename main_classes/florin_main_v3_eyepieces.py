from OpticalSystemManager_eyepieces import OpticalSystemManager_eyepieces
from SystemSetup_module import SystemSetup
import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as scrolledtext
import sys
import threading
import pythoncom
import os

data_from_ui = None
final_data = None

class PrintLogger:
    def __init__(self, textbox):  # Initialize with a reference to the GUI textbox
        self.textbox = textbox

    def write(self, text):
        self.textbox.configure(state="normal")  # Enable editing of the textbox
        self.textbox.insert(tk.END, text)  # Insert the text at the end of the textbox
        self.textbox.see(tk.END)  # Scroll to the end of the textbox
        self.textbox.configure(state="disabled")  # Disable editing of the textbox

    def flush(self):  # Placeholder for the flush method
        pass

class OpticalSystemConfigInterface:
    def __init__(self, root):
        self.root = root
        self.setup_variables()
        self.setup_ui()
        self.redirect_logging()
        self.initialize_default_values()
        self.system=SystemSetup()

    def setup_variables(self):
        self.spot_diagram_var = tk.IntVar()
        self.mtf_var = tk.IntVar()
        self.spot_diameter_var = tk.IntVar()
        self.wavelength_entries = []
        self.field_entries = []
        self.lens_thickness_steps_entries = []

    def setup_ui(self):
        self.root.title("Optical System Configuration Interface")
        self.tab_control = ttk.Notebook(self.root)
        self.setup_tabs()
        self.tab_control.pack(expand=1, fill="both")
        submit_button = ttk.Button(self.root, text="Submit", command=self.submit)
        submit_button.pack(pady=10)
        
       

    def setup_tabs(self):
        self.tab_environment = self.create_tab("Environment")
        self.tab_sp = self.create_tab("SP Parameters")
        self.tab_tree = self.create_tab("Tree")
        self.tab_starting_system = self.create_tab("Starting System")
        self.tab_console_output = self.create_tab("Console Output")
        self.tab_output = self.create_tab("Output")
        
        self.setup_environment_tab()
        self.setup_sp_parameters_tab()
        self.setup_tree_tab()
        self.setup_starting_system_tab()
        self.setup_console_output_tab()
        self.setup_output_tab()

    def create_tab(self, title):
        tab = ttk.Frame(self.tab_control)
        self.tab_control.add(tab, text=title)
        return tab

    def setup_environment_tab(self):
        env_frame = ttk.LabelFrame(self.tab_environment, text="Environment Settings")
        env_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Section pour les entrées de longueur d'onde
        wavelengths_frame = ttk.Frame(env_frame)
        wavelengths_frame.pack(fill="x", pady=5)
        ttk.Button(wavelengths_frame, text="+ Add Wavelength", command=self.add_wavelength_entry).pack()
        self.wavelengths_container = ttk.Frame(env_frame)
        self.wavelengths_container.pack(fill="both", expand=True)

        # Section pour les entrées de champs
        fields_frame = ttk.Frame(env_frame)
        fields_frame.pack(fill="x", pady=5)
        ttk.Button(fields_frame, text="+ Add Field", command=self.add_field_entry).pack()
        self.fields_container = ttk.Frame(env_frame)
        self.fields_container.pack(fill="both", expand=True)

        # Entrée pour EFL
        ttk.Label(env_frame, text="EFL").pack()
        self.efl_entry = ttk.Entry(env_frame)
        self.efl_entry.pack()

        # Entrée pour fd
        ttk.Label(env_frame, text="fd").pack()
        self.fd_entry = ttk.Entry(env_frame)
        self.fd_entry.pack()

        
    def setup_sp_parameters_tab(self):
        sp_frame = ttk.LabelFrame(self.tab_sp, text="SP Parameters")
        sp_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Entrée pour Epsilon
        ttk.Label(sp_frame, text="Epsilon").pack()
        self.epsilon_entry = ttk.Entry(sp_frame)
        self.epsilon_entry.pack()

        # Cadre pour le bouton d'ajout des pas d'épaisseur des lentilles
        lens_thickness_steps_frame = ttk.Frame(sp_frame)
        lens_thickness_steps_frame.pack()

        # Bouton pour ajouter un pas d'épaisseur des lentilles
        ttk.Button(lens_thickness_steps_frame, text="+ Add Lens Thickness Step", command=self.add_lens_thickness_step_entry).pack()

        # Cadre pour les entrées des pas d'épaisseur des lentilles
        self.lens_thickness_steps_container = ttk.Frame(sp_frame)
        self.lens_thickness_steps_container.pack()

        # Entrée pour les pas de distance d'air
        ttk.Label(sp_frame, text="Air Distance Steps").pack()
        self.air_distance_steps_entry = ttk.Entry(sp_frame)
        self.air_distance_steps_entry.pack()

        # Entrée pour l'épaisseur des lentilles
        ttk.Label(sp_frame, text="Lens Thickness").pack()
        self.lens_thickness_entry = ttk.Entry(sp_frame)
        self.lens_thickness_entry.pack()

        # Entrée pour le matériel de base
        ttk.Label(sp_frame, text="Base Material").pack()
        self.base_material_entry = ttk.Entry(sp_frame)
        self.base_material_entry.pack()

    

    def setup_tree_tab(self):
        tree_frame = ttk.LabelFrame(self.tab_tree, text="Tree")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Starting Depth Entry
        ttk.Label(tree_frame, text="Starting Depth:").pack()
        self.starting_depth_entry = ttk.Entry(tree_frame)
        self.starting_depth_entry.pack()

        # Target Depth Entry
        ttk.Label(tree_frame, text="Target Depth:").pack()
        self.target_depth_entry = ttk.Entry(tree_frame)
        self.target_depth_entry.pack()

        # Base File Path Entry
        ttk.Label(tree_frame, text="Base File Path:").pack()
        self.base_file_path_entry = ttk.Entry(tree_frame)
        self.base_file_path_entry.pack()

    def setup_starting_system_tab(self):
        starting_system_frame = ttk.LabelFrame(self.tab_starting_system, text="Starting System Parameters")
        starting_system_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Surface 1 Parameters
        surface1_frame = ttk.Frame(starting_system_frame)
        surface1_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(surface1_frame, text="Surface 1 Radius:").pack(side=tk.LEFT)
        self.surface1_radius_entry = ttk.Entry(surface1_frame, width=10)
        self.surface1_radius_entry.pack(side=tk.LEFT)

        ttk.Label(surface1_frame, text="Lens Thickness:").pack(side=tk.LEFT)
        self.surface1_thickness_entry = ttk.Entry(surface1_frame, width=10)
        self.surface1_thickness_entry.pack(side=tk.LEFT)

        ttk.Label(surface1_frame, text="Base Material:").pack(side=tk.LEFT)
        self.surface1_material_entry = ttk.Entry(surface1_frame, width=15)
        self.surface1_material_entry.pack(side=tk.LEFT)

        # Surface 2 Parameters
        surface2_frame = ttk.Frame(starting_system_frame)
        surface2_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(surface2_frame, text="Surface 2 Radius:").pack(side=tk.LEFT)
        self.surface2_radius_entry = ttk.Entry(surface2_frame, width=10)
        self.surface2_radius_entry.pack(side=tk.LEFT)

        ttk.Label(surface2_frame, text="Lens Thickness:").pack(side=tk.LEFT)
        self.surface2_thickness_entry = ttk.Entry(surface2_frame, width=10)
        self.surface2_thickness_entry.pack(side=tk.LEFT)


        # This setup assumes that the material for the second surface does not need to be specified,
        # or it's specified elsewhere. If needed, add a similar section for Surface 2 Material.

    
    def setup_console_output_tab(self):
        console_output_frame = ttk.LabelFrame(self.tab_console_output, text="Console Output")
        console_output_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.console_text = scrolledtext.ScrolledText(console_output_frame, wrap=tk.WORD, width=40, height=10)
        self.console_text.pack(fill="both", expand=True)
        self.console_text.configure(state="disabled")

    def setup_output_tab(self):
        output_frame = ttk.LabelFrame(self.tab_output, text="Optimization Results")
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # TreeView for displaying the optimization results
        self.tree = ttk.Treeview(output_frame)
        self.tree["columns"] = ("Node ID", "Parent ID", "Merit Function", "EFL", "SEQ File Path")
        self.tree.configure(show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(expand=True, fill="both")

        # Frame for the ComboBox and action buttons
        seq_combobox_frame = ttk.Frame(output_frame)
        seq_combobox_frame.pack(fill='x', expand=False, padx=10, pady=5)

        # ComboBox for selecting .seq files
        self.seq_combobox = ttk.Combobox(seq_combobox_frame, state="readonly", width=50)
        self.seq_combobox.pack(side="left", padx=5, pady=5)

        # Button to open the selected .seq file
        open_seq_file_button = ttk.Button(seq_combobox_frame, text="Open", command=self.open_selected_seq_file)
        open_seq_file_button.pack(side="left", padx=5)

        # Button to display the actions window
        actions_button = ttk.Button(seq_combobox_frame, text="Actions", command=self.show_actions_window)
        actions_button.pack(side="left", padx=5)

        # Initially populate the ComboBox with available .seq files
        self.update_seq_files_combobox()



    def add_wavelength_entry(self):
        frame = ttk.Frame(self.wavelengths_container)
        frame.pack(padx=5, pady=5)
        entry = ttk.Entry(frame, width=20)
        entry.pack(side=tk.LEFT)
        remove_button = ttk.Button(frame, text="-", command=lambda fr=frame: fr.destroy())
        remove_button.pack(side=tk.LEFT)
        self.wavelength_entries.append((frame,entry))

    def add_field_entry(self):
        frame = ttk.Frame(self.fields_container)
        frame.pack(padx=5, pady=5)
        entry1 = ttk.Entry(frame, width=10)
        entry1.pack(side=tk.LEFT)
        ttk.Label(frame, text=",").pack(side=tk.LEFT)
        entry2 = ttk.Entry(frame, width=10)
        entry2.pack(side=tk.LEFT)
        remove_button = ttk.Button(frame, text="-", command=lambda fr=frame: fr.destroy())
        remove_button.pack(side=tk.LEFT)
        self.field_entries.append((entry1, entry2))

    def add_lens_thickness_step_entry(self):
        frame = ttk.Frame(self.lens_thickness_steps_container)
        frame.pack(padx=5, pady=5)
        entry = ttk.Entry(frame, width=20)
        entry.pack(side=tk.LEFT)
        remove_button = ttk.Button(frame, text="-", command=lambda fr=frame: fr.destroy())
        remove_button.pack(side=tk.LEFT)
        self.lens_thickness_steps_entries.append((frame, entry))

    def submit(self):
        try:
            # Collect data from UI
            data = {
                "wavelengths": [float(entry[1].get()) for entry in self.wavelength_entries],
                "fields": [(float(entry1.get()), float(entry2.get())) for entry1, entry2 in self.field_entries],
                "efl": float(self.efl_entry.get()),
                "fd": float(self.fd_entry.get()),
                "epsilon": float(self.epsilon_entry.get()),
                "lens_thickness_steps": [float(entry.get()) for _, entry in self.lens_thickness_steps_entries],
                "air_distance_steps": list(map(int, self.air_distance_steps_entry.get().split(','))),
                "lens_thickness": float(self.lens_thickness_entry.get()),
                "base_material": self.base_material_entry.get(),
                "target_depth": int(self.target_depth_entry.get()),
                "starting_depth": int(self.starting_depth_entry.get()),
                "base_file_path": self.base_file_path_entry.get(),
                "starting_system": {
                    "surface1": {
                        "radius": float(self.surface1_radius_entry.get()),
                        "lens_thickness": float(self.surface1_thickness_entry.get()),
                        "material": self.surface1_material_entry.get(),
                    },
                    "surface2": {
                        "radius": float(self.surface2_radius_entry.get()),
                        "lens_thickness": float(self.surface2_thickness_entry.get()),
                    }
                }
            }
            self.start_optimization_thread(data)
        except ValueError as e:
            print(f"Error in input data: {e}")
    
    def start_optimization_thread(self, data):
        def manage_optical_system():
            global final_data
            pythoncom.CoInitialize()  # Initialize COM for this thread
            try:
                optical_system_manager = OpticalSystemManager_eyepieces()
                optical_system_manager.update_parameters_from_ui(data)
                optical_system_manager.start_system()
                final_data = optical_system_manager.evolve_and_optimize()
                optical_system_manager.end_system()
                print("Session CodeV finished")
                self.root.after(0, lambda: self.display_final_data_in_ui(final_data))
            except Exception as e:
                print(f"An error has occurred: {e}")
            finally:
                pythoncom.CoUninitialize()
            # Création et démarrage du thread pour exécuter manage_optical_system
        thread = threading.Thread(target=manage_optical_system)
        thread.start()

    def display_final_data_in_ui(self, final_data):
        # Efface les données existantes
        for i in self.tree.get_children():
            self.tree.delete(i)
        # Affiche les nouvelles données
        for item in final_data:
            self.tree.insert("", "end", values=(
                item['Node ID'], item['Parent ID'], item['Merit Function'],
                item['EFL'], item['SEQ File Path']
            ))
        self.update_seq_files_combobox()


    def update_seq_files_combobox(self):
        seq_files = [self.tree.item(row)['values'][-1] for row in self.tree.get_children()]
        self.seq_combobox['values'] = seq_files
        if seq_files:
            self.seq_combobox.current(0)


    def open_selected_seq_file(self):
        selected_file_path = self.seq_combobox.get()  # Assume self.seq_combobox is your ttk.Combobox widget
        if selected_file_path:
            try:
                os.startfile(selected_file_path)  # Fonctionne sur Windows
            except Exception as e:
                print(f"Error opening file: {e}")
        else:
            print("No file selected")


    def show_actions_window(self):
        actions_window = tk.Toplevel(self.root)
        actions_window.title("Select Actions")

        # Configurez vos variables et widgets ici
        tk.Checkbutton(actions_window, text="Spot Diagram", variable=self.spot_diagram_var).pack(anchor='w')
        tk.Checkbutton(actions_window, text="MTF", variable=self.mtf_var).pack(anchor='w')
        tk.Checkbutton(actions_window, text="Spot Diameter", variable=self.spot_diameter_var).pack(anchor='w')

        apply_button = tk.Button(actions_window, text="Apply", command=self.apply_actions)
        apply_button.pack()


    def apply_actions(self):
        selected_file = self.seq_combobox.get()  # Assume self.seq_combobox is your ttk.Combobox widget
        if not selected_file:
            print("No file selected")
            return
        
        absolute_path = os.path.abspath(selected_file)
        optical_system = SystemSetup()

        # Ici, vous appliquez les actions en fonction des variables de contrôle
        if self.spot_diagram_var.get():
            print(f"Applying Spot Diagram action on {selected_file}")
            # Implémentez l'action Spot Diagram ici

        if self.mtf_var.get() and final_data:
            print(f"Applying MTF action on {selected_file}")
        
            # Chargez le fichier .seq dans le système
            optical_system.load_seq_file(absolute_path)

            # Générez la MTF
            mtf_results = optical_system.get_mtf()
                    
        if self.spot_diameter_var.get():
            print(f"Applying Spot Diameter action on {selected_file}")
            # Implémentez l'action Spot Diameter ici


    def redirect_logging(self):
        logger = PrintLogger(self.console_text)
        sys.stdout = logger
        sys.stderr = logger
        
    # Reset logging to default
    def reset_logging():
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def initialize_default_values(self):
            # Default Wavelengths
        default_wavelengths = [486.1327, 546.074, 587.5618, 632.2, 657.2722]
        for wavelength in default_wavelengths:
            self.add_wavelength_entry()
            self.wavelength_entries[-1][1].insert(0, str(wavelength))


        # Default Fields
        default_fields = [(0, 3), (0, 6), (0, 35)]
        for field in default_fields:
            self.add_field_entry()
            last_field_entry = self.field_entries[-1]  # Correctement récupéré
            last_field_entry[0].insert(0, str(field[0]))
            last_field_entry[1].insert(0, str(field[1]))


        # EFL, fd, and other singular entries
        self.efl_entry.insert(0, "1")
        self.fd_entry.insert(0, "5")

        # SP Parameters
        self.epsilon_entry.insert(0, "0.5")
        self.lens_thickness_entry.insert(0, "0.2")
        self.air_distance_steps_entry.insert(0, "0")
        self.base_material_entry.insert(0, "NBK7_SCHOTT")
        
        # Default Lens Thickness Steps
        default_lens_thickness_steps = [0.05, 0.1, 0.15, 0.4]
        for step in default_lens_thickness_steps:
            self.add_lens_thickness_step_entry()
            self.lens_thickness_steps_entries[-1][1].insert(0, str(step))


        # Other defaults
        self.starting_depth_entry.insert(0, "0")
        self.target_depth_entry.insert(0, "1")
        self.base_file_path_entry.insert(0, "C:/CVUSER")
        
        # Starting System Parameters
        self.surface1_radius_entry.insert(0, "59.33336")
        self.surface1_thickness_entry.insert(0, "0.2")
        self.surface1_material_entry.insert(0, "NBK7_SCHOTT")
        self.surface2_radius_entry.insert(0, "-391.44174")
        self.surface2_thickness_entry.insert(0, "97.703035")

# Main application setup and execution
if __name__ == "__main__":
    root = tk.Tk()
    app = OpticalSystemConfigInterface(root)
    root.mainloop()