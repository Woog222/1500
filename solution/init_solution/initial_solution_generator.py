import config
from object.graph import Graph
from object.order import Order
from object.vehicle import Vehicle
from simulator.tools import can_time_cal


class Init_helper:
    def __init__(self, vehicle: Vehicle):
        self.vehicle = vehicle
        self.cur_loc = vehicle.start_loc
        self.cut_time = vehicle.free_time

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
        self.vehicle_list = [ Init_helper(veh) for veh in vehicle_list]
        self.order_list = order_list
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
        for order in self.order_list:
            if order.terminal_id != self.terminal:
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
        for order in self.order_list: terminals.append(order.terminal_id)
        terminals = list(set(terminals))

        for terminal in terminals:
            terminal_orders = []
            for order in self.order_list:
                if order.terminal_id == terminal: terminal_orders.append(order)

            self.terminal_alloc(terminal = terminal)




    def terminal_alloc(self, terminal):
        """
        The Kernel of Our Optimization,,
        :param orders: orders from this terminal
        :param terminal:
        :return:
        """

        while True:
            veh = self.next_veh()



    def next_veh(self, order:Order):
        """
            find best vehicle
        :param order:
        :return:
        """

    def next_order(self, cur_loc, cur_time, left, terminal: int):

        ret = None
        best_start = config.MAX
        for order in self.order_list:
            if order.serviced or left < order.cbm or terminal != order.terminal_id or \
                    self.graph.get_time(cur_loc, order.dest_id) < 0:
                continue

            arrival_time = cur_time + self.graph.get_time(cur_loc, order.dest_id)
            start_time = can_time_cal(arrival_time, order.start, order.end)

            if self.carry_over and start_time - arrival_time > config.HOUR * 6:
                continue

            if start_time < config.MAX_START_TIME and start_time < best_start and \
                    start_time + order.load <= (order.group + 12) * 6 * 60:
                ret = order
                best_start = start_time
        return ret