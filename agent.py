import numpy as np
from random import choice
from logic import *
import progressbar

from math import log2

def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate

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

@static_var('qmasks', [int(mask) for mask in (15 << np.arange(0, 16, 4))])
def warmup():
    def get(x, f):
        x = encode(f([decode(x), [0,0,0,0], [0,0,0,0], [0,0,0,0]])[0][0])
        return x
    print('Warming up state space...')
    bar = progressbar.ProgressBar()
    left_map = {}
    right_map = {}
    place_map = {}
    for i in bar(range(0xffff + 1)):
        left_map[i] = get(i, left)
        right_map[i] = get(i, right)
        
        successors = []
        for mask in warmup.qmasks:
            if (i & mask == 0):
                successors.append((i | (mask & (mask >> 3))))
        place_map[i] = successors
        
    return left_map, right_map, place_map

left_map, right_map, place_map = warmup()

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


@static_var('lmap', left_map)
def move_left(state):
    return \
        (move_left.lmap[(state & 0xffff000000000000) >> 48] << 48) |\
        (move_left.lmap[(state & 0x0000ffff00000000) >> 32] << 32) |\
        (move_left.lmap[(state & 0x00000000ffff0000) >> 16] << 16) |\
        (move_left.lmap[(state & 0x000000000000ffff)])

@static_var('rmap', right_map)
def move_right(state):
    return \
        (move_right.rmap[(state & 0xffff000000000000) >> 48] << 48) |\
        (move_right.rmap[(state & 0x0000ffff00000000) >> 32] << 32) |\
        (move_right.rmap[(state & 0x00000000ffff0000) >> 16] << 16) |\
        (move_right.rmap[(state & 0x000000000000ffff)])

@static_var('lmap', left_map)
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
    c1 = move_up.lmap[c1]
    c2 = move_up.lmap[c2]
    c3 = move_up.lmap[c3]
    c4 = move_up.lmap[c4]
    r1 = (c1 & 0xf000) | ((c2 & 0xf000) >> 4) | ((c3 & 0xf000) >> 8) | ((c4 & 0xf000) >> 12)
    r2 = ((c1 & 0x0f00) << 4) | (c2 & 0x0f00) | ((c3 & 0x0f00) >> 4) | ((c4 & 0x0f00) >> 8)
    r3 = ((c1 & 0x00f0) << 8) | ((c2 & 0x00f0) << 4) | (c3 & 0x00f0) | ((c4 & 0x00f0) >> 4)
    r4 = ((c1 & 0x000f) << 12) | ((c2 & 0x000f) << 8) | ((c3 & 0x000f) << 4) | (c4 & 0x000f)
    return (r1 << 48) | (r2 << 32) | (r3 << 16) | r4

@static_var('rmap', right_map)
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
    c1 = move_down.rmap[c1]
    c2 = move_down.rmap[c2]
    c3 = move_down.rmap[c3]
    c4 = move_down.rmap[c4]
    r1 = (c1 & 0xf000) | ((c2 & 0xf000) >> 4) | ((c3 & 0xf000) >> 8) | ((c4 & 0xf000) >> 12)
    r2 = ((c1 & 0x0f00) << 4) | (c2 & 0x0f00) | ((c3 & 0x0f00) >> 4) | ((c4 & 0x0f00) >> 8)
    r3 = ((c1 & 0x00f0) << 8) | ((c2 & 0x00f0) << 4) | (c3 & 0x00f0) | ((c4 & 0x00f0) >> 4)
    r4 = ((c1 & 0x000f) << 12) | ((c2 & 0x000f) << 8) | ((c3 & 0x000f) << 4) | (c4 & 0x000f)
    return (r1 << 48) | (r2 << 32) | (r3 << 16) | r4
    
def get_successors_move(state):
    return [move_up(state), move_down(state), move_left(state), move_right(state)]

@static_var('pmap', place_map)
def get_successors_place(state):
    return [((r << 48) | (state & 0x0000ffffffffffff)) for r in get_successors_place.pmap[(state & 0xffff000000000000) >> 48]] + \
     [((r << 32) | (state & 0xffff0000ffffffff)) for r in get_successors_place.pmap[(state & 0x0000ffff00000000) >> 32]] + \
     [((r << 16) | (state & 0xffffffff0000ffff)) for r in get_successors_place.pmap[(state & 0x00000000ffff0000) >> 16]] + \
        [(r | (state & 0xffffffffffff0000)) for r in get_successors_place.pmap[state & 0x000000000000ffff]]
    
@static_var('qmasks', [int(mask) for mask in (15 << np.arange(0, 64, 4))])
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
        for mask in is_terminal.qmasks:
            if (state & mask) == 0:
                return False
        return True

def alphabeta(state, depth, maximize, cost, a=(-float('inf')), b=float('inf'), first=True):
    if depth == 0 or is_terminal(state, maximize):
        return cost(state)
    if maximize:
        v = -float('inf')
        if first:
            next_states = {}
        for i, s in enumerate(get_successors_move(state)):
            m = alphabeta(s, depth - 1, False, cost, a, b, first=False)
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
        v = float('inf')
        if first:
            next_states = {}
        for i, s in enumerate(get_successors_place(state)):
            m = alphabeta(s, depth - 1, True, cost, a, b, first=False)
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

def montecarlo(state, maximize, try_num, max_moves):
    next_states = []
    if maximize:
        next_states.extend(get_successors_move(state))
    else:
        next_states.extend(get_successors_place(state))
       
    state_ranks = {}
       
    for in_state in next_states:
        state_ranks[in_state] = 0
        for cur_try in range(try_num):
            cur_max = not maximize
            cur_state = in_state
            move_num = 0
                      
            while not is_terminal(cur_state, cur_max) and move_num < max_moves:
                if cur_max:
                    cur_state = choice(get_successors_move(cur_state))
                else:
                    cur_state = choice(get_successors_place(cur_state))
                cur_max = not cur_max
                move_num += 1
            state_ranks[in_state] += move_num
    if maximize:
        index = np.argmax(list(state_ranks.values()))
    else:
        index = np.argmin(list(state_ranks.values()))
    return list(state_ranks.keys())[index], [index]
    
class Agent():
    def __init__(self, difficulty, cost, algorithm):
        self.difficulty = difficulty
        self.cost = cost
        self.algorithm = algorithm
        self.inf_p = float('inf')
        self.inf_m = -float('inf')

    def player_move(self, state):
        if self.algorithm == 'alphabeta':
            v, moves = alphabeta(state, self.difficulty, True, self.cost)
        elif self.algorithm == 'montecarlo':
            v, moves = montecarlo(state, True, 200, 4 ** self.difficulty)
        return get_successors_move(state)[choice(moves)]

    def adversary_move(self, state, rand=False):
        if rand:
            states = get_successors_place(state)
            if len(states) == 0:
                return state
            return choice(states)
        try:
            if self.algorithm == 'alphabeta':
                v, moves = alphabeta(state, self.difficulty, False, self.cost)
            elif self.algorithm == 'montecarlo':
                v, moves = montecarlo(state, False, 200, 4 ** self.difficulty)
        except TypeError:
            return state
        
        return get_successors_place(state)[choice(moves)]
