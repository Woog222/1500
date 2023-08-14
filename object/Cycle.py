from object.vehicle import Vehicle
from object.order import Order
from object.graph import Graph
import config
from tool.tools import can_time_cal


class Cycle:

    def __init__(self, orders:list[Order], vehicle:Vehicle, graph:Graph):
        self.graph = graph
        self.orders = orders
        self.vehicle = vehicle
        self.terminal = orders[0].terminal_id

        self.total_capa = 0.0
        for order in self.orders: self.total_capa += order.cbm

        if config.DEBUG and self.invalid():
            print(str(self))
            exit(1)

        self.terminal_loading_order = None # after confirmed

    def get_after_info(self, start_time:int, start_loc:int, allocate:bool = False):
        """
        :param terminal_arrival_time: The time at which you arrived at starting terminal
        :return:
        """
        cur_time = start_time + self.graph.get_time(start_loc, self.terminal)
        cur_loc = self.terminal

        if allocate:
            self.terminal_loading_order = Order(dest_id = self.terminal)
            self.terminal_loading_order.allocate(arrival_time=cur_time, vehicle=self.vehicle)

        load_max = 0
        for order in self.orders:
            if cur_loc != order.dest_id:
                arrival_time = cur_time + load_max + self.graph.get_time(cur_loc ,order.dest_id)
                start_time = can_time_cal(arrival_time, order.start, order.end)
                cur_time = start_time
                cur_loc = order.dest_id
                load_max = order.load
            else:
                load_max = max(load_max, order.load)

            if allocate:
                order.allocate(arrival_time=arrival_time, vehicle=self.vehicle)

        cur_time += load_max
        return cur_time, cur_loc


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

    def get_cycle_coordinates(self):
        if len(self.orders) == 0: return []



    def get_cycle_route(self):
        """
        Actual cycle traveling route

        no duplicates!
            ex) [1, 3, 3, 4] X, [1, 3, 4] O
        :return: [terminal, dest1, dest2 ..]
        """
        if len(self.orders) == 0: return []

        ret = [self.terminal]
        cur_loc = self.terminal
        for order in self.orders:
            if cur_loc != order.dest_id:
                ret.append(order.dest_id)
                cur_loc = order.dest_id
        return ret

    def get_cycle_capa(self):
        return self.total_capa

    def get_cycle_order_cnt(self):
        return len(self.orders)

    def get_cycle_service_time(self):
        ret = 0
        for order in self.orders:
            ret += order.load
        return ret

    def update_orders(self, cur_time:int):
        self.terminal_loading_order.update(cur_time)
        for order in self.orders: order.update(cur_time)


    def __str__(self):
        sb = [str(self.terminal_loading_order)]
        for order in self.orders:
            sb.append(str(order))
        ret = '\n'.join(sb)
        return f"{ret}\n"



