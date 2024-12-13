import pandas as pd
from ucimlrepo import fetch_ucirepo 
import numpy as np
  
# fetch dataset 
appliances_energy_prediction = fetch_ucirepo(id=374) 
  
# data (as pandas dataframes) 
X = appliances_energy_prediction.data.features 
y = appliances_energy_prediction.data.targets 
  

y.index = X["date"]
y.to_csv("data/y.csv")