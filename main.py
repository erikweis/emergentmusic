# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 12:38:15 2021

@author: Erik
"""

from ensemble import Ensemble
import networkx as nx
from create_midi_file import create_midi_file

if __name__=="__main__":
    
    #create player graph
    G = nx.watts_strogatz_graph(40, 4, 0.3)
    
    #create ensembel object5
    ensemble=Ensemble(G)
    
    #evolve ensemble
    ensemble.evolve(300)
    
    #show pitch history
    ensemble.show_pitch_history()
    
    tempo = 108
    create_midi_file(ensemble,tempo)