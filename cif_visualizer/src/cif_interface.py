#src/cif_interface.py

from PyQt5.QtWidgets import QFrame, QWidget, QPushButton, QSpinBox, QVBoxLayout,QLabel, QMenuBar, QAction, QFileDialog, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt
from src.cif_parser import CIFParser
from src.cif_crystal_window import CrystalViewer

class CIFInterface(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.visualization_frame = QFrame(self)
        layout.addWidget(self.visualization_frame)

        self.crystal_viewer = CrystalViewer(self)
        layout.addWidget(self.crystal_viewer)

        supercell_layout = QHBoxLayout()

        supercell_label = QLabel("Add cells")
        supercell_label.setAlignment(Qt.AlignRight)
        supercell_layout.addWidget(supercell_label)

        #X repetition
        supercell_layout.addWidget(QLabel("X:"))
        self.x_repetition = QSpinBox()
        self.x_repetition.setMinimum(1)
        self.x_repetition.setValue(1)
        supercell_layout.addWidget(self.x_repetition)

        #Y repetition
        supercell_layout.addWidget(QLabel("Y:"))
        self.y_repetition = QSpinBox()
        self.y_repetition.setMinimum(1)
        self.y_repetition.setValue(1)
        supercell_layout.addWidget(self.y_repetition)

        #Z repetition
        supercell_layout.addWidget(QLabel("Z:"))
        self.z_repetition = QSpinBox()
        self.z_repetition.setMinimum(1)
        self.z_repetition.setValue(1)
        supercell_layout.addWidget(self.z_repetition)

        #Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_visualization)
        supercell_layout.addWidget(self.refresh_button)

        supercell_layout.addStretch()
        layout.addLayout(supercell_layout)

        self.create_menu()

    
    def create_menu(self):
        menubar = QMenuBar(self)
        file_menu = menubar.addMenu('File')
        open_action = QAction('Open CIF', self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        layout = self.layout()
        layout.setMenuBar(menubar)
        
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open CIF File",
            "",
            "CIF files (*.cif);;All Files (*)"
        )

        if filename:
            try:
                parser = CIFParser(filename)

                parsed_data = parser.parse_file()
                if parsed_data is None:
                    QMessageBox.critical(self, "Error", "Failed to parse file")
                    return
                
                self.cell_params = parser.extract_cell_parameters()
                self.space_group = parser.extract_space_group()
                self.system_class = parser.extract_system_class()
                self.atomic_positions = parser.extract_atomic_positions()
                self.space_group_number = parser.extract_spaceGroup_number()
                validate = parser.validate_cif()

                if self.cell_params:
                    print("\nCell Parameters:")
                    for param, value in self.cell_params.items():
                        print(f"{param}: {value}")
                else:
                    print("No cell parameters found")

                if self.space_group:
                    print("\nSpace Group:")
                    for param, value in self.space_group.items():
                        print(f"{param}: {value}")
                else:
                    print("No space group found")
                
                if self.system_class:
                    print("\nSystem Class:")
                    for param, value in self.system_class.items():
                        print(f"{param}: {value}")
                else:
                    print("No system class found")

                if self.atomic_positions:
                    print("\nAtomic Positions:")
                    for param, value in self.atomic_positions.items():
                        print(f"{param}: {value}")
                else:
                    print("No atomic positions found")

                if self.space_group_number:
                    print("\nSpace Group Number:", self.space_group_number)
                else:
                    print("No space_group_found")
                
                if validate:
                    print("\nCIF file has all required data")
                else:
                    print("Missing data")

                
                if self.cell_params and self.atomic_positions:
                    self.atom_list = self.crystal_viewer.convert_to_atom_list(self.atomic_positions)
                    for atom in self.atom_list:
                        frac_coords = (atom['x'], atom['y'], atom['z'])
                        cart_coords = self.crystal_viewer.fractional_to_cartesian(frac_coords, self.cell_params)
                        atom['cart_x'], atom['cart_y'], atom['cart_z'] = cart_coords
                    
                    repetitions = (
                        self.x_repetition.value(),
                        self.y_repetition.value(),
                        self.z_repetition.value()
                    )

                    self.crystal_viewer.visualize_structure(self.cell_params, self.atom_list, repetitions, self.space_group_number)
                else:
                    QMessageBox.warning(self, "Warning", "Insufficient data to visualize the crystal structure")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error processing file: {str(e)}")
    
    def refresh_visualization(self):
        """
        Refresh the visualization with the current repetition values.
        """
        if not hasattr(self, 'cell_params') or not hasattr(self, 'atom_list'):
            QMessageBox.warning(self, "Warning", "No file has been opened yet.")
            return

        repetitions = (
            self.x_repetition.value(),
            self.y_repetition.value(),
            self.z_repetition.value()
        )


        # Check if the repetitions are too large
        if repetitions[0] > 5 or repetitions[1] > 5 or repetitions[2] > 5:
            QMessageBox.warning(self, "Warning", "Large repetitions may impact performance. Consider using smaller values.")
        
        # Generate supercell atomic positions
        super_atomic_positions = self.crystal_viewer.generate_supercell_atomic_positions(
            self.atom_list, repetitions, 
            self.cell_params['_cell_length_a'], 
            self.cell_params['_cell_length_b'], 
            self.cell_params['_cell_length_c']
        )

        # Re-apply the visualization with the new repetitions
        self.crystal_viewer.visualize_structure(self.cell_params, super_atomic_positions, repetitions, self.space_group_number)