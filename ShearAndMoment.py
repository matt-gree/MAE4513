import matplotlib.pyplot as plt
from scipy.integrate import simpson
import numpy as np
import pandas as pd

class BeamCrossSection:
    def __init__(self, beam_type, flange_thickness=0, flange_width=0, web_thickness=0, web_height=0, radius=0, width=0, height=0, thickness=0):
        self.beam_type = beam_type
        self.flange_thickness = flange_thickness
        self.flange_width = flange_width
        self.web_thickness = web_thickness
        self.web_height = web_height
        self.radius = radius
        self.thickness = thickness

        if self.beam_type == 'I':
            self.total_beam_width = flange_width
            self.total_beam_height = 2*flange_thickness + web_height

            A_1 = self.flange_thickness*self.flange_width
            I_X1 = (1/12)*self.flange_width*(self.flange_thickness**3)
            I_Y1 = (1/12)*self.flange_thickness*(self.flange_width**3)

            I_X2 = (1/12)*self.web_thickness*(self.web_height**3)
            I_Y2 = (1/12)*self.web_height*(self.web_thickness**3)
            A_2 = self.web_thickness*self.web_height

            self.beam_Ix = I_X2 + 2*(I_X1+(A_1*(((self.web_height + self.flange_thickness)**2)/4)))
            self.beam_Iy = I_Y2 + 2*I_Y1
            self.area = A_2 + 2* A_1

        elif self.beam_type == 'Thin-Wall Circle':
            self.beam_Ix = 0.25*np.pi*(self.radius**4 - (self.radius-self.thickness)**4) # in^4
            self.beam_Iy = 0.25*np.pi*(self.radius**4 - (self.radius-self.thickness)**4) # in^4
            self.total_beam_width = self.radius*2
            self.total_beam_height = self.radius*2
            self.area = np.pi*self.radius**2

        elif self.beam_type == 'Thin-Wall Rectangle':
            self.beam_Ix = 2*((1/12)*thickness*height**3 + thickness*width*(height/2)**2)
            self.total_beam_width = width
            self.total_beam_height = height
            self.area = width*height


