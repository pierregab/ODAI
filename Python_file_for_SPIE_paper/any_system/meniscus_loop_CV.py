import pygmo as pg
import win32com.client
import time
import re
import os

def add_meniscus(system_setup):
  # Get the last surface number and its radius
  last_surface_number = system_setup.get_last_surface_number()
  last_surface = system_setup.get_surface(last_surface_number)
  last_surface_radius = last_surface.radius if last_surface else 0  # Default to 0 if no last surface

  # Calculate the weaker curvature for the new meniscus
  weakening_factor = 1.25 if last_surface_radius > 0 else 0.75
  weaker_curvature = last_surface_radius * weakening_factor

  # Set the thickness to zero initially
  meniscus_thickness = 0

  # Create the first surface of the meniscus
  surface1 = system_setup.Surface(system_setup, last_surface_number + 1, 
                                  -weaker_curvature, meniscus_thickness, 
                                 "SF2_SCHOTT")  # Example material, adjust as needed
  surface1.make_radius_variable()
  surface1.make_thickness_fixed()

  # Create the second surface of the meniscus
  # Assuming the second surface has the same curvature but in the opposite direction
  surface2 = system_setup.Surface(system_setup, last_surface_number + 2, 
                                  -weaker_curvature, meniscus_thickness)
  surface2.make_radius_variable()
  surface2.make_thickness_fixed()

def main():
  system_setup = SystemSetup()  # Assuming SystemSetup is already defined
  system_setup.start_session()
  system_setup.create_new_system()
  # On utilise les 5 longueurs d'onde du cahier des charges
  system_setup.set_wavelengths([486.1327, 546.074, 587.5618, 632.2, 657.2722])
  system_setup.set_entrance_pupil_diameter(15)
  system_setup.set_dimensions('m')
  # On utilise les champs du cachier des charges
  system_setup.set_fields([(0, 3),(0, 6)])

  # Adding First Surfaces
  surface1 = system_setup.Surface(system_setup, 1, 1e18, 0)  # First surface
  surface2 = system_setup.Surface(system_setup, 2, 23.8, 0.6, "NBK7_SCHOTT")  # Second surface
  surface2.make_radius_variable()
  surface2.make_thickness_variable()


  surface3 = system_setup.Surface(system_setup, 3, -17, 0.05)  # Third surface
  surface3.make_radius_variable()
  surface3.make_thickness_variable()
  system_setup.optimize_system()
  print("Error function value:", system_setup.error_fct())

  surface2.make_thickness_fixed()
  surface3.make_thickness_fixed()

  # Adding Meniscus

  last_error = float('inf')  # Initialize last_error to a very high value
  improvement = True
  temp_file_path = "C:/CVUSER/temp_best_lens"  # Temporary file path for saving the best configuration

  while improvement:
      # Add a new meniscus
      add_meniscus(system_setup)

      # Optimize only with variable radius
      system_setup.make_all_thicknesses_fixed()
      system_setup.optimize_system()
      current_error = system_setup.error_fct()
      print("Error function value after radius optimization:", current_error)

      # Unlock all widths (thicknesses)
      system_setup.make_all_thicknesses_variable()

      # Optimize with radius and width
      system_setup.optimize_system()
      new_error = system_setup.error_fct()
      print("Error function value after full optimization:", new_error)

      # Check if there is an improvement or if too mny iterations have been done
      if new_error < last_error:
          last_error = new_error  # Update the last error
          # Save the current (best) system configuration
          system_setup.save_system(temp_file_path)
      else:
          improvement = False  # No improvement, break the loop
  
  # If the loop exits without improvement, revert to the best configuration
  if os.path.exists(temp_file_path):
      # Load the best configuration
      system_setup.cv.Command(f"RES {temp_file_path}")
      # Remove the temporary file
      os.remove(temp_file_path)
      print("Reverted to the best configuration.")

  # Save the final lens system
  system_setup.save_system("C:/CVUSER/my_final_lens")
  system_setup.stop_session()

if __name__ == '__main__':
  main()
