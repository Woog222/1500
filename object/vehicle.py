import math
from operator import itemgetter

from object.order import Order
from simulator.tools import can_time_cal
import config


class Vehicle:
    def __init__(self, capa, fc, vc, veh_ton, start_center, veh_num, graph):


        """
            CONST
        """
        self.capa = capa
        self.fc = fc
        self.vc = vc
        self.veh_ton = veh_ton
        self.veh_num = veh_num
        self.start_center = start_center

        self.free_time = 0
        self.graph = graph
        self.allocated_order_list = []

        """
            CONST in batch
        """
        self.start_loc = start_center


        """
            NON-CONST 
        """
        self.cur_loc = self.cur_time = self.left = 0
        self.order_list = [] # solution

    def __str__(self):
        return f"{self.veh_num}," \
               f"{self.get_count()}," \
               f"{self.get_total_volume()}," \
               f"{self.get_travel_distance()}," \
               f"{self.get_spent_time()}," \
               f"{self.get_travel_time()}," \
               f"{self.get_work_time()}," \
               f"{self.get_waiting_time()}," \
               f"{self.get_total_cost()}," \
               f"{self.fc}" \
               f"{self.get_total_cost() - self.fc}\n"

    def __lt__(self, other):
        if self.free_time == other.free_time:
            if self.capa == other.capa:
                return self.vc < other.vc
            return self.capa > other.capa
        return self.free_time < other.free_time

    def init(self):
        self.cur_loc = self.start_center
        self.cur_time = self.free_time
        self.left = self.capa
        self.order_list = []

    def add_order(self, order:Order):
        self.order_list.append(order)

        if order.terminal_id != self.cur_loc:
            self.cur_time += self.graph.get_time(self.cur_loc, order.terminal_id)
            self.cur_loc = order.terminal_id
        self.cur_time += self.graph.get_time(self.cur_loc, order.dest_id) + order.load
        self.cur_loc = order.dest_id

        self.left -= order.cbm

    def alloc(self):
        if len(self.order_list) == 0: return

        left = self.capa
        cur_terminal = -1
        for order in self.order_list:

            # terminal loading
            if cur_terminal != order.terminal_id or left < order.cbm:
                self.cur_time += self.graph.get_time(self.cur_loc, order.terminal_id)
                self.cur_loc = order.terminal_id

                terminal_order = Order(dest_id = order.terminal_id)
                terminal_order.allocate(arrival_time = self.cur_loc, veh_id = self.veh_num)
                self.allocated_order_list.append(terminal_order)
                cur_terminal = order.terminal_id
                left = self.capa

            # same dest
            if order.dest_id == self.cur_loc:
                order.allocate(arrival_time = self.cur_time - order.load, veh_id = self.veh_num)
            else:
                arrival_time = self.cur_time + self.graph.get_time(self.cur_loc, order.dest_id)
                start_time = can_time_cal(arrival_time, order.start, order.end)
                order.allocate(arrival_time = arrival_time, veh_id = self.veh_num)
                self.cur_time = start_time + order.load
                self.cur_loc = order.dest_id

            self.allocated_order_list.append(order)
            left -= order.cbm

        self.start_loc = self.cur_loc
        self.free_time = self.cur_time
        self.order_list = []


    """
        Complex Methods
    """
    def get_route(self):
        if len(self.order_list) == 0: return []

        ret = [self.start_center]
        for order in self.allocated_order_list:
            ret.append(order.dest_id)
        return ret

    def get_total_volume(self):
        ret = 0
        for order in self.allocated_order_list:
            ret += order.cbm
        return ret

    def get_max_capa(self):
        if len(self.order_list) == 0:
            return 0

        ret = 0; temp = 0
        for order in self.allocated_order_list:
            if self.graph.is_terminal(order.dest_id):
                ret = max(ret, temp)
                temp = 0
            temp += order.cbm

        ret = max(ret, temp)
        return ret

    def get_count(self):
        ret = 0
        for order in self.allocated_order_list:
            ret += 0 if self.graph.is_terminal(order.dest_id) else 1
        return ret

    def get_travel_distance(self):
        route = self.get_route()
        ret = 0
        for i in range(1, len(route)):
            ret += self.graph.get_dist(route[i-1], route[i])
        return ret

    def get_travel_time(self):
        route = self.get_route()
        ret = 0
        for i in range(1, len(route)):
            ret += self.graph.get_time(route[i-1], route[i])
        return ret

    def get_work_time(self):
        ret = 0
        for order in self.allocated_order_list:
            ret += order.load
        return ret

    def get_total_cost(self):
        ret = self.fc + self.vc * self.get_travel_distance()
        return int(math.ceil(ret))

    def get_waiting_time(self):
        return self.get_spent_time() - self.get_travel_time()

    def get_waiting_time_test(self):
        if len(self.allocated_order_list) == 0: return 0

        ret = 0
        cur_time = self.free_time; cur_loc = self.start_center
        cur_terminal = self.start_center

        prev = self.start_center
        for order in self.allocated_order_list:
            if self.graph.is_terminal(order.dest_id):
                cur_time += self.graph.get_time(prev, order.dest_id)
            else:
                arrival_time = cur_time + self.graph.time(prev, order.dest_id)
                start_time = can_time_cal(arrival_time, order.start, order.end)
                ret += start_time - arrival_time
                cur_time = start_time + order.load

            prev = order.dest_id

        return ret

    def get_spent_time(self):
        if len(self.allocated_order_list) == 0: return 0

        cur_time = 0

        prev = self.start_center
        for order in self.allocated_order_list:
            arrival_time = self.graph.get_time(prev, order.dest_id) + cur_time

            if self.graph.is_terminal(order.dest_id):
                cur_time = arrival_time
            else:
                start_time = can_time_cal(arrival_time, order.start, order.end)
                cur_time = start_time + order.load

            prev = order.dest_id

        return cur_time

class Vehicle_Table:
    def __init__(self, file_dir, graph):
        self.table = []
        with open(file_dir) as f:
            for line in f:
                veh_num, veh_ton, _, _, capa, start_center, fc, vc = line.split()
                capa, fc, vc, veh_ton = map(float, [capa, fc, vc, veh_ton])
                start_center = graph.id2idx(start_center)
                vehicle = Vehicle(capa, fc, vc, veh_ton, start_center, veh_num, graph = graph)
                self.table.append(vehicle)

        self.table.sort()

    def __str__(self):
        return '\n'.join(str(vehicle) for vehicle in self.table)

    def init_vehicles(self):
        for veh in self.table: veh.init()

    def alloc(self):
        for veh in self.table: veh.alloc()

    def write_order_result(self, init=False, final=False):

        file_dir = config.FINAL_ORDER_RESULT_DIR if final else config.ORDER_RESULT_DIR
        with open(file_dir, 'w' if init else 'a') as f:
            if init: f.write(config.ORDER_COLUMNS)

            for veh in self.table:
                for order in veh.allocated_order_list:
                    f.write(str(order))


    def write_veh_result(self):

        with open(config.VEH_RESULT_DIR, 'w') as f:
            f.write(config.VEH_COLUMNS)
            for veh in self.table:
                f.write(str(veh))


