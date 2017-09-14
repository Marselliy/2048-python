import numpy as np
from random import choice
from logic import *

from math import log2

qmasks = [int(mask) for mask in (15 << np.arange(0, 16, 4))]

def encode(row):
    row = [0 if r == 0 else int(log2(r)) for r in row]
    return row[3] | (row[2] << 4) | (row[1] << 8) | (row[0] << 12) 
def decode(x):
    row = (x & 61440) >> 12, (x & 3840) >> 8, (x & 240) >> 4, x & 15
    row = [0 if c == 0 else 2 ** c for c in row]
    return row
def encode_field(field):
    return (encode(field[0]) << 48) | (encode(field[1]) << 32) | (encode(field[2]) << 16) | encode(field[3])
def decode_field(x):
    return [decode((x & 0xffff000000000000) >> 48),
        decode((x & 0x0000ffff00000000) >> 32),
        decode((x & 0x00000000ffff0000) >> 16),
        decode(x & 0x000000000000ffff)]
def warmup():
    def get(x, f):
        x = encode(f([decode(x), [0,0,0,0], [0,0,0,0], [0,0,0,0]])[0][0])
        return x
    left_map = {}
    right_map = {}
    place_map = {}
    costs = {}
    for i in range(0xffff + 1):
        left_map[i] = get(i, left)
        right_map[i] = get(i, right)
        costs[i] = cost(i)
        
        successors = []
        for mask in qmasks:
            if (i & mask == 0):
                successors.append((i | (mask & (mask >> 3))))
        place_map[i] = successors
        
    return left_map, right_map, place_map, costs

def cost(row):
    row = [0 if c == 0 else (3 ** np.log(c)) for c in decode(row)]
    s = sum(row)
    return s

def init_state():
#    field = add_two(new_game(4))
    field = [[2, 0, 4, 4], [2, 256, 4, 4], [2, 32, 4, 4], [2, 0, 4, 16]]
    r1, r2, r3, r4 = [encode(f) for f in field]
    
    return r1 << 48 | r2 << 32 | r3 << 16 | r4

def print_state(state):
    rows = (state & 0xffff000000000000) >> 48, \
        (state & 0x0000ffff00000000) >> 32, \
        (state & 0x00000000ffff0000) >> 16, \
        (state & 0x000000000000ffff)
    print(np.array([decode(r) for r in rows]))

def move_left(state):
    return \
        (lmap[(state & 0xffff000000000000) >> 48] << 48) |\
        (lmap[(state & 0x0000ffff00000000) >> 32] << 32) |\
        (lmap[(state & 0x00000000ffff0000) >> 16] << 16) |\
        (lmap[(state & 0x000000000000ffff)])

def move_right(state):
    return \
        (rmap[(state & 0xffff000000000000) >> 48] << 48) |\
        (rmap[(state & 0x0000ffff00000000) >> 32] << 32) |\
        (rmap[(state & 0x00000000ffff0000) >> 16] << 16) |\
        (rmap[(state & 0x000000000000ffff)])

def move_up(state):
    c1 = (state & 0xf000000000000000) >> 48 | \
        (state & 0x0000f00000000000) >> 36 | \
        (state & 0x00000000f0000000) >> 24 | \
        (state & 0x000000000000f000) >> 12
    c2 = (state & 0x0f00000000000000) >> 44 | \
        (state & 0x00000f0000000000) >> 32 | \
        (state & 0x000000000f000000) >> 20 | \
        (state & 0x0000000000000f00) >> 8
    c3 = (state & 0x00f0000000000000) >> 40 | \
        (state & 0x000000f000000000) >> 28 | \
        (state & 0x0000000000f00000) >> 16 | \
        (state & 0x00000000000000f0) >> 4
    c4 = (state & 0x000f000000000000) >> 36 | \
        (state & 0x0000000f00000000) >> 24 | \
        (state & 0x00000000000f0000) >> 12 | \
        (state & 0x000000000000000f)
    c1 = lmap[c1]
    c2 = lmap[c2]
    c3 = lmap[c3]
    c4 = lmap[c4]
    r1 = (c1 & 0xf000) | ((c2 & 0xf000) >> 4) | ((c3 & 0xf000) >> 8) | ((c4 & 0xf000) >> 12)
    r2 = ((c1 & 0x0f00) << 4) | (c2 & 0x0f00) | ((c3 & 0x0f00) >> 4) | ((c4 & 0x0f00) >> 8)
    r3 = ((c1 & 0x00f0) << 8) | ((c2 & 0x00f0) << 4) | (c3 & 0x00f0) | ((c4 & 0x00f0) >> 4)
    r4 = ((c1 & 0x000f) << 12) | ((c2 & 0x000f) << 8) | ((c3 & 0x000f) << 4) | (c4 & 0x000f)
    return (r1 << 48) | (r2 << 32) | (r3 << 16) | r4

