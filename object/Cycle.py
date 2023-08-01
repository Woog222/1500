from object.vehicle import Vehicle
from object.order import Order
from object.graph import Graph
import config
from simulator.tools import can_time_cal


class Cycle:

    def __init__(self, orders:list[Order], vehicle:Vehicle, graph:Graph):
        self.graph = graph
        self.orders = orders
        self.vehicle = vehicle
        self.terminal = orders[0].terminal_id

        self.total_capa = 0
        for order in self.orders: self.total_capa += order.cbm


        if config.DEBUG and self.invalid():
            print(str(self))
            exit(1)

    # for debugging
    def invalid(self):
        ret = False
        # same terminal?
        for order in self.orders:
            if order.terminal_id != self.terminal:
                ret = True
        """ 
        # max_capa?
        if self.vehicle.capa < self.total_capa:
            ret = True
        """

    def get_cycle_route(self):
        """
        Actual cycle traveling route

        no duplicates!
            ex) [1, 3, 3, 4] X, [1, 3, 4] O
        :return: [terminal, dest1, dest2 ..]
        """
        if len(self.orders): return []


        ret = [self.terminal]
        cur_loc = self.terminal
        for order in self.orders:
            if cur_loc != order.dest_id:
                ret.append(order.dest_id)
                cur_loc = order.dest_id
        return ret

    def get_after_info(self, start_time:int, start_loc:int):
        """
        :param start_time: The time at which this vehicle begins processing this cycle
        :param start_loc: The location at which this vehicle begins processing this cycle
        :return: end_time (which might be the next start_time), end_loc (which might be the next start_loc)
        """

        cur_time = start_time + self.graph.get_time(start_loc, self.terminal)
        cur_loc = self.terminal

        for order in self.orders:
            # same dest
            if cur_loc == order.dest_id: continue

            arrival_time = cur_time + self.graph.get_time(cur_loc, order.dest_id)
            service_start_time = can_time_cal(arrival_time, order.start, order.end)

            cur_loc = order.dest_id
            cur_time = service_start_time + order.load

        return cur_time


    def __str__(self):
        print(f"{self.vehicle.veh_num : }", end="")
        for order in self.orders: print(f"{order.order_id}", end=" - ")
        print(f"total_capa : {self.total_capa}, veh_limit_capa : {self.vehicle.capa}")


