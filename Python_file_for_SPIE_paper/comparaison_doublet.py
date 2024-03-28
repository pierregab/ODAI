
optical_system = SystemSetup()  # Assuming SystemSetup is already defined
optical_system.start_session()
optical_system.create_new_system()
# On utilise les 5 longueurs d'onde du cahier des charges
optical_system.set_wavelengths([486.1327, 546.074, 587.5618, 632.2, 657.2722])
optical_system.set_entrance_pupil_diameter(20)
optical_system.set_dimensions('m')
# On utilise les champs du cachier des charges
optical_system.set_fields([(0, 3),(0, 6)])

# Definition de la fonction de mérite
optical_system.cv.Command("REF   2")
optical_system.cv.Command("WTW   1 1 1")
optical_system.cv.Command("INI   'ORA'")
optical_system.cv.Command("XAN   0.0 0.0 0.0")
optical_system.cv.Command("YAN   0.0 3.0 5.0")
optical_system.cv.Command("WTF   1.0 1.0 1.0")
optical_system.cv.Command("VUY   0.0 0.0 0.0")
optical_system.cv.Command("VLY   0.0 0.0 0.0")

# Define parameters
reference_surface_number = 2  # Adjust based on your singlet design
epsilon = 0.5  # Small radius change
efl = 100  # Effective focal length, adjust as needed

# Adding Surfaces
#surface1 = optical_system.Surface(optical_system, 1, 1e18, 0)  # First surface

surface1 = optical_system.Surface(optical_system, 1, 59.33336, 4.000000, "NBK7_SCHOTT")  # Second surface
surface1.make_radius_variable()

surface2 = optical_system.Surface(optical_system, 2, -391.44174, 97.703035)  # Third surface
surface2.make_radius_variable()

optical_system.cv.Command("PIM Yes")

optical_system.save_system("C:/CVUSER/Singlet_test")

# Step 1: Reoptimize the Singlet (if necessary)
optical_system.optimize_system(efl, constrained=False)
optical_system.save_system("C:/CVUSER/systemInter")
optical_system.update_all_surfaces_from_codev(output=True)


# Step 2: Insert a null element next to the reference surface of the singlet
optical_system.add_null_surfaces(reference_surface_number)

#surface3.make_radius_fixed()
#surface4.make_radius_fixed()

# Step 3: Modify curvatures to create two systems on either side of the saddle point
surface_numbers = [3, 4]  # Surface numbers of the new null element
system1_params, system2_params = optical_system.modify_curvatures_for_saddle_point(surface_numbers, epsilon, efl, output=True)


optical_system.load_system_parameters(system1_params)
optical_system.save_system("C:/CVUSER/system1_final")

optical_system.load_system_parameters(system2_params)
optical_system.save_system("C:/CVUSER/system2_final")

# Step 4: Optimize the two systems (this is done within the modify_curvatures_for_saddle_point method)

# Step 5: Gradually increase thickness and optimize
lens_thickness_steps = [1, 2, 3, 4]  # Example thickness steps in mm
air_distance_steps = [1, 2]  # Example air distance steps in mm
lens_surface_number = 3  # Surface number of the lens (new null element)
air_surface_number = 2  # Surface number of the air gap


optical_system.load_system_parameters(system2_params)
optical_system.cv.Command("THI S3 1")
optical_system.optimize_system(efl, constrained=False)
optical_system.cv.Command("THI S3 2")
optical_system.optimize_system(efl, constrained=False)
optical_system.cv.Command("THI S3 3")
optical_system.optimize_system(efl, constrained=False)
optical_system.cv.Command("THI S3 4")
optical_system.optimize_system(efl, constrained=False)
optical_system.cv.Command("THI S2 1")
optical_system.optimize_system(efl, constrained=False)
optical_system.cv.Command("THI S2 2")
optical_system.optimize_system(efl, constrained=False)
optical_system.save_system("C:/CVUSER/system2_final")

optical_system.load_system_parameters(system1_params)
optical_system.cv.Command("THI S3 1")
optical_system.optimize_system(efl, constrained=False)
optical_system.cv.Command("THI S3 2")
optical_system.optimize_system(efl, constrained=False)
optical_system.cv.Command("THI S3 3")
optical_system.optimize_system(efl, constrained=False)
optical_system.cv.Command("THI S3 4")
optical_system.optimize_system(efl, constrained=False)
optical_system.cv.Command("THI S2 1")
optical_system.optimize_system(efl, constrained=False)
optical_system.cv.Command("THI S2 2")
optical_system.optimize_system(efl, constrained=False)
optical_system.save_system("C:/CVUSER/system1_final")

"""
# Optimize system 1 with gradual thickness increase
optical_system.load_system_parameters(system1_params)
optical_system.increase_thickness_and_optimize(lens_thickness_steps, air_distance_steps, lens_surface_number, air_surface_number, efl)

# Save system 1 as a CODE V file
system1_final_params = optical_system.save_system_parameters()
optical_system.load_system_parameters(system1_final_params)
optical_system.save_system("C:/CVUSER/system1_final")

# Optimize system 2 with gradual thickness increase
optical_system.load_system_parameters(system2_params)
optical_system.increase_thickness_and_optimize(lens_thickness_steps, air_distance_steps, lens_surface_number, air_surface_number, efl)

# Save system 2 as a CODE V file
system2_final_params = optical_system.save_system_parameters()
optical_system.load_system_parameters(system2_final_params)
optical_system.save_system("C:/CVUSER/system2_final")
"""

# End the CODE V session
optical_system.stop_session()

# The files "system1_final.cv" and "system2_final.cv" are now saved with the final doublet systems
