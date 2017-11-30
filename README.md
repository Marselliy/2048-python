2048-python
===========

The game is a more complicated version of popular [2048](https://github.com/gabrielecirulli/2048) game by Gabriele Cirulli.
This version embeds an intelligent agent that spawns new cells in the worst position (for the player) instead of a random one like in the original game. 

The game is written using Python and TKinter.

![screenshot](img/screenshot.png)

To start the game, run:
    
    $ python3 puzzle.py [player] [adversary] [algorithm] [difficulty]
  
  - player:      player or AI 
  - adversary:   random or AI 
  - algorithm:   alphabeta or montecarlo
  - difficulty:  (integer greater than 0. Note: large difficulty values require a lot of computations)


Contributors:
==

- [Tay Yang Shun](http://github.com/yangshun)
- [Emmanuel Goh](http://github.com/emman27)
- [Marselliy](https://github.com/Marselliy)
