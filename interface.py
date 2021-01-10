# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 11:01:11 2021

@author: Erik
"""

import numpy as np

from main import create_song

from bokeh.io import curdoc, output_notebook, show
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, TextInput, Button, Select, RangeSlider, Div
from bokeh.plotting import figure
from bokeh.palettes import viridis

#--------------------------------------------------

#run button
run = Button(label="Create MIDI File", button_type="success")
run_message = Div(text = "")

#player options
div_player_options = Div(text = """<h2>Player Options</h2>""")
susceptibility_to_influence = Slider(title = "Susceptibility to Influence", start = 0, end = 1, value = 0.35)
duration = RangeSlider(start = 1, end = 200, value = (5,100), step = 1, title = "Note Duration")
harmonicity = Select (title = "Harmonicity", value = "Fixed", options = ["Fixed", "% Moving Average"] )
harmonicity_fixed = Slider(title = "Fixed Harmonicity Threshold", value = 1, start = 0, end = 10, step = 0.05)
harmonicity_average = Slider(title = "%Moving Average", value = 0.5, start = 0, end = 1, step = 0.05)
change_options = Select (title = "Note Change Choices", value = "All", options = ["All", "Neighbors", "Neighbors of Neighbors"])
player_options = column(div_player_options, duration, change_options, harmonicity, harmonicity_fixed, harmonicity_average, susceptibility_to_influence,)

#song options
div_song_options = Div(text = """<h2>Song Options</h2>""")
number_players = Slider(title = "Number of Players", value = 20, start = 2, end = 40)
number_time_steps = Slider(title = "Song Length", value = 300, start = 100, end = 1000, step =10) 
song_options = column(div_song_options, number_players, number_time_steps)

#graph options
div_graph_options = Div(text = """<h2>Graph Options </h2>""")
graph_type = Select(title = "Graph Type", value = "Small World", options = ["Random", "Small World", "Structured"])
average_degree = Slider(title = "Average Degree", value = 4, start = 1, end = number_players.value  , step = 0.5) 
rewiring_prob = Slider(title = "Rewiring Probability", start = 0, end = 1, value = 0.3, step = 0.05, visible = (graph_type.value == "Small World"))
graph_options = column (div_graph_options, graph_type, average_degree, rewiring_prob)

# max degree changes with number of players
def number_players_change(attr, old, new):
    average_degree.end = number_players.value
number_players.on_change('value', number_players_change)

#only show rewiring prob for small world
def graph_type_change(attr, old, new):
    if graph_type.value == "Small World":
        rewiring_prob.visible = True
    else: rewiring_prob.visible = False
graph_type.on_change('value', graph_type_change)

#--------------------------------------------------

#make pitch history plot
blank_data = {'xs':[], 'ys':[], 'color':[]}
source = ColumnDataSource(blank_data)
p = figure(plot_width = 800, plot_height = 400)
p.multi_line(xs = 'xs' ,ys = 'ys', color = 'color', source = source)

#turn off bokeh settings
p.toolbar.logo=None
p.toolbar_location=None
p.toolbar.active_drag = None
p.toolbar.active_scroll = None
p.toolbar.active_tap = None


# function for updating plot data
def update_pitch_history_plot(filename, pitch_history_data):
    
    song_length = len(pitch_history_data[0])
    xs = [list(range(song_length)) for _ in pitch_history_data]
    ys = pitch_history_data
    
    #color pallete 
    palette = viridis(88)
    color = [palette[data[0]] for data in pitch_history_data] 
    
    new_data = {'xs':xs, 'ys':ys, 'color':color}
    source.data =new_data

#---------------------------------------------------

#button push
def button_push(event):
    filename, data = create_song(
        graph_type = graph_type.value,
        average_degree = average_degree.value,
        rewiring_prob = rewiring_prob.value,
        number_time_steps = number_time_steps.value,
        tempo = 108,
        player_attributes = None)
    
    run_message.text = filename
    update_pitch_history_plot(filename, data)
    

    
run.on_click(button_push)

layout = column(row(player_options, column(song_options, graph_options)), column(run,run_message),p)

curdoc().add_root(layout)
curdoc().title = "Emergent Music"

#output_notebook(hide_banner = True)
#show(layout,notebook_handle=True)