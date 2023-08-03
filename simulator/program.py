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
            batch = self.orderTable.table[group]
            if not batch: continue
            batch.extend(left)

            print(f"\tbatch {group}.. ", end='')
            init_solution_generator = Initial_Solution_Generator(
                graph = self.graph,
                vehicle_list= self.vehicleTable.table,
                order_list= batch,
                carry_over = (group!=config.LAST_BATCH)
            )
            init_solution = init_solution_generator.get_init_solution()

            # optimization
            solution = init_solution
            solver = Solver(solution, self.graph, group)
            solver.solve()

            # allocate
            solution.allocate_solution()
            self.orderTable.update_orders(group* config.GROUP_INTERVAL)
            self.vehicleTable.write_order_result(init=False, final=False)
            print("done")

            left = []
            for order in batch:
                ## 72 hour limit
                if order.serviced or order.group + 12 <= group:
                    continue
                left.append(order)

        self.vehicleTable.write_order_result(final = True, init=True)
        self.vehicleTable.write_veh_result()

    def batch_alloc(self, batch:list[Order], cur_batch):
        """

        :param batch:
        :param cur_batch:
        :return: Solution object in a batch setting
        """



        # terminal list
        terminals = []
        for order in batch: terminals.append(order.terminal_id)
        terminals = list(set(terminals))

        for terminal in terminals:
            terminal_orders = []
            for order in batch:
                if order.terminal_id == terminal: terminal_orders.append(order)

            self.vehicleTable.init_vehicles()
            self.terminal_alloc(terminal_orders, terminal, cur_batch != LAST_BATCH)
            self.vehicleTable.alloc()

    def terminal_alloc(self, orders:list[Order], terminal:int, carry_over:bool):
        """
        The Kernel of Our Optimization,,
        :param orders: orders from this terminal
        :param terminal:
        :return:
        """

        # sort in order of arrival time
        vehicles = self.vehicleTable.table
        vehicles.sort(key = lambda x:
            self.graph.get_time(x.cur_loc, terminal) + x.cur_time
        )

        for veh in vehicles:
            order = self.next_order(batch = orders, veh =  veh,
                             terminal = terminal, carry_over= carry_over)
            if order is None: continue
            veh.add_order(order)


    def next_order(self, batch: list[Order], veh: Vehicle, terminal:int,
                   carry_over:bool):

        where = veh.cur_loc; when = veh.cur_time
        left = veh.left

        ret = None
        best_start = MAX
        for order in batch:
            if  order.serviced or left < order.cbm or terminal != order.terminal_id or \
                self.graph.get_time(where, order.dest_id) < 0:
                continue

            arrival_time = when + self.graph.get_time(where, order.dest_id)
            start_time = can_time_cal(arrival_time, order.start, order.end)

            if carry_over and start_time - arrival_time > HOUR * 6:
                continue

            if start_time < MAX_START_TIME and start_time < best_start and \
                    start_time + order.load <= (order.group + 12) * 6 * 60:
                ret = order
                best_start = start_time

        return ret


