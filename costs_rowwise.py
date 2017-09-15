import numpy as np
import progressbar

from agent import encode, decode

def cost(row):
    row = [0 if c == 0 else (3 ** np.log(c)) for c in decode(row)]
    s = sum(row)
    return s

def warmup():
    def get(x, f):
        x = encode(f([decode(x), [0,0,0,0], [0,0,0,0], [0,0,0,0]])[0][0])
        return x
    print('Warming up costs...')
    bar = progressbar.ProgressBar()
    costs = {}
    for i in bar(range(0xffff + 1)):
        costs[i] = cost(i)
        
    return costs

costs = warmup()

def get_cost(state):
    return costs[(state & 0xffff000000000000) >> 48] + \
        costs[(state & 0x0000ffff00000000) >> 32] + \
        costs[(state & 0x00000000ffff0000) >> 16] + \
        costs[(state & 0x000000000000ffff)]