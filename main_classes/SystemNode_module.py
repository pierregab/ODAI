import matplotlib.pyplot as plt
import matplotlib.patches as patches
from rayoptics.environment import InteractiveLayout, open_model
import io
import os
import numpy as np
from affichage import print_decorative_header, print_blank_line
import re

class SystemNode:
  def __init__(self, system_params, optical_system_state=None,seq_file_path=None, parent=None, merit_function=None, efl = None, is_optimized=False, depth=0, high_debuging=False):
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

  def parse_seq_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    seq_data = {}
    surface_pattern = r"S\s+([-\d\.Ee\+\-]+)\s+([-\d\.Ee\+\-]+)\s+(\w+)"

    for line in lines:
        # Check for surface data
        match = re.match(surface_pattern, line.strip())
        if match:
            radius, thickness, material = match.groups()
            radius = float(radius)
            curvature = 1 / radius if radius != 0 else 0
            seq_data[f"S{len(seq_data)}"] = {
                'radius': radius,
                'curvature': curvature,
                'thickness': float(thickness),
                'material': material
            }

    return seq_data
  
  def compare_systems(node_state, seq_data):
    discrepancies = []
    for surface_num, surface in node_state['surfaces'].items():
        seq_surface = seq_data.get(surface_num)
        if not seq_surface:
            discrepancies.append(f"Surface {surface_num} not found in SEQ data")
            continue

        # Compare radius or curvature based on the mode
        if node_state['mode'] == 'radius':
            if surface['radius'] != seq_surface['radius']:
                discrepancies.append(f"Surface {surface_num} radius mismatch: Node {surface['radius']} vs SEQ {seq_surface['radius']}")
        elif node_state['mode'] == 'curvature':
            if surface['curvature'] != seq_surface['curvature']:
                discrepancies.append(f"Surface {surface_num} curvature mismatch: Node {surface['curvature']} vs SEQ {seq_surface['curvature']}")

        if surface['thickness'] != seq_surface['thickness']:
            discrepancies.append(f"Surface {surface_num} thickness mismatch: Node {surface['thickness']} vs SEQ {seq_surface['thickness']}")
        if surface['material'] != seq_surface['material']:
            discrepancies.append(f"Surface {surface_num} material mismatch: Node {surface['material']} vs SEQ {seq_surface['material']}")

    return discrepancies


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
