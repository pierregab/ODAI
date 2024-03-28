from SystemSetup_module import SystemSetup
import csv

# Initialize SystemSetup and start a session
optical_system = SystemSetup()
optical_system.start_session()

# Set global parameters
optical_system.set_wavelengths([486.1327, 546.074, 587.5618, 632.2, 657.2722])
optical_system.set_fd(5)
optical_system.set_dimensions('m')
optical_system.set_fields([(0, 3, 6, 40)])

# Define paths to the .seq files
seq_file_path_to_optimize = "C:/CVUSER/pantent_eyepiece.seq"
seq_file_path_for_comparison = "C:/CVUSER/best.seq"

# Define the target effective focal length for the optimization
efl_target = 50  # Assuming a target EFL of 50 mm

# Load the system to be optimized
load_command_to_optimize = f'run "{seq_file_path_to_optimize}"; GO'
optical_system.cv.Command(load_command_to_optimize)

# Perform desired optimizations on the first system
optical_system.cv.Command('AUT')
optical_system.cv.Command('IMP 1E-10')
optical_system.cv.Command(f"EFL Z1 = {efl_target}")  # Condition on the EFL
optical_system.cv.Command('MNT 0.2')
optical_system.cv.Command("GLA SO..I  NFK5 NSK16 NLAF2 SF4")
optical_system.cv.Command("GO")

# Calculate the optimized merit function for the first system
optimized_merit = optical_system.error_fct(efl=efl_target)

# Save the optimized system with a new file path
optimized_file_path = "C:/CVUSER/pantent_eyepiece_optimized.seq"
optical_system.save_system(optimized_file_path, seq=True)

# Load the second system for comparison
load_command_for_comparison = f'run "{seq_file_path_for_comparison}"; GO'
optical_system.cv.Command(load_command_for_comparison)

# Calculate the merit function for the comparison system without optimizing it
comparison_merit = optical_system.error_fct(efl=efl_target)

# Record the comparison result
comparison_result = {
    'Optimized_System_File_Path': optimized_file_path,
    'Comparison_System_File_Path': seq_file_path_for_comparison,
    'Optimized_System_Merit': optimized_merit,
    'Comparison_System_Merit': comparison_merit
}

# Save the comparison result to a CSV
csv_file_path = "system_comparison_result.csv"
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=comparison_result.keys())
    writer.writeheader()
    writer.writerow(comparison_result)

# Stop session after processing
optical_system.stop_session()
