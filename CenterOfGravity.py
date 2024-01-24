import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


class aircraftcomponent:
    def __init__(self, weight, locations, dimesions, color):
        self.total_weight = weight
        self.component_locations = locations if isinstance(locations[0], (list, set)) else [locations]
        self.component_dimensions = dimesions
        self.color = color
        self.x_cg = 0
        self.y_cg = 0
        
        for coordinate in self.component_locations:
            self.x_cg += coordinate[0]/len(self.component_locations)
            self.y_cg += coordinate[1]/len(self.component_locations)

        self.cg = [self.x_cg, self.y_cg]

def draw_rectangles(components):
    fig, ax = plt.subplots()

    for component_name, component in components.items():
        x, y = component.x_cg, component.y_cg
        width, height = component.component_dimensions

        # Draw rectangle
        ax.add_patch(Rectangle((component.x_cg-component.component_dimensions[0]/2, component.y_cg-component.component_dimensions[1]/2),
            component.component_dimensions[0],
            component.component_dimensions[1],
            facecolor = component.color,
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
    ax.plot(x_cg, y_cg, marker='o', markersize=8, label='CG', color='red')
    plt.show()


#Component Dictionary (LBF)
component_dict_traditional = {
    'payload': aircraftcomponent(3, [0,2.25], (2, 3.5), 'black'),
    'RmleicNB20': aircraftcomponent(1.32, [0,5.5], (4.5, 2.5), 'dodgerblue'),
    'Reciever JettiDuplex System': aircraftcomponent(0.05, [0,23], (2, 1.1), 'pink'),
    'Here2 GPS': aircraftcomponent(0.1, [0,5.5], (3, 3), 'limegreen'),
    'Orange Cube': aircraftcomponent(0.16, [0,24], (3.75, 1.75), 'darkorange'),
    'Fuel': aircraftcomponent(1, [0, 14], (7, 12), 'gold'),
    'Battery': aircraftcomponent(.3, [0, 29], (4.13, 1.34), 'crimson'),
    'Fuel Pump': aircraftcomponent(.3, [0, 27], (0.75, 1.5), 'darkgoldenrod'),
    'ECU': aircraftcomponent(.2, [0,29], (3.42, 2.05), 'blue'),
    'Engine': aircraftcomponent(1.6, [0, 36.5], (3, 7.2), 'gray')
}


x_cg_num = 0
y_cg_num = 0
mass_tot = 0

for items, value in component_dict_traditional.items():
    x_cg_num += (value.x_cg*value.total_weight)
    y_cg_num += (value.y_cg*value.total_weight)
    mass_tot += value.total_weight
    x_cg = x_cg_num/mass_tot
    y_cg = y_cg_num/mass_tot
    

print(x_cg)
print(y_cg)

draw_rectangles(component_dict_traditional)