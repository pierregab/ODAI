import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
import win32com.client
import os
import re

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

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


# Define the Environment for CodeV
class CodeVEnvironment:
    def __init__(self, max_steps=100):
        self.max_steps = max_steps
        self.step_count = 0
        self.codev_setup = system_setup
        self.state_size = 10
        self.reset()

    def reset(self):
        self.step_count = 0
        # ... [Reset or initialize your lens system in CodeV] ...
        for i in range(system_setup.get_last_surface_number()) :
          self.codev_setup.surfaces[i].set_radius(0)
          self.codev_setup.surfaces[i].set_thickness(0)
          if i%2 == 0:
            self.codev_setup.surfaces[i].set_material(516800.641673)
        return self.get_state()

    def get_state(self):
        x = []
        # ... [Get the state of your lens system in CodeV] ...
        for i in range(system_setup.get_last_surface_number()) :
          x.append(self.codev_setup.surfaces[i].get_radius())
          x.append(self.codev_setup.surfaces[i].get_thickness())
          if i%2 == 0:
            x.append(self.codev_setup.surfaces[i].get_material())
        return x

    def step(self, action):
      # Apply the action to the CodeV system
      self.apply_action(action)
  
      # Update the state
      new_state = self.get_state()
  
      # Calculate the reward
      reward = -self.codev_setup.error_fct(efl)  # Using negative error as the reward
  
      # Check if the episode is done
      self.step_count += 1
      done = self.step_count >= self.max_steps
  
      return new_state, reward, done
  
    def apply_action(self, action):
      # Define how an action modifies the CodeV system
      # Example: action could be a tuple (surface_number, parameter_type, change)
      surface_number, parameter_type, change = action
      surface = self.codev_setup.get_surface(surface_number)
  
      if parameter_type == 'radius':
          surface.set_radius(surface.radius + change)
      elif parameter_type == 'thickness':
          surface.set_thickness(surface.thickness + change)
      elif parameter_type == 'material':
          # Assuming change is an index to select a material from a predefined list
          surface.set_material(materials_list[change])
  
      # Don't forget to update the surface after changes
      surface.update()

# Define the Q-Network
class QNetwork(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

# Define the DQN Agent
class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.0001
        self.model = QNetwork(state_size, action_size).to(device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        q_values = self.model(torch.FloatTensor(state).to(device))
        return np.argmax(q_values.detach().cpu().numpy())

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        states = torch.FloatTensor([item[0] for item in minibatch]).to(device)
        actions = [item[1] for item in minibatch]
        rewards = [item[2] for item in minibatch]
        next_states = torch.FloatTensor([item[3] for item in minibatch]).to(device)
        dones = [item[4] for item in minibatch]

        # Predict Q-values
        q_values = self.model(states)

        # Calculate target Q-values
        next_q_values = self.model(next_states)
        targets = torch.FloatTensor(rewards).to(device) + self.gamma * torch.max(next_q_values, dim=1)[0]
        for i, done in enumerate(dones):
            if done:
                targets[i] = rewards[i]

        # Update Q-values for the actions taken
        for i, action in enumerate(actions):
            q_values[i][action] = targets[i]

        # Train the Q-network
        self.optimizer.zero_grad()
        predicted_q_values = self.model(states)
        loss = self.criterion(predicted_q_values, q_values)
        loss.backward()
        self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

# Main DRL Training Loop
env = CodeVEnvironment()
state_size = 8  # Adjust based on your lens system
action_size = 16  # Adjust as needed
agent = DQNAgent(state_size, action_size)
episodes = 1000
batch_size = 32

for e in range(episodes):
    state = env.reset()
    done = False
    total_reward = 0  # Initialize total_reward to zero at the start of each episode
    while not done:
        action = agent.act(state)
        next_state, reward, done = env.step(action)
        agent.remember(state, action, reward, next_state, done)
        state = next_state
        total_reward += reward  # Accumulate rewards (negative of merit function values)
        if len(agent.memory) > batch_size:
            agent.replay(batch_size)
    merit_function_value = -total_reward  # Convert total_reward back to merit function value
    print(f"Episode {e+1}/{episodes} finished! Merit Function Value: {merit_function_value}")
