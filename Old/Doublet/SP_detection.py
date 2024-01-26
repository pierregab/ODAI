optical_system = SystemSetup()  # Assuming SystemSetup is already defined
optical_system.start_session()
optical_system.create_new_system()
# On utilise les 5 longueurs d'onde du cahier des charges
optical_system.set_wavelengths([486.1327, 546.074, 587.5618, 632.2, 657.2722])
optical_system.set_entrance_pupil_diameter(20)
optical_system.set_dimensions('m')
# On utilise les champs du cachier des charges
optical_system.set_fields([(0, 3),(0, 6)])

# Define parameters
reference_surface_number = 2  # Adjust based on your singlet design
epsilon = 0.5  # Small radius change
surface_numbers = [3, 4]  # Surface numbers of the new null element
lens_thickness_steps = [1, 2, 3, 4]  # Thickness steps in mm
air_distance_steps = [0]  # Air distance steps in mm (0 here)
efl = 100  # Effective focal length
lens_thickness = 4

# Adding Surfaces
surface1 = optical_system.Surface(optical_system, 1, 59.33336, lens_thickness, "NBK7_SCHOTT")  # Second surface
surface1.make_radius_variable()

surface2 = optical_system.Surface(optical_system, 2, -391.44174, 97.703035)  # Third surface
surface2.make_radius_variable()

# Set paraxial image distance for constant efl
optical_system.set_paraxial_image_distance()

# Step 1: Reoptimize the Singlet (if necessary)
optical_system.optimize_system(efl, constrained=False)
optical_system.update_all_surfaces_from_codev(output=False)

# Step 2: Insert a null element next to the reference surface of the singlet
optical_system.add_null_surfaces(reference_surface_number)

# Define parameters for derivative computation using curvature
delta_curvature = 0.00025  # Small change in curvature
num_points = 400  # Number of points for derivative computation
initial_curvature = 1 /(-391.44174)

optical_system.switch_ref_mode('curvature')

sps = optical_system.perform_sp_scan(reference_surface_number, efl, output = False)

for i, sp in enumerate(sps):

    sp_filename=f"C:/CVUSER/sp_{i+1}.seq"
    optical_system.sp_create_and_increase_thickness(sp,reference_surface_number,lens_thickness,sp_filename)

    # Step 3: Modify curvatures to create two systems on either side of the saddle point
    system1_params, system2_params = optical_system.modify_curvatures_for_saddle_point(surface_numbers, epsilon, efl, output=False)

    # Optimize system 1 with gradual thickness increase
    optical_system.load_system_parameters(system1_params)
    system1_filename = f"C:/CVUSER/system1_final_sp_{i+1}.seq"
    optical_system.increase_thickness_and_optimize(lens_thickness_steps, air_distance_steps, 3, 2, efl, system1_filename)
    system1_params = optical_system.save_system_parameters()
    system1_params['seq_file_path'] = system1_filename
    system1_thickness_modified_name = f"system1_thickness_modified_sp_{i+1}"
    optical_system.saved_systems[system1_thickness_modified_name] = system1_params

    # Optimize system 2 with gradual thickness increase
    optical_system.load_system_parameters(system2_params)
    system2_filename = f"C:/CVUSER/system2_final_sp_{i+1}.seq"
    optical_system.increase_thickness_and_optimize(lens_thickness_steps, air_distance_steps, 3, 2, efl, system2_filename)
    system2_params = optical_system.save_system_parameters()
    system2_params['seq_file_path'] = system2_filename
    system2_thickness_modified_name = f"system2_thickness_modified_sp_{i+1}"
    optical_system.saved_systems[system2_thickness_modified_name] = system2_params

# Print all saved systems and their parameters
optical_system.print_saved_systems()

# Iterate over all saved systems and plot them
for system_name, system_params in optical_system.saved_systems.items():
    seq_file_path = system_params.get('seq_file_path')
    if seq_file_path:
        print(f"Plotting system: {system_name}")
        optical_system.plot_optical_system(seq_file_path)

# End the CODE V session
optical_system.stop_session()

