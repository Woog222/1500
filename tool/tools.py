import itertools
import math
from collections import deque
import random

import config
from object.graph import Graph


def can_time_cal(arrival_time: float, start: int, end: int):
    quotient = int(arrival_time // config.DAY)
    remainder = arrival_time % config.DAY

    if start < end:
        if start <= remainder <= end:
            return arrival_time
        elif remainder < start:
            return quotient * config.DAY + start
        else:  # end < remainder
            return (quotient + 1) * config.DAY + start
    else:
        if end < remainder < start:
            return quotient * config.DAY + start
        else:
            return arrival_time


def euclidean_distance(loc1:(float, float), loc2: (float, float)) -> float:
    scaling_factor = 111

    dx = abs(loc1[0] - loc2[0]); dy = abs(loc1[1] - loc2[1])

    dx *= scaling_factor; dy *= scaling_factor
    return (dx**2 + dy**2)**0.5

def deque_slice(deq:deque, start_idx = 0, end_idx = None):
    return deque(itertools.islice(deq, start_idx, end_idx))


def list_insert(to:list, from_idx:int, to_idx:int, items:list)->list:
    return to[:from_idx] + items + to[to_idx:]

def list_delete(lst:list, from_idx:int ,to_idx) -> list:
    return lst[:from_idx] + lst[to_idx:]

def time_check(order_list, time_limit:int, last:bool): # order_helper list
    if len(order_list) == 0: return True

    order_helper = order_list[-1]
    start_time = order_helper.departure_time - order_helper.order.load

    if last:
        return start_time <= config.MAX_START_TIME
    else:
        return start_time <= time_limit



def random_combinations(lst:list, r:int, graph:Graph):
    all_combinations = list(itertools.combinations(lst, r))

    def fun(veh_tuple):
        veh1 = veh_tuple[0]
        veh2 = veh_tuple[1]

        no = (len(veh1.order_list) == 0) and (len(veh2.order_list) == 0)

        return (1 if no else 0,
                euclidean_distance(
                    graph.get_coordinates(veh1.vehicle.start_loc),
                    graph.get_coordinates(veh2.vehicle.start_loc)
                )
        )

    all_combinations.sort(key = lambda x : fun(x))

    idx = 0
    for i, comb in enumerate(all_combinations):
        veh1 = comb[0]; veh2 = comb[1]
        if (len(veh1.order_list) ==0) and (len(veh2.order_list) == 0):
            break
        else:
            idx += 1
    return all_combinations[:idx]