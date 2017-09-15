import numpy as np
from math import log2
import progressbar

from agent import encode_field, decode_field

def get_cost(state, params):
    field = np.array(decode(state)).reshape(-1)
    place = [0, 1, 1, 0, 1, 2, 2, 1, 1, 2, 2, 1, 0, 1, 1, 0]
    res = [place[i] if c == 0 else place[log2(c) * 3 + place[i]] * np.log(c) for i, c in enumerate(field)]
    return sum(res)




