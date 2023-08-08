from solution.Solution import Solution
from itertools import combinations
from object.graph import Graph
from simulator.tools import *
import copy


class Solver:
    def __init__(self, solution: Solution, graph: Graph, cur_batch):
        self.solution = solution
        self.graph = graph
        self.cur_batch = cur_batch

    def solve(self):
        self.solution.vehicle_list = self.swap_vehicles()
        self.solution.vehicle_list = self.swap_orders()

    def swap_vehicles(self):
        vehicle_list = self.solution.vehicle_list
        for (veh1, veh2) in combinations(vehicle_list, 2):
            if self.do_swap_vehicle(veh1, veh2):
                self.swap_vehicle(veh1, veh2)
        return vehicle_list

    def do_swap_vehicle(self, veh1, veh2):
        # capa check
        if veh1.get_max_capa() > veh2.vehicle.capa: return False
        if veh2.get_max_capa() > veh1.vehicle.capa: return False

        temp_veh1 = copy.copy(veh1)
        temp_veh2 = copy.copy(veh2)
        temp = temp_veh1.order_list
        temp_veh1.order_list = temp_veh2.order_list
        temp_veh2.order_list = temp
        temp_veh1.update_cycle()
        temp_veh2.update_cycle()

        if temp_veh1.get_time_violation() > 0: return False
        if temp_veh2.get_time_violation() > 0: return False

        # cost reduction check
        original_cost = veh1.get_var_cost() + veh2.get_var_cost()
        if veh1.vehicle.get_total_count()==0 and veh1.get_count() > 0: original_cost += veh1.vehicle.fc
        if veh2.vehicle.get_total_count()==0 and veh2.get_count() > 0: original_cost += veh2.vehicle.fc

        new_cost = temp_veh1.get_var_cost() + temp_veh2.get_var_cost()
        if veh1.vehicle.get_total_count()==0 and temp_veh1.get_count() > 0: new_cost += veh1.vehicle.fc
        if veh2.vehicle.get_total_count()==0 and temp_veh2.get_count() > 0: new_cost += veh2.vehicle.fc
        if new_cost >= original_cost: return False

        return True


    def swap_vehicle(self, veh1, veh2):
        temp = veh1.order_list
        veh1.order_list = veh2.order_list
        veh2.order_list = temp
        for veh in [veh1, veh2]:
            veh.update_cycle()


    def swap_orders(self):
        vehicle_list = self.solution.vehicle_list
        for (veh1, veh2) in combinations(vehicle_list, 2):
            for order1_idx in range(veh1.get_count()):
                for order2_idx in range(veh2.get_count()):
                    if self.do_swap_order(veh1, order1_idx, veh2, order2_idx):
                        self.swap_order(veh1, order1_idx, veh2, order2_idx)
        return vehicle_list

    def do_swap_order(self, veh1, order1_idx, veh2, order2_idx):
        order1 = veh1.order_list[order1_idx]
        order2 = veh2.order_list[order2_idx]

        # feasibility check - cbm
        if order2.order.cbm > veh1.vehicle.capa: return False
        if order1.order.cbm > veh2.vehicle.capa: return False

        temp_veh1 = copy.copy(veh1)
        temp_veh2 = copy.copy(veh2)
        new_list1 = temp_veh1.order_list.copy()
        new_list1[order1_idx] = order2
        new_list2 = temp_veh2.order_list.copy()
        new_list2[order2_idx] = order1
        temp_veh1.order_list = new_list1
        temp_veh2.order_list = new_list2
        temp_veh1.update_cycle()
        temp_veh2.update_cycle()

        # feasibility check - time
        if temp_veh1.get_time_violation() > 0: return False
        if temp_veh2.get_time_violation() > 0: return False

        # cost reduction check
        original_cost = veh1.get_var_cost() + veh2.get_var_cost()
        new_cost = temp_veh1.get_var_cost() + temp_veh2.get_var_cost()

        if new_cost >= original_cost: return False


        return True

    def swap_order(self, veh1, order1_idx, veh2, order2_idx):
        # swap
        temp = veh1.order_list[order1_idx]
        veh1.order_list[order1_idx] = veh2.order_list[order2_idx]
        veh2.order_list[order2_idx] = temp

        for veh in [veh1, veh2]:
            veh.update_cycle()

