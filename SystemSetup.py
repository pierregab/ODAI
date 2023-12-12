import re    
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import win32com.client

class SystemSetup:
      def __init__(self):
          self.cv = win32com.client.Dispatch("CodeV.Application")
          self.surfaces = {}   # dict to keep track of surfaces

      class Surface:
          def __init__(self, parent, number, radius, thickness, material=None):
              self.parent = parent
              self.cv = parent.cv
              self.number = number
              self.radius = radius
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
            self.cv.Command(f"RDY S{self.number} {self.radius}")
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

      def update_all_surfaces_from_codev(self, output = False):
        # Get the current parameters for all surfaces from CODE V
        result = self.cv.Command("LIS")

        if output:
            # Split the result into lines
            lines = result.split('\n')

            # Print only the first line or until "SPECIFICATION DATA" is encountered
            for line in lines:
                if "SPECIFICATION DATA" in line:
                    break
                print(line)

        # Regular expression to match each surface's parameters
        pattern = r"\s+(\d+):\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([\w_]+))?"
        matches = re.finditer(pattern, result, re.MULTILINE)

        for match in matches:
            surface_number = int(match.group(1))
            radius = float(match.group(2))
            thickness = float(match.group(3))
            material = match.group(4) if match.group(4) is not None else None

            if surface_number in self.surfaces:
                surface = self.surfaces[surface_number]
                surface.radius = radius
                surface.thickness = thickness
                if material != 0 or material != 'None':
                  surface.material = material
                # You can add more code here if you need to update other properties


      def optimize_system(self, efl, constrained = True):
        # Optimize the system
        self.cv.Command("AUT ; CAN")
        self.cv.Command("AUT")
        self.cv.Command("MXC 100")
        self.cv.Command("IMP 0.0001")
        self.cv.Command("EFL Z1 = " + str(efl))
        self.cv.Command("MNA 0")
        self.cv.Command("MAE 0")
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


      def error_fct(self, efl):
        self.cv.Command("AUT ; CAN")
        self.cv.Command("AUT")
        self.cv.Command("MXC 0")
        self.cv.Command("MNC 0")
        self.cv.Command("EFL Z1 = " + str(efl))
        self.cv.Command("MNA 0")
        self.cv.Command("MAE 0")
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
        result = self.cv.Command("GO")

        # Regular expression to find the error function value in scientific notation
        match = re.search(r'ERR\. F\.\s*=\s*([+-]?[0-9]*\.?[0-9]+(?:[Ee][+-]?[0-9]+)?)', result)

        if match:
            return float(match.group(1))
        else:
            return None




      ############## Global Usage method ###############


  

      def save_system(self, file_path):
        # Save the lens system
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
        Save the current parameters of the system including the variability status of radius and thickness.
        :return: A dictionary containing the parameters of all surfaces.
        """
        saved_params = {}
        for surface_num, surface in self.surfaces.items():
            saved_params[surface_num] = {
                'radius': surface.radius,
                'thickness': surface.thickness,
                'material': surface.material,
                'radius_variable': surface.radius_variable,
                'thickness_variable': surface.thickness_variable
            }
        return saved_params
    
    
      def load_system_parameters(self, saved_params):
        """
        Load a set of saved parameters into the system including the variability status of radius and thickness.
        :param saved_params: A dictionary containing the parameters to be loaded.
        """
        for surface_num, params in saved_params.items():
            if surface_num in self.surfaces:
                surface = self.get_surface(surface_num)
                surface.set_radius(params['radius'])
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
            print(num)

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

        print(f"Added null surfaces {reference_surface_number + 2} and {reference_surface_number + 3}")



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
          self.make_all_thicknesses_variable()
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
          self.make_all_thicknesses_variable()
          self.optimize_system(efl, constrained=False)
          self.update_all_surfaces_from_codev(output=output)
          system2_params = self.save_system_parameters()  # Save parameters of the second system

          return system1_params, system2_params


      def increase_thickness_and_optimize(self, lens_thickness_steps, air_distance_steps, lens_surface_number, air_surface_number, efl):
        """
        Gradually increase the thickness of the lens and the air distance between lenses, followed by optimization.
        :param lens_thickness_steps: List of thickness values to increment for the lens.
        :param air_distance_steps: List of air distance values to increment between lenses.
        :param lens_surface_number: The surface number of the lens whose thickness is to be increased.
        :param air_surface_number: The surface number of the air gap whose distance is to be increased.
        """
        for lens_thickness in lens_thickness_steps:
            self.get_surface(lens_surface_number).set_thickness(lens_thickness)
            for air_distance in air_distance_steps:
                self.get_surface(air_surface_number).set_thickness(air_distance)
                self.optimize_system(efl)
                self.update_all_surfaces_from_codev()
