import re    

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

          def update(self):
            # Update the surface with the current parameters
            self.set_radius(self.radius)
            self.set_thickness(self.thickness)
            if self.material:
                self.set_material(self.material)

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

      def optimize_system(self, efl):
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
          self.cv.Command("SD SO Z1 > 12.5")
        elif efl == 50 or efl == -50 or efl == -100 or efl == -200:
          self.cv.Command("MXT 14")
          self.cv.Command("SD SO Z1 > 40")
        elif efl == 100 or efl == 200:
          self.cv.Command("MXT 60")
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
