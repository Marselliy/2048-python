import numpy as np
import progressbar

from agent import encode, decode

def get_cost(state):
    field = np.array(decode(state))
    
