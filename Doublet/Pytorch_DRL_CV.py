import gym
from gym import spaces
import numpy as np
from stable_baselines3 import PPO

class LensOptimizationEnv(gym.Env):
    def __init__(self, system_setup, materials_list, efl=15):
        super(LensOptimizationEnv, self).__init__()
        self.system_setup = system_setup
        self.materials_list = materials_list
        self.efl = efl

        # Define action and observation space
        # Action space: [radius, thickness, material index] for each surface
        self.action_space = spaces.Box(
        low=np.array([-100, 0, -100, 0, 0, -100, 0, 0, -100, 0]),
        high=np.array([100, 7, 100, 7, len(materials_list)-1, 100, 7, len(materials_list)-1, 100, 7]),
        dtype=np.float32
        )

        # Observation space: the same as action space for simplicity
        self.observation_space = self.action_space

    def step(self, action):
      # Apply the action to the system
      self.apply_action_to_system(action)

      # Debugging: Print the current state of the system
      print("Current System State:", [self.system_setup.surfaces[i].get_parameters() for i in range(2, 6)])

      # Calculate the error (reward is negative error)
      error = self.system_setup.error_fct(self.efl)
      print("Error:", error)  # Debugging print

      if error is None:
          raise ValueError("Error function returned None. Check system state.")

      reward = -error

      # Placeholder for termination condition
      done = False
      info = {}

      return action, reward, done, info

    def reset(self):
        # Reset the state of the environment to an initial state
        initial_state = np.zeros(12)  # Placeholder
        self.apply_action_to_system(initial_state)
        return initial_state

    def apply_action_to_system(self, action):
        # Unpack the actions
        radius_2, thickness_2, material_2, radius_3, thickness_3, radius_4, thickness_4, material_4, radius_5, thickness_5 = action

        # Apply actions to surface 2
        self.system_setup.surfaces[2].set_parameters(radius_2, thickness_2)
        material_index_2 = max(0, min(int(material_2), len(self.materials_list) - 1))
        self.system_setup.surfaces[2].set_material(self.materials_list[material_index_2])

        # Apply actions to surface 3
        self.system_setup.surfaces[3].set_parameters(radius_3, thickness_3)

        # Apply actions to surface 4
        self.system_setup.surfaces[4].set_parameters(radius_4, thickness_4)
        material_index_4 = max(0, min(int(material_4), len(self.materials_list) - 1))
        self.system_setup.surfaces[4].set_material(self.materials_list[material_index_4])

        # Apply actions to surface 5
        self.system_setup.surfaces[5].set_parameters(radius_5, thickness_5)



def train_drl_agent(env):
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=10000)  # Adjust timesteps as needed
    return model

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

    # Initialize the environment
    env = LensOptimizationEnv(system_setup, materials_list, efl)

    # Train the DRL agent
    model = train_drl_agent(env)

    # Test the trained agent (can be expanded into a more detailed testing routine)
    obs = env.reset()
    for _ in range(1000):
        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, dones, info = env.step(action)
        if dones:
            break

    # Save the trained model for later use
    model.save("lens_optimization_model")

if __name__ == '__main__':
    main()
