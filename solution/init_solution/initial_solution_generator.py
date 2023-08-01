import config
from object.graph import Graph
from object.order import Order
from object.vehicle import Vehicle
from simulator.tools import can_time_cal


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
        self.vehicle_list = vehicle_list
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

    def terminal_alloc(self):
        """
        The Kernel of Our Optimization,,
        :param orders: orders from this terminal
        :param terminal:
        :return:
        """
        self.vehicle_list.sort(key=lambda x:
        self.graph.get_time(x.cur_loc, self.terminal) + x.cur_time
                      )

        for veh in self.vehicle_list:
            order = self.next_order(batch=self.order_list, veh=veh,
                                    terminal=self.terminal, carry_over=self.carry_over)
            if order is None: continue
            veh.add_order(order)

    def next_veh(self, order:Order):
        """
            find best vehicle
        :param order:
        :return:
        """

    def next_order(self, batch: list[Order], veh: Vehicle, terminal: int,
                   carry_over: bool):

        where = veh.cur_loc;
        when = veh.cur_time
        left = veh.left

        ret = None
        best_start = config.MAX
        for order in batch:
            if order.serviced or left < order.cbm or terminal != order.terminal_id or \
                    self.graph.get_time(where, order.dest_id) < 0:
                continue

            arrival_time = when + self.graph.get_time(where, order.dest_id)
            start_time = can_time_cal(arrival_time, order.start, order.end)

            if carry_over and start_time - arrival_time > config.HOUR * 6:
                continue

            if start_time < config.MAX_START_TIME and start_time < best_start and \
                    start_time + order.load <= (order.group + 12) * 6 * 60:
                ret = order
                best_start = start_time

        return ret