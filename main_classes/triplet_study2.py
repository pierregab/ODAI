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
seq_file_paths = ["C:/CVUSER/FinalOptimized_Node15.seq", "C:/CVUSER/FinalOptimized_Node16.seq", "C:/CVUSER/FinalOptimized_Node12.seq", "C:/CVUSER/FinalOptimized_Node10.seq", "C:/CVUSER/FinalOptimized_Node9.seq"]  # Replace with actual paths
material_dict = {1: "FK51", 2: "638424.320", 3: "SF1"}  # Replace with actual materials

# Loop over each seq file path
for seq_file_path in seq_file_paths:
    # Load the .seq file into the system
    load_command = f'run "{seq_file_path}"; GO'
    optical_system.cv.Command(load_command)
    
    # Change the material of the three lenses
    for lens_number, material in material_dict.items():
        surface_number = 2 * lens_number  # Assuming lenses are at even-numbered surfaces
        optical_system.cv.Command(f"GL1 S{surface_number} {material}")
    
    # Make all thicknesses and radii variable
    for i in range(1, len(material_dict)):
        optical_system.cv.Command(f"CCY S{i} 0")    
        i+=1

    for i in range(1, len(material_dict)):
        optical_system.cv.Command(f"THC S{i} 0")
        
    # Perform optimization
    optical_system.optimize_system(efl=1)  # Replace 'efl=1' with the desired effective focal length
    
    error_fct = optical_system.error_fct(efl=1)

    # Optionally, you can save the optimized system with a new file name
    optimized_file_path = seq_file_path.replace(".seq", "_optimized.seq")
    optical_system.save_system(optimized_file_path, seq=True)

# Stop session after all files have been processed
optical_system.stop_session()
