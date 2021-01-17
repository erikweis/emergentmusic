# Emergent Music

What does complexity sound like? The ideas of complexity apply to a wide range of phenomena, and one of the central themes is emergence. From delocalized interactions of many interacting components, properties or order emerges that can be quite beautiful and surprising, such as the flocking behavior of birds or fish. That begs the question, what would emergent music sound like?

All music today has been written by humans, talented and creative the individuals or groups working to improve an overall product, or AI that has been trained on music written by humans. All this music was written and conceived with some centralized control, i.e. with an overal vision and ability to hear the finished product. But what would music sound like as an emergent phenomena?

This project simulates a group of musicians whose only goal is to maximize the "beauty" of the music in their sonic periphery. They can hear the notes of musicians around them, and respond to what their fellow musicians play, but cannot respond to the overall soundscape in any way. What kind of music could be produced by a set of stochastic, local rules by which musicians choose what notes to play? What local rules produce emergent phenomena we recognize as interesting, beautiful or dynamic?

## Mathematical Model

Musicians are positioned on a graph, and listen only to their neighbors. The graph can take any shape, and the structure of that graph seems to play an important role in what kind of music is produced. Musicians evaluate their currently played note based on that note's proximity to those they hear in *note space*. The note space is created via a bipartite graph of notes and fundamental harmonic series and projecting onto the notes. A notes tie strength to each harmonic series is stronger when that note is a lower harmonic, i.e. an octave, fifth, fourth, or third. Musicians decide to change notes based on some probabilistic parameters, including how well their note fits in with what they here.

## How to Use the Interface

Clone the repository, and then in the command line, run the following.

```
bokeh serve interface.py
```
You can adjust the parameters of the model, though some are not functional. 

[](./interface.png)

## Examples

For some examples, see www.erikweis.com/music. To run, you will need MIDIUtil and networkx, and the simulation outputs a midi file.
