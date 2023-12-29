from SystemSetup_module import SystemSetup
from SystemNode_module import SystemNode, SystemTree

optical_system = SystemSetup()  # Initialize SystemSetup
optical_system.start_session()
optical_system.create_new_system()

# Set wavelengths, entrance pupil diameter, and dimensions
optical_system.set_wavelengths([486.1327, 546.074, 587.5618, 632.2, 657.2722])
optical_system.set_entrance_pupil_diameter(20)
optical_system.set_dimensions('m')
optical_system.set_fields([(0, 3), (0, 6)])

efl = 100

# Root Node Parameters
root_params = {
    'epsilon': 0.5,
    'lens_thickness_steps': [1, 2, 3, 4],
    'air_distance_steps': [0],
    'lens_thickness': 4,
}

# Create initial optical system (Singlet)
surface1 = optical_system.Surface(optical_system, 1, 59.33336, root_params['lens_thickness'], "NBK7_SCHOTT")
surface1.make_radius_variable()
surface2 = optical_system.Surface(optical_system, 2, -391.44174, 97.703035)
surface2.make_radius_variable()

optical_system.set_paraxial_image_distance()

# Optimize the initial system
optical_system.optimize_system(efl, constrained=False)
optical_system.update_all_surfaces_from_codev(output=False)


# Save initial system parameters
root_system = optical_system.save_system_parameters()
root_merit = optical_system.error_fct(efl, constrained=False)
root_efl = optical_system.get_efl_from_codev()

# Create root node and system tree
root_node = SystemNode(system_params=root_params, optical_system_state=root_system, merit_function=root_merit, efl=root_efl, is_optimized=True)
system_tree = SystemTree(root_node)

# Define base path for saving files
base_file_path = "C:/CVUSER"

# Evolve the optical systems
starting_depth = 0
target_depth = 0  # Or any other depth you wish to reach
optical_system.evolve_optimized_systems(system_tree, starting_depth, target_depth, base_file_path, efl)

# Print and plot the system tree
system_tree.print_tree()
system_tree.plot_optical_system_tree()

# End the CODE V session
optical_system.stop_session()
