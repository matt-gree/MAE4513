import pandas as pd
from scipy.integrate import simpson
from scipy import odr
import numpy as np
import matplotlib.pyplot as plt

velocity = 293 # ft/s
wing_area = 2.678 # ft
density = 0.002377 # slug/ft^3
lift_coeff = 1.050

lift = 0.5*wing_area*lift_coeff*density*velocity**2

print(lift)

lift_distribution = {0: 1.122621,
3.958: 1.113327,
7.8205:	1.119947,
11.4915: 1.120706,
14.8755: 1.103479,
17.897:	1.063521,
20.476: 0.991291,
22.5525: 0.868825,
24.0715: 0.675703,
25:	0.381249,
}

lift_distribution_df = pd.DataFrame.from_dict(lift_distribution, orient='index', columns=['lift_coeff'])
integrated_lift_coeff = simpson(lift_distribution_df.lift_coeff, lift_distribution_df.index)

lift_coeff_scaling_factor = lift/(2*integrated_lift_coeff)

lift_distribution_df.lift_coeff = lift_coeff_scaling_factor*lift_distribution_df.lift_coeff


wing_length = 25
wing_root = 8.661
taper_ratio = 0.727
wing_tip = 0.727*8.661
wing_slope = ((wing_root-wing_tip)/2)/wing_length

beam_load_dataframe = pd.DataFrame(columns=['x_loc', 'Area', 'Lift_Coeff', 'Lift'])
beam_load_dataframe.x_loc = np.linspace(0, 25, 101)
step = 0.25

for index, data in beam_load_dataframe.iterrows():
    beam_load_dataframe.loc[index, 'Lift_Coeff'] = (-0.0000002270*data['x_loc']**6
                                                + 0.0000155296*data['x_loc']**5
                                                - 0.0004019925*data['x_loc']**4
                                                + 0.0047874923*data['x_loc']**3
                                                - 0.0254196192*data['x_loc']**2
                                                + 0.0454462422*data['x_loc']
                                                + 1.1222016951)
    
    beam_load_dataframe.loc[index, 'Area'] = (wing_root-wing_slope*(2*data['x_loc']+step))*step/144

    beam_load_dataframe.loc[index, 'Lift'] = 2*beam_load_dataframe.loc[index, 'Area']*beam_load_dataframe.loc[index, 'Lift_Coeff']*density*velocity**2
    
print(np.sum(beam_load_dataframe.Area),'area') 


print(beam_load_dataframe)
integrated_lift_check = simpson(beam_load_dataframe.Lift, beam_load_dataframe.x_loc)
print(integrated_lift_check)