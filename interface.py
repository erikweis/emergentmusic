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
from bokeh.palettes import viridis, plasma

#--------------------------------------------------

#run button
run = Button(label="Create MIDI File", button_type="success")
run_message = Div(text = "")

#player options
div_player_options = Div(text = """<h2>Player Options</h2>""")
susceptibility_to_influence = Slider(title = "Susceptibility to Influence", start = 0, end = 1, value = 0.35, step = 0.05)
duration = RangeSlider(start = 1, end = 200, value = (20,37), step = 1, title = "Note Duration")
harmonicity = Select (title = "Harmonicity Theshold Type", value = "Fixed", options = ["Fixed", "Moving Average"] )
harmonicity_fixed = Slider(title = "Fixed Harmonicity Threshold", value = 1, start = 0, end = 10, step = 0.05)
harmonicity_average = Slider(title = "Moving Average (%)", value = 0.5, start = 0, end = 2, step = 0.05)
change_options = Select (title = "Note Change Choices", value = "All", options = ["All", "Neighbors", "Neighbors of Neighbors"])
player_options = column(div_player_options, duration, change_options, harmonicity, harmonicity_fixed, harmonicity_average, susceptibility_to_influence)

#song options
div_song_options = Div(text = """<h2>Song Options</h2>""")
number_players = Slider(title = "Number of Players", value = 20, start = 2, end = 40)
number_time_steps = Slider(title = "Song Length", value = 300, start = 100, end = 2000, step =10) 
song_options = column(div_song_options, number_players, number_time_steps)

#graph options
div_graph_options = Div(text = """<h2>Graph Options </h2>""")
graph_type = Select(title = "Graph Type", value = "Small World", options = ["Random", "Small World", "Structured"])
average_degree = Slider(title = "Average Degree", value = 10, start = 1, end = number_players.value  , step = 1) 
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
p = figure(plot_width = 800, plot_height = 400,
           y_range = (0,88))
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

#--------------------------------------------------
    
#make harmonicitiy_plot
#make pitch history plot
blank_data = {'xs':[], 'ys':[], 'color':[]}
source_q = ColumnDataSource(blank_data)
q = figure(plot_width = 800, plot_height = 400)
q.multi_line(xs = 'xs' ,ys = 'ys', color = 'color', source = source_q)

#turn off bokeh settings
q.toolbar.logo=None
q.toolbar_location=None
q.toolbar.active_drag = None
q.toolbar.active_scroll = None
q.toolbar.active_tap = None

def update_harmonicity_plot(harmonicity_data):
    
    #one line records average of all
    average = [sum(i)/len(i) for i in harmonicity_data]
    harmonicity_data.append(average)
    
    xs = [list(range(len(harmonicity_data[0]))) for _ in harmonicity_data]
    ys = harmonicity_data
    
    #color pallete 
    palette = viridis(100)
    color = [palette[np.random.randint(0,99)] for data in harmonicity_data]
    color[-1] = 'FF0000'
    
    new_data = {'xs':xs, 'ys':ys, 'color':color}
    source_q.data =new_data

#---------------------------------------------------

#button push
def button_push(event):
    
    """
    create midi file based on parameters outlined by input parameters. 
    passes two dictionaries with paraemters, which adapt to provide the
    necessary information:
        graph_attributes --> used to create graph for Ensemble object
            - graph_type: 'Small World', 'Random', 'Configuration', 'Structured'
            - other parameters depending on graph type
        player_attributes --> passed to player object to regulate dynamic behavior
            - duration: min and max note duration
            - susceptibility_to_influence: how likely a player is to repsond to a
                ping from another player
            - harmonicity_threshold_type: how does a player decide they are out
                of harmonic balance with their environment:
                1. learning via a moving average (truncated?)
                2. fixed value
            - change_options: when a player decides to change notes, what notes
                may that player select as a new note
                1. all notes
                2. neighbors of neighbors
                3. neighbors
    """
    
    #create graph attributes
    graph_attributes = {'graph_type':graph_type.value}
    if graph_type.value == 'Small World':
        graph_attributes.update({
            'average_degree':average_degree.value,
            'rewiring_prob':rewiring_prob.value})
    elif graph_type.value == 'Random':
        pass
    else:
        pass 
    
    #create player attributes
    player_attributes = {
        'duration':duration.value,
        'susceptibility_to_influence':susceptibility_to_influence.value,
        'harmonicity_threshold_type':harmonicity.value,
        'change_options':change_options.value}
    if harmonicity.value == 'Fixed':
        player_attributes.update({
            'harmonicity_threshold':harmonicity_fixed.value})
    elif harmonicity.value == 'Moving Average':
        player_attributes.update({
            'harmonicity_threshold':harmonicity_average.value})
    else:
        print("Harmonicity options should be 'Fixed' or 'Moving Average'")
    
    filename, pitch_data, harmonicity_data = create_song(
        graph_attributes = graph_attributes,
        number_time_steps = number_time_steps.value,
        number_players = number_players.value,
        tempo = 108,
        player_attributes = player_attributes)
    
    run_message.text = filename
    update_pitch_history_plot(filename, pitch_data)
    update_harmonicity_plot(harmonicity_data)

    
run.on_click(button_push)

left_column = column(song_options, player_options,graph_options, run,run_message)
right_column = column(p,q)

layout = row(left_column,right_column)

curdoc().add_root(layout)
curdoc().title = "Emergent Music"

#output_notebook(hide_banner = True)
#show(layout,notebook_handle=True)