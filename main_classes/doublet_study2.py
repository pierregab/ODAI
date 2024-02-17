from SystemSetup_module import SystemSetup
import csv

# Initialize SystemSetup and start a session
optical_system = SystemSetup()
optical_system.start_session()

# Set global parameters
optical_system.set_wavelengths([486, 587, 656])
optical_system.set_fd(4)
optical_system.set_dimensions('m')
optical_system.set_fields([(0, 0.7)])


# Store tabulated merit function values
tabulated_merit_functions = []

################################# PAPER STARTING POINTS #################################


doublets_data = [
    ("PK1","SF2", 60.93, -42.25, -42.25,-123.23),
    ("BK7","SF12", 61.79, -42.51, -42.51,-134.11),
    ("BK8","SF5", 61.93, -44.22, -44.22, -130.40),
    ("SSK50","SF5", 66.57, -38.20, -38.20, -304.62),
    ("BK7","SF5", 61.78, -44.18, -44.18, -127.70),
    ("BaBK5","SF8", 63.86, -45.30, -45.30, -160.51),
    ("K50","SF15", 62.07, -45.80, -45.80, -126.32),
    ("BaBK4","SF15", 64.46, -45.93, -45.93, -170.71),
    ("K3","SF15", 61.79, -47.06, -47.06, -117.89),
    ("K10","SF14", 60.79, -47.32, -47.32, -103.59),
    ("KF3","SF11", 61.48, -48.81, -48.81, -108.08),
    ("BaF5","SF11", 66.24, -52.49, -52.49, -183.12),
    ("SF5","BaK50", 46.03, 24.39, 24.39, 1254.1),
    ("SF15","ZK1", 42.12, 24.97, 24.97, 3274.2),
    ("SF10","SSKN8", 48.33, 25.40, 25.40, 693.8),
    ("SF10","BaF9", 50.69, 24.87, 24.87, 580.9),
    ("SF5","BaK5", 45.01, 24.50, 24.50, 1545.0),
    ("SF2","BK7", 42.01, 23.93, 23.93, 4752.8)
]

num_surfaces = 4 # Total number of surfaces for a doublet system
for num in range(1, num_surfaces + 1):
    thickness = 0.1 if num % 2 != 0 else 0  # Assign thickness 0.1 to glass surfaces, 0 to air gaps
    optical_system.Surface(optical_system, number=num, radius=1, thickness=thickness, material=None)

for index,doublet in enumerate(doublets_data):
    glass1, glass2, r1, r2, r3, r4 = doublet
    
    # Update the surfaces with the actual triplet data
    optical_system.surfaces[1].set_parameters(radius=r1, thickness=0.1, material=glass1)
    optical_system.surfaces[2].set_parameters(radius=r2, thickness=0)
    optical_system.surfaces[3].set_parameters(radius=r3, thickness=0.1, material=glass2)
    optical_system.surfaces[4].set_parameters(radius=r4, thickness=0)
    
    optical_system.set_paraxial_image_distance()
    optical_system.make_all_thicknesses_variable(last_one = False)
    optical_system.make_all_radii_variable()
    optical_system.optimize_system(efl=1, mxt=0.1) 

    # Save the system with a unique file path for each triplet
    file_path = f"C:/CVUSER/doublet_system_{index+1}"  # Unique file path for each system
    optical_system.save_system(file_path, seq=True)

    # Calculate the merit function
    tabulated_merit = optical_system.error_fct(efl=1)
    tabulated_merit_functions.append((glass1, glass2,tabulated_merit))

print(tabulated_merit_functions)

comparison_results = []
seq_file_paths = ["C:/CVUSER/FinalOptimized_Node4.seq"] 
# Loop over each triplet material combination
for doublet in doublets_data:
    glass1, glass2, r1, r2, r3, r4 = doublet

    # Loop over each seq file path
    for seq_file_path in seq_file_paths:
        # Load the .seq file into the system
        load_command = f'run "{seq_file_path}"; GO'
        optical_system.cv.Command(load_command)
        
        # Change the material of the three lenses using the current triplet combination
        optical_system.cv.Command(f"GL1 S1 {glass1}")
        optical_system.cv.Command(f"GL1 S3 {glass2}")
        
        # Make all thicknesses and radii variable
        for i in range(1, 4):
            optical_system.cv.Command(f"CCY S{i} 0")    
            i+=1

        for i in range(1, 4):
            optical_system.cv.Command(f"THC S{i} 0")

        # Fix all materials
        for i in range(1, 4):
            optical_system.cv.Command(f"GC1 S{i} 100")

        # Perform optimization
        optical_system.optimize_system(efl=1, mnt=0.02)  # Replace 'efl=1' with the desired effective focal length
        
        # Calculate the optimized merit function
        optimized_merit = optical_system.error_fct(efl=1)
        
        # Record the comparison
        comparison_results.append({
            'Seq_File_Path': seq_file_path,
            'Doublet': f"{glass1}_{glass2}",
            'Optimized_Merit': optimized_merit,
        })

         # Save the system with a new file name indicating the materials used
        base_name = seq_file_path.split('/')[-1].split('.')[0]  # Extract base name of the file without extension
        optimized_file_path = f"C:/CVUSER/{base_name}_optimized_{glass1}_{glass2}_.seq"
        optical_system.save_system(optimized_file_path, seq=True)

# Save the comparison results to a CSV
csv_file_path = "comparison_results.csv"
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=comparison_results[0].keys())
    writer.writeheader()
    writer.writerows(comparison_results)

# Stop session after all files have been processed
optical_system.stop_session()



# Prepare the final structure for the CSV export
final_comparison_results = []

# Iterate over each unique triplet to gather its comparison results
for glass_combination in tabulated_merit_functions:
    glass1, glass2,tabulated_merit = glass_combination
    doublet_identifier = f"{glass1}_{glass2}"

    # Find all optimized merits for this triplet from different starting points
    optimized_merits = [comp for comp in comparison_results if comp['Doublet'] == doublet_identifier]

    # For each starting point's optimized merit, prepare a row in the final comparison results
    for optimized_merit in optimized_merits:
        final_comparison_results.append({
            'Glass Combination': f"{glass1}, {glass2}",
            'Tabulated Merit Function': tabulated_merit,
            'Seq File Path': optimized_merit['Seq_File_Path'],
            'Optimized Merit Function': optimized_merit['Optimized_Merit']
        })

# CSV headers
csv_headers = ['Glass Combination', 'Tabulated Merit Function', 'Seq File Path', 'Optimized Merit Function']

# Export to CSV
csv_file_path = "final_comparison_results.csv"
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()
    writer.writerows(final_comparison_results)