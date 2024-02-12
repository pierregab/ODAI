from SystemSetup_module import SystemSetup

# Initialize SystemSetup and start a session
optical_system = SystemSetup()
optical_system.start_session()

# Set global parameters
optical_system.set_wavelengths([486, 587, 656])
optical_system.set_fd(5)
optical_system.set_dimensions('m')
optical_system.set_fields([(0, 0.7)])

triplets_data = [
    ("FK51", "638424.320", "SF1", 0.78040, -0.26833, -0.28528, -2.09468, 1.4514),
    ("FK51", "638424.320", "SF10", 0.74376, -0.27169, -0.28857, -2.00724, 1.6283),
    ("FK51", "638424.320", "SF4", 0.71635, -0.27411, -0.29081, -1.90816, 1.8667),
    ("FK51", "638424.320", "SF8", 0.88060, -0.26021, -0.27696, -2.10795, 1.1926),
    ("FK51", "KZFS4", "SF2", 1.11226, -0.22997, -0.24275, -1.9530, 0.98067),
    ("FK51", "KZFS4", "SF57", 0.66332, -0.25813, -0.27093, -1.65476, 3.0816),
    ("FK51", "KZFS5", "SF10", -1.34126, -0.16583, -0.17521, -0.52381, 0.79746),
    ("FK51", "KZFS5", "SF57", 0.91218, -0.23371, -0.25026, -1.56151, 1.4607),
    ("FK51", "LAK10", "SF66", 0.64693, -0.22008, -0.23801, -0.77359, 7.0171),
    ("FK51", "LAK10", "SF67", 0.65421, -0.21678, -0.23460, -0.76903, 6.2693)
]

# Assuming we have a list of .seq file paths and a dictionary mapping lens numbers to materials
seq_file_paths = ["C:/CVUSER/FinalOptimized_Node15.seq", "C:/CVUSER/FinalOptimized_Node16.seq", "C:/CVUSER/FinalOptimized_Node12.seq", "C:/CVUSER/FinalOptimized_Node10.seq", "C:/CVUSER/FinalOptimized_Node9.seq"]  # Replace with actual paths
material_dict = {1: "FK51", 2: "638424.320", 3: "SF1"}  # Replace with actual materials


# Loop over each triplet material combination
for triplet in triplets_data:
    glass1, glass2, glass3, r1, r1_prime, r2, r2_prime, r3 = triplet

    # Loop over each seq file path
    for seq_file_path in seq_file_paths:
        # Load the .seq file into the system
        load_command = f'run "{seq_file_path}"; GO'
        optical_system.cv.Command(load_command)
        
        # Change the material of the three lenses
        for lens_number, material in material_dict.items():
            surface_number = 2 * lens_number - 1 # Assuming lenses are at even-numbered surfaces
            optical_system.cv.Command(f"GL1 S{surface_number} {material}")
        
        # Make all thicknesses and radii variable
        for i in range(1, len(material_dict)):
            optical_system.cv.Command(f"CCY S{i} 0")    
            i+=1

        for i in range(1, len(material_dict)):
            optical_system.cv.Command(f"THC S{i} 0")

        # Fix all materials
        for i in range(1, len(material_dict)):
            optical_system.cv.Command(f"GC1 S{i} 100")

        # Perform optimization
        optical_system.optimize_system(efl=1, mnt=0.02)  # Replace 'efl=1' with the desired effective focal length
        
        error_fct = optical_system.error_fct(efl=1)
        print(f"Error function value for {seq_file_path} with materials {glass1}, {glass2}, {glass3}: {error_fct}")

         # Save the system with a new file name indicating the materials used
        base_name = seq_file_path.split('/')[-1].split('.')[0]  # Extract base name of the file without extension
        optimized_file_path = f"C:/CVUSER/{base_name}_optimized_{glass1}_{glass2}_{glass3}.seq"
        optical_system.save_system(optimized_file_path, seq=True)

# Stop session after all files have been processed
optical_system.stop_session()
