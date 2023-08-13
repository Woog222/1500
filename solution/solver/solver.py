import copy
from random import shuffle

import config
from solution.Solution import Solution
from itertools import combinations
from object.graph import Graph
from solution.vehicle_alloc import Vehicle_Alloc
from tool.tools import deque_slice, list_insert, random_combinations, euclidean_distance


class Solver:
    def __init__(self, solution: Solution, graph: Graph, cur_batch):
        self.solution = solution
        self.graph = graph
        self.cur_batch = cur_batch

    def solve(self):

        print(f"\tinit solution -> {self.solution.get_total_cost():.2f}")

        self.swap_spatial_bundles()
        print(f"\tswap spatial bundles -> {self.solution.get_total_cost():.2f}")

        self.swap_vehicles()
        print(f"\tswap vehicles -> {self.solution.get_total_cost():.2f}")

        """
        self.solution.vehicle_list = self.swap_cycles()
        print(f"\tswap cycles -> {self.solution.get_total_cost():.2f}")

        self.solution.vehicle_list = self.swap_orders()
        print(f"\tswap orders -> {self.solution.get_total_cost():.2f}")
        """


    def swap_vehicles(self) -> None:

        swapped = True
        cnt = 0
        while swapped and cnt < 100:
            swapped = False

            for veh1, veh2 in random_combinations(self.solution.vehicle_list, 2, self.graph):

                if self.do_swap_vehicle(veh1, veh2):
                    swapped = True
                    cnt += 1
                    break

    def do_swap_vehicle(self, veh1, veh2) -> bool:
        # capa check
        if veh1.get_max_capa() > veh2.vehicle.capa: return False
        if veh2.get_max_capa() > veh1.vehicle.capa: return False

        temp_veh1 = Vehicle_Alloc(veh1.vehicle, self.graph, veh2.order_list)
        temp_veh2 = Vehicle_Alloc(veh2.vehicle, self.graph, veh1.order_list)

        # violation
        if temp_veh1.get_violation() + temp_veh2.get_violation() > 0: return False

        if len(temp_veh1.order_list) > 0:
            order_helper = temp_veh1.order_list[-1]
            start_time = order_helper.departure_time - order_helper.order.load
            if (start_time > (self.cur_batch + 1) * config.GROUP_INTERVAL) or start_time >= config.MAX_START_TIME:
                return False
        if len(temp_veh2.order_list) > 0:
            order_helper = temp_veh2.order_list[-1]
            start_time = order_helper.departure_time - order_helper.order.load
            if (start_time > (self.cur_batch + 1) * config.GROUP_INTERVAL) or start_time >= config.MAX_START_TIME:
                return False

        # cost reduction check
        original_cost = veh1.get_added_cost() + veh2.get_added_cost()
        new_cost = temp_veh1.get_added_cost() + temp_veh2.get_added_cost()
        if new_cost > original_cost: return False

        # now swap
        temp = veh1.order_list
        veh1.order_list = veh2.order_list
        veh2.order_list = temp
        for veh in [veh1, veh2]: veh.update()
        return True

    def swap_spatial_bundles(self) -> None:

        swapped = True
        cnt = 0
        while swapped and cnt < 100:
            swapped = False

            for veh1, veh2 in random_combinations(self.solution.vehicle_list, 2, self.graph):
                idxs1 = list(range(len(veh1.spatial_bundle)))
                idxs2 = list(range(len(veh2.spatial_bundle)))
                shuffle(idxs1); shuffle(idxs2)

                for idx1, idx2 in zip(idxs1, idxs2):
                    if euclidean_distance(veh1.spatial_bundle[idx1].center, veh2.spatial_bundle[idx2].center) >= config.NEIGHBORHOOD_CRITERION:
                        continue
                    if self.do_swap_spatial_bundle(veh1, veh2, idx1, idx2):
                        swapped = True
                        cnt += 1
                        break

                if swapped: break

    def do_swap_spatial_bundle(self, veh1:Vehicle_Alloc, veh2:Vehicle_Alloc, idx1, idx2) -> bool:

        from1 = from2 = 0
        for bundle in veh1.spatial_bundle[:idx1]: from1 += bundle.get_size()
        for bundle in veh2.spatial_bundle[:idx2]: from2 += bundle.get_size()
        to1 = from1 + veh1.spatial_bundle[idx1].get_size()
        to2 = from2 + veh2.spatial_bundle[idx2].get_size()

        veh1_temp = copy.copy(veh1.order_list)
        veh2_temp = copy.copy(veh2.order_list)
        temp1 = copy.copy(veh1.order_list[from1:to1])
        temp2 = copy.copy(veh2.order_list[from2:to2])
        veh1_temp = list_insert(veh1_temp, from1, to1, temp2)
        veh2_temp = list_insert(veh2_temp, from2, to2, temp1)

        veh1_alloc_temp = Vehicle_Alloc(veh1.vehicle, self.graph, allocated_order_list=veh1_temp)
        veh2_alloc_temp = Vehicle_Alloc(veh2.vehicle, self.graph, allocated_order_list=veh2_temp)

        # violation
        if veh1_alloc_temp.get_violation() + veh2_alloc_temp.get_violation() > 0: return False

        # cost
        prev_cost = veh1.get_added_cost() + veh2.get_added_cost()
        new_cost = veh1_alloc_temp.get_added_cost() + veh2_alloc_temp.get_added_cost()
        if prev_cost < new_cost: return False

        # now swap!
        veh1.order_list = veh1_temp
        veh2.order_list = veh2_temp
        veh1.update(); veh2.update()
        return True

    def swap_cycles(self):
        vehicle_list = self.solution.vehicle_list
        for (veh1, veh2) in combinations(vehicle_list, 2):
            for cycle1_idx in range(len(veh1.cycle_list)):
                for cycle2_idx in range(len(veh2.cycle_list)):
                    if self.do_swap_cycle(veh1, cycle1_idx, veh2, cycle2_idx):
                        self.swap_cycle(veh1, cycle1_idx, veh2, cycle2_idx)
        return vehicle_list

    def do_swap_cycle(self, veh1, cycle1_idx, veh2, cycle2_idx) -> bool:
        try:
            cycle1 = veh1.cycle_list[cycle1_idx]
            cycle2 = veh2.cycle_list[cycle2_idx]
        except:
            return False

        # feasibility - cbm
        max1 = 0
        for order in cycle1.orders:
            max1 = max(order.cbm, max1)
        max2 = 0
        for order in cycle2.orders:
            max2 = max(order.cbm, max2)
        if max1 > veh2.vehicle.capa: return False
        if max2 > veh1.vehicle.capa: return False


        start_idx1 = start_idx2 = 0
        for i in range(cycle1_idx):
            start_idx1 += veh1.cycle_list[i].get_cycle_order_cnt()
        for j in range(cycle2_idx):
            start_idx2 += veh2.cycle_list[j].get_cycle_order_cnt()
        end_idx1 = start_idx1 + cycle1.get_cycle_order_cnt()
        end_idx2 = start_idx2 + cycle2.get_cycle_order_cnt()

        new_order_list1 = veh1.order_list.copy()
        new_order_list2 = veh2.order_list.copy()
        temp = new_order_list1

        #new_order_list1 = deque_slice(new_order_list1, 0, start_idx1) + deque_slice(new_order_list2, start_idx2, end_idx2) + deque_slice(new_order_list1, end_idx1)
        #new_order_list2 = deque_slice(new_order_list1, 0, start_idx2) + deque_slice(new_order_list2, start_idx1, end_idx1) + deque_slice(new_order_list2, end_idx2)

        new_order_list1 = new_order_list1[:start_idx1] + new_order_list2[start_idx2:end_idx2] + new_order_list1[end_idx1:]
        new_order_list2 = new_order_list2[:start_idx2] + temp[start_idx1:end_idx1] + new_order_list2[end_idx2:]

        temp_veh1 = Vehicle_Alloc(veh1.vehicle, self.graph, new_order_list1)
        temp_veh2 = Vehicle_Alloc(veh2.vehicle, self.graph, new_order_list2)
        temp_veh1.update()
        temp_veh2.update()

        if temp_veh1.get_time_violation() + temp_veh2.get_time_violation() > 0: return False

        if len(temp_veh1.order_list) > 0:
            order_helper = temp_veh1.order_list[-1]
            start_time = order_helper.departure_time - order_helper.order.load
            if start_time > (self.cur_batch + 1) * config.GROUP_INTERVAL or start_time >= config.MAX_START_TIME:
                return False
        if len(temp_veh2.order_list) > 0:
            order_helper = temp_veh2.order_list[-1]
            start_time = order_helper.departure_time - order_helper.order.load
            if start_time > (self.cur_batch + 1) * config.GROUP_INTERVAL or start_time >= config.MAX_START_TIME:
                return False

        original_cost = veh1.get_var_cost() + veh2.get_var_cost()
        if veh1.vehicle.get_total_count() == 0 and veh1.get_count() > 0: original_cost += veh1.vehicle.fc
        if veh2.vehicle.get_total_count() == 0 and veh2.get_count() > 0: original_cost += veh2.vehicle.fc
        new_cost = temp_veh1.get_var_cost() + temp_veh2.get_var_cost()
        if veh1.vehicle.get_total_count() == 0 and temp_veh1.get_count() > 0: new_cost += veh1.vehicle.fc
        if veh2.vehicle.get_total_count() == 0 and temp_veh2.get_count() > 0: new_cost += veh2.vehicle.fc

        if new_cost >= original_cost: return False
        return True

    def swap_cycle(self, veh1, cycle1_idx, veh2, cycle2_idx):
        cycle1 = veh1.cycle_list[cycle1_idx]
        cycle2 = veh2.cycle_list[cycle2_idx]

        start_idx1 = start_idx2 = 0
        for i in range(cycle1_idx):
            start_idx1 += veh1.cycle_list[i].get_cycle_order_cnt()
        for j in range(cycle2_idx):
            start_idx2 += veh2.cycle_list[j].get_cycle_order_cnt()
        end_idx1 = start_idx1 + cycle1.get_cycle_order_cnt()
        end_idx2 = start_idx2 + cycle2.get_cycle_order_cnt()

        temp = veh1.order_list


        veh1.order_list = temp[:start_idx1] + veh2.order_list[start_idx2:end_idx2] + temp[end_idx1:]
        veh2.order_list = veh2.order_list[:start_idx2] + temp[start_idx1:end_idx1] + veh2.order_list[end_idx2:]

        #veh1.order_list = deque_slice(temp, 0, start_idx1) + deque_slice(veh2.order_list, start_idx2, end_idx2) + deque_slice(temp,end_idx1)
        #veh2.order_list = deque_slice(veh2.order_list, 0, start_idx2) + deque_slice(temp, start_idx1, end_idx1) + deque_slice(veh2.order_list,end_idx2)


        for veh in [veh1, veh2]:
            veh.update()


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

        temp_veh1 = Vehicle_Alloc(veh1.vehicle, self.graph, veh1.order_list)
        temp_veh2 = Vehicle_Alloc(veh2.vehicle, self.graph, veh2.order_list)
        new_list1 = temp_veh1.order_list.copy()
        new_list1[order1_idx] = order2
        new_list2 = temp_veh2.order_list.copy()
        new_list2[order2_idx] = order1
        temp_veh1.order_list = new_list1
        temp_veh2.order_list = new_list2
        temp_veh1.update()
        temp_veh2.update()

        # feasibility check - time
        if temp_veh1.get_time_violation() > 0: return False
        if temp_veh2.get_time_violation() > 0: return False

        order_helper = temp_veh1.order_list[-1]
        start_time = order_helper.departure_time - order_helper.order.load
        if start_time > (self.cur_batch + 1) * config.GROUP_INTERVAL or start_time >= config.MAX_START_TIME:
            return False
        order_helper = temp_veh2.order_list[-1]
        start_time = order_helper.departure_time - order_helper.order.load
        if start_time > (self.cur_batch + 1) * config.GROUP_INTERVAL or start_time >= config.MAX_START_TIME:
            return False

        # cost reduction check
        original_cost = veh1.get_var_cost() + veh2.get_var_cost()
        new_cost = temp_veh1.get_var_cost() + temp_veh2.get_var_cost()

        if new_cost >= original_cost:
            return False


        return True

    def swap_order(self, veh1, order1_idx, veh2, order2_idx):
        # swap
        temp = veh1.order_list[order1_idx]
        veh1.order_list[order1_idx] = veh2.order_list[order2_idx]
        veh2.order_list[order2_idx] = temp

        for veh in [veh1, veh2]:
            veh.update()
