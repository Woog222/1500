import itertools
import math
from collections import deque
import random

from config import *

def can_time_cal(arrival_time:int, start:int ,end:int):
    quotient = arrival_time // DAY
    remainder = arrival_time % DAY

    if start < end:
        if start<= remainder and remainder <= end:
            return arrival_time
        elif remainder < start:
            return quotient*DAY + start
        else: # end < remainder
            return (quotient+1)*DAY + start
    else:
        if end < remainder and remainder < start:
            return quotient*DAY + start
        else:
            return arrival_time


def euclidean_distance(loc1:(float, float), loc2: (float, float)) -> float:
    dx = loc1[0] - loc2[0]; dy = loc1[1] - loc2[1]
    return math.sqrt(dx**2 + dy**2)

def deque_slice(deq:deque, start_idx = 0, end_idx = None):
    return deque(itertools.islice(deq, start_idx, end_idx))


def list_insert(to:list, from_idx:int, to_idx:int, items:list)->list:
    return to[:from_idx] + items + to[to_idx:]


def random_combinations(lst:list, r:int):
    all_combinations = list(itertools.combinations(lst, r))
    random.shuffle(all_combinations)
    return all_combinations