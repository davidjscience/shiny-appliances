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
        ui.input_select(  
        "select",  
        "Rooms (multi)", 
        choices = rooms,
        multiple=True, 
        size=len(rooms)
    )
    ,ui.input_switch("energy", "Show power consumption chart", False) 
    ,ui.input_switch("legend", "Hide legend", False) 
    ,width=350
    ),
    ui.layout_columns(
        ui.value_box(
            "Average temperature", ui.output_ui("average_temp"),
        ),
        ui.value_box(
            "Average humidity", ui.output_ui("average_hum"), 
        ),
        ui.value_box(
            "Total power consumption", ui.output_ui("total_energy"),
        ),
        fill=False,
    ),
    ui.layout_columns(
        ui.output_plot("lines", width = "100%", height= "100%")
    )
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
        

    @reactive.calc
    def rooms():
        r = list(input.select())
        if len(r) == 0:
            r = list(df["inside"]["temperature"].columns)  
        return r
    

    @render.ui
    def average_temp():
        r = rooms()
        dmx = date_min_max()
         
        return "{:.1f}°C".format(df["inside"]["temperature"][r][dmx[0]:dmx[1]].mean().mean())
    
    @render.ui
    def average_hum():
        r = rooms()
        dmx = date_min_max()
         
        return "{:.1f} g/m³".format(df["inside"]["humidity"][r][dmx[0]:dmx[1]].mean().mean())
    

    @render.ui
    def total_energy():
        r = rooms()
        dmx = date_min_max()
        return "{:.1f} kWh".format((y[dmx[0]:dmx[1]].sum()/1000).iloc[0])
    

    @render.ui
    def average_hum():
        r = rooms()
        dmx = date_min_max()
         
        return "{:.1f} g/m³".format(df["inside"]["humidity"][r][dmx[0]:dmx[1]].mean().mean())



    @render.plot
    def lines():

        r = rooms()

        dmx = date_min_max()


        sensors = input.sensor()

        if len(sensors) == 0:
            sensors = ["temperature","humidity"]

    


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

            l = not input.legend() and i == 0

            e_result = df["inside"][s][r][dmx[0]:dmx[1]].resample(sample()).mean()
            e_result.plot(title=sensors[i],ax=axes[i],legend=l)

        if nrgy:
            e_result = y[dmx[0]:dmx[1]].resample(sample()).mean()
            e_result.plot(title="power consumption",ax=axes[-1],legend=l)

        return fig



app = App(app_ui, server)
