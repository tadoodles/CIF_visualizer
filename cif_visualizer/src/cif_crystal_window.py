# src/cif_crystal_window.py
import re
import pyvista as pv
from pyvistaqt import QtInteractor
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from src.constants import element_colors

class CrystalViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        
        # Initialize the plotter
        self.plotter = QtInteractor(self)  # Pass self as parent
        layout.addWidget(self.plotter)

        self.setup_plotter()

    def setup_plotter(self):
        self.plotter.background_color = 'white'
        self.plotter.enable_trackball_style()
        self.plotter.show_axes()
        self.plotter.add_axes()
    
    def visualize_structure(self, cell_params, atomic_positions, repetitions=(1, 1, 1), space_group_number=None):
        """
        Visualize the crystal structure based on cell parameters and atomic positions.

        Args:
            cell_params: dictionary containing cell params: a, b, c, alpha, beta, gamma
            atomic_positions: list of dictionaries containing atomic positions and properties        
        """
        self.plotter.clear()


        #extract cell paramas
        a = cell_params.get('_cell_length_a', 1.0)
        b = cell_params.get('_cell_length_b', 1.0)
        c = cell_params.get('_cell_length_c', 1.0)
        alpha_rad = np.radians(cell_params.get('_cell_angle_alpha', 90.0))
        beta_rad = np.radians(cell_params.get('_cell_angle_beta', 90.0))
        gamma_rad = np.radians(cell_params.get('_cell_angle_gamma', 90.0))

        #print cell params for debugging
        print(f"Cell parameters: a={a}, b={b}, c={c}")
        print(f"Angles: alpha={alpha_rad}, beta={beta_rad}, gamma={gamma_rad}")

        #calculate unit cell vertices
        vertices = self.calculate_unit_cell_vertices(a, b, c, alpha_rad, beta_rad, gamma_rad, space_group_number)

        print("Unit cell vertices:")
        for v in vertices:
            print(v)

        #visualize the unit cell
        self.visualize_unit_cell(vertices)

        if repetitions != (1, 1, 1):
            supercell_atomic_positions = self.generate_supercell_atomic_positions(atomic_positions, repetitions, a, b, c)
            self.visualize_supercell_unit_cells(vertices, repetitions, a, b, c)
        else:
            supercell_atomic_positions = atomic_positions

        #visualize atomic positions
        self.visualize_atomic_positions(supercell_atomic_positions)
    
    def visualize_unit_cell(self, vertices, color='black', line_width=2):
        """
        
        """
        lines = []
        edge_pairs = [
            [0, 1], [1, 2], [2, 3], [3, 0], #bottom face
            [4, 5], [5, 6], [6, 7], [7, 4], #top face
            [0, 4], [1, 5], [2, 6], [3, 7], #vertical edges
        ]

        for edge in edge_pairs:
            lines.extend([2, edge[0], edge[1]])

        unit_cell = pv.PolyData(vertices, lines=np.array(lines))
        self.plotter.add_mesh(unit_cell, color=color, line_width=line_width)
    
    def visualize_atomic_positions(self, atomic_positions):
        """
        Visualize atoms as spheres at their positions
        """
        default_color = 'lightgrey'

        for atom in atomic_positions:

            label = atom.get('label', atom.get('element', atom.get('type', '')))
            element = self.extract_element(label)

            # Check if atom is a dictionary
            if not isinstance(atom, dict):
                continue
            
            if element.upper() == 'H':
                continue
                
            # Get coordinates with proper error handling
            try:
                x = float(atom.get('cart_x', 0.0))
                y = float(atom.get('cart_y', 0.0))
                z = float(atom.get('cart_z', 0.0))

                radius = float(atom.get('radius', 0.5))
                color = element_colors.get(element, default_color)
                
                sphere = pv.Sphere(radius=radius, center=(x, y, z))
                self.plotter.add_mesh(sphere, color=color)

                
            except (ValueError, TypeError) as e:
                print(f"Error processing atom: {atom}, error: {e}")
    
    def extract_element(self, label):
        # Try to match standard element symbols (1 or 2 characters)
        element_match = re.match(r'([A-Z][a-z]?)', label)
        if element_match:
            return element_match.group(1)
        else:
            # Fallback to extracting only the alphabetic characters
            return ''.join(c for c in label if c.isalpha())
    
    def convert_to_atom_list(self, atomic_data):
        """
        Convert data from parallel arrays to a list of atom dictionaries
        """
        atom_list = []
        
        # Get the number of atoms (length of any array)
        num_atoms = len(atomic_data.get('labels', []))
        
        # Create a dictionary for each atom
        for i in range(num_atoms):
            atom = {
                'label': atomic_data.get('labels', [])[i] if i < len(atomic_data.get('labels', [])) else None,
                'x': float(atomic_data.get('x', [])[i]) if i < len(atomic_data.get('x', [])) else 0.0,
                'y': float(atomic_data.get('y', [])[i]) if i < len(atomic_data.get('y', [])) else 0.0,
                'z': float(atomic_data.get('z', [])[i]) if i < len(atomic_data.get('z', [])) else 0.0,
                'U': float(atomic_data.get('U', [])[i]) if i < len(atomic_data.get('U', [])) else 0.0,
            }
            atom_list.append(atom)
        
        return atom_list
    
    def fractional_to_cartesian(self, frac_coords, cell_params):
        """
        Convert fractional coordinates to cartesian coordinates
        
        Parameters:
        frac_coords (tuple): x, y, z in fractional coordinates
        cell_params (dict): Contains a, b, c, alpha, beta, gamma
        
        Returns:
        tuple: x, y, z in cartesian coordinates
        """
        a = float(cell_params['_cell_length_a'])
        b = float(cell_params['_cell_length_b'])
        c = float(cell_params['_cell_length_c'])
        alpha = float(cell_params['_cell_angle_alpha'])
        beta = float(cell_params['_cell_angle_beta'])
        gamma = float(cell_params['_cell_angle_gamma'])
        
        # Convert angles from degrees to radians
        alpha_rad = np.radians(alpha)
        beta_rad = np.radians(beta)
        gamma_rad = np.radians(gamma)
        
        # Calculate the transformation matrix
        v1 = np.array([a, 0, 0])
        v2 = np.array([b * np.cos(gamma_rad), b * np.sin(gamma_rad), 0])
        
        cx = c * np.cos(beta_rad)
        cy = c * (np.cos(alpha_rad) - np.cos(beta_rad) * np.cos(gamma_rad)) / np.sin(gamma_rad)
        cz = np.sqrt(c**2 - cx**2 - cy**2)
        
        v3 = np.array([cx, cy, cz])
        
        # Apply transformation
        x_frac, y_frac, z_frac = frac_coords
        cart_coords = x_frac * v1 + y_frac * v2 + z_frac * v3
        
        return cart_coords
    
    def generate_supercell_atomic_positions(self, atomic_positions, repetitions, a, b, c):
        """
        
        """
        supercell_atomic_positions = []
        for i in range(repetitions[0]):
            for j in range(repetitions[1]):
                for k in range(repetitions[2]):
                    for atom in atomic_positions:
                        new_atom = atom.copy()
                        new_atom['cart_x'] = atom['cart_x'] + i * a
                        new_atom['cart_y'] = atom['cart_y'] + j * b
                        new_atom['cart_z'] = atom['cart_z'] + k * c
                        supercell_atomic_positions.append(new_atom)

        return supercell_atomic_positions

    def visualize_supercell_unit_cells(self, vertices, repetitions, a, b, c):
        """
        Visualize individual unit cells in the supercell.

        Args:
            vertices (np.array): Vertices of the original unit cell.
            repetitions (tuple): Number of repetitions in the x, y, and z directions.
            a (float): Length of the unit cell in the x direction.
            b (float): Length of the unit cell in the y direction.
            c (float): Length of the unit cell in the z direction.
        """
        for i in range(repetitions[0]):
            for j in range(repetitions[1]):
                for k in range(repetitions[2]):
                    translation = np.array([i * a, j * b, k * c])
                    translated_vertices = vertices + translation
                    self.visualize_unit_cell(translated_vertices, color='gray', line_width=1)

    def calculate_unit_cell_vertices(self, a, b, c, alpha, beta, gamma, space_group_number):
            
            cos_alpha = np.cos(alpha)
            cos_beta = np.cos(beta)
            sin_beta = np.sin(beta)
            cos_gamma = np.cos(gamma)
            sin_gamma = np.sin(gamma)

            # Calculate the volume factor for the triclinic system
            volume_factor = np.sqrt(
                1 - cos_alpha**2 - cos_beta**2 - cos_gamma**2 + 2 * cos_alpha * cos_beta * cos_gamma
            )

            # Calculate the unit cell vertices for a general triclinic system
            vertices = np.array([
                [0, 0, 0],  # origin (0)
                [a, 0, 0],  # along a (1)
                [a + b * cos_gamma, b * sin_gamma, 0],  # a + b (2)
                [b * cos_gamma, b * sin_gamma, 0],  # along b (3)
                [c * cos_beta, c * (cos_alpha - cos_beta * cos_gamma) / sin_gamma, c * volume_factor / sin_gamma],  # along c (4)
                [a + c * cos_beta, c * (cos_alpha - cos_beta * cos_gamma) / sin_gamma, c * volume_factor / sin_gamma],  # a + c (5)
                [a + b * cos_gamma + c * cos_beta, b * sin_gamma + c * (cos_alpha - cos_beta * cos_gamma) / sin_gamma, c * volume_factor / sin_gamma],  # a + b + c (6)
                [b * cos_gamma + c * cos_beta, b * sin_gamma + c * (cos_alpha - cos_beta * cos_gamma) / sin_gamma, c * volume_factor / sin_gamma]  # b + c (7)
            ])

            # Define vertex adjustments for different space group ranges
            space_group_adjustments = {
                (1, 2): lambda: vertices,  # Triclinic
                (3, 15): lambda: np.array([
                    [0, 0, 0],                  # origin
                    [a, 0, 0],                  # along a
                    [a, b, 0],                  # a + b
                    [0, b, 0],                  # along b
                    [c * cos_beta, 0, c * sin_beta],            # along c
                    [a + c * cos_beta, 0, c * sin_beta],        # a + c
                    [a + c * cos_beta, b, c * sin_beta],        # a + b + c
                    [c * cos_beta, b, c * sin_beta]             # b + c
                ]),  # Monoclinic
                (16, 74): lambda: np.array([  # Orthorhombic
                    [0, 0, 0],
                    [a, 0, 0],
                    [a, b, 0],
                    [0, b, 0],
                    [0, 0, c],
                    [a, 0, c],
                    [a, b, c],
                    [0, b, c],
                ]),
                (75, 142): lambda: np.array([  # Tetragonal
                    [0, 0, 0],
                    [a, 0, 0],
                    [a, a, 0],
                    [0, a, 0],
                    [0, 0, c],
                    [a, 0, c],
                    [a, a, c],
                    [0, a, c],
                ]),
                (143, 194): lambda: np.array([  # Hexagonal/Trigonal
                    [0, 0, 0],
                    [a, 0, 0],
                    [a / 2, a * np.sqrt(3) / 2, 0],
                    [-a / 2, a * np.sqrt(3) / 2, 0],
                    [0, 0, c],
                    [a, 0, c],
                    [a / 2, a * np.sqrt(3) / 2, c],
                    [-a / 2, a * np.sqrt(3) / 2, c],
                ]),
                (195, 230): lambda: np.array([  # Cubic
                    [0, 0, 0],
                    [a, 0, 0],
                    [a, a, 0],
                    [0, a, 0],
                    [0, 0, a],
                    [a, 0, a],
                    [a, a, a],
                    [0, a, a],
                ]),
            }

            # Apply adjustments based on space group number
            if space_group_number is not None:
                for (start, end), adjustment in space_group_adjustments.items():
                    if start <= space_group_number <= end:
                        vertices = adjustment()
                        break
                else:
                    print(f"Warning: Space group number {space_group_number} is not recognized.")

            return vertices