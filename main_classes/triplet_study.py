from SystemSetup_module import SystemSetup
from SystemNode_module import SystemNode, SystemTree

optical_system = SystemSetup()  # Initialize SystemSetup
optical_system.start_session()
optical_system.create_new_system()

# Set wavelengths, entrance pupil diameter, and dimensions
optical_system.set_wavelengths([486, 587, 656])
optical_system.set_fd(5)
optical_system.set_dimensions('m')
optical_system.set_fields([(0, 0.7)])

# (Glass 1, Glass 2, Glass 3, r1, r1', r2, r2', r3)
# Example: [("N-FK51A", "N-KZFS11", "N-SF1", 0.78040, -0.26833, -0.28528, -2.09468, 1.4514), ...]

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


# Create surfaces with placeholder values outside the loop
num_surfaces = 6  # Total number of surfaces for a triplet system
for num in range(1, num_surfaces + 1):
    thickness = 0.1 if num % 2 != 0 else 0  # Assign thickness 0.1 to glass surfaces, 0 to air gaps
    optical_system.Surface(optical_system, number=num, radius=1, thickness=thickness, material=None)

# Loop over each triplet to update the system and test the merit function
for index, triplet in enumerate(triplets_data):
    glass1, glass2, glass3, r1, r1_prime, r2, r2_prime, r3 = triplet
    
    # Update the surfaces with the actual triplet data
    optical_system.surfaces[1].set_parameters(radius=r1, thickness=0.1, material=glass1)
    optical_system.surfaces[2].set_parameters(radius=r1_prime, thickness=0)
    optical_system.surfaces[3].set_parameters(radius=r2, thickness=0.1, material=glass2)
    optical_system.surfaces[4].set_parameters(radius=r2_prime, thickness=0)
    optical_system.surfaces[5].set_parameters(radius=r3, thickness=0.1, material=glass3)
    optical_system.surfaces[6].set_parameters(radius=1e10, thickness=0)  # r3' is infinity

    optical_system.set_paraxial_image_distance()

    # Make all thicknesses variable and optimize the system
    optical_system.make_all_thicknesses_variable(last_one=False)
    optical_system.optimize_system(efl=1, mxt=0.1)  # Use r3 as the effective focal length

    error_fct_value = optical_system.error_fct(efl=1)

    # Save the system with a unique file path for each triplet
    file_path = f"C:/CVUSER/triplet_system_{index+1}"  # Unique file path for each system
    optical_system.save_system(file_path, seq=True)

    # Print the error function value for the triplet
    print(f"Triplet {index+1} Error Function: {error_fct_value}")

# Stop session after all triplets have been processed
optical_system.stop_session()


    
