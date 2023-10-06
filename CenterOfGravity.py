aircraft_length = 65 #in
aircraft_length_pixels = 3720
pixel_to_length_ratio = aircraft_length_pixels/aircraft_length
aircraft_wingspan = 59 #in

class aircraftcomponent:
    def __init__(self, weight, locations):
        self.total_weight = weight
        self.component_locations = locations
        self.x_cg = 0
        self.y_cg = 0
        
        for coordinate in self.component_locations:
            self.x_cg += (coordinate[0]/pixel_to_length_ratio)/len(self.component_locations)
            self.y_cg += (coordinate[1]/pixel_to_length_ratio)/len(self.component_locations)

        self.cg = [self.x_cg, self.y_cg]





#Component Dictionary (LBF)
component_dict = {
    'structure': aircraftcomponent(4.968, [[0,2025]]),
    'engine': aircraftcomponent(1.5375, [[0,1950]]),
    'RC_reciever': aircraftcomponent(0.085, [[0, 200]]),
    'servo_motors': aircraftcomponent(0.8675, [[0, 900],[-575, 2375], [575, 2375],
                                            [-375,2650], [375, 2650], [0,2375]]),
    'control_board': aircraftcomponent(0.075, [[0, 45]]),
    'battery': aircraftcomponent(0.774, [[0, 1300]]),
    'exhaust_nozzle': aircraftcomponent(0.0625, [[0, 2700]]),
    'fuel_tank': aircraftcomponent(0.1, [[0,2150]]),
    #'fuel': aircraftcomponent(2.7, [[0,2150]]),
    'landing_gear': aircraftcomponent(0.25, [[0, 700], [-400, 2500], [400, 2500]]),
    'wiring': aircraftcomponent(0.325, [[0, 2500]]),
    #'rocket_motor': aircraftcomponent(1.562, [[0, 3000]]),
    'rato_bracket': aircraftcomponent(0.1, [[-775, 2275], [775, 2275]])
}

# Rocket Dimensions
# Length 8.59 in 
# Diameter 2.13 in

x_cg_num = 0
y_cg_num = 0
mass_tot = 0

for items, value in component_dict.items():
    x_cg_num += (value.x_cg*value.total_weight)
    y_cg_num += (value.y_cg*value.total_weight)
    mass_tot += value.total_weight
    x_cg = x_cg_num/mass_tot
    y_cg = y_cg_num/mass_tot
    

print(x_cg)
print(y_cg)
print(y_cg*pixel_to_length_ratio)