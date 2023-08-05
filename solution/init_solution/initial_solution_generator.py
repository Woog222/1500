import config
from object.graph import Graph
from object.order import Order
from object.vehicle import Vehicle
from simulator.tools import can_time_cal
from solution.Solution import Solution
from solution.helper import Veh_helper, Order_helper
from solution.vehicle_alloc import Vehicle_Alloc



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
        self.order_list = [Order_helper(order) for order in order_list]
        self.carry_over = carry_over

        if config.DEBUG and self.invalid():
            print("different terminal")
            exit(1)

    def invalid(self):
        # no orders
        if len(self.order_list) == 0:
            print("no orders")
            return True

        return False

    def get_init_solution(self):
        """
        Solution 객체 형태로 초기해를 만들어서 리턴하는 함수 작성하면 됨!
        :return: Solution Object for Batch Problem
        """
        # terminal list
        terminals = []
        for order_helper in self.order_list: terminals.append(order_helper.order.terminal_id)
        terminals = list(set(terminals))

        for terminal in terminals:
            terminal_orders = []
            for order_helper in self.order_list:
                if order_helper.order.terminal_id == terminal: terminal_orders.append(order_helper)
            self.terminal_alloc(terminal = terminal, orders = terminal_orders)

        vehicle_alloc_list = [ Vehicle_Alloc(vehicle=veh.vehicle, graph = self.graph, allocated_order_list=veh.allocated_order)  for veh in self.vehicle_list]
        order_list = [ order_helper for order_helper in self.order_list]
        return Solution(graph = self.graph, order_list = order_list, vehicle_list= vehicle_alloc_list)


    def terminal_alloc(self, terminal, orders:list[Order_helper]):
        """
        The Kernel of Our Optimization,,
        :param orders: orders from this terminal
        :param terminal:
        :return:
        """
        vehicle_list = self.vehicle_list


        allocated = True
        while allocated == True:
            allocated = False
            vehicle_list.sort(key=lambda x: (self.graph.get_time(x.cur_loc, terminal) + x.cur_time, -x.vehicle.capa))
            for veh in vehicle_list:
                order_helper = self.next_order(veh.cur_loc, veh.cur_time, veh.left, orders = orders)
                if order_helper is None: continue


                allocated = order_helper.allocated = True
                veh.allocated_order.append(order_helper)

                veh.left -= order_helper.order.cbm
                arrival_time = veh.cur_time + self.graph.get_time(veh.cur_loc, terminal) + \
                               self.graph.get_time(terminal, order_helper.order.dest_id)
                veh.cur_time = can_time_cal(arrival_time, order_helper.order.start, order_helper.order.end) + order_helper.order.load
                veh.cur_loc = order_helper.order.dest_id

                while True:
                    order_helper = self.next_order(veh.cur_loc, veh.cur_time, veh.left, orders = orders)
                    if order_helper is None: break
                    order_helper.allocated = allocated = True
                    veh.allocated_order.append(order_helper)
                    veh.left -= order_helper.order.cbm
                    if veh.cur_loc != order_helper.order.dest_id:
                        arrival_time = veh.cur_time + self.graph.get_time(veh.cur_loc, order_helper.order.dest_id)
                        veh.cur_time = can_time_cal(arrival_time, order_helper.order.start, order_helper.order.end) + order_helper.order.load
                        veh.cur_loc = order_helper.order.dest_id

            for veh in vehicle_list:
                veh.left = veh.vehicle.capa


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


    def next_order(self, cur_loc, cur_time, left, orders:list[Order_helper]):
        ret = None
        best_start = config.MAX
        for order_helper in orders:
            order = order_helper.order
            if order_helper.allocated or left < order.cbm or self.graph.get_time(cur_loc, order.dest_id) < 0:
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