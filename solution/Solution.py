from sympy.integrals.rubi.utility_function import Order

from object.graph import Graph
from solution.vehicle_alloc import Vehicle_Alloc


class Solution:
    """
        General Solution Frame
    """

    def __init__(self, graph:Graph, vehicle_list:list[Vehicle_Alloc], order_list:list[Order]):
        """
        :param graph:
        :param vehicle_list: The list of vehicles to be considered.
            For the terminal problem, it could be the top N vehicles sorted by their spatial closeness.
            For the batch problem, it includes all the vehicles.
        :param order_list: The list of orders to be dealt with.
            For the terminal problem, it includes every order starting in a certain terminal (excluding ones that have been carried over to the next batch).
            For the batch problem, it includes every order in a batch (excluding ones that have been carried over to the next batch).
        """


        """
            CONST
            for reference only
        """
        self.graph = graph
        self.order_list = order_list

        """
            improve it!
        """
        self.vehicle_list = vehicle_list


    def update(self):
        """
            Whenever any modification was made,, must be called
        """
        for veh in self.vehicle_list:
            veh.reset_cache()
            veh.update_cycle()

    def get_var_cost(self):
        ret = 0
        for veh in self.vehicle_list:
            ret += veh.get_var_cost()
        return ret

    def get_total_waiting_time(self):
        ret = 0
        for veh in self.vehicle_list:
            ret += veh.get_wating_time()
        return ret

    def get_total_spent_time(self):
        ret = 0
        for veh in self.vehicle_list:
            ret += veh.get_spent_time()
        return ret


