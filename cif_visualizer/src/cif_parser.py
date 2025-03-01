#src/cif_parser.py
from src.constants import space_group_dict

class CIFParser:
    def __init__(self, filename):
        self.filename = filename
        self.data = {}

    def parse_file(self):
        try:
                with open(self.filename, 'r') as file:
                    header_collection_phase = False
                    in_loop = False
                    loop_headers = []
                    loop_data = []

                    for line in file:
                        line = line.strip()

                        if line.startswith('#') or line.startswith(';'):
                            continue
                        
                        if line.startswith('_') and not in_loop:
                            parts = line.split(None, 1)
                            if len(parts) == 2:
                                key, value = parts
                                self.data[key] = value
                            else:
                                continue

                        if line.startswith('loop_'):
                            if in_loop:
                                result = self.process_loop(loop_headers, loop_data)
                                if 'loops' not in self.data:
                                    self.data['loops'] = []
                                self.data['loops'].append(result)

                            in_loop = True
                            loop_data = []
                            loop_headers = []
                            header_collection_phase = True
                            continue

                        if in_loop:
                            if line.startswith('_'):
                                if header_collection_phase:
                                    loop_headers.append(line)
                                else:
                                    result = self.process_loop(loop_headers, loop_data)
                                    if 'loops' not in self.data:
                                        self.data['loops'] = []
                                    self.data['loops'].append(result)

                                    in_loop = False
                                    loop_data = []
                                    loop_headers = []
                                    
                                    # Process this as a new data item
                                    if len(line.split()) > 1:
                                        key, value = line.split(None, 1)
                                        self.data[key] = value
                                    else:
                                        continue
                            else: 
                                if header_collection_phase:
                                    header_collection_phase = False
                                                              
                                values = self.parse_line(line)
                                if len(values) != len(loop_headers):  # If values don't match headers
                                    result = self.process_loop(loop_headers, loop_data)
                                    if 'loops' not in self.data:
                                        self.data['loops'] = []
                                    self.data['loops'].append(result)
                                    in_loop = False
                                else:
                                    loop_data.append(values)

                    if in_loop and loop_data:
                        result = self.process_loop(loop_headers, loop_data)
                        if 'loops' not in self.data:
                            self.data['loops'] = []
                        self.data['loops'].append(result)

                    return self.data
                
        except FileNotFoundError:
            print(f"Error: File {self.filename} not found")
            return None 

    def process_loop(self, headers, data):
            loop_dict = {}
            for header in headers:
                loop_dict[header] = []
            for row in data:
                for col_index, value in enumerate(row):
                    current_header = headers[col_index]
                    loop_dict[current_header].append(value)

            return loop_dict                      
       
    def extract_cell_parameters(self):
        cell_parameters = {}

        cell_parameters_enum = ['_cell_length_a',
                                '_cell_length_b',
                                '_cell_length_c',
                                '_cell_angle_alpha',
                                '_cell_angle_beta',
                                '_cell_angle_gamma'
                            ]
        
        try:
            for param in cell_parameters_enum:
                if param in self.data:
                    cell_parameters[param] = self.clean_value(self.data[param])
                
            if 'loops' in self.data:
                for loop in self.data['loops']:
                    for param in cell_parameters_enum:
                        if param not in cell_parameters and param in loop:
                            cell_parameters[param] = self.clean_value(loop[param][0])

            return cell_parameters
        except Exception as e:
            print(f"Error extracting cell parameters: {e}")
            return None

    def extract_space_group(self):
        space_group = {}

        params = ['_symmetry_space_group_name_H-M',
                '_space_group_name_H-M_alt',
                '_space_group_name_Hall'
                ]

        try:
            for param in params:
                if param in self.data:
                    value = self.data[param].strip("'").replace(' ', '')
                    space_group[param] = value
            
            if 'loops' in self.data:
                for loop in self.data['loops']:
                        if param not in space_group and param in loop:
                            value = loop[param][0].strip("'").replace(' ', '')
                            space_group[param] = value

            return space_group if space_group else None       
        except Exception as e:
            print(f"Error extracting space group: {e}")
            return None          

    def extract_system_class(self):
        system_class = {}

        params = ['_symmetry_cell_setting']

        try:
            for param in params:
                if param in self.data:
                    system_class[param] = self.data[param]
            
            if 'loops' in self.data:
                for loop in self.data['loops']:
                        if param not in system_class and param in loop:
                            system_class[param]  = loop[param]

            return system_class if system_class else None       
        except Exception as e:
            print(f"Error extracting space group: {e}")
            return None
    
    def extract_atomic_positions(self):

        atomic_positions = {
            'labels': [],
            'x': [],
            'y': [],
            'z': [],
            'U': []
        }

        required_params = [ '_atom_site_label',
                            '_atom_site_fract_x',
                            '_atom_site_fract_y',
                            '_atom_site_fract_z'                                   
                            ]
        
        optional_param = '_atom_site_U_iso_or_equiv'

        try:
            for loop in self.data['loops']:
                if all(param in loop for param in required_params):

                    num_atoms = len(loop[required_params[0]])

                    for i in range(num_atoms):
                        atomic_positions['labels'].append(loop['_atom_site_label'][i])
                        atomic_positions['x'].append(self.clean_value(loop['_atom_site_fract_x'][i]))
                        atomic_positions['y'].append(self.clean_value(loop['_atom_site_fract_y'][i]))
                        atomic_positions['z'].append(self.clean_value(loop['_atom_site_fract_z'][i]))

                        if optional_param in loop:
                            atomic_positions['U'].append(self.clean_value(loop[optional_param][i]))
                        else:
                            atomic_positions['U'].append(0)                       
            
            return atomic_positions

        except Exception as e:
            print(f"Error extracting atomic positions: {e}")
            return None

    def validate_cif(self):
        return (self.extract_atomic_positions() and
                self.extract_cell_parameters() and
                self.extract_space_group())

    def clean_value(self, value):
            if '(' in value:
                value = value.split('(')[0]
            return float(value)
    
    def parse_line(self, line):
        values = []
        current_value = []
        in_quotes = False
        
        for char in line:
            if char == "'":
                in_quotes = not in_quotes
                current_value.append(char)
            elif char.isspace() and not in_quotes:
                if current_value:
                    values.append(''.join(current_value).strip())
                    current_value = []
            else:
                current_value.append(char)
        
        if current_value:
            values.append(''.join(current_value).strip())
        
        return values
    
    def extract_spaceGroup_number(self):
        space_group_data = self.extract_space_group()

        if '_symmetry_space_group_name_H-M' in space_group_data:
            space_group_symbol = space_group_data['_symmetry_space_group_name_H-M']
        elif '_space_group_name_H-M_alt' in space_group_data:
            space_group_symbol = space_group_data['_space_group_name_H-M_alt']

        if space_group_symbol in space_group_dict:
            return space_group_dict[space_group_symbol]
        else:
            print(f"Warning: Space group '{space_group_symbol}' not found in dictionary.")
            return None 

