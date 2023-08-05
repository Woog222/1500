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
        # self.solution.vehicle_list = self.swap_vehicles()
        self.solution.vehicle_list = self.swap_orders()

    def swap_vehicles(self):
        vehicle_list = self.solution.vehicle_list
        swap_count = 0
        for (veh1, veh2) in combinations(vehicle_list, 2):
            if self.do_swap_vehicle(veh1, veh2):
                swap_count += 1
                self.swap_vehicle(veh1, veh2)
        return vehicle_list

    def do_swap_vehicle(self, veh1, veh2):
        # capa check
        if veh1.get_max_capa() > veh2.vehicle.capa: return False
        if veh2.get_max_capa() > veh1.vehicle.capa: return False

        # time check
        if len(veh2.order_list) > 0:
            arrival_time1 = veh1.vehicle.free_time + \
                            self.graph.get_time(veh1.vehicle.start_loc, veh2.order_list[0].order.terminal_id) + \
                            self.graph.get_time(veh2.order_list[0].order.terminal_id, veh2.order_list[0].order.dest_id)
            arrival_time2 = veh2.vehicle.free_time + \
                            self.graph.get_time(veh2.vehicle.start_loc, veh2.order_list[0].order.terminal_id) + \
                            self.graph.get_time(veh2.order_list[0].order.terminal_id, veh2.order_list[0].order.dest_id)
            if arrival_time1 > arrival_time2: return False
        if len(veh1.order_list) > 0:
            arrival_time2 = veh2.vehicle.free_time + \
                           self.graph.get_time(veh2.vehicle.start_loc, veh1.order_list[0].order.terminal_id) + \
                           self.graph.get_time(veh1.order_list[0].order.terminal_id, veh1.order_list[0].order.dest_id)
            arrival_time1 = veh1.vehicle.free_time + \
                            self.graph.get_time(veh1.vehicle.start_loc, veh1.order_list[0].order.terminal_id) + \
                            self.graph.get_time(veh1.order_list[0].order.terminal_id, veh1.order_list[0].order.dest_id)
            if arrival_time2 > arrival_time1: return False

        temp_veh1 = veh1
        temp_veh2 = veh2
        temp = temp_veh1.order_list
        temp_veh1.order_list = temp_veh2.order_list
        temp_veh2.order_list = temp
        temp_veh1.reset_cache()
        temp_veh2.reset_cache()

        # cost reduction check
        original_cost = veh1.get_var_cost() + veh2.get_var_cost()
        if len(veh1.vehicle.allocated_cycle_list) + len(veh1.order_list) > 0: original_cost += veh1.vehicle.fc
        if len(veh2.vehicle.allocated_cycle_list) + len(veh2.order_list) > 0: original_cost += veh2.vehicle.fc
        new_cost = temp_veh1.get_var_cost() + temp_veh2.get_var_cost()
        if len(veh1.vehicle.allocated_cycle_list) + len(temp_veh1.order_list) > 0: new_cost += veh1.vehicle.fc
        if len(veh2.vehicle.allocated_cycle_list) + len(temp_veh2.order_list) > 0: new_cost += veh2.vehicle.fc
        if new_cost >= original_cost: return False

        return True


    def swap_vehicle(self, veh1, veh2):
        temp = veh1.order_list
        veh1.order_list = veh2.order_list
        veh2.order_list = temp
        for veh in [veh1, veh2]:
            veh.update_cycle()
            veh.reset_cache()


    def swap_orders(self):
        vehicle_list = self.solution.vehicle_list
        swap_count = 0
        for (veh1, veh2) in combinations(vehicle_list, 2):
            for order1_idx in range(veh1.get_count()):
                for order2_idx in range(veh2.get_count()):
                    # swap
                    if self.do_swap_order(veh1, order1_idx, veh2, order2_idx):
                        swap_count += 1
                        self.swap_order(veh1, order1_idx, veh2, order2_idx)
        print(swap_count)
        return vehicle_list

    def do_swap_order(self, veh1, order1_idx, veh2, order2_idx):
        prev_order1, order1, next_order1, prev_order2, order2, next_order2 = self.return_prev_next(veh1, order1_idx,
                                                                                                   veh2, order2_idx)

        # feasibility check - cbm
        if veh1.get_max_capa() - order1.cbm + order2.cbm > veh1.vehicle.capa: return False
        if veh2.get_max_capa() - order2.cbm + order1.cbm > veh2.vehicle.capa: return False

        # feasibility check - time
        new_distance = 0
        if not prev_order1:
            prev_end_time = self.cur_batch * HOUR
            arrival_time = prev_end_time + self.graph.get_time(veh1.vehicle.start_loc, order2.terminal_id) + \
                           self.graph.get_time(order2.terminal_id, order2.dest_id)
            new_distance += self.graph.get_dist(veh1.vehicle.start_loc, order2.terminal_id) + \
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
            if end_time > (self.cur_batch + 1) * GROUP_INTERVAL: return False
        else:
            end_time = start_time + order2.load
            if order2.terminal_id != next_order1.terminal_id:
                next_start_time = end_time + self.graph.get_time(order2.order.dest_id, next_order1.terminal_id) + \
                                  self.graph.get_time(next_order1.terminal_id, next_order1.order.dest_id)
                new_distance += self.graph.get_dist(order2.order.dest_id, next_order1.terminal_id) + \
                                self.graph.get_dist(next_order1.terminal_id, next_order1.order.dest_id)
            else:
                next_start_time = end_time + self.graph.get_time(order2.order.dest_id, next_order1.order.dest_id)
                new_distance += self.graph.get_dist(order2.order.dest_id, next_order1.order.dest_id)
            if next_start_time > next_order1.start_time: return False

        # cost reduction check
        original_distance = 0
        if not prev_order1:
            original_distance += self.graph.get_dist(veh1.vehicle.start_loc, order1.order.terminal_id) + \
                                 self.graph.get_dist(order1.order.terminal_id, order1.order.dest_id)
        else:
            if prev_order1.order.terminal_id != order1.order.terminal_id:
                original_distance += self.graph.get_dist(prev_order1.order.dest_id, order1.order.terminal_id) + \
                                     self.graph.get_dist(order1.order.terminal_id, order1.order.dest_id)
            else:
                original_distance += self.graph.get_dist(prev_order1.order.dest_id, order1.order.dest_id)

        if next_order1:
            if order1.order.terminal_id != next_order1.order.terminal_id:
                original_distance += self.graph.get_dist(order1.order.dest_id, next_order1.order.terminal_id) + \
                                     self.graph.get_dist(next_order1.order.terminal_id, next_order1.order.dest_id)
            else:
                original_distance += self.graph.get_dist(order1.order.dest_id, next_order1.order.dest_id)
        cost_diff = veh1.vehicle.vc * (new_distance - original_distance)

        if cost_diff >= 0: return False

        return True

    def swap_order(self, veh1, i, veh2, j):
        temp = veh1.order_list[i]
        veh1.order_list[i] = veh2.order_list[j]
        veh2.order_list[j] = temp
        for veh in [veh1, veh2]:
            veh.update_cycle()
            veh.reset_cache()

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
