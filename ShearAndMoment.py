import matplotlib.pyplot as plt
from scipy.integrate import simpson
import numpy as np
import pandas as pd

class BeamCrossSection:
    def __init__(self, beam_type, flange_thickness=0, flange_width=0, web_thickness=0, web_height=0, radius=0):
        self.beam_type = beam_type

        self.flange_thickness = flange_thickness
        self.flange_width = flange_width
        self.web_thickness = web_thickness
        self.web_height = web_height
        self.radius = radius

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

        elif self.beam_type == 'Circular':
            self.beam_Ix = 0.25*np.pi*self.radius**4 #in ^4
            self.beam_Iy = 0.25*np.pi*self.radius**4 #in ^4
            self.total_beam_width = self.radius
            self.total_beam_height = self.radius

class WingLoad:
    def __init__(self, cross_section_Ix, beam_length):

        self.beam_Ix = cross_section_Ix
        self.beam_length = beam_length # inches
        self.modulus_of_elasticity = 10000000 #psi
        self.beam_load_dataframe = pd.DataFrame(columns=['x_loc', 'SectionArea' 'Lift_Coeff', 'Load', 'Shear', 'Moment', 'ddxDeflection', 'Deflection'])
        self.beam_load_dataframe.x_loc = np.linspace(0, self.beam_length, 1001)
        self.step = self.beam_load_dataframe.x_loc[1]
        print(self.step)

    def load_function(self):
        # Flight choices
        velocity = 293 # ft/s
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
        max_moment = self.beam_load_dataframe['Moment'].max()
        num_points = 1000  # Number of points to sample within the circle
        self.beam_Ix

        print(I_beam.total_beam_height)
        
        # Create a contour plot of the stress distribution
        x = np.linspace(-I_beam.total_beam_width/2, I_beam.total_beam_width/2, num_points)
        y = np.linspace(-I_beam.total_beam_height/2, I_beam.total_beam_height/2, num_points)
        X, Y = np.meshgrid(x, y)

        stress_data = (max_moment / self.beam_Ix) * Y

        print(stress_data.max())
        print(I_beam.area)

        rectangular_mask = (np.abs(X) >= I_beam.web_thickness/2) & (np.abs(Y) <= (I_beam.total_beam_height-2*I_beam.flange_thickness)/2)

        # Apply the mask to stress data
        stress_data[rectangular_mask] = np.nan


        plt.figure(figsize=(8, 8))
        contour = plt.contourf(X, Y, stress_data, 60, cmap='viridis')
        plt.colorbar(contour, label='Stress (psi)')  # Add a colorbar

        # Add labels and title
        plt.xlabel('X Position (in)')
        plt.ylabel('Y Position (in)')
        plt.title('Stress Distribution, Beam Cross Section at location of Max Moment')

        # Display the plot
        plt.axis('equal')  # Equal aspect ratio to maintain the circular shape
        plt.show()

    def cantilever_graph(self):
        plt.plot(self.beam_load_dataframe.x_loc, self.beam_load_dataframe.Load)
        plt.title("Load Distribution")
        plt.show()

        plt.plot(self.beam_load_dataframe.x_loc, self.beam_load_dataframe.Shear)
        plt.title("Shear Diagram")
        plt.show()

        plt.plot(self.beam_load_dataframe.x_loc, self.beam_load_dataframe.Moment)
        plt.title("Moment Diagram")
        plt.show()

        plt.plot(self.beam_load_dataframe.x_loc, self.beam_load_dataframe.Deflection)
        plt.title("Deflection Diagram")
        plt.show()

        
I_beam = BeamCrossSection('I', flange_thickness=0.15, flange_width=1.2, web_thickness=0.25, web_height=0.26)


OpenSection = WingLoad(I_beam.beam_Ix, 25)
OpenSection.load_function()
OpenSection.shear_values()
OpenSection.moment_values()
print(OpenSection.root_shear)
print(OpenSection.root_moment)
OpenSection.beam_deflection()
OpenSection.cantilever_graph()
OpenSection.shear_at_max_moment()