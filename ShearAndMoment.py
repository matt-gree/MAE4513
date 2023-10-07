import matplotlib.pyplot as plt
from scipy.integrate import simpson
import numpy as np
import pandas as pd
from sympy import SingularityFunction

class Wing:
    def __init__(self):
        self.beam_length = 10
        self.beam_Ix = 10
        self.beam_load_dataframe = pd.DataFrame(columns=['x_loc', 'Load', 'Shear', 'Moment'])
        self.beam_load_dataframe.x_loc = np.linspace(0, self.beam_length, 10000)

    def load_function(self):
        for index, data in self.beam_load_dataframe.iterrows():
            if data['x_loc'] < 4:
                self.beam_load_dataframe.loc[index, 'Load'] = 500*(1-data['x_loc']/self.beam_length)
            elif data[0] < 6:
                self.beam_load_dataframe.loc[index, 'Load'] = 500*(1-data['x_loc']/self.beam_length)-300
            else:
                self.beam_load_dataframe.loc[index, 'Load'] = 500*(1-data['x_loc']/self.beam_length)


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


        

test = Wing()
test.load_function()
test.shear_values()
test.moment_values()
print(test.root_shear)
print(test.root_moment)
test.cantilever_graph()