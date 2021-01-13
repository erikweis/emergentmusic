# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 01:20:42 2021

@author: Erik
"""

from note_space import NoteSpace
from player import Player
import networkx as nx
import matplotlib.pyplot as plt
from copy import deepcopy

class Ensemble():
    
    """
    Class Ensemble()
    
    set of musician that interact to create music
    
    dynamics:
        note changes are recognized by a players neighbors
    """
    
    def __init__(self,G, player_attributes, note_space=None,):
        
        #set graph of musicians
        self.G=G
        starting_pitches = nx.get_node_attributes(G,'starting_pitch')
        
        #create a NodeSpace Object if nonexistent
        note_space_graph = NoteSpace().projected_graph()
        
        #establish a Player() object under the attribute 'player' for each
        #node on the player graph G
        player_dict={}
        for node in G.nodes():
            player_dict[node]= Player(note_space_graph,node,G.degree[node],
                                      starting_pitches[node],player_attributes)
        nx.set_node_attributes(G,player_dict,'player')
    
    def evolve(self, steps = 1):
    
        for _ in range(steps):
            self._evolve()
    
    def _evolve(self):
        
        """
        evolves each player running an update function
        
        sends trigger to change to all players that might need to change if necessary
        """
        
        # get players list, notes of those players
        players = list(nx.get_node_attributes(self.G, 'player').values())
        notes = [deepcopy(p.note) for p in players]
        
        # create landscape dict, where landscape_dict[node] = [ # list of Notes]
        landscape_dict = {}
        neighbor_dict = {}
        for i in range(len(players)):
            
            neighbor_dict[i] = list(self.G[i])
            landscape_dict[i] = [notes[p] for p in neighbor_dict[i]]
        
        # evolve all players
        for player in players:
            player.evolve()
            
        # get list of notes that must be changed
        change_status = [players[i].decide_to_change(landscape_dict[i]) for i in range(len(players))]
        
        # change all notes needed to be changed
        for i in range(len(players)):
            
            if change_status[i]:
                
                # send ping to all players adjacent to current changers
                neighbor_list = list(self.G[i])
                for n in neighbor_list:
                    players[n].response_change = True
                    
                # change note
                neighbor_notes = [notes[p] for p in neighbor_list]
                players[i].change_note(neighbor_notes)
    
    def get_pitch_history_data(self):
        
        data = []
        
        for node in self.G.nodes:
            pitch_history_data = deepcopy(self.G.nodes[node]['player'].data)
            
            pitch_data = []
            for pitch, volume, duration in pitch_history_data:
                    pitch_data += [pitch]*duration
            data.append(pitch_data)
    
        return data
    
    def show_pitch_history(self):
        
        fig=plt.figure(figsize=(6,6), dpi=300)
        
        for pitch_data in self.get_pitch_history_data():    
            plt.plot(pitch_data)
            
        plt.show()
    
    def get_harmonicity_data(self):
        
        data = []
        
        for node in self.G.nodes:
            temp_data = deepcopy(self.G.nodes[node]['player'].harmonicity_data)
            data.append(temp_data)
    
        return data
    
    def finish(self):
        
        """
        end last note for all players
        """
        
        players = list(nx.get_node_attributes(self.G, 'player').values())
        for p in players:
            p.finish()
    


if __name__=='__main__':
    
    G = nx.watts_strogatz_graph(20, 4, 0.1)
    
    ensemble=Ensemble(G)  
    ensemble.evolve(100)
    ensemble.show_pitch_history()