#src/cif_interface.py

import tkinter as tk
from tkinter import ttk, filedialog
from src.cif_parser import CIFParser

class CIFViewer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("3D Crystal Viewer")
        self.geometry("800x600")

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill='both', expand=True)

        self.create_menu()

    
    def create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Open CIF', command=self.open_file)
        menubar.add_cascade(label='File', menu=file_menu)
        self.config(menu=menubar)
    
    def open_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CIF files", "*.cif"), ("All files", "*.*")]
        )

        if filename:
       
            parser = CIFParser(filename)

            parsed_data = parser.parse_file()
            if parsed_data is None:
                print('Failed to parse file')
                return
            
            cell_params = parser.extract_cell_parameters()
            space_group = parser.extract_space_group()
            system_class = parser.extract_system_class()
            atomic_positions = parser.extract_atomic_positions()
            validate = parser.validate_cif()

            if cell_params:
                print("\nCell Parameters:")
                for param, value in cell_params.items():
                    print(f"{param}: {value}")
            else:
                print("No cell parameters found")

            if space_group:
                print("\nSpace Group:")
                for param, value in space_group.items():
                    print(f"{param}: {value}")
            else:
                print("No space group found")
            
            if system_class:
                print("\nSystem Class:")
                for param, value in system_class.items():
                    print(f"{param}: {value}")
            else:
                print("No system class found")

            if atomic_positions:
                print("\nAtomic Positions:")
                for param, value in atomic_positions.items():
                    print(f"{param}: {value}")
            else:
                print("No atomic positions found")
            
            if validate:
                print("\nCIF file has all required data")
            else:
                print("Missing data")