import copy

import config
from object.graph import Graph
from object.order import OrderTable, Order
from object.vehicle import Vehicle_Table, Vehicle
from simulator.tools import *
from solution.init_solution.initial_solution_generator import Initial_Solution_Generator
from solution.solver.solver import Solver


class Program:
    def __init__(self):
        self.graph = Graph(config.OD_MATRIX)
        print("Graph constructed")
        self.vehicleTable = Vehicle_Table(config.VEHICLES, self.graph)
        print("Vehicle Table constructed")
        # self.terminalTable = Terminal_Table(config.TERMINALS, self.graph)
        # print("Terminal Table constructed")
        self.orderTable = OrderTable(config.ORDERS, self.graph)
        print("Order Table constructed", end="\n\n")

    def simulator(self):
        print("Simulation ongoing..")
        self.vehicleTable.write_order_result(init=True, final=False)

        left = []
        for group in range(config.LAST_BATCH):

            # left
            batch = copy.copy(self.orderTable.table[group])
            if len(batch)==0: continue
            batch.extend(left)

            # free_time update
            self.vehicleTable.update_freetime(group * config.GROUP_INTERVAL)

            # init solution
            print(f"\tbatch {group} : ", end=' ')
            init_solution_generator = Initial_Solution_Generator(
                graph = self.graph,
                vehicle_list= self.vehicleTable.table,
                order_list= batch,
                carry_over = ((group+1)!=config.LAST_BATCH),
                group = group
            )
            init_solution = init_solution_generator.get_init_solution()

            # optimization
            solution = init_solution
            solver = Solver(solution, self.graph, group)
            solver.solve()

            # allocation
            print(solution, end=' ')
            solution.update()
            solution.allocate_solution()
            self.vehicleTable.update_allocated_orders(group * config.GROUP_INTERVAL)
            self.vehicleTable.write_order_result(init=False, final=False)

            left = []
            for order in batch:
                ## 72 hour limit
                if order.serviced: continue
                left.append(order)
            print(f"{len(batch)} -> {len(left)}")

            total_cost = 0
            for veh in self.vehicleTable.table:
                total_cost += veh.get_total_cost()
            print(f"\tTotal Cost: {total_cost}")

        self.vehicleTable.update_allocated_orders(WEEK)
        self.vehicleTable.write_order_result(final = True, init=True)
        self.vehicleTable.write_veh_result()

        total_service = total_not = 0
        for group, order_group in enumerate(self.orderTable.table):
            serviced_cnt = not_cnt = 0
            for order in order_group:
                if order.serviced: serviced_cnt += 1
                else: not_cnt += 1
            print(f"batch {group} : ( {serviced_cnt} , {not_cnt} )")
            total_service += serviced_cnt
            total_not += not_cnt

        print(f"{total_service}, {total_not}")

        total_cost = 0
        for veh in self.vehicleTable.table:
            total_cost += veh.get_total_cost()
        print(f"Total Cost: {total_cost}")





