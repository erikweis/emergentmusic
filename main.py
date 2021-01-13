# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 12:38:15 2021

@author: Erik
"""

from ensemble import Ensemble
import networkx as nx
from create_midi_file import create_midi_file

def create_song(graph_attributes = {'graph_type':'Small World',
                                    'average_degree':4,
                                    'rewiring_prob':0.3},
        number_players = 20,
        number_time_steps = 300,
        tempo = 108,
        player_attributes = None):
    
    """
    arguments:
        graph_type : 'Small World', 'Random', 'Configuration', 'Structured'
        average_degree
        number_of_players
        rewiring_prob
        number_time_steps
        tempo
        player_attributes: {
            duration: (min_duration, max_duration)
            note_change_choices: 'All', 'Neighbors of Neighbors'
            harmonicity threshold: 'Fixed' or 'Moving Average'
                fixed threshold
                moving average threshold
            susceptibility to influence
        }
    """
    
    graph_type = graph_attributes['graph_type']
    
    #create player graph
    if graph_type == 'Small World':
        #assert rewiring_prob
        G = nx.watts_strogatz_graph(number_players, 
                                    graph_attributes['average_degree'], 
                                    graph_attributes['rewiring_prob'])
    elif graph_type =='Random':
        pass
    elif graph_type == 'Structured':
        pass
    
    #add starting pitch to node 
    starting_pitches = {i:'random' for i in range(len(G))}
    nx.set_node_attributes(G,starting_pitches, 'starting_pitch')
    
    #create ensembel object5
    ensemble=Ensemble(G, player_attributes)
    
    #evolve ensemble
    ensemble.evolve(number_time_steps)
    
    #show pitch history
    pitch_history_data = ensemble.get_pitch_history_data()
    harmonicity_data = ensemble.get_harmonicity_data()
    
    #create file
    filename = create_midi_file(ensemble,tempo)    

    return filename, pitch_history_data, harmonicity_data

if __name__=="__main__":
    
    create_song()