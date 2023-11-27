import SystemSetup

def main():
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

  # Adding Surfaces
  surface1 = system_setup.Surface(system_setup, 1, 1e18, 0.650)  # First surface

  surface2 = system_setup.Surface(system_setup, 2, 23.875, 0, "NBK7_SCHOTT")  # Second surface
  surface2.make_radius_variable()
  surface2.make_thickness_variable()

  surface3 = system_setup.Surface(system_setup, 3, -17.011, 0.050)  # Third surface
  surface3.make_radius_variable()
  surface3.make_thickness_variable()

  surface4 = system_setup.Surface(system_setup, 4, -16.998, 0.650, "SF2_SCHOTT")  # Fourth surface
  surface4.make_radius_variable()
  surface4.make_thickness_variable()

  surface5 = system_setup.Surface(system_setup, 5, -58.355, 39.289)  # Fifth surface
  surface5.make_radius_variable()
  surface5.make_thickness_variable()
  system_setup.optimize_system(efl)
  print("Error function value:", system_setup.error_fct(efl))

  # Save the lens system
  system_setup.save_system("C:/CVUSER/my_new_lens")

  # Stop the CODE V session
  system_setup.stop_session()

if __name__ == '__main__':
  main()
