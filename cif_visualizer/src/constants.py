#src/constants.py

element_colors = {
        'H': 'black',
        'C': 'red',
        'N': 'yellow',
        'O': 'blue',
        'S': 'white',
        'P': 'green',
        'F': 'pink',
        'Cl': 'green',
        'Br': 'brown',
        'I': 'purple',
        'Te': 'darkgoldenrod',
        'Cu': 'copper',
        'Na': 'purple',
        'K': 'purple',
        'Mg': 'forestgreen',
        'Ca': 'darkgrey',
        'Zn': 'skyblue',
        'Fe': 'orange',
        # Add more elements as needed
    }

space_group_dict = {
        "P1": 1, "P-1": 2, "P21/c": 14, "C2/c": 15, "P212121": 19,
        "P21212": 18, "Pna21": 33, "Pca21": 29, "Pbca": 61, 
        "Pbcn": 60, "P21/m": 11, "C2/m": 12, "P2/c": 13,
        "P1": 1, "P2": 3, "P21": 4, "C2": 5, "Pm": 6,
        "Pc": 7, "Cm": 8, "Cc": 9, "P2/m": 10,
        "Pnma": 62, "Cmcm": 63, "Cmca": 64,
        "P4/mmm": 123, "P4/nmm": 129, "Fm-3m": 225,
        "R-3c": 167, "R-3": 148, "R-3m": 166, "P63mc": 186, "P63/mmc": 186, "P121/n1": 14
        # Add other common space groups as needed
    }

covalent_radii = {
            'H': 0.31,
            'C': 0.76,
            'N': 0.71,
            'O': 0.66,
            'F': 0.57,
            'P': 1.07,
            'S': 1.05,
            'Cl': 1.02,
            'Br': 1.20,
            'I': 1.39,
            #add other atoms as needed
        }

    