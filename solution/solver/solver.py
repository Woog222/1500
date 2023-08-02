from solution.Solution import Solution
from itertools import combinations
from object.graph import Graph
from simulator.tools import *


class Solver:
    def __init__(self, solution: Solution, graph: Graph, cur_batch):
        self.solution = solution
        self.graph = graph
        self.cur_batch = cur_batch

    def solve(self):
        self.swap_vehicles()
        self.swap_orders()

    def swap_vehicles(self):
        return

    def swap_orders(self):
        vehicle_list = self.solution.vehicle_list

        for (veh1, veh2) in combinations(vehicle_list, 2):
            for order1_idx in range(veh1.get_count()):
                for order2_idx in range(veh2.get_count()):
                    # swap
                    if self.do_swap_order(veh1, order1_idx, veh2, order2_idx):
                        self.swap_order(veh1, order1_idx, veh2, order2_idx)

    def do_swap_order(self, veh1, order1_idx, veh2, order2_idx):
        prev_order1, order1, next_order1, prev_order2, order2, next_order2 = self.return_prev_next(veh1, order1_idx,
                                                                                                   veh2, order2_idx)

        # feasibility check - cbm
        if veh1.get_max_capa() - order1.cbm + order2.cbm > veh1.capa: return False
        if veh2.get_max_capa() - order2.cbm + order1.cbm > veh2.capa: return False

        # feasibility check - time
        new_distance = 0
        if not prev_order1:
            prev_end_time = self.cur_batch * HOUR
            arrival_time = prev_end_time + self.graph.get_time(veh1.veh.start_loc, order2.terminal_id) + \
                           self.graph.get_time(order2.terminal_id, order2.dest_id)
            new_distance += self.graph.get_dist(veh1.veh.start_loc, order2.terminal_id) + \
                            self.graph.get_dist(order2.terminal_id, order2.dest_id)
        else:
            prev_end_time = prev_order1.start_time + prev_order1.load
            if prev_order1.terminal_id != order2.terminal_id:
                arrival_time = prev_end_time + self.graph.get_time(prev_order1.dest_id, order2.terminal_id) + \
                               self.graph.get_time(order2.terminal_id, order2.dest_id)
                new_distance += self.graph.get_dist(prev_order1.dest_id, order2.terminal_id) + \
                                self.graph.get_dist(order2.terminal_id, order2.dest_id)
            else:
                arrival_time = prev_end_time + self.graph.get_time(prev_order1.dest_id, order2.dest_id)
                new_distance += self.graph.get_dist(prev_order1.dest_id, order2.dest_id)
        start_time = can_time_cal(arrival_time, order2.start, order2.end)
        if start_time > order2.end: return False

        if not next_order1:
            end_time = start_time + order2.load
            if end_time > (self.cur_batch + 1) * HOUR: return False
        else:
            end_time = start_time + order2.load
            if order2.terminal_id != next_order2.terminal_id:
                next_start_time = end_time + self.graph.get_time(order2.dest_id, next_order1.terminal_id) + \
                                  self.graph.get_time(next_order1.terminal_id, next_order1.dest_id)
                new_distance += self.graph.get_dist(order2.dest_id, next_order1.terminal_id) + \
                                self.graph.get_dist(next_order1.terminal_id, next_order1.dest_id)
            else:
                next_start_time = end_time + self.graph.get_time(order2.dest_id, next_order1.dest_id)
                new_distance += self.graph.get_dist(order2.dest_id, next_order1.dest_id)
            if next_start_time > next_order1.start_time: return False

        # cost reduction check
        original_distance = 0
        if not prev_order1:
            original_distance += self.graph.get_dist(veh1.veh.cur_loc, order1.terminal_id) + \
                                 self.graph.get_dist(order1.terminal_id, order1.dest_id)
        else:
            if prev_order1.terminal_id != order1.terminal_id:
                original_distance += self.graph.get_dist(prev_order1.dest_id, order1.terminal_id) + \
                                     self.graph.get_dist(order1.terminal_id, order1.dest_id)
            else:
                original_distance += self.graph.get_dist(prev_order1.dest_id, order1.dest_id)

        if next_order1:
            if order1.terminal_id != next_order1.terminal_id:
                original_distance += self.graph.get_dist(order1.dest_id, next_order1.terminal_id) + \
                                     self.graph.get_dist(next_order1.terminal_id, next_order1.dest_id)
            else:
                original_distance += self.graph.get_dist(order1.dest_id, next_order1.dest_id)
        new_cost = veh1.vc * (new_distance - original_distance)

        if new_cost > 0: return False

        return True

    def swap_order(self, veh1, i, veh2, j):
        temp = veh1.order_list[i]
        veh1.order_list[i] = veh1.order_list[j]
        veh2.order_list[j] = temp

    def return_prev_next(self, veh1, i, veh2, j):
        order1 = veh1.order_list[i]
        order2 = veh2.order_list[j]
        # prev_order alloc
        if i == 0:
            prev_order1 = None
        else:
            prev_order1 = veh1.order_list[i - 1]
        if j == 0:
            prev_order2 = None
        else:
            prev_order2 = veh2.order_list[j - 1]
        # next_order alloc
        if i == len(veh1.order_list) - 1:
            next_order1 = None
        else:
            next_order1 = veh1.order_list[i + 1]
        if j == len(veh2.order_list) - 1:
            next_order2 = None
        else:
            next_order2 = veh2.order_list[j + 1]

        return prev_order1, order1, next_order1, prev_order2, order2, next_order2
