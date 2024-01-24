import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


class aircraft:
    def __init__(self, design_type):

        self.component_dict = {
            'payload': {'weight': 3, 'dimensions': (2, 3.5), 'color': 'black'},
            'RmleicNB20': {'weight': 0.11, 'dimensions': (4.5, 2.5), 'color': 'dodgerblue'},
            'Reciever JettiDuplex System': {'weight': 0.05, 'dimensions': (2, 1.1), 'color': 'pink'},
            'Here2 GPS': {'weight': 0.1, 'dimensions': (3, 3), 'color': 'limegreen'},
            'Orange Box': {'weight': 0.16, 'dimensions': (3.75, 1.75), 'color': 'darkorange'},
            'Fuel': {'weight': 1, 'dimensions': (7, 12), 'color': 'gold'},
            'Battery': {'weight': 0.3, 'dimensions': (4.13, 1.34), 'color': 'crimson'},
            'Fuel Pump': {'weight': 0.3, 'dimensions': (0.75, 1.5), 'color': 'darkgoldenrod'},
            'ECU': {'weight': 0.2, 'dimensions': (3.42, 2.05), 'color': 'blue'},
            'Engine': {'weight':1.6, 'dimensions': (3, 7.2), 'color': 'gray'},
            'Wing': {'weight': 2, 'dimensions': (80,6), 'color': 'purple'},
            'Tail': {'weight': 1, 'dimensions': (20,6), 'color': 'purple'}
        }

        def traditional_location():
            self.component_dict['payload']['location'] = [0,2.25]
            self.component_dict['RmleicNB20']['location'] = [0,5.5]
            self.component_dict['Reciever JettiDuplex System']['location'] = [0,23]
            self.component_dict['Here2 GPS']['location'] = [0,5.5]
            self.component_dict['Orange Box']['location'] = [0,24]
            self.component_dict['Fuel']['location'] = [0, 14]
            self.component_dict['Battery']['location'] = [0, 29]
            self.component_dict['Fuel Pump']['location'] = [0, 27]
            self.component_dict['ECU']['location'] = [0,29]
            self.component_dict['Engine']['location'] = [0, 36.5]
            self.component_dict['Wing']['location'] = [0, 20]
            

        def canard_location():
            self.component_dict['payload']['location'] = [0,4.5]
            self.component_dict['RmleicNB20']['location'] = [0,9]
            self.component_dict['Reciever JettiDuplex System']['location'] = [0,1]
            self.component_dict['Here2 GPS']['location'] = [0,9]
            self.component_dict['Orange Box']['location'] = [0,12.5]
            self.component_dict['Fuel']['location'] = [0, 24]
            self.component_dict['Battery']['location'] = [0, 33]
            self.component_dict['Fuel Pump']['location'] = [0,14.5]
            self.component_dict['ECU']['location'] = [0, 36.5]
            self.component_dict['Engine']['location'] = [0, 40]
            self.component_dict['Wing']['location'] = [0, 34]

        def traditional_location_board():
            self.component_dict['payload']['location'] = [0,4]
            self.component_dict['RmleicNB20']['location'] = [0,7.25]
            self.component_dict['Reciever JettiDuplex System']['location'] = [0,28.5]
            self.component_dict['Here2 GPS']['location'] = [0,7]
            self.component_dict['Orange Box']['location'] = [0,28.5]
            self.component_dict['Fuel']['location'] = [0, 14]
            self.component_dict['Battery']['location'] = [0, 25.25]
            self.component_dict['Fuel Pump']['location'] = [0, 20]
            self.component_dict['ECU']['location'] = [0,25.25]
            self.component_dict['Engine']['location'] = [0, 33]
            self.component_dict['Wing']['location'] = [0, 18]

        def new_traditional_design():
            self.component_dict['payload']['location'] = [0,4]
            self.component_dict['RmleicNB20']['location'] = [0,11]
            self.component_dict['Reciever JettiDuplex System']['location'] = [0,4]
            self.component_dict['Here2 GPS']['location'] = [0,8]
            self.component_dict['Orange Box']['location'] = [0,4]
            self.component_dict['Fuel']['location'] = [0, 18.5]
            self.component_dict['Battery']['location'] = [0, 11]
            self.component_dict['Fuel Pump']['location'] = [0, 25.5]
            self.component_dict['ECU']['location'] = [0,8]
            self.component_dict['Engine']['location'] = [0, 34.25]
            self.component_dict['Wing']['location'] = [0, 18.5]
            self.component_dict['Tail']['location'] = [0, 38.5]

        if design_type == 'traditional':
            traditional_location()
        elif design_type == 'canard':
            canard_location()
        elif design_type == 'board':
            traditional_location_board()
        elif design_type == 'new':
            new_traditional_design()


        for key, component in self.component_dict.items():
            component_x_cg, component_y_cg = 0, 0
            print(component)
            loc = component['location'] if isinstance(component['location'][0], (list, set)) else [component['location']]
            for location in loc:
                component_x_cg += location[0]/len(loc)
                component_y_cg += location[1]/len(loc)

            self.component_dict[key]['cg'] = (component_x_cg, component_y_cg)

        x_cg_num = 0
        y_cg_num = 0
        mass_tot = 0

        for value in self.component_dict.values():
            x_cg_num += (value['cg'][0] * value['weight'])
            y_cg_num += (value['cg'][1] * value['weight'])
            mass_tot += value['weight']
            self.x_cg = x_cg_num/mass_tot
            self.y_cg = y_cg_num/mass_tot
        print(mass_tot)
        print(self.x_cg)
        print(self.y_cg)

        self.draw_rectangles()
        
    def draw_rectangles(self):
        fig, ax = plt.subplots()

        for component_name, component in self.component_dict.items().__reversed__():
            x, y = component['cg'][0], component['cg'][1]
            width, height = component['dimensions']

            # Draw rectangle
            ax.add_patch(Rectangle((component['cg'][0] - component['dimensions'][0]/2, component['cg'][1] - component['dimensions'][1]/2),
                component['dimensions'][0],
                component['dimensions'][1],
                facecolor = component['color'],
                fill=True))

            # Print component name next to the rectangle
            ax.text(x + 8, y, component_name, fontsize=8, verticalalignment='center')

        ax.set_aspect('equal', adjustable='box')  # Ensure equal scaling
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.title('Aircraft Components')
        plt.grid(True)
        plt.xlim(-20,20)
        plt.ylim(0,40)
        ax.plot(self.x_cg, self.y_cg, marker='o', markersize=8, label='CG', color='red')
        plt.show()

traditional = aircraft('new')