class WingLoad:
    def __init__(self, beam, beam_length, material, percent=0,):

        self.beam_percent_analysis = percent
        self.beam = beam
        self.beam_Ix = beam.beam_Ix
        self.beam_length = beam_length # inches

        self.modulus_of_elasticity = material['Modulus of Elasticity']
        self.ultimate_stress = material['Ultimate Stress']
        self.ultimate_shear = material['Ultimate Shear']

        self.beam_load_dataframe = pd.DataFrame(columns=['x_loc', 'SectionArea' 'Lift_Coeff', 'Load', 'Shear', 'Moment', 'ddxDeflection', 'Deflection'])
        self.num_points = 1001
        self.beam_load_dataframe.x_loc = np.linspace(0, self.beam_length, self. num_points)
        self.step = self.beam_load_dataframe.x_loc[1]

    def load_function(self):
        # Flight choices
        velocity = 300 # ft/s
        wing_area = 2.687 # ft
        density = 0.002377 # slug/ft^3
        lift_coeff = 1.050

        # Wing Design
        wing_length = 25
        wing_root = 8.661
        taper_ratio = 0.727
        wing_tip = taper_ratio*wing_root
        wing_slope = ((wing_root-wing_tip)/2)/wing_length

        for index, data in self.beam_load_dataframe.iterrows():
            self.beam_load_dataframe.loc[index, 'Lift_Coeff'] = (-0.0000002270*data['x_loc']**6
                                                        + 0.0000155296*data['x_loc']**5
                                                        - 0.0004019925*data['x_loc']**4
                                                        + 0.0047874923*data['x_loc']**3
                                                        - 0.0254196192*data['x_loc']**2
                                                        + 0.0454462422*data['x_loc']
                                                        + 1.1222016951)
            
            self.beam_load_dataframe.loc[index, 'Area'] = (wing_root-wing_slope*(2*data['x_loc']+self.step))*self.step/144
            self.beam_load_dataframe.loc[index, 'Load'] = (0.5*self.beam_load_dataframe.loc[index, 'Area']*self.beam_load_dataframe.loc[index, 'Lift_Coeff']*density*velocity**2)/(self.step)

    def shear_values(self):
        self.root_shear = simpson(self.beam_load_dataframe.Load, self.beam_load_dataframe.x_loc)
        for index, data in self.beam_load_dataframe.iterrows():
            if index == 0:
                self.beam_load_dataframe.loc[index, "Shear"] = -self.root_shear
                continue

            self.beam_load_dataframe.loc[index, "Shear"] = simpson(self.beam_load_dataframe.Load[0:index], self.beam_load_dataframe.x_loc[0:index]) - self.root_shear

    def moment_values(self):
        self.root_moment = simpson(self.beam_load_dataframe.Shear, self.beam_load_dataframe.x_loc)
        for index, data in self.beam_load_dataframe.iterrows():
            if index == 0:
                self.beam_load_dataframe.loc[index, "Moment"] = -self.root_moment
                continue

            self.beam_load_dataframe.loc[index, "Moment"] = simpson(self.beam_load_dataframe.Shear[0:index], self.beam_load_dataframe.x_loc[0:index]) - self.root_moment

    def beam_deflection(self):
        for index, data in self.beam_load_dataframe.iterrows():
            if index == 0:
                self.beam_load_dataframe.loc[index, "ddxDeflection"] = 0
                continue

            self.beam_load_dataframe.loc[index, "ddxDeflection"] = simpson(self.beam_load_dataframe.Moment[0:index], self.beam_load_dataframe.x_loc[0:index])
        
        for index, data in self.beam_load_dataframe.iterrows():
            if index == 0:
                self.beam_load_dataframe.loc[index, "Deflection"] = 0
                continue

            self.beam_load_dataframe.loc[index, "Deflection"] = simpson(self.beam_load_dataframe.ddxDeflection[0:index], self.beam_load_dataframe.x_loc[0:index])/(self.modulus_of_elasticity * self.beam_Ix)

    def shear_at_max_moment(self):
        def margin_of_safety(stress, ultimate):
            return (ultimate/(1.5*stress))-1
        
        def contour_plotter(x_data, y_data, contour_data, title, data_label):
            bending_contour = plt.contourf(x_data, y_data, contour_data, 60, cmap='viridis')
            plt.colorbar(bending_contour, label=data_label)  # Add a colorbar
            plt.title(f'{title}, Cross Section at z={self.beam_length*self.beam_percent_analysis}')
            plt.xlabel('X Position (in)')
            plt.ylabel('Y Position (in)')
            plt.axis('equal')
            plt.savefig(title, dpi=300)
            plt.show()

        
        if self.beam.beam_type == 'I':
            max_shear = np.abs(self.beam_load_dataframe['Shear']).max()
            distance_from_AC_to_shear = 0.28 # in
            max_moment = self.beam_load_dataframe['Moment'].max()
            num_points = 1000
            self.beam_Ix

            self.beam_load_dataframe['Torque'] = -self.beam_load_dataframe['Shear']*distance_from_AC_to_shear

            torsion = max_shear*distance_from_AC_to_shear

            # Calculate shear stress for each x value
            max_shear_stress_torsion = torsion / (2 * self.beam.area * self.beam.thickness)

            # Plot shear stress as a function of x
            plt.plot(self.beam_load_dataframe['x_loc'], self.beam_load_dataframe['Torque'], label='Torsion')

            # Add labels and title
            plt.xlabel('z (in)')
            plt.ylabel('Torque (lbf*in)')  # Assuming torsion has units of force and area is in square meters
            plt.title('Torque Diagram')

            # Add a legend
            plt.legend()
            plt.show()

            max_torsion = max_shear*distance_from_AC_to_shear
            print(max_torsion)

            max_shear_stress = max_shear/(2*self.beam.beam_Ix)*(self.beam.web_thickness*
                                                          (self.beam.total_beam_height/2-self.beam.flange_thickness)**2+
                                                          self.beam.flange_thickness*
                                                          (self.beam.total_beam_height-self.beam.flange_thickness)
                                                          *(self.beam.total_beam_width-self.beam.web_thickness))
            
            print('Max Shear', max_shear_stress)

            print(self.beam.total_beam_height)
            
            # Create a contour plot of the stress distribution
            x = np.linspace(-self.beam.total_beam_width/2, self.beam.total_beam_width/2, num_points)
            y = np.linspace(-self.beam.total_beam_height/2, self.beam.total_beam_height/2, num_points)
            X, Y = np.meshgrid(x, y)

            stress_data = (max_moment / self.beam_Ix) * Y

            print(stress_data.max())
            print(self.beam.area)

            rectangular_mask = (np.abs(X) >= self.beam.web_thickness/2) & (np.abs(Y) <= (self.beam.total_beam_height-2*self.beam.flange_thickness)/2)

            print('Max Bending Stress', stress_data.max())
            # Apply the mask to stress data
            stress_data[rectangular_mask] = np.nan

            plt.figure(figsize=(8, 8))
            contour = plt.contourf(X, Y, stress_data, 60, cmap='viridis')
            plt.colorbar(contour, label='Stress (psi)')  # Add a colorbar

        if self.beam.beam_type == 'Thin-Wall Circle':
            print(f'The following parameters have been calculated at the beam location z={self.beam_length*self.beam_percent_analysis}:')
            num_points = 1000
            span_location_shear = -np.abs(self.beam_load_dataframe['Shear'][(self.num_points-1)*self.beam_percent_analysis])
            print('Shear:', span_location_shear)

            distance_from_AC_to_shear = 0

            span_location_moment = self.beam_load_dataframe['Moment'][(self.num_points-1)*self.beam_percent_analysis]
            print('Moment:', span_location_moment)

            S_y = np.abs(self.beam_load_dataframe['Shear'][(self.num_points-1)*self.beam_percent_analysis])
            q_so =  (S_y*self.beam.thickness*self.beam.radius**2)/(self.beam_Ix)

            self.beam_load_dataframe['Torque'] = -self.beam_load_dataframe['Shear']*distance_from_AC_to_shear

            max_torsion = span_location_shear*distance_from_AC_to_shear

            # Calculate shear stress for each x value
            span_location_shear_stress_torsion = max_torsion / (2 * self.beam.area * self.beam.thickness)

            # Plot shear stress as a function of x
            plt.plot(self.beam_load_dataframe['x_loc'], self.beam_load_dataframe['Torque'], label='Torsion')

            # Add labels and title
            plt.xlabel('z (in)')
            plt.ylabel('Torque (lbf*in)')  # Assuming torsion has units of force and area is in square meters
            plt.title('Torque Diagram')

            # Add a legend
            plt.legend()
            plt.show()

            theta = np.linspace(0, 2 * np.pi, num_points)
            r = np.linspace(0, self.beam.radius, num_points)
            R, Theta = np.meshgrid(r, theta)

            X = R * np.cos(Theta)
            Y = R * np.sin(Theta)

            bending_stress_data = (span_location_moment / self.beam_Ix) * Y
            print('Max Direct Stress:', bending_stress_data.max())
            print('Minimum Direct Stress Margin of Safety:', margin_of_safety(bending_stress_data.max(), self.ultimate_stress))

            shear_flow_data = (S_y/self.beam.beam_Ix)*self.beam.radius**2*self.beam.thickness*(np.cos(Theta)-1)+q_so
            print('Max Shear Flow:', shear_flow_data.max())

            max_shear_stress = shear_flow_data.max()/self.beam.thickness+span_location_shear_stress_torsion
            print('Max Shear Stress:', max_shear_stress)
            print('Minimum Shear Stress Margin of Safety:', margin_of_safety(max_shear_stress, self.ultimate_shear))

            rectangular_mask = (R < self.beam.radius-self.beam.thickness)
            
            bending_stress_data[rectangular_mask] = np.nan
            shear_flow_data[rectangular_mask] = np.nan

            contour_plotter(X, Y, bending_stress_data, 'Bending Stress Diagram', 'Bending Stress (psi)')
            contour_plotter(X, Y, shear_flow_data, 'Shear Flow Diagram', 'Shear Flow (lb/in)')
            contour_plotter(X, Y, shear_flow_data/self.beam.thickness, 'Shear Stress Diagram', 'Shear Stress (psi)')

        if self.beam.beam_type == 'Thin-Wall Rectangle':

            num_points = 1000
            max_shear = np.abs(self.beam_load_dataframe['Shear']).max()
            print(self.beam_load_dataframe['Shear'])
            print(max_shear)
            distance_from_AC_to_shear = 0.95
            torsion = max_shear*distance_from_AC_to_shear
            shear_stress_torsion = torsion/(2*self.beam.area*self.beam.thickness)

            self.beam_load_dataframe['Torque'] = -self.beam_load_dataframe['Shear']*distance_from_AC_to_shear

            # Calculate shear stress for each x value
            max_shear_stress_torsion = torsion / (2 * self.beam.area * self.beam.thickness)

            # Plot shear stress as a function of x
            plt.plot(self.beam_load_dataframe['x_loc'], self.beam_load_dataframe['Torque'], label='Torsion')

            # Add labels and title
            plt.xlabel('z (in)')
            plt.ylabel('Torque (lbf*in)')  # Assuming torsion has units of force and area is in square meters
            plt.title('Torque Diagram')

            # Add a legend
            plt.legend()
            plt.show()

            max_moment = self.beam_load_dataframe['Moment'].max()

            x = np.linspace(-self.beam.total_beam_width/2, self.beam.total_beam_width/2, num_points)
            y = np.linspace(-self.beam.total_beam_height/2, self.beam.total_beam_height/2, num_points)
            X, Y = np.meshgrid(x, y)

            bending_stress_data = (max_moment / self.beam_Ix) * Y
            rectangular_mask = (np.abs(Y) <= self.beam.total_beam_height/2-self.beam.thickness) & (np.abs(X) <= self.beam.total_beam_width/2-self.beam.thickness)
            
            print('Max Shear', bending_stress_data.max())
            
            bending_stress_data[rectangular_mask] = np.nan

            bending_contour = plt.contourf(X, Y, bending_stress_data, 60, cmap='viridis')
            plt.colorbar(bending_contour, label='Bending Stress (psi)')  # Add a colorbar
            plt.title('Bending Stress Diagram')
            plt.axis('equal')
            plt.show()

            x = np.linspace(-self.beam.total_beam_width/2-self.beam.thickness, self.beam.total_beam_width/2+self.beam.thickness, num_points)
            y = np.linspace(-self.beam.total_beam_height/2-self.beam.thickness, self.beam.total_beam_height/2+self.beam.thickness, num_points)
            X, Y = np.meshgrid(x, y)

            S_y = -max_shear
            K = -(S_y * self.beam.thickness)/(2*self.beam.beam_Ix)

            q_so = K * (self.beam.total_beam_height/3) * (self.beam.total_beam_width-(self.beam.total_beam_height/4))
            q_s_12 = K*Y + q_so
            
            rectangular_mask = (X > -self.beam.total_beam_width/2) & (np.abs(Y) > self.beam.total_beam_height)
            q_s_12[rectangular_mask] = 0

            q_s_23 = K*(self.beam.total_beam_height*(X+self.beam.total_beam_width/2)-0.25*self.beam.total_beam_height**2) + q_so
            rectangular_mask = (Y < self.beam.total_beam_height/2) & (np.abs(X) > self.beam.total_beam_width)
            q_s_23[rectangular_mask] = 0

            q_s_34 = K*(-(Y-self.beam.total_beam_height/2)**2+self.beam.total_beam_height*(Y-self.beam.total_beam_height/2)+self.beam.total_beam_height*self.beam.total_beam_width-0.25*self.beam.total_beam_height**2) + q_so
            rectangular_mask = (X < self.beam.total_beam_width/2) & (np.abs(Y) > self.beam.total_beam_height)
            q_s_34[rectangular_mask] = 0

            q_s_56 = K*(self.beam.total_beam_height*(X+self.beam.total_beam_width/2)-0.25*self.beam.total_beam_height**2) + q_so
            rectangular_mask = (Y > -self.beam.total_beam_height/2) & (np.abs(X) > self.beam.total_beam_width)
            q_s_56 [rectangular_mask] = 0

            combined_data = q_s_12 + q_s_23 + q_s_34 + q_s_56

            print('Max Shear Stress', combined_data.max()/self.beam.thickness+max_shear_stress_torsion)

            rectangular_mask = (np.abs(Y) < self.beam.total_beam_height/2) & (np.abs(X) < self.beam.total_beam_width/2)
            combined_data[rectangular_mask] = np.nan


            contour = plt.contourf(X, Y, combined_data, 60, cmap='viridis')
            plt.colorbar(contour, label='Shear Flow (lb/in)')  # Add a colorbar

    def cantilever_graph(self):
        plt.plot(self.beam_load_dataframe.x_loc, self.beam_load_dataframe.Load)
        plt.title("Lift (Load) Distribution")
        plt.xlabel('Z Position (in)')
        plt.ylabel('Lift (lbf)')
        plt.show()

        plt.plot(self.beam_load_dataframe.x_loc, self.beam_load_dataframe.Shear)
        plt.title("Shear Diagram")
        plt.xlabel('Z Position (in)')
        plt.ylabel('Shear (lbf)')
        plt.show()

        plt.plot(self.beam_load_dataframe.x_loc, self.beam_load_dataframe.Moment)
        plt.title("Moment Diagram")
        plt.xlabel('Z Position (in)')
        plt.ylabel('Moment (lbf-in)')
        plt.show()

        plt.plot(self.beam_load_dataframe.x_loc, self.beam_load_dataframe.Deflection)
        plt.title("Deflection Diagram")
        plt.xlabel('Z Position (in)')
        plt.ylabel('Deflection (in)')
        plt.show()

        
