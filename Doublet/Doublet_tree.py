from SystemSetup_module import SystemSetup
from SystemNode_module import SystemNode, SystemTree

optical_system = SystemSetup()   # Initialize SystemSetup
optical_system.start_session()
optical_system.create_new_system()
# On utilise les 5 longueurs d'onde du cahier des charges
optical_system.set_wavelengths([486.1327, 546.074, 587.5618, 632.2, 657.2722])
optical_system.set_entrance_pupil_diameter(20)
optical_system.set_dimensions('m')
# On utilise les champs du cachier des charges
optical_system.set_fields([(0, 3),(0, 6)])

efl = 100

# Root Node Parameters
root_params = {
    'epsilon': 0.5,
    'lens_thickness_steps': [1, 2, 3, 4],
    'air_distance_steps': [0],
    'lens_thickness': 4,
}

reference_surface = 2

# Creating Singlet to start the Tree
surface1 = optical_system.Surface(optical_system, 1, 59.33336, root_params['lens_thickness'], "NBK7_SCHOTT")  # Second surface
surface1.make_radius_variable()

surface2 = optical_system.Surface(optical_system, 2, -391.44174, 97.703035)  # Third surface
surface2.make_radius_variable()

# Set paraxial image distance for constant efl
optical_system.set_paraxial_image_distance()

# Step 1: Reoptimize the Singlet (if necessary)
optical_system.optimize_system(efl, constrained=False)
optical_system.update_all_surfaces_from_codev(output=False)

# Step 2: Insert a null element next to the reference surface of the singlet
optical_system.add_null_surfaces(reference_surface)

root_system = optical_system.save_system_parameters()
root_merit = optical_system.error_fct(efl, constrained=False)
root_efl = optical_system.get_efl_from_codev()

# Create root node and system tree
root_node = SystemNode(system_params=root_params, optical_system_state=root_system, merit_function=root_merit, efl=root_efl, is_optimized=True)
system_tree = SystemTree(root_node)

# Perform saddle point scans and optimizations from root
base_file_path = "C:/CVUSER"

optical_system.find_and_optimize_from_saddle_points(root_node, system_tree, efl, base_file_path, depth=0, reference_surface=2)

system_tree.print_tree()

# Plot the optical system tree
system_tree.plot_optical_system_tree()

# End the CODE V session
optical_system.stop_session()
