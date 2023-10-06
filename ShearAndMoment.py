import matplotlib.pyplot as plt
from scipy.integrate import quad
import numpy as np

class Wing:
    def __init__(self):
        self.beam_length = 10
        self.beam_Ix = 10
        
    def lift_distribution(self, x):
        self.linear_load = 500*(1 - x/self.beam_length)
        return self.linear_load
    
    def shear_function(self, x):
        self.root_shear, err = quad(self.lift_distribution, 0, self.beam_length)
        return quad(self.lift_distribution, 0, x)[0] - self.root_shear

    def cantilever_solve(self):
        self.root_shear, err = quad(self.lift_distribution, 0, self.beam_length)
        self.root_moment, err = quad(self.shear_function, 0, self.beam_length)

    def cantilever_graph(self):
        x = np.arange(0, self.beam_length, 0.001)
        def integrate(x):
            shear = np.zeros_like(x)
            moment = np.zeros_like(x)
            for i, val in enumerate(x):
                y_shear, err = quad(self.lift_distribution, 0, val)
                y_shear -= self.root_shear
                shear[i]=y_shear

                y_moment, err = quad(self.shear_function, 0, val)
                y_moment -= self.root_moment
                moment[i]=y_moment

            return shear, moment

        plt.plot(x, self.lift_distribution(x))
        plt.title("Lift Distripution Diagram")
        plt.show()

        plt.plot(x, integrate(x)[0])
        plt.title("Shear Diagram")
        plt.show()

        plt.plot(x, integrate(x)[1])
        plt.title("Moment Diagram")
        plt.show()


        

test = Wing()
test.cantilever_solve()
print(test.root_shear)
print(test.root_moment)
test.cantilever_graph()