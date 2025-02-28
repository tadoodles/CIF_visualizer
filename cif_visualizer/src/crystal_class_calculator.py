#src/crystal_class_caculator.py

import numpy as np

def calculate_unit_cell_vertices(a, b, c, alpha, beta, gamma, space_group_number):
        
        cos_alpha = np.cos(alpha)
        cos_beta = np.cos(beta)
        cos_gamma = np.cos(gamma)
        sin_gamma = np.sin(gamma)

        # Calculate the volume factor for the triclinic system
        volume_factor = np.sqrt(
            1 - cos_alpha**2 - cos_beta**2 - cos_gamma**2 + 2 * cos_alpha * cos_beta * cos_gamma
        )

        # Calculate the unit cell vertices for a general triclinic system
        vertices = np.array([
            [0, 0, 0],  # origin
            [a, 0, 0],  # along a
            [a * cos_gamma, a * sin_gamma, 0],  # a + b in xy plane
            [0, b, 0],  # along b
            [c * cos_beta, c * (cos_alpha - cos_beta * cos_gamma) / sin_gamma, c * volume_factor / sin_gamma],  # along c
            [a + c * cos_beta, c * (cos_alpha - cos_beta * cos_gamma) / sin_gamma, c * volume_factor / sin_gamma],  # a + c
            [a * cos_gamma + c * cos_beta, a * sin_gamma + c * (cos_alpha - cos_beta * cos_gamma) / sin_gamma, c * volume_factor / sin_gamma],  # a + b + c
            [c * cos_beta, b + c * (cos_alpha - cos_beta * cos_gamma) / sin_gamma, c * volume_factor / sin_gamma],  # b + c
        ])

        # Define vertex adjustments for different space group ranges
        space_group_adjustments = {
            (1, 2): lambda: vertices,  # Triclinic
            (3, 15): lambda: vertices,  # Monoclinic
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
