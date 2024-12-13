# Import data from shared.py

from shiny import App, render, ui, reactive
from datetime import timedelta
import pandas as pd

path = 'data/ex6df.pkl'

import pickle

import matplotlib.pyplot as plt

with open(path, 'rb') as df_file:
    df  = pickle.load(df_file)

rooms = list(df["inside"]["temperature"].columns)
date_min = df.index[0]
date_max = df.index[-1]

y = pd.read_csv("data/y.csv")
y.index = df.index
y = y.drop("date",axis=1)


app_ui = ui.page_sidebar( 
    ui.sidebar(
        ui.input_date_range("daterange", 
                        "Date range", start=date_min
                        ,end=date_max),
        ui.input_select(
            "sensor", "Sensors (multi)", choices=["temperature","humidity"],
            multiple=True            
        ),
        ui.input_switch("energy", "Show energy consumption", False),  
        ui.input_select(  
        "select",  
        "Rooms (multi)", 
        choices = rooms,
       # { "bathroom": "bathroom",
       #   "ironing room": "ironing room",
       #   "kitchen": "kitchen",
       #   "laundry room": "laundry room" },
        multiple=True, 
        size=len(rooms)
    )
    ,width=320
    ),
    ui.output_plot("hist", width = "100%", height= "100%")
    ,window_title="Appliances Energy Prediction Dashoard"
    ,title="Appliances Energy Dashoard"
)


def server(input, output, session):


    @reactive.calc
    def date_min_max():
        return [input.daterange()[0],input.daterange()[1]]



    @reactive.calc
    def sample():

        dmx = date_min_max()

    
        days = (dmx[1]-dmx[0]).days
        if(days<=14):
            return "h"
        elif(days<=70):
            return "d"
        else: 
            return "W"


    @render.plot
    def hist():
        l= list(input.select())
        sensors = list(input.sensor())
        if len(l) == 0:
            l = list(df["inside"]["temperature"].columns)

        if len(sensors) == 0:
            sensors = ["temperature","humidity"]

        dmx = date_min_max()


        nrgy = input.energy()

        fig = plt.figure()

        if len(sensors) == 1 and not nrgy:
            axes = [fig.subplots(1,1)]
        elif len(sensors) == 0:
            return fig
        else:
            axes = fig.subplots(1,len(sensors)+int(nrgy))


        
        if((dmx[1]-dmx[0]).days<1):
            dmx[1] = dmx[0] + timedelta(days=1)

        

        for i,s in enumerate(sensors):

            e_result = df["inside"][s][l][dmx[0]:dmx[1]].resample(sample()).mean()
            e_result.plot(title=sensors[i],ax=axes[i]).legend(loc='best')

        if nrgy:
            e_result = y[dmx[0]:dmx[1]].resample(sample()).mean()
            e_result.plot(title="energy",ax=axes[-1],legend=False)

        return fig



app = App(app_ui, server)
