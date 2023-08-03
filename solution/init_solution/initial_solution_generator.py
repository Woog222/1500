import config
from object.graph import Graph
from object.order import Order
from object.vehicle import Vehicle
from simulator.tools import can_time_cal
from solution.Solution import Solution
from solution.vehicle_alloc import Vehicle_Alloc


class Order_helper:
    def __init__(self, order:Order):
        self.order = order
        self.allocated = False

class Veh_helper:
    def __init__(self, vehicle: Vehicle):
        self.vehicle = vehicle
        self.cur_loc = vehicle.start_loc
        self.cur_time = vehicle.free_time
        self.allocated_order = []

class Initial_Solution_Generator:
    """
        For Batch
    """
    def __init__(self, graph:Graph, vehicle_list:list[Vehicle], order_list:list[Order], carry_over:bool):
        """
        :param graph:
        :param vehicle_list
        :param order_list: The list of orders to be dealt with.
            For the terminal problem, it includes every order starting in a certain terminal (excluding ones that have been carried over to the next batch).
        """

        self.graph = graph
        self.vehicle_list = [Veh_helper(veh) for veh in vehicle_list]
        self.order_list = [Order(order) for order in order_list]
        self.carry_over = carry_over

        if config.DEBUG and self.invalid():
            print("different terminal")
            exit(1)
        self.terminal = order_list[0].terminal_id

    def invalid(self):
        # no orders
        if len(self.order_list) == 0:
            print("no orders")
            return True

        # same terminal
        for order_helper in self.order_list:
            if order_helper.order.terminal_id != self.terminal:
                print("different terminal")
                return True
        return False

    def get_init_solution(self):
        """
        Solution 객체 형태로 초기해를 만들어서 리턴하는 함수 작성하면 됨!
        :return: Solution Object for Terminal Problem
        """
        # terminal list
        terminals = []
        for order_helper in self.order_list: terminals.append(order_helper.order.terminal_id)
        terminals = list(set(terminals))

        for terminal in terminals:
            terminal_orders = []
            for order in self.order_list:
                if order.terminal_id == terminal: terminal_orders.append(order)
            self.terminal_alloc(terminal = terminal)

        vehicle_alloc_list = [ Vehicle_Alloc(vehicle=veh.vehicle, graph = self.graph, allocated_order_list=veh.allocated_order)  for veh in self.vehicle_list]
        return Solution(graph = self.graph, order_list = self.order_list, vehicle_list= vehicle_alloc_list)


    def terminal_alloc(self, terminal):
        """
        The Kernel of Our Optimization,,
        :param orders: orders from this terminal
        :param terminal:
        :return:
        """

        left_order = True
        while left_order:
            veh_helper = self.next_veh(terminal = terminal)

            cur_loc = veh_helper.cur_loc
            cur_time = veh_helper.cur_time + self.graph.get_time(cur_loc, terminal)
            cur_loc = terminal
            left = veh_helper.vehicle.capa

            # cycle alloc
            allocated = False
            while True:
                order_helper = self.next_order(cur_loc = cur_loc, cur_time = cur_time,
                                        left= left, terminal = terminal)
                if order_helper is None: break

                order = order_helper.order
                # order load_max not yet
                if cur_loc != order.dest_id:
                    arrival_time = cur_time + self.graph.get_time(cur_loc, order.dest_id)
                    start_time = arrival_time + order.load

                    cur_time = start_time + order.load
                    cur_loc = order.dest_id
                veh_helper.allocated_order.append(order)
                left -= order.cbm
                allocated = True
                order_helper.allocated = True

            if allocated:
                veh_helper.cur_time = cur_time
                veh_helper.cur_loc = cur_loc
            else:
                break

            left_order = False
            for order_helper in self.order_list:
                if order_helper.allocated == False:
                    left_order = True
                    break







    def next_veh(self, terminal):
        """
            find best vehicle
        :param order:
        :return:
        """
        ret = self.vehicle_list[0]
        best_arrival_time = config.MAX
        for veh_helper in self.vehicle_list:
            arrival_time = veh_helper.cur_time + self.graph.get_time(veh_helper.cur_loc, terminal)
            if arrival_time < best_arrival_time:
                ret = veh_helper
                best_arrival_time = arrival_time
        return ret


    def next_order(self, cur_loc, cur_time, left, terminal: int):
        ret = None
        best_start = config.MAX
        for order_helper in self.order_list:
            order = order_helper.order
            if order.serviced or left < order.cbm or terminal != order.terminal_id or \
                    self.graph.get_time(cur_loc, order.dest_id) < 0:
                continue

            arrival_time = cur_time + self.graph.get_time(cur_loc, order.dest_id)
            start_time = can_time_cal(arrival_time, order.start, order.end)

            if self.carry_over and start_time - arrival_time > config.HOUR * 6:
                continue

            if start_time < config.MAX_START_TIME and start_time < best_start and \
                    start_time + order.load <= (order.group + 12) * 6 * 60:
                ret = order_helper
                best_start = start_time
        return ret