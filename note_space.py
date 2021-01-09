# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 19:52:21 2020

@author: Erik
"""

import networkx as nx
from networkx.algorithms import bipartite
import numpy as np
import matplotlib.pyplot as plt

class Note(object):
    
    def __init__(self,pitch,volume=0):
        
        self.pitch = pitch
        self.volume = volume

class Series(object):
    
    def __init__(self, fundamental):
        
        self.fundamental = fundamental

class NoteSpace(object):
    
    """
    Wrapper class for storing the graph that governs the relationship
    between notes.
    
    
    """
    
    def __init__(self,alpha=0.5):
        
        self.alpha = alpha
        self.B = None
        self.G = self.create_graph()        
        
    def create_bipartite_graph(self):
        
        """
        Create a bipartite graph of two node types:
            Notes (stored as integer)
            Harmonic series (stores as Series() object)
            Between a note and a given harmonic series, the edge weight is
            given by n, where the note is the nth harmonic of the fundamental
        """
        
        note_list = list(range(88)) 
        series_list = [Series(i) for i in note_list]
        
        B = nx.Graph()
        B.add_nodes_from(note_list,bipartite=0)
        B.add_nodes_from(series_list,bipartite=1)
        
        for series in series_list:
            for note in note_list:
                
                #check if the note is in the given truncated harmonic series
                truncation = 6
                series_notes = [0,12,19,24,28,31]
                for i in range(truncation):
                    #if so, add it to the graph with weight n,
                    #where the note is the nth harmonic of the fundamental
                    if (note == series.fundamental + series_notes[i]):
                        #add edge
                        B.add_edge(note, series, weight = i)
                
        self.B = B
        assert nx.is_bipartite(B)
        
        #top = nx.bipartite.sets(B)[0]
        #pos = nx.bipartite_layout(B, top)
        #nx.draw(B,pos=pos,node_size=100,with_labels=True)
        
    
    def projected_graph(self):
        
        if not self.B:
            self.create_bipartite_graph()
            
        bottom = bipartite.sets(self.B)[0]
        G = bipartite.generic_weighted_projected_graph(self.B,bottom,
                                                       weight_function=self.projection_weight) 
        
        return G
    
    @staticmethod
    def projection_weight(B,u,v):
        
        """
        return projected graph where notes with strong ties have many similar
        harmonic series where both play an important role
        
        for each harmonic series where both play an important role, say 
        the 2nd and 3rd harmonics, the weight between the two notes is 
        increased by 1 / 2.5
        
        note that less sinificant contributions increase the weight by a lower
        amount
        
        the larger the weight, the more closely related the two notes are
        """
        
        #remove self loops
        if u==v:
            return 0
        
        weight = 0
        
        u_neighbors = set(B[u])
        v_neighbors = set(B[v])
        
        #for each similarity
        for s in u_neighbors.intersection(v_neighbors):
            #notes u and v are the ith and jth harmonic of s
            if u==s: 
                i=0
                j = B[v][s]["weight"]
            elif v==s: 
                i = B[u][s]["weight"]
                j=0
            else:
                i = B[u][s]["weight"]
                j = B[v][s]["weight"]
            avg_harmonic = (i + j)/2
            weight += 1/avg_harmonic
            
        return weight
    
    #create graph not from bipartite projection but some other weighting procedure
    def create_graph(self):
        
        """
        Create graph of note space, where the distance between two notes is
            small if there is some behavior
        """
        
        note_list = list(range(88))
        
        G=nx.Graph()
        G.add_nodes_from(note_list)
    
        for note1 in note_list:
            for note2 in note_list:
                d = self.note_distance(note1,note2)
                if d > 0: 
                    G.add_edge(note1,note2,weight=d)
    
    def note_distance(self,note1,note2):
        
        """
        two notes are similar if they are an octave, fifth, fourth, 
            major, or minor third appart
        if greater than an octave, the distance decreases by n*alpha
            n is the number of octaves of differnce
            alpha is the weight, currently set to 1/2
        """
        distance=abs(note1-note2)
        
        if distance in [12,7,5,4,3]:
            return 1/distance
        elif (distance%12 in [12,7,5,4,3]) and (distance//12 <4) :
            return 1/(distance%12) + self.alpha*(distance//12)
        else: return 0

# =============================================================================
# def note_distance(note1,note2):
#     
#     distance=abs(note1-note2)
#     alpha=0.5
#     
#     if distance in [12,7,5,4,3]:
#         return 1/distance
#     elif (distance%12 in [12,7,5,4,3]) and (distance//12 <4) :
#         return 1/(distance%12) + alpha*(distance//12)
#     else: return 0
#     
# def frequency_score(fundamental_frequency, f):
#     
#     if fundamental_frequency==0:return 0
#     
#     harmonic_number = np.round(f/fundamental_frequency)
#     closest_harmonic_frequency=harmonic_number*fundamental_frequency
#     difference = 1200*np.log(closest_harmonic_frequency/f)/np.log(2)
#     
#     if abs(difference)<50:
#         return harmonic_number
#     else: return 0
#     
# def series_harmonic_score(fundamental_frequency,frequencies):
#     score =0
#     for f in frequencies:
#         score += frequency_score(fundamental_frequency,f) 
#     
#     return score
# 
# def series_score(frequencies):
#     
#     scores=[]
#     for i in range(0,1000):
#         scores.append(series_harmonic_score(i, frequencies))
#     
#     return scores
# 
#     
#     
# =============================================================================
if __name__=="__main__":
    
    N = NoteSpace()
    N.create_bipartite_graph()
    nx.draw(N.projected_graph())
    