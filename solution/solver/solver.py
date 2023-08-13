import copy

import config
from solution.Solution import Solution
from itertools import combinations
from object.graph import Graph
from solution.vehicle_alloc import Vehicle_Alloc


class Solver:
    def __init__(self, solution: Solution, graph: Graph, cur_batch):
        self.solution = solution
        self.graph = graph
        self.cur_batch = cur_batch

    def solve(self):
        # self.solution.vehicle_list = self.swap_vehicles()
        # self.solution.vehicle_list = self.swap_cycles()
        # self.solution.vehicle_list = self.swap_orders()
        self.solution.vehicle_list = self.insert_cycles()

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

        temp_veh1 = Vehicle_Alloc(veh1.vehicle, self.graph, veh2.order_list)
        temp_veh2 = Vehicle_Alloc(veh2.vehicle, self.graph, veh1.order_list)
        temp_veh1.update()
        temp_veh2.update()

        if temp_veh1.get_time_violation() > 0: return False
        if temp_veh2.get_time_violation() > 0: return False


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
            veh.update()

    def swap_orders(self):
        vehicle_list = self.solution.vehicle_list
        for veh1 in vehicle_list:
            for veh2 in vehicle_list:
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

    def swap_cycles(self):
        vehicle_list = self.solution.vehicle_list
        for veh1 in vehicle_list:
            for veh2 in vehicle_list:
                for cycle1_idx in range(len(veh1.cycle_list)):
                    for cycle2_idx in range(len(veh2.cycle_list)):
                        if self.do_swap_cycle(veh1, cycle1_idx, veh2, cycle2_idx):
                            self.swap_cycle(veh1, cycle1_idx, veh2, cycle2_idx)
        return vehicle_list

    def do_swap_cycle(self, veh1, cycle1_idx, veh2, cycle2_idx):
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


        for veh in [veh1, veh2]:
            veh.update()


    def insert_cycles(self):
        insert_count = 0
        vehicle_list = vehicle_list2 = self.solution.vehicle_list
        vehicle_list.sort(key=lambda x: (x.vehicle.get_total_count(), x.get_count()))
        for from_veh in vehicle_list:
            for cycle_idx in range(len(from_veh.cycle_list)):
                vehicle_list2.sort(key=lambda x: x.get_waiting_time()+max(0, (self.cur_batch+1)*config.GROUP_INTERVAL-x.get_after_time()))
                for to_veh in vehicle_list2:
                    best_idx, feasibility = self.do_insert_cycle(from_veh, to_veh, cycle_idx)
                    if feasibility:
                        insert_count += 1
                        self.insert_cycle(from_veh, to_veh, cycle_idx, best_idx)
        print("insert count: ", insert_count)
        return vehicle_list

    def do_insert_cycle(self, from_veh, to_veh, cycle_idx):
        try: cycle = from_veh.cycle_list[cycle_idx]
        except: return -1, False

        # feasibility check - cbm
        max_cbm = 0
        for order in cycle.orders:
            max_cbm = max(max_cbm, order.cbm)
        if max_cbm > to_veh.vehicle.capa: return -1, False

        start_idx = 0
        for i in range(cycle_idx-1): start_idx += from_veh.cycle_list[i].get_cycle_order_cnt()
        end_idx = start_idx + cycle.get_cycle_order_cnt()
        target_orders = from_veh.order_list[start_idx:end_idx]

        new_order_list = from_veh.order_list[:start_idx] + from_veh.order_list[end_idx:]
        new_from_veh = Vehicle_Alloc(from_veh.vehicle, self.graph, new_order_list)
        new_from_veh.update_cycle()
        original_cost = from_veh.get_var_cost()
        if from_veh.vehicle.get_total_count()==0 and from_veh.get_count() > 0: original_cost += from_veh.vehicle.fc
        new_cost = new_from_veh.get_var_cost()
        if new_from_veh.vehicle.get_total_count()==0 and new_from_veh.get_count() > 0:
            new_cost += from_veh.vehicle.fc


        start_idx2 = 0
        best_idx = -1
        best_cost = config.MAX
        for to_cycle_idx in range(-1, len(to_veh.cycle_list)):
            if to_cycle_idx != -1:
                to_cycle = to_veh.cycle_list[to_cycle_idx]
                start_idx2 += to_cycle.get_cycle_order_cnt()
            new_order_list = to_veh.order_list[:start_idx2] + target_orders + to_veh.order_list[start_idx2:]
            new_to_veh = Vehicle_Alloc(to_veh.vehicle, self.graph, new_order_list)
            new_to_veh.update_cycle()

            if new_to_veh.get_time_violation() > 0: continue

            if new_to_veh.get_after_time() > (self.cur_batch + 1)*config.GROUP_INTERVAL or \
                    new_to_veh.get_after_time() > config.MAX_START_TIME: continue

            original_cost2 = original_cost + to_veh.get_var_cost()
            if to_veh.vehicle.get_total_count() == 0 and to_veh.get_count() > 0: original_cost2 += to_veh.vehicle.fc
            new_cost2 = new_cost + new_to_veh.get_var_cost()
            if new_to_veh.vehicle.get_total_count() == 0 and new_to_veh.get_count() > 0:
                new_cost2 += to_veh.vehicle.fc

            if new_cost2 >= original_cost2: continue


            if new_cost2 < best_cost:
                best_idx = start_idx2
                best_cost = new_cost2

        if best_idx < 0: return -1, False

        return best_idx, True

    def insert_cycle(self, from_veh, to_veh, cycle_idx, best_idx):
        cycle = from_veh.cycle_list[cycle_idx]
        start_idx = 0
        for i in range(cycle_idx-1): start_idx += from_veh.cycle_list[i].get_cycle_order_cnt()
        end_idx = start_idx + cycle.get_cycle_order_cnt()
        new_order_list = from_veh.order_list[:start_idx] + from_veh.order_list[end_idx:]
        target_list = from_veh.order_list[start_idx:end_idx]
        from_veh.order_list = new_order_list
        to_veh.order_list = to_veh.order_list[:best_idx] + target_list + to_veh.order_list[best_idx:]

        for veh in [from_veh, to_veh]:
            veh.update_cycle()

    def next_to_veh(self, vehicle_list):
        max_waiting_time = -1
        to_veh = None
        for veh in vehicle_list:
            waiting_time = veh.get_waiting_time() + max((self.cur_batch + 1) * config.GROUP_INTERVAL - veh.get_after_time(), 0)
            if waiting_time > max_waiting_time:
                max_waiting_time = waiting_time
                to_veh = veh
        return to_veh









