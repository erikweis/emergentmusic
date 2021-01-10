# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 12:38:15 2021

@author: Erik
"""

from ensemble import Ensemble
import networkx as nx
from create_midi_file import create_midi_file

def create_song(graph_type='Small World',
        average_degree = 4,
        number_of_players = 20,
        rewiring_prob = None,
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
    
    
    #create player graph
    if graph_type == 'Small World':
        assert rewiring_prob
        G = nx.watts_strogatz_graph(number_of_players, average_degree, rewiring_prob)
    elif graph_type =='Random':
        pass
    elif graph_type == 'Structured':
        pass
    
    #create ensembel object5
    ensemble=Ensemble(G, player_attributes)
    
    #evolve ensemble
    ensemble.evolve(number_time_steps)
    
    #show pitch history
    pitch_history_data = ensemble.get_pitch_history_data()
    
    #create file
    filename = create_midi_file(ensemble,tempo)    

    return filename, pitch_history_data

if __name__=="__main__":
    
    create_song()