import matplotlib.pyplot as plt
import matplotlib.patches as patches
from rayoptics.environment import InteractiveLayout, open_model
import io
import os
import numpy as np
from affichage import print_decorative_header, print_blank_line
import re

class SystemNode:
  id_counter = 0  # Class-level counter for unique IDs

  @classmethod
  def generate_unique_id(cls):
      cls.id_counter += 1
      return cls.id_counter

  def __init__(self, system_params, optical_system_state=None,seq_file_path=None, parent=None, merit_function=None, efl = None, is_optimized=False, depth=0, high_debuging=False):
      self.id = SystemNode.generate_unique_id()
      self.system_params = system_params  # Parameters for saddle point optimization
      self.seq_file_path = seq_file_path
      self.high_debuging = high_debuging
      self.optical_system_state = optical_system_state  # State of the optical system
      self.merit_function = merit_function
      self.efl = efl
      self.parent = parent  # Parent node
      self.children = []  # Children nodes
      self.saddle_points = []  # List to store saddle points
      self.minima = []  # List to store minima found at each saddle point
      self.is_optimized = is_optimized  # Track if the node is an optimized system derived from an SP
      self.depth = depth  # Track the depth of the node in the tree

  @property
  def optical_system_state(self):
        if self.high_debuging:
            print(f"Accessing optical system state for node {self.seq_file_path}.")
            print(f"Optical system state is {self._optical_system_state}.")
        return self._optical_system_state

  @optical_system_state.setter
  def optical_system_state(self, new_state):
        if self.high_debuging:
            print(f"Updating optical system state for node {self.seq_file_path}.")
        self._optical_system_state = new_state

  def add_child(self, child_node):
      self.children.append(child_node)

  def add_saddle_point(self, saddle_point):
      self.saddle_points.append(saddle_point)

  def add_minimum(self, minimum):
      self.minima.append(minimum)


