#src/cif_interface.py

from PyQt5.QtWidgets import QFrame, QWidget, QDialog, QPushButton, QSpinBox, QVBoxLayout,QLabel, QMenuBar, QAction, QFileDialog, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt
from src.cif_parser import CIFParser
from src.cif_crystal_window import CrystalViewer

class CIFInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):

        main_layout = QHBoxLayout(self)

        content_layout = QVBoxLayout()

        self.setup_visualization_frame(content_layout)
        self.setup_crystal_viewer(content_layout)
        self.setup_supercell_controls(content_layout)
        main_layout.addLayout(content_layout)

        self.setup_parameter_sidebar(main_layout)

        self.setLayout(main_layout)      
        self.create_menu()
    
    def setup_visualization_frame(self, layout):

        self.visualization_frame = QFrame(self)
        layout.addWidget(self.visualization_frame)
    
    def setup_crystal_viewer(self, layout):

        self.crystal_viewer = CrystalViewer(self)
        layout.addWidget(self.crystal_viewer)
    
    def setup_supercell_controls(self, layout):

        supercell_layout = QHBoxLayout()

        self.add_supercell_label(supercell_layout)

        self.add_repetition_spin_boxes(supercell_layout)

        self.add_refresh_button(supercell_layout)

        supercell_layout.addStretch()
        layout.addLayout(supercell_layout)

    def add_supercell_label(self, layout):

        supercell_label = QLabel("Add cells")
        supercell_label.setAlignment(Qt.AlignRight)
        layout.addWidget(supercell_label)
    
    def add_repetition_spin_boxes(self, layout):

        #X repetition
        layout.addWidget(QLabel("X:"))
        self.x_repetition = QSpinBox()
        self.x_repetition.setMinimum(1)
        self.x_repetition.setValue(1)
        layout.addWidget(self.x_repetition)

        #Y repetition
        layout.addWidget(QLabel("Y:"))
        self.y_repetition = QSpinBox()
        self.y_repetition.setMinimum(1)
        self.y_repetition.setValue(1)
        layout.addWidget(self.y_repetition)

        #Z repetition
        layout.addWidget(QLabel("Z:"))
        self.z_repetition = QSpinBox()
        self.z_repetition.setMinimum(1)
        self.z_repetition.setValue(1)
        layout.addWidget(self.z_repetition)
    
    def add_refresh_button(self, layout):

        #Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_visualization)
        layout.addWidget(self.refresh_button)
    
    def create_menu(self):
        menubar = QMenuBar(self)
        file_menu = menubar.addMenu('File')
        open_action = QAction('Open CIF', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        layout = self.layout()
        layout.setMenuBar(menubar)
    
    def setup_parameter_sidebar(self, layout):
        
        self.sidebar = QFrame(self)
        self.sidebar.setFrameShape(QFrame.StyledPanel)
        self.sidebar.setFixedWidth(200)  
        sidebar_layout = QVBoxLayout(self.sidebar)

        sidebar_title = QLabel("Unit Cell Parameters")
        sidebar_title.setAlignment(Qt.AlignCenter)
        sidebar_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        sidebar_layout.addWidget(sidebar_title)

        self.a_label = QLabel("a: N/A")
        self.b_label = QLabel("b: N/A")
        self.c_label = QLabel("c: N/A")
        self.alpha_label = QLabel("α: N/A")
        self.beta_label = QLabel("β: N/A")
        self.gamma_label = QLabel("γ: N/A")

        sidebar_layout.addWidget(self.a_label)
        sidebar_layout.addWidget(self.b_label)
        sidebar_layout.addWidget(self.c_label)
        sidebar_layout.addWidget(self.alpha_label)
        sidebar_layout.addWidget(self.beta_label)
        sidebar_layout.addWidget(self.gamma_label)

        sidebar_layout.addStretch()

        layout.addWidget(self.sidebar)
        
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
                self.update_sidebar(self.cell_params)
                self.space_group = parser.extract_space_group()
                self.system_class = parser.extract_system_class()
                self.atomic_positions = parser.extract_atomic_positions()
                self.space_group_number = parser.extract_spaceGroup_number()
                #validate = parser.validate_cif()

                """if self.cell_params:
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
                    print("Missing data")"""

                
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

        if not hasattr(self, 'cell_params') or not hasattr(self, 'atom_list'):
            QMessageBox.warning(self, "Warning", "No file has been opened yet.")
            return

        repetitions = (
            self.x_repetition.value(),
            self.y_repetition.value(),
            self.z_repetition.value()
        )


        # Check if the repetitions are too large
        if repetitions[0] > 4 or repetitions[1] > 4 or repetitions[2] > 4: #set to 4 for performance's sake
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

    def update_sidebar(self, cell_params):
        
        if cell_params:
            self.a_label.setText(f"a: {cell_params.get('_cell_length_a', 'N/A')} Å")
            self.b_label.setText(f"b: {cell_params.get('_cell_length_b', 'N/A')} Å")
            self.c_label.setText(f"c: {cell_params.get('_cell_length_c', 'N/A')} Å")
            self.alpha_label.setText(f"α: {cell_params.get('_cell_angle_alpha', 'N/A')}°")
            self.beta_label.setText(f"β: {cell_params.get('_cell_angle_beta', 'N/A')}°")
            self.gamma_label.setText(f"γ: {cell_params.get('_cell_angle_gamma', 'N/A')}°")
        else:
            self.a_label.setText("a: N/A")
            self.b_label.setText("b: N/A")
            self.c_label.setText("c: N/A")
            self.alpha_label.setText("α: N/A")
            self.beta_label.setText("β: N/A")
            self.gamma_label.setText("γ: N/A")