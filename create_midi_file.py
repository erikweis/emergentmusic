# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 20:49:34 2021

@author: Erik
"""

from midiutil.MidiFile import MIDIFile
import os
import networkx as nx

def create_midi_file(ensemble, tempo):
    
    num_players = len(ensemble.G)
    mf = MIDIFile(num_players)
    channel = 0 #all on the same channel?
    
    for node in ensemble.G.nodes():
        
        # initialize new track
        track = node #track index is the same as node index
        time = 0 #start at beginning
        mf.addTrackName(track,time,"Player {}".format(node))
        mf.addProgramChange(track, channel, time, 42)
        mf.addTempo(track, time, tempo)
        
        #get player object and get data
        player=ensemble.G.nodes[node]['player']
        data = player.data
        
        #add notes from (# note time = 0 here)
        for pitch, volume, duration in data:
            mf.addNote(track, channel, pitch, time, duration, volume)
            time += duration
    
    savefile(mf)

def savefile(mf):
    
    #get filename
    exists, i = False,0
    dirpath=os.path.dirname(os.path.realpath(__file__)) +'\output_1'
    while exists==False:
        filename=os.path.join(dirpath,'song_{}.mid'.format(i))
        if os.path.exists(filename)==False:
            exists=True
        else: i+=1
    
    # write it to disk
    with open(filename, 'wb') as outf:
        mf.writeFile(outf)
        
    print(filename)