class SystemTree:
    def __init__(self, root_node):
        self.root = root_node
        self.all_nodes = [self.root]  # List to store all nodes
        self.target_depths = [1, 2]  # Define the depths you want to plot
        # Initialize row counters for each node type at each depth
        self.row_counters = {depth: {'SP': 0, 'OptA': 0, 'OptB': 0} for depth in self.target_depths}

    def add_node(self, node):
        self.all_nodes.append(node)

    def print_tree(self, node=None, depth=0):
        if node is None:
            if depth == 0:  # Print header and border only once at the start
                print_decorative_header()
            node = self.root

        indent = " " * depth * 4  # Increase indentation for better readability
        seq_file = node.seq_file_path if node.seq_file_path else 'No file'
        merit_function = node.merit_function if node.merit_function else 'No merit function'
        efl = node.efl if node.efl else 'No efl'
        is_optimized = "Yes" if node.is_optimized else "No"
        node_info = f"{indent}Node Depth {depth} | Optimized: {is_optimized} | SEQ File: {seq_file} | Merit: {merit_function} | EFL: {efl}"
        print(node_info)

        for child in node.children:
            self.print_tree(child, depth + 1)

        #print_blank_line()

    def calculate_similarity(self, params1, params2, threshold=0.1):
        # Check if the number of parameters is the same
        if len(params1) != len(params2): 
            return False

        # Calculate the sum of Euclidean distances between corresponding parameters
        distance = sum(np.linalg.norm(np.array(p1) - np.array(p2)) for p1, p2 in zip(params1, params2))

        # Determine if the systems are similar based on the distance and threshold
        return distance < threshold

    def plot_node(self, node, axs, row, col):
        if node.seq_file_path and os.path.exists(node.seq_file_path):
            png_buffer = self.plot_single_system(node.seq_file_path)
            img_arr = plt.imread(png_buffer)
            ax = axs[row, col]
            ax.imshow(img_arr)
            ax.axis('off')
            ax.set_title(os.path.basename(node.seq_file_path).split('.')[0])

    def plot_single_system(self, file_path):
        opm = open_model(file_path)
        layout_plt = plt.figure(FigureClass=InteractiveLayout, opt_model=opm, 
                                do_draw_rays=False, do_draw_beams=False, 
                                do_draw_edge_rays=False, do_draw_ray_fans=False, 
                                do_paraxial_layout=False)
        ax = layout_plt.gca()
        ax.grid(False)
        ax.axis('off')
        ax.set_ylim(0, 0.5)
        layout_plt.plot()
        plt.xlim(0, 10)
        plt.ylim(-15, 15)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(layout_plt)
        buf.seek(0)
        return buf


    def plot_optical_system_tree(self, node=None, depth=0, col=0, axs=None):
        if node is None:
            node = self.root

        # Initialize at the root level
        if depth == 0:
            fig, axs = plt.subplots(self.count_nodes_at_depths(self.target_depths), 3, figsize=(30, 5))

        # Only plot nodes at specific depths
        if depth in self.target_depths:
            # Determine node type and correct column
            node_type = self.get_node_type(node)
            new_col = {'SP': 1, 'OptA': 0, 'OptB': 2}.get(node_type, 1)

            # Get the current row for this node type and depth
            row = self.row_counters[depth][node_type]
            self.plot_node(node, axs, row, new_col)

            # Increment the row counter for this node type and depth
            self.row_counters[depth][node_type] += 1

        # Recursively plot child nodes
        for child in node.children:
            self.plot_optical_system_tree(child, depth + 1, col, axs)

        # Show plot at root level
        if depth == 0:
            plt.tight_layout()
            plt.show()

    def get_node_type(self, node):
        """ Determine the type of node (SP, OptA, OptB) based on the filename. """
        if node.seq_file_path:
            if '_OptA' in node.seq_file_path:
                return 'OptA'
            elif '_OptB' in node.seq_file_path:
                return 'OptB'
            else:
                return 'SP'
        return 'Unknown'


    def count_nodes_at_depths(self, depths):
        """ Count the total number of unique rows needed at the specified depths. """
        total = 0
        for depth in depths:
            total += len(set([self.get_node_type(node) for node in self.all_nodes if node.depth == depth]))
        return total


    def find_optimized_nodes_at_depth(self, target_depth):
        optimized_nodes = [node for node in self.all_nodes if node.depth == target_depth and node.is_optimized]
        return optimized_nodes
    

    ################################# Print tree with all details for each nodes methods #################################


    def print_tree_with_system_states(self, node=None, depth=0):
        if node is None:
            if depth == 0:  # Print header and border only once at the start
                print_decorative_header()
            node = self.root

        # Print the tree structure with system state details
        self._print_node_with_state(node, depth)
        print_blank_line()

    def _print_node_with_state(self, node, depth):
        indent = " " * depth * 4
        seq_file = node.seq_file_path if node.seq_file_path else 'No file'
        merit_function = node.merit_function if node.merit_function else 'No merit function'
        efl = node.efl if node.efl else 'No efl'
        is_optimized = "Yes" if node.is_optimized else "No"
        node_info = f"{indent}Node Depth {depth} | Optimized: {is_optimized} | SEQ File: {seq_file} | Merit: {merit_function} | EFL: {efl}"
        print(node_info)

        # Print the optical system state
        if node.optical_system_state:
            self._print_optical_system_state(node.optical_system_state)
            print(node.optical_system_state)

        for child in node.children:
            self._print_node_with_state(child, depth + 1)

    def _print_optical_system_state(self, system_state):
        if system_state is None:
            print("No optical system state available.")
            return

        # Determine the maximum width required for each column
        max_radius_len = max((len(f"{params.get('radius', 'INFINITY'):.6f}") for params in system_state['surfaces'].values()), default=8)
        max_thickness_len = max((len(f"{params.get('thickness', 'INFINITY'):.6f}") for params in system_state['surfaces'].values()), default=8)
        max_material_len = max((len(params.get('material', 'None') or '') for params in system_state['surfaces'].values()), default=4)



        print("Optical System State:")
        print(f"System is in {system_state['mode']} mode.")
        header = f"    {'RDY':>{max_radius_len}}   {'THI':>{max_thickness_len}}   {'GLA':>{max_material_len}}    RMD   CCY   THC"
        print(header)

        last_surface_number = max(system_state['surfaces'].keys(), default=0)
        for surface_num, params in system_state['surfaces'].items():
            # Print the properties for each surface
            self._print_surface_properties(surface_num, params, max_radius_len, max_thickness_len, max_material_len)

        # Print the properties for the image surface
        self._print_surface_properties(last_surface_number + 1, {'radius': 'INFINITY', 'thickness': 0, 'material': None, 'radius_variable': False, 'thickness_variable': False}, max_radius_len, max_thickness_len, max_material_len, is_image=True)

        print("-" * 30)  # Separator

    def _print_surface_properties(self, surface_num, params, max_radius_len, max_thickness_len, max_material_len, is_image=False):
        radius = f"{params.get('radius', 'INFINITY'):.6f}" if isinstance(params.get('radius'), float) else str(params.get('radius', 'INFINITY'))
        thickness = f"{params.get('thickness', 'INFINITY'):.6f}" if isinstance(params.get('thickness'), float) else str(params.get('thickness', 'INFINITY'))
        material = params.get('material', 'None')
        material_str = f"{material:>{max_material_len}}" if material else " " * max_material_len
        radius_variable = "0" if params.get('radius_variable', False) else "100"
        thickness_variable = "0" if params.get('thickness_variable', False) else "100"

        label = "IMG:" if is_image else f"{surface_num:4}:"
        print(f"{label}{radius:>{max_radius_len}} {thickness:>{max_thickness_len}} {material_str} {radius_variable:>4}   {thickness_variable:>4}")


    ################################# Final optimisation #################################
        
    
    def final_optimization(self, system_setup, efl, base_file_path):
        """
        Perform final optimization on all nodes at the maximum depth of the tree.
        :param system_setup: Instance of SystemSetup class for performing optimization.
        :param efl: Effective focal length for optimization.
        :param base_file_path: Base path for saving optimized systems.
        """
        # Find the final depth of the tree
        final_depth = self.find_final_depth()

        # Find all optimized nodes at the final depth
        final_depth_nodes = self.find_optimized_nodes_at_depth(final_depth)

        for i, node in enumerate(final_depth_nodes):
            print(f"Optimizing Node {i+1}/{len(final_depth_nodes)} at Final Depth {final_depth}")

            # Load the state of the node into SystemSetup
            system_setup.load_system_parameters(node.optical_system_state)

            # Make all radii, thicknesses, and applicable materials variable for optimization
            system_setup.make_all_thicknesses_variable(last_one = False)
            system_setup.make_all_radii_variable()
            system_setup.make_all_materials_variable()

            # Perform optimization
            system_setup.optimize_system(efl, constrained=False)

            # Update and save the optimized state
            system_setup.update_all_surfaces_from_codev()
            optimized_state = system_setup.save_system_parameters()

            # Update the node's state and merit function
            node.optical_system_state = optimized_state
            node.merit_function = system_setup.error_fct(efl, constrained=False)

            # Save the optimized system
            optimized_file_path = f"{base_file_path}/FinalOptimized_Node{node.id}.seq"
            system_setup.save_system(optimized_file_path)
            node.seq_file_path = optimized_file_path

            # Print the merit function of the optimized system
            print(f"Node {node.id} Optimized: Merit Function: {node.merit_function}, Saved at: {optimized_file_path}")

    def find_final_depth(self):
        """
        Find the maximum depth of the tree.
        :return: The maximum depth among all nodes in the tree.
        """
        max_depth = 0
        for node in self.all_nodes:
            if node.depth > max_depth:
                max_depth = node.depth
        return max_depth
    

    def print_final_optimized_systems_table(self):
        """
        Print a fancy table of all final optimized systems, sorted by their merit function values.
        Includes additional interesting data for analysis. Handles cases where the merit function is
        'No merit function' and sorts accordingly.
        """
        final_depth = self.find_final_depth()
        final_depth_nodes = self.find_optimized_nodes_at_depth(final_depth)

        # Collect data for all final optimized systems
        optimized_systems_data = []
        for node in final_depth_nodes:
            parent_id = node.parent.id if node.parent else 'Root'
            num_children = len(node.children)
            merit_function = node.merit_function if isinstance(node.merit_function, float) else float('inf')  # Assign a high value for sorting
            optimized_systems_data.append({
                'Node ID': node.id,
                'Parent ID': parent_id,
                'Merit Function': merit_function if merit_function != float('inf') else "No merit function",
                'EFL': node.efl,
                'Children Count': num_children,
                'SEQ File Path': node.seq_file_path
            })

        # Sort the systems by merit function, placing 'No merit function' at the end
        optimized_systems_data.sort(key=lambda x: float('inf') if x['Merit Function'] == "No merit function" else x['Merit Function'])

        # Print the table header
        headers = ['Node ID', 'Parent ID', 'Merit Function', 'EFL', 'Children Count', 'SEQ File Path']
        header_line = " | ".join("{:<15}".format(header) for header in headers)
        print(header_line)
        print("-" * len(header_line))

        # Print each row in the table
        for system in optimized_systems_data:
            row_data = [system[header] for header in headers]
            row_data_formatted = []
            for data in row_data:
                # Format 'Merit Function' specifically to handle 'No merit function' text properly
                if headers == 'Merit Function' and data == "No merit function":
                    row_data_formatted.append("{:<15}".format(data))
                else:
                    row_data_formatted.append("{:<15}".format(str(data)))
            print(" | ".join(row_data_formatted))

        # Check if there are no systems to display
        if not optimized_systems_data:
            print("No optimized systems available at the final depth.")

