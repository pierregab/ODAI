import pygmo as pg
import win32com.client
import time
import re
from tqdm import tqdm
import datetime

# Global variable to store parameters
global_parameters = None
efl = 15

system_setup = SystemSetup()  # Assuming SystemSetup is already defined
system_setup.start_session()
system_setup.create_new_system()
# On utilise les 5 longueurs d'onde du cahier des charges
system_setup.set_wavelengths([486.1327, 546.074, 587.5618, 632.2, 657.2722])
system_setup.set_entrance_pupil_diameter(15)
system_setup.set_dimensions('m')
# On utilise les champs du cachier des charges
system_setup.set_fields([(0, 3),(0, 6)])

materials_list = [487490.704058, 516800.641673, 589130.612668, 531719.487626, 579569.537082, 608589.464424, 620040.363665, 620410.603236, 647689.338482, 652242.449305, 658440.508829, 672697.322098, 664460.360006, 704000.393844, 716998.479611, 717360.295128, 743972.448504, 749502.349506, 755201.275795, 528554.769755]


# Adding Surfaces
# Note: You may store these surfaces in a list or dictionary for easy access.
system_setup.surfaces = {}
# Diaphragme collé à la première lentille
system_setup.surfaces[1] = system_setup.Surface(system_setup, 1, 1e18, 0) 
system_setup.surfaces[2] = system_setup.Surface(system_setup, 2, 22.63216, 7.0, "NBK7_SCHOTT")
system_setup.surfaces[3] = system_setup.Surface(system_setup, 3, -144.99525, 22.022504)
system_setup.surfaces[4] = system_setup.Surface(system_setup, 4, 4.77927, 6.998062, "SF2_SCHOTT")
system_setup.surfaces[5] = system_setup.Surface(system_setup, 5, 5.73415, 0.212388)
# ... [Add other surfaces]

# Make radius and thickness variable
system_setup.surfaces[2].make_radius_variable()
system_setup.surfaces[2].make_thickness_variable()
system_setup.surfaces[3].make_radius_variable()
system_setup.surfaces[3].make_thickness_variable()
system_setup.surfaces[4].make_radius_variable()
system_setup.surfaces[4].make_thickness_variable()
system_setup.surfaces[5].make_radius_variable()
system_setup.surfaces[5].make_thickness_variable()
# ... [Repeat for other surfaces]
system_setup.surfaces[2].make_material_variable()
system_setup.surfaces[4].make_material_variable()

def apply_parameters_to_com(parameters):
    # Apply parameters to the surfaces
    system_setup.surfaces[2].set_radius(parameters[0])
    system_setup.surfaces[2].set_thickness(parameters[1])
    system_setup.surfaces[3].set_radius(parameters[2])
    system_setup.surfaces[3].set_thickness(parameters[3])
    system_setup.surfaces[4].set_radius(parameters[4])
    system_setup.surfaces[4].set_thickness(parameters[5])
    system_setup.surfaces[5].set_radius(parameters[6])
    system_setup.surfaces[5].set_thickness(parameters[7])

    # Map integer parameters to material names
    material_2_index = int(parameters[8])
    material_4_index = int(parameters[9])
    material_2 = materials_list[material_2_index]
    material_4 = materials_list[material_4_index]

    system_setup.surfaces[2].set_material(material_2)
    system_setup.surfaces[4].set_material(material_4)

    # Calculate and return the error function value
    return system_setup.error_fct(efl)

