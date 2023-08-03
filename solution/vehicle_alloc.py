
import copy

from object.Cycle import Cycle
from object.graph import Graph
from object.order import Order
from object.vehicle import Vehicle


class Vehicle_Alloc:

    def __init__(self, vehicle:Vehicle, graph:Graph, allocated_order_list:list[Order]):
        self.graph = graph
        self.vehicle = vehicle # const
        self.order_list = [] # temp list, not including terminal loading order (-1)
        self.cycle_list = [] #

        # cache
        self.route_cache = [-1]
        self.dist_cache = -1
        self.work_cache = -1
        self.max_capa_cache = -1
        self.after_time_cache = -1


    """
    When any modifications are made to the "self.order_list",
    update cycle must be called
    """


    def update_cycle(self):
        self.reset_cache()

        self.cycle_list = []
        if len(self.order_list) == 0: return

        temp_orders = []
        left = self.vehicle.capa
        cur_terminal = -1

        for order in self.order_list:

            # terminal loading
            if cur_terminal != order.terminal_id or left < order.cbm:
                if cur_terminal != -1:
                    self.cycle_list.append(Cycle(copy.deepcopy(temp_orders), self.vehicle))
                cur_terminal = order.terminal_id
                left = self.vehicle.capa
                temp_orders = []

            left -= order.cbm
            temp_orders.append(order)

        # last one
        self.cycle_list.append(Cycle(copy.deepcopy(temp_orders), self.vehicle))
        return


    def reset_cache(self):
        self.route_cache = [-1]
        self.dist_cache = -1
        self.work_cache = -1
        self.max_capa_cache = -1
        self.after_time_cache = -1

    """
           Complex Methods
    """

    def get_route(self):
        """
            In this batch problem, the 'start_loc' (which might be determined during the previous batch problem)
            moves to the 'final loc' (the next 'start_loc').

            it assumes that the self.cycle_list has been updated earlier

            No duplicates!
            ex) [1, 3, 3, 4] X, [1, 3, 4] O

        :return: [1,5,7,2,7,8..] (including terminal loading)
        """

        # caching
        if self.route_cache[0] != -1: return self.route_cache
        if len(self.cycle_list) == 0: return []

        ret = []
        if self.cycle_list[0].terminal != self.vehicle.start_loc:
            ret.append(self.vehicle.start_loc)

        for cycle in self.cycle_list:
            ret.extend(cycle.get_cycle_route())

        self.route_cache = ret
        return copy.deepcopy(self.route_cache)

    def get_travel_distance(self):
        # caching
        if self.dist_cache != -1: return self.dist_cache
        route = self.get_route()
        if len(route) == 0: return 0

        ret = 0
        cur = route[0]
        for next in route[1:]:
            ret += self.graph.get_dist(cur, next)
            cur = next

        self.dist_cache = ret
        return self.dist_cache

    def get_travel_time(self):
        # caching
        if self.dist_cache != -1: return self.dist_cache
        route = self.get_route()
        if len(route) == 0: return 0

        ret = 0
        cur = route[0]
        for next in route[1:]:
            ret += self.graph.get_time(cur, next)
            cur = next

        self.dist_cache = ret
        return self.dist_cache

    # variable cost only
    def get_var_cost(self):
        return self.get_travel_distance() * self.vehicle.vc

    # order count
    def get_count(self):
        return len(self.order_list)

    def get_work_time(self):
        # caching
        if self.work_cache != -1: return self.work_cache

        ret = 0
        for order in self.order_list: ret += order.load

        self.work_cache = ret
        return self.work_cache

    def get_max_capa(self):
        # caching
        if self.max_capa_cache != -1: return self.max_capa_cache
        if len(self.order_list): return 0

        ret = 0
        for cycle in self.cycle_list:
            ret = max(ret, cycle.total_capa)
        return ret

    def get_after_time(self):
        # caching
        if self.after_time_cache != -1: return self.after_time_cache


        cur_time = self.vehicle.free_time
        cur_loc = self.vehicle.start_loc
        for cycle in self.cycle_list:
            cur_time, cur_loc = cycle.get_after_info(start_time = cur_time, start_loc=cur_loc)

        self.after_time_cache = cur_time
        return self.after_time_cache

    def get_spent_time(self):
        return self.get_after_time() - self.vehicle.free_time

    def get_wating_time(self):
        return self.get_spent_time() - self.get_travel_time() - self.get_work_time()