def move_down(state):
    c1 = (state & 0xf000000000000000) >> 48 | \
        (state & 0x0000f00000000000) >> 36 | \
        (state & 0x00000000f0000000) >> 24 | \
        (state & 0x000000000000f000) >> 12
    c2 = (state & 0x0f00000000000000) >> 44 | \
        (state & 0x00000f0000000000) >> 32 | \
        (state & 0x000000000f000000) >> 20 | \
        (state & 0x0000000000000f00) >> 8
    c3 = (state & 0x00f0000000000000) >> 40 | \
        (state & 0x000000f000000000) >> 28 | \
        (state & 0x0000000000f00000) >> 16 | \
        (state & 0x00000000000000f0) >> 4
    c4 = (state & 0x000f000000000000) >> 36 | \
        (state & 0x0000000f00000000) >> 24 | \
        (state & 0x00000000000f0000) >> 12 | \
        (state & 0x000000000000000f)
    c1 = rmap[c1]
    c2 = rmap[c2]
    c3 = rmap[c3]
    c4 = rmap[c4]
    r1 = (c1 & 0xf000) | ((c2 & 0xf000) >> 4) | ((c3 & 0xf000) >> 8) | ((c4 & 0xf000) >> 12)
    r2 = ((c1 & 0x0f00) << 4) | (c2 & 0x0f00) | ((c3 & 0x0f00) >> 4) | ((c4 & 0x0f00) >> 8)
    r3 = ((c1 & 0x00f0) << 8) | ((c2 & 0x00f0) << 4) | (c3 & 0x00f0) | ((c4 & 0x00f0) >> 4)
    r4 = ((c1 & 0x000f) << 12) | ((c2 & 0x000f) << 8) | ((c3 & 0x000f) << 4) | (c4 & 0x000f)
    return (r1 << 48) | (r2 << 32) | (r3 << 16) | r4
    
def get_successors_move(state):
    return [move_up(state), move_down(state), move_left(state), move_right(state)]

def get_successors_place(state):
    return [((r << 48) | (state & 0x0000ffffffffffff)) for r in pmap[(state & 0xffff000000000000) >> 48]] + \
     [((r << 32) | (state & 0xffff0000ffffffff)) for r in pmap[(state & 0x0000ffff00000000) >> 32]] + \
     [((r << 16) | (state & 0xffffffff0000ffff)) for r in pmap[(state & 0x00000000ffff0000) >> 16]] + \
        [(r | (state & 0xffffffffffff0000)) for r in pmap[state & 0x000000000000ffff]]
    
    
def is_terminal(state, mode):
    if mode:
        if move_left(state) != state:
            return False
        if move_right(state) != state:
            return False
        if move_up(state) != state:
            return False
        if move_down(state) != state:
            return False
        return True
    else:
        for mask in qmasks:
            if (state & mask) == 0:
                return False
        return True

def get_cost(state):
    return costs[(state & 0xffff000000000000) >> 48] + \
        costs[(state & 0x0000ffff00000000) >> 32] + \
        costs[(state & 0x00000000ffff0000) >> 16] + \
        costs[(state & 0x000000000000ffff)]
        
inf_p = float('inf')
inf_m = -float('inf')

def alphabeta(state, depth, a, b, maximize, first=True):
    if depth == 0 or is_terminal(state, maximize):
        return get_cost(state)
    if maximize:
        v = inf_m
        if first:
            next_states = {}
        for i, s in enumerate(get_successors_move(state)):
            m = alphabeta(s, depth - 1, a, b, False, first=False)
            if m >= v:
                v = m
                if first:
                    if m in next_states.keys():
                        next_states[m].append(i)
                    else:
                        next_states[m] = [i]
            a = max(a, v)
            if b <= a:
                break
        if first:
            return v, next_states[v]
        return v
    else:
        v = inf_p
        if first:
            next_states = {}
        for i, s in enumerate(get_successors_place(state)):
            m = alphabeta(s, depth - 1, a, b, True, first=False)
            if m <= v:
                v = m
                if first:
                    if m in next_states.keys():
                        next_states[m].append(i)
                    else:
                        next_states[m] = [i]
            b = min(b, v)
            if b <= a:
                break
        if first:
            return v, next_states[v]
        return v
    
class Agent():
    def __init__(self, difficulty):
        self.difficulty = difficulty
        global lmap, rmap, pmap, costs
        lmap, rmap, pmap, costs = warmup()

    def player_move(self, state):
        v, moves = alphabeta(state, self.difficulty, inf_m, inf_p, True)
        return get_successors_move(state)[choice(moves)]

    def adversary_move(self, state, rand=False):
        if rand:
            states = get_successors_place(state)
            if len(states) == 0:
                return state
            return choice(states)
        try:
            v, moves = alphabeta(state, self.difficulty, inf_m, inf_p, False)
        except TypeError:
            return state
        
        return get_successors_place(state)[choice(moves)]
