# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 23:50:10 2021

@author: Erik
"""

import numpy as np
import random
from scipy.stats import truncnorm

from note_space import Note

class Player():
    
    def __init__(self, note_space_graph, 
                 ensemble_graph_id, 
                 degree,
                 starting_pitch,
                 player_attributes):
        
        """
        Player class
        
        Attributes:
            note: a Note object
            pitch_data: a list of pitches at each time step
            volume_data: a list of volumes at each time step
            net_change: keep track of how far up or down the musican has moved
                since the first note
            note_space: a Graph object generated as the note space
            
        Arguments:
            player_attributes (dictionary of parameters):
            - duration: min and max note duration
            - susceptibility_to_influence: how likely a player is to repsond to a
                ping from another player
            - harmonicity_threshold_type: how does a player decide they are out
                of harmonic balance with their environment:
                1. learning via a (truncated?)
                2. fixed value
            - change_options: when a player decides to change notes, what notes
                may that player select as a new note
                1. all notes
                2. neighbors of neighbors
                3. neighbors
        """
        
        # record the id (integer) that corresponds to the node name where
        # the player is stored
        self.id = ensemble_graph_id
        self.degree = degree
        
        #restrict the starting pitches to the center of the range
        if starting_pitch == 'random':
            std=15
            a , b = (-24)/std, (32)/std 
            starting_pitch=int(truncnorm.rvs(a,b,loc=44,scale=std))
        self.starting_pitch = starting_pitch
        
        #set note
        self.note=Note(self.starting_pitch,volume=80)
        
        #start the clock and all time stuff
        self.t = 0
        self.note_duration = 0
        self.response_change = False
        
        #signal a small percentage of players to change immediately
        if random.random() < 0.1:
            self.response_change = True
        
        #record data for first note
        self.data = []
        
        #store net change
        self.net_change=0
        
        #store note space graph
        self.G = note_space_graph
        
        #note parameters
        self.off_velocity = 127
        self.min_duration = player_attributes['duration'][0]
        self.max_duration = player_attributes['duration'][0]
        
        #harmonicity threshold
        self.harmonicity_threshold_type = player_attributes['harmonicity_threshold_type']
        self.harmonicity_data = []
        self.harmonicity_threshold = player_attributes['harmonicity_threshold']
        
        self.susceptibility_to_influence = player_attributes['susceptibility_to_influence']
    
        #change options
        self.change_options = player_attributes['change_options']
    
    def evolve(self):
        
        """
        move time steps forward one unit
        """
        
        self.t += 1
        self.note_duration += 1
        
    def decide_to_change(self, note_landscape):
        
        """
        determines whether a player should change note or not
            1. if it's been too long since a note change, the note change will be 
            triggered automatically.
            2. a neighboring player has changed notes, sending a signal.
            this is done according to probability 20%
            3. the harmonicity is drastically out of line with the rest of the texture
            
            note: 2 and 3 might be joined together, such that a neighbor triggers a change
            based on harmonicity score
        
        returns True if a change is necessary
        """
        
        #calculate harmonicity score
        harmonicity = self.harmonicity_score(note_landscape)
        self.harmonicity_data.append(harmonicity)
        avg_harmonicity = sum(self.harmonicity_data)/len(self.harmonicity_data)
        
        if self.response_change:
            if self.note_duration < self.min_duration:
                return False
            elif random.random() < self.susceptibility_to_influence:
                self.response_change = False
                return True
            else:
                self.response_change = False
                return False
        elif self.note_duration >= self.max_duration:
            return True
        elif harmonicity < self.harmonicity_threshold*avg_harmonicity:
            return True
        else:
            return False
    
    def change_note(self,note_list):
        
        """
        reads in a list of audible notes as Note() objects
        records the pitch, volume and duration of the previous note before updating
        resets trackers such as 'note_duration' and 'response_change'
        """
        
        self.data.append((self.note.pitch,self.note.volume,self.note_duration))
        
        #change timer
        self.note_duration = 0
        self.response_change = False
        
        #log old note off
        old_pitch = self.note.pitch
        
        #get new pitch and set new note
        new_pitch = self.get_new_pitch(note_list)
        self.note = Note(new_pitch,self.note.volume)
        
        #update net change
        self.net_change += new_pitch - old_pitch
        
    def get_new_pitch(self, note_landscape):
        
        """
        use note space graph to choose next note randomly, where the weights
        of the harmonic similarities guide the choice
        
        the possible notes to choose from could be:
            the entire note space
            the immediate neighbors of the current pitch
            anywhere in between
            
        the note choice could be based on:
            the subgraph of the note selection aligns with the others currently
            another standout harmonic series
        """
        
        # choice list of all neighbors of neighbors
        if self.change_options == 'Neighbors of Neighbors':
            choice_list = list(self.G[self.note.pitch])
            for c in range(len(choice_list)):
                choice_list +=(list(self.G[c]))
        elif self.change_options == 'All':
            choice_list = list(self.G.nodes)
        else:
            pass
        
        #determine weights for all choice possibilities
        weights = [0]*len(choice_list)

        for i in range(len(choice_list)):
            choice = choice_list[i]
            weights[i] = self.harmonicity_score(note_landscape, choice)
        
        choices = list(zip(choice_list,weights))
        
        #if too far down, limit choices to up steps, and vice versa
        if self.net_change <= -12:
            choices=[i for i in choices if i[0]>=self.note.pitch]
        elif self.net_change >= 12:
            choices=[i for i in choices if i[0]<=self.note.pitch]
        
        #restrict range to three octaves
        choices = [i for i in choices if self.starting_pitch -18 <= i[0] <= self.starting_pitch + 18]
        
        choice_list , weights = [c for c,w in choices], [w for c,w, in choices]
        new_pitch = random.choices(choice_list, weights=weights)[0]
        
        return new_pitch
    
    def harmonicity_score(self, note_landscape, pitch=None):
        
        """
        given a note in some aural landscape, how well does that note
        align with its environment. If it does not, there is a certain threshold
        for changing it
        """
        
        #if no pitch is given, assume we should compare the player's current note
        if not pitch:
            pitch = self.note.pitch
        
        score = 0
        
        for note in note_landscape:
            if self.G.has_edge(pitch,note.pitch):
                score += self.G[pitch][note.pitch]["weight"]
        
        return score/self.degree
            