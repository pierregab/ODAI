import re    
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import win32com.client
from SystemNode_module import SystemNode, SystemTree
from affichage import *

class SystemSetup:
      def __init__(self):
          self.cv = win32com.client.Dispatch("CodeV.Application")
          self.surfaces = {}   # dict to keep track of surfaces
          self.ref_mode = 'radius'  # Default mode is 'radius'
          self.saved_systems = {}  # dict to keep track of saved systems

      class Surface:
          def __init__(self, parent, number, radius, thickness, material=None):
              self.parent = parent
              self.cv = parent.cv
              self.number = number
              self.radius = radius
              self.curvature = 1 / radius if radius != 0 else 0
              self.thickness = thickness
              self.material = material
              self.radius_variable = False
              self.thickness_variable = False
              self.material_variable = False

              self.create_surface()
              self.parent.surfaces[number] = self 

          def create_surface(self):
            # Add a new surface with the initial parameters
            command = f"INS S{self.number} {self.radius} {self.thickness}"
            if self.material:
                command += f" {self.material}"
            self.cv.Command(command)
            #print(f"Created surface {self.number}: {command}")

          def set_radius(self, radius):
            self.radius = radius
            if self.parent.ref_mode == 'radius':
                self.cv.Command(f"RDY S{self.number} {self.radius}")
                if self.radius_variable:
                  self.cv.Command(f"CCY S{self.number} 0")
            else:
                curvature = 1 / radius if radius != 0 else 0
                self.cv.Command(f"CUY S{self.number} {curvature}")
                print(f"Warning: Radius set to {radius}, but system is in curvature mode. Radius converted to curvature: {curvature}.")
                if self.radius_variable:
                  self.cv.Command(f"CCY S{self.number} 0")

          def set_curvature(self, curvature):
              self.curvature = curvature
              if self.parent.ref_mode == 'curvature':
                  self.cv.Command(f"CUY S{self.number} {self.curvature}")
                  if self.radius_variable:
                    self.cv.Command(f"CCY S{self.number} 0")
              else:
                  radius = 1 / curvature if curvature != 0 else float('inf')
                  self.cv.Command(f"RDY S{self.number} {radius}")
                  print(f"Warning: Curvature set to {curvature}, but system is in radius mode. Curvature converted to radius: {radius}.")
                  if self.radius_variable:
                    self.cv.Command(f"CCY S{self.number} 0")


          def set_thickness(self, thickness):
            self.thickness = thickness
            self.cv.Command(f"THI S{self.number} {self.thickness}")
            if self.thickness_variable:
                self.cv.Command(f"THC S{self.number} 0")

          def set_material(self, material):
            self.material = material
            self.cv.Command(f"GL1 S{self.number} {self.material}")

          def make_radius_variable(self):
            self.radius_variable = True
            self.cv.Command(f"CCY S{self.number} 0")

          def make_thickness_variable(self):
            self.thickness_variable = True
            self.cv.Command(f"THC S{self.number} 0")

          def make_radius_fixed(self):
            self.radius_variable = False
            self.cv.Command(f"CCY S{self.number} 100")

          def make_thickness_fixed(self):
            self.thickness_variable = False
            self.cv.Command(f"THC S{self.number} 100")

          def make_material_variable(self):
            self.material_variable = True
            self.cv.Command(f"GC1 S{self.number} 0")

          def make_material_fixed(self):
            self.material_variable = False
            self.cv.Command(f"GC1 S{self.number} 100")

          def update_from_codev(self):
            # Get the current parameters from CODE V
            current_params = self.parent.get_current_surface_params(self.number)
            if current_params:
                self.radius, self.thickness, self.material = current_params

          def set_parameters(self, radius, thickness, material=None):
            self.set_radius(radius)
            self.set_thickness(thickness)
            if material:
                self.set_material(material)
            # Note: You might also need to update material or other properties if required.

      def start_session(self):
        # Start a session of CODE V
        self.cv = win32com.client.Dispatch("CodeV.Application")
        self.cv.StartCodeV()
        print("CODE V session started.")

      def create_new_system(self):
        # Create a new lens system
        self.cv.Command("new")

      def set_wavelengths(self, wavelengths):
        # Set wavelengths (list of wavelengths in nm)
        wl_command = "WL " + " ".join(map(str, wavelengths))
        self.cv.Command(wl_command)

      def set_entrance_pupil_diameter(self, diameter):
        # Set entrance pupil diameter
        self.cv.Command(f"EPD {diameter}")

      def set_dimensions(self, dimension_unit):
        # Set measurement unit (e.g., 'mm' or 'm')
        self.cv.Command(f"DIM {dimension_unit}")

      def set_fields(self, fields):
        # Set fields (list of field points)
        for index, (angle, weight) in enumerate(fields, start=1):
            self.cv.Command(f"INS F{index} {angle} {weight}")

      def set_paraxial_image_distance(self):
         self.cv.Command("PIM Yes")

      def switch_ref_mode(self, mode):
        """Switch between radius and curvature mode."""
        if mode not in ['radius', 'curvature']:
            raise ValueError("Mode must be 'radius' or 'curvature'.")

        self.ref_mode = mode
        self.cv.Command(f"RDM {'Y' if mode == 'radius' else 'N'}")


      def update_all_surfaces_from_codev(self, output=False):
        # Get the current parameters for all surfaces from CODE V
        result = self.cv.Command("LIS")

        # Determine whether the system is in radius or curvature mode
        is_curvature_mode = "CUY" in result.split('\n')[0]

        if output:
            # Print the actual mode 
            print("System is in curvature mode." if is_curvature_mode else "System is in radius mode.")

            # Split the result into lines
            lines = result.split('\n')

            # Print only the first line or until "SPECIFICATION DATA" is encountered
            for line in lines:
                if "SPECIFICATION DATA" in line:
                    break
                print(line)

        # Regular expression patterns for radius and curvature modes
        pattern_radius = r"\s+(\d+):\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([\w_]+))?"
        pattern_curvature = r"\s+(\d+):\s+([-\d\.Ee\+\-]+)\s+([-\d\.]+)(?:\s+([\w_]+))?"

        pattern = pattern_curvature if is_curvature_mode else pattern_radius
        matches = re.finditer(pattern, result, re.MULTILINE)

        for match in matches:
            surface_number = int(match.group(1))
            value = float(match.group(2))
            thickness = float(match.group(3))
            material = match.group(4) if match.group(4) is not None else None

            if surface_number in self.surfaces:
                surface = self.surfaces[surface_number]
                if is_curvature_mode:
                    surface.set_curvature(value)
                else:
                    surface.set_radius(value)
                surface.set_thickness(thickness)
                if material and material not in ['0', 'None']:
                    surface.set_material(material)


      def get_efl_from_codev(self):
        # Execute the LIS command and get the output
        result = self.cv.Command("LIS")

        # Regular expression to find the EFL in the output
        efl_pattern = r"\s+EFL\s+([-\d\.Ee\+\-]+)"

        # Search for the EFL in the output
        match = re.search(efl_pattern, result)

        if match:
            # Extract and return the EFL value
            efl = float(match.group(1))
            return efl
        else:
            # Return None or raise an error if EFL is not found
            return None



      ##############  Methods for optimization ###############



      def optimize_system(self, efl, constrained = True):
        # Optimize the system
        self.cv.Command("AUT")
        self.cv.Command('DEL 0.15') # Ray grid interval
        if not constrained:
          self.cv.Command('MXT  1E10; MNT  -1E10; MNE  -1E10; MNA  -1E10; MAE  -1E10')

        if constrained:
          self.cv.Command("MNA 0")
          self.cv.Command("MAE 0")

        self.cv.Command("MXC 100")
        self.cv.Command('MNC 25')
        self.cv.Command("IMP 1E-15")
        self.cv.Command('WFR n') # Opti with transverse aberration

        self.cv.Command("DRA S0..I y")
        self.cv.Command("CNV 0") # Step optimisation
        self.cv.Command("EFL = " + str(efl)) # Condition on the EFL

        if efl == 15 or efl == -15:
          if constrained == True:
            self.cv.Command("SD SO Z1 > 12.5")
            self.cv.Command("MXT 7")
        elif efl == 50 or efl == -50 or efl == -100 or efl == -200:
          if constrained == True:
            self.cv.Command("SD SO Z1 > 40")
            self.cv.Command("MXT 14")
        elif efl == 100 or efl == 200:
          if constrained == True:
            self.cv.Command("SD SO Z1 > 75")
            self.cv.Command("MXT 60")

        #self.cv.Command("GLA SO..I  NFK5 NSK16 NLAF2 SF4")
        self.cv.Command("GO")  # Perform optimization

      def global_optimize_system(self, efl):
        # Optimize the system
        self.cv.Command("AUT ; CAN")
        self.cv.Command("AUT")
        self.cv.Command("MXC 100")
        self.cv.Command("IMP 0.0001")
        self.cv.Command("EFL Z1 = " + str(efl))
        self.cv.Command("MNA 0")
        self.cv.Command("MAE 0")
        self.cv.Command("GS 1")
        self.cv.Command("TIM 2")
        if efl == 15 or efl == -15:
          self.cv.Command("MXT 7")
          self.cv.Command("SD SO Z1 > 12.5")
        elif efl == 50 or efl == -50 or efl == -100 or efl == -200:
          self.cv.Command("MXT 14")
          self.cv.Command("SD SO Z1 > 40")
        elif efl == 100 or efl == 200:
          self.cv.Command("MXT 60")
          self.cv.Command("SD SO Z1 > 75")

        self.cv.Command("GLA SO..I  NFK5 NSK16 NLAF2 SF4")
        self.cv.Command("GO")  # Perform global synthesis


      def error_fct(self, efl, constrained = True):
        self.cv.Command("AUT ; CAN")
        self.cv.Command("AUT")
        self.cv.Command('DEL 0.15') # Ray grid interval
        if not constrained:
          self.cv.Command('MXT  1E10; MNT  -1E10; MNE  -1E10; MNA  -1E10; MAE  -1E10')

        if constrained:
          self.cv.Command("MNA 0")
          self.cv.Command("MAE 0")

        self.cv.Command('MNC 0')
        self.cv.Command("MXC 0")
        self.cv.Command("IMP 1E-15")
        self.cv.Command('WFR n') # Opti with transverse aberration
        self.cv.Command("EFL Z1 = " + str(efl)) # Condition on the EFL

        self.cv.Command("CNV 0") # Step optimisation

        if efl == 15 or efl == -15:
          self.cv.Command("MXT 7")
          if constrained == True:
            self.cv.Command("SD SO Z1 > 12.5")
        elif efl == 50 or efl == -50 or efl == -100 or efl == -200:
          self.cv.Command("MXT 14")
          if constrained == True:
            self.cv.Command("SD SO Z1 > 40")
        elif efl == 100 or efl == 200:
          self.cv.Command("MXT 60")
          if constrained == True:
            self.cv.Command("SD SO Z1 > 75")

        self.cv.Command("GLA SO..I  NFK5 NSK16 NLAF2 SF4")
        result = self.cv.Command("GO")  # Perform optimization

        # Regular expression to find the error function value in scientific notation
        match = re.search(r'ERR\. F\.\s*=\s*([+-]?[0-9]*\.?[0-9]+(?:[Ee][+-]?[0-9]+)?)', result)

        if match:
            return float(match.group(1))
        else:
            return None



      ############## Global Usage method ###############



      def save_system(self, file_path, seq = True):
        # Save the lens system
        if seq :
           self.cv.Command(f"WRL {file_path}")
        else :
           self.cv.Command(f"SAV {file_path}")
        print(f"Lens system saved at: {file_path}")

      def stop_session(self):
        # Stop the CODE V session
        self.cv.StopCodeV()
        print("CODE V session stopped.")

      def get_last_surface_number(self):
            # Get the number of the last surface in the dictionary
            if self.surfaces:
                return max(self.surfaces.keys())
            else:
                return 0  # Return 0 if no surfaces are present

      def get_surface(self, surface_num):
        return self.surfaces.get(surface_num, None)  # Return None if the surface is not found

      def make_all_thicknesses_fixed(self):
        for surface_num in self.surfaces.keys():
            self.get_surface(surface_num).make_thickness_fixed()
        print("All thicknesses have been fixed.")

      def make_all_thicknesses_variable(self):
        # Iterate over all surfaces and make their thickness variable
        for surface_num in range(1, self.get_last_surface_number() + 1):
            self.get_surface(surface_num).make_thickness_variable()
        print("All thicknesses have been made variable.")

      def save_system_parameters(self):
        """
        Save the current parameters of the system including the variability status of radius and thickness, and the current mode.
        :return: A dictionary containing the parameters of all surfaces and the current mode.
        """
        saved_params = {
            'mode': self.ref_mode,
            'surfaces': {}
        }
        for surface_num, surface in self.surfaces.items():
            saved_params['surfaces'][surface_num] = {
                'radius': surface.radius,
                'curvature': surface.curvature,
                'thickness': surface.thickness,
                'material': surface.material,
                'radius_variable': surface.radius_variable,
                'thickness_variable': surface.thickness_variable
            }
        return saved_params



      def load_system_parameters(self, saved_params):
        """
        Load a set of saved parameters into the system including the variability status of radius and thickness, and the current mode.
        :param saved_params: A dictionary containing the parameters to be loaded.
        """
        # Load the mode
        if 'mode' in saved_params:
            self.switch_ref_mode(saved_params['mode'])

        # Load parameters for each surface
        for surface_num, params in saved_params['surfaces'].items():
            if surface_num in self.surfaces:
                surface = self.get_surface(surface_num)
                if saved_params['mode'] == 'radius':
                    surface.set_radius(params['radius'])
                elif saved_params['mode'] == 'curvature':
                    surface.set_curvature(params['curvature'])
                surface.set_thickness(params['thickness'])

                if params['material'] is not None:
                    surface.set_material(params['material'])

                if params['radius_variable']:
                    surface.make_radius_variable()
                else:
                    surface.make_radius_fixed()

                if params['thickness_variable']:
                    surface.make_thickness_variable()
                else:
                    surface.make_thickness_fixed()


      def print_saved_systems(self):
        """
        Prints all the saved systems and their corresponding parameters in a formatted manner.
        """
        if not self.saved_systems:
            print("No systems have been saved.")
            return

        for system_name, system_data in self.saved_systems.items():
            print(f"System Name: {system_name}")
            print(f"System is in {system_data['mode']} mode.")
            print("    RDY             THI     RMD       GLA           CCY   THC")

            # Printing each surface's parameters
            for surface_num, params in system_data['surfaces'].items():
                radius = f"{params.get('radius', 'INFINITY'):>15}"
                thickness = f"{params.get('thickness', 'INFINITY'):>10}"
                material = params.get('material', 'None')
                material_str = f"{material:12}" if material else "            "  # 12 spaces if None
                radius_variable = "0" if params.get('radius_variable', False) else "100"
                thickness_variable = "0" if params.get('thickness_variable', False) else "100"

                if surface_num == 0:
                    label = "OBJ:"
                elif surface_num == len(system_data['surfaces']):
                    label = "IMG:"
                else:
                    label = f"{surface_num:4}:"

                print(f"{label}{radius}{thickness:12}{material_str}{radius_variable:>8}{thickness_variable:>8}")

            print("-" * 30)  # Separator for better readability




      ############## Methods for the saddle point ###############



      def initialize_buffer(self, num_points):
        """ Initialize a buffer for storing merit function values """
        buffer = np.zeros((num_points, num_points))
        return buffer

      def calculate_merit_function_values(self, surface_numbers, initial_curvatures, num_points, xp_min, xp_max, yp_min, yp_max, efl):
        """ Calculate merit function values for a range of curvatures """
        mf_values = np.zeros((num_points, num_points))
        for i in range(num_points):
            for j in range(num_points):
                xp = xp_min + i * (xp_max - xp_min) / (num_points - 1)
                yp = yp_min + j * (yp_max - yp_min) / (num_points - 1)

                curvatures = {
                    surface_numbers[0]: initial_curvatures[surface_numbers[0]] + xp / np.sqrt(2) + yp / np.sqrt(6),
                    surface_numbers[1]: initial_curvatures[surface_numbers[1]] + yp * np.sqrt(2 / 3),
                    surface_numbers[2]: initial_curvatures[surface_numbers[2]] - xp / np.sqrt(2) + yp / np.sqrt(6)
                }

                for surface, curvature in curvatures.items():
                    self.get_surface(surface).set_radius(curvature)

                mf_values[i, j] = self.error_fct(efl)  
        return mf_values

      def update_buffer_with_mf_values(self, buffer, mf_values):
        """ Update the buffer with calculated merit function values """
        np.copyto(buffer, mf_values)

      def plot_1d_merit_function(self, buffer, dpi=150):
        """ Plot the 1D merit function along both the x and y axes """
        num_points = buffer.shape[0]
        plt.figure(dpi=dpi)

        # Assuming the middle row and column represent the y-axis and x-axis, respectively
        middle_index = num_points // 2

        # X-axis cut (Vertical cut)
        y_values_x_cut = buffer[middle_index, :]
        x_values_x_cut = np.linspace(-num_points // 2, num_points // 2, num_points)
        plt.plot(x_values_x_cut, y_values_x_cut, label='X-axis cut')

        # Y-axis cut (Horizontal cut)
        y_values_y_cut = buffer[:, middle_index]
        x_values_y_cut = np.linspace(-num_points // 2, num_points // 2, num_points)
        plt.plot(x_values_y_cut, y_values_y_cut, label='Y-axis cut')

        plt.xlabel('Axis')
        plt.ylabel('Merit Function Value')
        plt.title('1D Merit Function Plot')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()  # Adjusts the plot to ensure everything fits
        plt.show()

      def plot_2d_merit_function(self, buffer, view_angles=None, dpi=150):
        """ Plot the 2D merit function """
        num_points = buffer.shape[0]
        x = np.linspace(-num_points // 2, num_points // 2, num_points)
        y = np.linspace(-num_points // 2, num_points // 2, num_points)
        X, Y = np.meshgrid(x, y)
        Z = buffer

        fig = plt.figure(dpi=dpi)
        ax = fig.add_subplot(111, projection='3d')

        # Plot surface with transparency
        ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.7)

        # Set labels and title
        ax.set_xlabel('X Axis')
        ax.set_ylabel('Y Axis')
        ax.set_zlabel('Merit Function Value')
        ax.set_title('2D Merit Function Plot')

        # Enhanced saddle point marker
        central_index = num_points // 2
        saddle_point_z = Z[central_index, central_index]

        # Create a vertical line for the saddle point
        ax.plot([0, 0], [0, 0], [0, saddle_point_z], color='red', linestyle='--', linewidth=2)
        ax.scatter(0, 0, saddle_point_z, color='red', marker='*', s=100)

        # Add annotation for clarity
        ax.text(0, 0, saddle_point_z, "Saddle Point", color='blue')

        # Adjust the viewing angle if provided
        if view_angles:
            ax.view_init(elev=view_angles[0], azim=view_angles[1])

        plt.tight_layout()
        plt.show()

      def add_null_surfaces(self, reference_surface_number):
        """
        Adds two null surfaces after the specified reference surface with zero thickness,
        and the same radius and material as the reference surface.

        :param reference_surface_number: The number of the reference surface after which the null surfaces will be added.
        """
        last_surface_number = self.get_last_surface_number()

        # Get properties of the reference surface
        ref_surface = self.get_surface(reference_surface_number)
        material = self.get_surface(reference_surface_number-1).material
        radius = ref_surface.radius
        thickness = ref_surface.thickness
        if ref_surface is None:
            raise ValueError(f"Reference surface number {reference_surface_number} does not exist.")

        print(f"Reference surface properties - Radius: {radius}, Material: {material}")

        # Shift existing surfaces to make room for new null surfaces
        for num in range(last_surface_number, reference_surface_number, -1):
            self.surfaces[num + 2] = self.surfaces[num]
            self.surfaces[num + 2].number += 2
            #print(num)

        # Insert two new null surfaces after the reference surface
        for i in range(1, 3):
            new_surface_number = reference_surface_number + i 

            # Create the new null surface with zero thickness
            if i == 2:
                self.surfaces[new_surface_number] = self.Surface(self, new_surface_number, radius, thickness)
                self.surfaces[new_surface_number].make_radius_variable()
            else:
                self.surfaces[new_surface_number] = self.Surface(self, new_surface_number, radius, 0, material)
                self.surfaces[new_surface_number].make_radius_variable()

        ref_surface.set_thickness(0)  # Set thickness of the reference surface to zero@

        print(f"Added null surfaces {reference_surface_number + 1} and {reference_surface_number + 2}")



      def add_null_surfaces2(self, reference_surface_number):
          """
          Adds two null surfaces in front of the specified reference surface with zero thickness,
          and the same radius and material as the reference surface.

          :param 
          reference_surface_number: The number of the reference surface in front of which the null surfaces will be added.
          """
          last_surface_number = self.get_last_surface_number()

          # Get properties of the reference surface
          ref_surface = self.get_surface(reference_surface_number)
          if ref_surface is None:
              raise ValueError(f"Reference surface number {reference_surface_number} does not exist.")

          radius = ref_surface.radius
          material = ref_surface.material

          print(radius)
          print(material)

          # Insert two new surfaces after the reference surface
          for i in range(1, 3):
              new_surface_number = reference_surface_number + i -1
              # Shift the existing surfaces to make room for the new null surfaces
              for num in range(last_surface_number, new_surface_number - 1, -1):
                  self.get_surface(num).number += 1
                  self.surfaces[num + 1] = self.surfaces.pop(num)

              # Create the new null surface with zero thickness
              if i == 2 :
                surface = self.Surface(self, new_surface_number, radius, 0)
                surface.make_radius_variable()
              else :
                surface = self.Surface(self, new_surface_number, radius, 0, material)
                surface.make_radius_variable()


      def modify_curvatures_for_saddle_point(self, surface_numbers, epsilon, efl, output=False):
          """
          Modify the curvatures of specified surfaces to position the system on either side of the saddle point.
          :param surface_numbers: List of two surface numbers whose curvatures will be modified.
          :param epsilon: The small curvature change to be applied.
          :param efl: Effective focal length for optimization.
          """
          # Save the current state of the system
          original_system_state = self.save_system_parameters()

          # Modify the curvatures for System 1
          for num in surface_numbers:
              original_radius = self.get_surface(num).radius
              new_radius = original_radius - epsilon
              self.get_surface(num).set_radius(new_radius)

          # Optimize the first system
          #self.make_all_thicknesses_variable()
          self.optimize_system(efl, constrained=False)
          self.optimize_system(efl, constrained=False)
          self.update_all_surfaces_from_codev(output=output)
          system1_params = self.save_system_parameters()  # Save parameters of the first system

          # Restore the original system state before modifying for the second system
          self.load_system_parameters(original_system_state)

          # Modify the curvatures for System 2
          for num in surface_numbers:
              original_radius = self.get_surface(num).radius
              new_radius = original_radius + epsilon
              self.get_surface(num).set_radius(new_radius)

          # Optimize the second system
          #self.make_all_thicknesses_variable()
          self.optimize_system(efl, constrained=False)
          self.optimize_system(efl, constrained=False)
          self.update_all_surfaces_from_codev(output=output)
          system2_params = self.save_system_parameters()  # Save parameters of the second system

          return system1_params, system2_params


      def increase_thickness_and_optimize(self, lens_thickness_steps, air_distance_steps, lens_surface_number, air_surface_number, efl, file_path):
          """
          Gradually increase the thickness of the lens and the air distance between lenses, followed by optimization.

          :param lens_thickness_steps: List of thickness values to increment for the lens.
          :param air_distance_steps: List of air distance values to increment between lenses.
          :param lens_surface_number: The surface number of the lens whose thickness is to be increased.
          :param air_surface_number: The surface number of the air gap whose distance is to be increased.
          :param efl: Effective focal length for optimization.
          :param file_path: Path to save the final optimized system.
          """

          # Loop for lens thickness adjustments
          for lens_thickness in lens_thickness_steps:
              self.cv.Command(f"THI S{lens_surface_number} {lens_thickness}")
              self.optimize_system(efl, constrained=False)
              self.optimize_system(efl, constrained=False)
              self.update_all_surfaces_from_codev()

          # Loop for air distance adjustments
          for air_thickness in air_distance_steps:
              self.cv.Command(f"THI S{air_surface_number} {air_thickness}")
              self.optimize_system(efl, constrained=False)
              self.optimize_system(efl, constrained=False)
              self.update_all_surfaces_from_codev()

          # Save the final system
          self.save_system(file_path)

      def plot_optical_system(self, file_path, xlim=(0, 10), ylim=(-15, 15), hide_axes=True):
          """
          Plot the final optical system layout using rayoptics.

          :param file_path: Path to the .seq file for the optical system.
          :param xlim: Tuple for x-axis limits of the plot.
          :param ylim: Tuple for y-axis limits of the plot.
          :param hide_axes: Boolean to determine whether to hide the axes.
          """
          # Import necessary modules for rayoptics
          from rayoptics.environment import open_model, InteractiveLayout
          import matplotlib.pyplot as plt

          # Load the optical model
          opm = open_model(file_path)

          # Create an InteractiveLayout instance
          layout_plt = plt.figure(FigureClass=InteractiveLayout, opt_model=opm, 
                                  do_draw_rays=False, do_draw_beams=False, 
                                  do_draw_edge_rays=False, do_draw_ray_fans=False, 
                                  do_paraxial_layout=False)

          # Get the axis for customization
          ax = layout_plt.gca()
          if hide_axes:
              ax.grid(False)
              ax.axis('off')
          else:
              ax.grid(True)

          ax.set_ylim(0, 0.5)

          # Adjust figure size and limits
          layout_plt.plot()
          plt.xlim(*xlim)
          plt.ylim(*ylim)

          # Show the plot
          plt.show()

      def sp_create_and_increase_thickness(self,sp,reference_surface_number,lens_thickness,file_path, efl):

          self.switch_ref_mode('curvature')
          self.get_surface(reference_surface_number+1).set_curvature(sp)
          self.get_surface(reference_surface_number+2).set_curvature(sp)
          merit_function = self.error_fct(efl, constrained=False)

          # save system to restore it later
          buffer = self.save_system_parameters()

          self.cv.Command(f"THI S{reference_surface_number+1} {lens_thickness}")
          self.save_system(file_path)

          # restore system
          self.load_system_parameters(buffer)
          self.switch_ref_mode('radius')

          return merit_function


      ############## Saddle point Scan method ###############



      def perform_sp_scan(self, reference_surface_number, efl, delta_curvature=0.00025, num_points=400, threshold_multiplier=3, output=False):
        # Nested function to evaluate the derivative at a given curvature
        def derivative_at_curvature(curvature, curvatures, derivatives):
            index = np.searchsorted(curvatures, curvature) - 1
            return derivatives[index]

        # Nested function for the bisection method
        def bisection_method(f, a, b, tol=1e-5, max_iter=100):
            for _ in range(max_iter):
                mid = (a + b) / 2
                if f(mid) * f(a) < 0:
                    b = mid
                else:
                    a = mid
                if abs(b - a) < tol:
                    break
            return (a + b) / 2

        # Nested function to check if the zero at the given index is smooth
        def is_smooth_zero(derivatives, index, window_size=5):
            start = max(index - window_size, 0)
            end = min(index + window_size, len(derivatives))
            window = derivatives[start:end]
            return np.std(window) < threshold  # using the same threshold as before


        # Define initial curvature based on the reference surface
        initial_curvature = 1 / self.get_surface(reference_surface_number).radius

        # Arrays to store curvatures and corresponding MF values
        curvatures = np.linspace(initial_curvature - delta_curvature * num_points / 2, 
                                 initial_curvature + delta_curvature * num_points / 2, 
                                 num_points)
        mf_values = np.zeros(num_points)

        # Compute the derivative for each curvature using the central finite difference method
        for i, curvature in enumerate(curvatures):
            self.get_surface(reference_surface_number + 1).set_curvature(curvature)
            mf = self.error_fct(efl, constrained=False)
            mf_values[i] = mf

        # Compute the derivative using the central finite difference method
        derivatives = np.zeros(num_points)
        for i in range(1, num_points - 1):
            derivatives[i] = (mf_values[i + 1] - mf_values[i - 1]) / (2 * delta_curvature)

        # Compute the standard deviation of the derivative values
        std_deviation = np.std(derivatives)

        # Set the threshold as a multiple of the standard deviation
        threshold = threshold_multiplier * std_deviation

        # Filter the data to focus on the region near zero
        mask = np.abs(derivatives) < threshold
        filtered_curvatures = curvatures[mask]
        filtered_derivatives = derivatives[mask]

        # Finding all intervals where the derivative changes sign and is smooth
        zero_points = []
        for i in range(1, len(curvatures) - 1):
            if derivatives[i] * derivatives[i - 1] < 0:
                a, b = curvatures[i - 1], curvatures[i]
                zero_point = bisection_method(lambda x: derivative_at_curvature(x, curvatures, derivatives), a, b)

                # Check if the zero point is smooth
                if is_smooth_zero(derivatives, i):
                    zero_points.append(zero_point)

        if output:
            # Plot the filtered derivative against curvature with the zero points marked
            plt.plot(filtered_curvatures, filtered_derivatives, label="Filtered Derivative")
            for zp in zero_points:
                plt.scatter([zp], [0], color='red')  # Marking the zero points
            plt.xlabel("Curvature")
            plt.ylabel("Derivative of Merit Function")
            plt.title("Filtered Derivative of Merit Function vs Curvature with Zero Points")
            plt.legend()
            plt.grid(True)
            plt.show()

            # Plotting the merit function against curvature
            plt.plot(curvatures, mf_values)
            plt.xlabel("Curvature")
            plt.ylabel("Merit Function")
            plt.title("Merit Function vs Curvature")
            plt.grid(True)
            plt.show()

        return zero_points

  

    ############## Global interaction for Tree Creation ##############

  

      def find_and_optimize_from_saddle_points(self, current_node, system_tree, efl, base_file_path, depth, reference_surface):
        print_subheader(f"Optimizing from Saddle Points - Depth {depth}, Ref. Surface {reference_surface}")
        # Load the current optical system state from the parent node
        # self.load_system_parameters(current_node.optical_system_state)
        # self.update_all_surfaces_from_codev(output=False)

        # Perform Saddle Point Scan
        self.switch_ref_mode('curvature')
        sps = self.perform_sp_scan(reference_surface, efl, output=False)
        print(f"  Saddle Points Found: {len(sps)}")
      
        for i, sp in enumerate(sps):
            print(f"  Processing Saddle Point {i+1}: Value {sp}")
            # Save the current optical system state before modifications
            original_state = self.save_system_parameters()

            # Saddle Point File Naming
            sp_filename = f"{base_file_path}/L{depth+1}_SP{i+1}.seq"
            sp_merit = self.sp_create_and_increase_thickness(sp, reference_surface, current_node.system_params['lens_thickness'], sp_filename, efl)
            self.update_all_surfaces_from_codev(output=False)

            # Save the state after creating and increasing thickness
            sp_state = self.save_system_parameters()

            # Create a node for the saddle point and add it to the tree
            sp_node = SystemNode(system_params=current_node.system_params, optical_system_state=sp_state, seq_file_path=sp_filename,
                                  parent=current_node, merit_function=sp_merit, is_optimized=False, depth=depth+1)
            current_node.add_child(sp_node)
            system_tree.add_node(sp_node)

            # Surface numbers (list like 3,4 for ref 2)
            surface_numbers = [reference_surface + 1, reference_surface + 2]

            # Modify curvatures for two systems around the saddle point
            system1_params, system2_params = self.modify_curvatures_for_saddle_point(surface_numbers, current_node.system_params['epsilon'], efl, output=False)

            # Optimize and Save System 1
            self.load_system_parameters(system1_params)
            system1_filename = f"{base_file_path}/L{depth+1}_SP{i+1}_OptA.seq"
            self.increase_thickness_and_optimize(current_node.system_params['lens_thickness_steps'], current_node.system_params['air_distance_steps'], 3, 2, efl, system1_filename)
            system1_state = self.save_system_parameters()
            system1_merit_function = self.error_fct(efl, constrained=False)
            system1_efl = self.get_efl_from_codev()
            system1_node = SystemNode(system_params=current_node.system_params, optical_system_state=system1_state, seq_file_path=system1_filename, 
                                      parent=sp_node, merit_function=system1_merit_function, efl=system1_efl, is_optimized=True, depth=depth+1)
            sp_node.add_child(system1_node)
            system_tree.add_node(system1_node)

            # Restore original state and Optimize and Save System 2
            self.load_system_parameters(system2_params)
            system2_filename = f"{base_file_path}/L{depth+1}_SP{i+1}_OptB.seq"
            self.increase_thickness_and_optimize(current_node.system_params['lens_thickness_steps'], current_node.system_params['air_distance_steps'], 3, 2, efl, system2_filename)
            system2_state = self.save_system_parameters()
            system2_merit_function = self.error_fct(efl, constrained=False)
            system2_efl = self.get_efl_from_codev()
            system2_node = SystemNode(system_params=current_node.system_params, optical_system_state=system2_state, seq_file_path=system2_filename,
                                       parent=sp_node, merit_function=system2_merit_function, efl=system2_efl, is_optimized=True, depth=depth+1)
            sp_node.add_child(system2_node)
            system_tree.add_node(system2_node)

            # Restore the original optical system state after each saddle point iteration
            self.load_system_parameters(original_state)
          
        print("  Completed Saddle Point Optimization")

        
      
      def evolve_optimized_systems(self, system_tree, starting_depth, target_depth, base_file_path, efl):
        print_evolution_header(starting_depth, target_depth)

        current_depth = starting_depth

        while current_depth <= target_depth:
            print_subheader(f"Processing Depth {current_depth}")
            optimized_nodes = system_tree.find_optimized_nodes_at_depth(current_depth)
            print(f"Found {len(optimized_nodes)} optimized nodes at depth {current_depth}")

            for i, node in enumerate(optimized_nodes):
                print(f"  Optimizing Node number {i+1} of {len(optimized_nodes)} (Seq File: {node.seq_file_path}) at Depth {current_depth}")
                self.load_system_parameters(node.optical_system_state)
                self.update_all_surfaces_from_codev(output=False)   # Keep this in mind
                system_tree.print_tree()

                # Perform SP detection and optimization for each optimized node
                viable_surfaces = self.identify_viable_surfaces()
                print(f"Viable surfaces for node: {viable_surfaces}")
                if viable_surfaces is not None:
                    for surface in viable_surfaces:
                        print("\n")
                        print(f"    Optimizing at Surface {surface}")
                        buffer = self.save_system_parameters()
                        self.add_null_surfaces(surface)
                        self.find_and_optimize_from_saddle_points(node, system_tree, efl, base_file_path, current_depth, surface)
                        self.load_system_parameters(buffer)
                else:
                    print("No viable surfaces found")

            current_depth += 1
            print(f"Completed Depth {current_depth - 1}")

        print_header("System Evolution Process Completed")


      def identify_viable_surfaces(self):
          """
          Identify the surfaces that are viable for adding null surfaces.
          :return: A list of surface numbers that are viable for adding null surfaces.
          """
          viable_surfaces = []
          last_surface_number = self.get_last_surface_number()
          print(f"Last surface number: {last_surface_number}")

          if last_surface_number is not None:
              for surface_num in range(1, last_surface_number+1):
                  if surface_num % 2 == 0:
                      viable_surfaces.append(surface_num)
          else:
              print("Error: Unable to retrieve the last surface number")

          return viable_surfaces
      