# I_beam = BeamCrossSection('I', flange_thickness=0.15, flange_width=1.2, web_thickness=0.25, web_height=0.26)
# OpenSection = WingLoad(I_beam, 25)

# Thin_Walled_Rectangle = BeamCrossSection('Thin-Wall Rectangle', width=3.82, height=0.39, thickness=0.1)
# OpenSection = WingLoad(Thin_Walled_Rectangle, 25)

Thin_Walled_Tube = BeamCrossSection('Thin-Wall Circle', radius=0.32, thickness=0.15)
materials_properties = {
    'Aluminum': {
        'Modulus of Elasticity': 10000000,
        'Ultimate Stress': 76900,
        'Ultimate Shear': 41000
    },
    'Carbon Fiber':{
        'Modulus of Elasticity': 20000000,
        'Ultimate Stress': 270000,
        'Ultimate Shear': 23800
    },
    'Titanium':{
        'Modulus of Elasticity': 16400000,
        'Ultimate Stress': 170000,
        'Ultimate Shear': 111000
    }
}

OpenSection = WingLoad(Thin_Walled_Tube, 25, materials_properties['Carbon Fiber'], percent=0)

OpenSection.load_function()
OpenSection.shear_values()
OpenSection.moment_values()
print('Root Shear:', OpenSection.root_shear)
print('Root Moment:', OpenSection.root_moment)
OpenSection.beam_deflection()
# OpenSection.cantilever_graph()
OpenSection.shear_at_max_moment()