# Define the PyGMO Optimization Problem
class CodeVOptimization():
    def __init__(self):
        pass

    def fitness(self, x):
        # Map the continuous values of x8 and x9 to the nearest integer values
        x[8] = round(x[8])  # Or use int(x[8]) for flooring
        x[9] = round(x[9])  # Or use int(x[9]) for flooring
        global global_parameters
        global_parameters = x
        error_value = apply_parameters_to_com(x)
        return [error_value]

    def get_nix(self):
      # Number of integer dimensions
      return 2

    def get_bounds(self):
      # Define bounds for radius and thickness
      radius_bounds = (-100, 100)  # Assuming -100 to 100 is the range for radii
      # 7mm maximum pour l'épaisseur des lentilles
      lens_thickness_bounds = (0, 7)  # Maximum thickness for lens surfaces set to 7mm
      air_gap_thickness_bounds = (0, 100)  # Assuming 0 to 100 is the range for air gaps

      # Bounds for material selection (as integer indices)
      material_bounds = (0, len(materials_list) - 1)

      # Combine the bounds for each surface parameter (radius and thickness)
      lower_bounds = []
      upper_bounds = []
      for i in range(4):  # Assuming 4 surfaces with variable radius and thickness
          # Apply different thickness bounds for lens surfaces and air gaps
          if i % 2 == 0:  # Even index: lens surface
              lower_bounds.extend([radius_bounds[0], lens_thickness_bounds[0]])
              upper_bounds.extend([radius_bounds[1], lens_thickness_bounds[1]])
          else:  # Odd index: air gap
              lower_bounds.extend([radius_bounds[0], air_gap_thickness_bounds[0]])
              upper_bounds.extend([radius_bounds[1], air_gap_thickness_bounds[1]])

      # Append material bounds for surfaces 2 and 4
      lower_bounds.extend([material_bounds[0], material_bounds[0]])
      upper_bounds.extend([material_bounds[1], material_bounds[1]])

      return (lower_bounds, upper_bounds)


def main():

    # Create and configure the optimization problem
    prob = CodeVOptimization()

    # Define initial solution
    initial_solution = [22.63216, 7.0, -144.99525, 22.022504, 4.77927, 6.998062, 5.73415, 0.212388, 1, 8]

    # Initialize Population with the initial solution
    pop = pg.population(prob, size=200)
    pop.push_back(initial_solution)  # Add the initial solution to the population

    # Choose an Algorithm for PyGMO
    algo = pg.algorithm(pg.de(gen=1))  # Set generations to 1 for manual iteration
    # à tester : gaco ihs sga nsga2 maco


    total_generations = 100  # Set the total number of generations you want to run
    with tqdm(total=total_generations, desc="Optimizing") as pbar:  # Initialize tqdm progress bar
      for gen in range(total_generations):
          start_time = datetime.datetime.now()  # Record the start time
          pop = algo.evolve(pop)  # Evolve the population for one generation
          end_time = datetime.datetime.now()  # Record the end time

          # Get the current best merit function value from the champion
          current_best_merit = pop.champion_f[0]

          # Calculate the estimated finish time
          elapsed_time = end_time - start_time
          estimated_total = elapsed_time * total_generations
          estimated_finish = start_time + estimated_total
          finish_time_str = estimated_finish.strftime("%Y-%m-%d %H:%M:%S")

          # Update the progress bar with elapsed time, estimated finish, and current merit
          pbar.set_postfix_str(f"Elapsed: {elapsed_time}, ETA: {finish_time_str}, Current Merit: {current_best_merit}")
          pbar.update(1)

    # Extract the best solution
    best_solution = pop.champion_x
    best_merit = pop.champion_f

    print("Best solution:", best_solution)
    print(f"Best merit: {best_merit}")

    # Apply the best solution to your CODE V system
    system_setup.surfaces[2].set_parameters(best_solution[0], best_solution[1])
    system_setup.surfaces[3].set_parameters(best_solution[2], best_solution[3])
    system_setup.surfaces[4].set_parameters(best_solution[4], best_solution[5])
    system_setup.surfaces[5].set_parameters(best_solution[6], best_solution[7])
    system_setup.surfaces[2].set_material(materials_list[int(best_solution[8])])
    system_setup.surfaces[4].set_material(materials_list[int(best_solution[9])])
    # ... [Apply parameters to other surfaces]

    # Apply the best solution to the CODE V system
    system_setup.save_system("C:/CVUSER/my_optimized_lens")
    system_setup.stop_session()

if __name__ == '__main__':
    main()
