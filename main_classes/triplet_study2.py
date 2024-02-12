from SystemSetup_module import SystemSetup

# Initialize SystemSetup and start a session
optical_system = SystemSetup()
optical_system.start_session()

# Set global parameters
optical_system.set_wavelengths([486, 587, 656])
optical_system.set_fd(5)
optical_system.set_dimensions('m')
optical_system.set_fields([(0, 0.7)])

# Assuming we have a list of .seq file paths and a dictionary mapping lens numbers to materials
seq_file_paths = ["path/to/first_file.seq", "path/to/second_file.seq", ...]  # Replace with actual paths
material_dict = {1: "FK51", 2: "638424.320", 3: "SF1"}  # Replace with actual materials

# Loop over each seq file path
for seq_file_path in seq_file_paths:
    # Load the .seq file into the system
    load_command = f'run "{seq_file_path}"; GO'
    optical_system.cv.Command(load_command)
    
    # Change the material of the three lenses
    for lens_number, material in material_dict.items():
        surface_number = 2 * lens_number  # Assuming lenses are at even-numbered surfaces
        optical_system.get_surface(surface_number).set_material(material)
    
    # Make all thicknesses and radii variable
    optical_system.make_all_thicknesses_variable()
    optical_system.make_all_radii_variable()

    # Perform optimization
    optical_system.optimize_system(efl=1)  # Replace 'efl=1' with the desired effective focal length

    # Optionally, you can save the optimized system with a new file name
    optimized_file_path = seq_file_path.replace(".seq", "_optimized.seq")
    optical_system.save_system(optimized_file_path, seq=True)

# Stop session after all files have been processed
optical_system.stop_session()
