import config
from config import *
from object.vehicle import Vehicle
from simulator.tools import can_time_cal


class Order:

    general_sequence = 0
    def __init__(self, dest_id, order_id = ORDER_ID_NULL,
                 terminal_id = -1, latitude=-1.0, longitude=-1.0, cbm=0.0,
                 load=0, group=-1, start=0, end=DAY):
        self.order_id = order_id #str
        self.terminal_id = terminal_id #int idx
        self.dest_id = dest_id #int idx
        self.latitude = latitude
        self.longitude = longitude
        self.cbm = cbm # double
        self.load = load # double? int ?
        self.group = group # 0~23
        self.start = start # 0~1440
        self.end = end # 0 ~ 1440

        # for optimization
        self.prev_free = -1
        self.next_arrival = -1

        # for logging
        self.vehicle = None
        self.serviced = self.delivered = False
        self.arrival_time = -1
        self.start_time = -1
        self.sequence = -1



    def allocate(self, arrival_time:int, vehicle:Vehicle):
        self.serviced = True
        self.arrival_time = arrival_time
        self.vehicle = vehicle
        self.start_time = can_time_cal(arrival_time, self.start, self.end)
        Order.general_sequence += 1
        self.sequence = Order.general_sequence

    def update(self, cur_time:int):
        if self.serviced and (self.start_time + self.load <= cur_time):
            self.delivered = True


    def __str__(self):
        seperator = ","
        sb = []

        terminal_order = self.order_id == STRING_NULL

        sb.append(str(self.order_id))
        sb.append(str(self.vehicle.veh_num))
        sb.append(str(self.sequence))
        sb.append(str(self.dest_id))

        if self.delivered:
            sb.append(str(self.arrival_time)) # arrival
            sb.append(str(self.start_time - self.arrival_time)) # wating
            sb.append(str(self.load)) # service
            sb.append(str(self.start_time + self.load)) # departure
            sb.append(STRING_NULL if terminal_order else "Yes")
        else:
            sb.append(STRING_NULL)
            sb.append(STRING_NULL)
            sb.append(STRING_NULL)
            sb.append(STRING_NULL)
            sb.append(STRING_NULL if terminal_order else "No")
        return seperator.join(sb)


class OrderTable:
    def __init__(self, file_dir=None, graph=None):
        self.table = [[] for _ in range(LAST_BATCH)]
        if file_dir is not None and graph is not None:
            self.initialize(file_dir, graph)

    def initialize(self, file_dir, graph):
        try:
            with open(file_dir, 'r') as fs:
                for line in fs:
                    data = line.split()
                    order_id = data[0]
                    latitude = float(data[1])
                    longitude = float(data[2])
                    terminal_id = data[3]
                    dest_id = data[4]
                    cbm = float(data[5])
                    start = int(data[6])
                    end = int(data[7])
                    load = int(data[8])
                    group = int(data[9])

                    if group < config.LAST_BATCH:
                        self.table[group].append(
                            Order(order_id = order_id,
                                  terminal_id= graph.id2idx(terminal_id),
                                  dest_id= graph.id2idx(dest_id),
                                  latitude = latitude,
                                  longitude = longitude,
                                  cbm= cbm,
                                  load = load,
                                  group= group,
                                  start = start,
                                  end = end
                                  )
                        )
        except FileNotFoundError:
            print(f"invalid directories : {file_dir}")
            exit(1)

    def update_orders(self, cur_time:int):
        for batch in self.table:
            for order in batch:
                order.update(cur_time)
