from config import *

class Order:
    def __init__(self, order_id, terminal_id, dest_id, latitude, longitude, cbm, load, group, start, end):
        self.order_id = order_id
        self.terminal_id = terminal_id
        self.dest_id = dest_id
        self.latitude = latitude
        self.longitude = longitude
        self.cbm = cbm
        self.load = load
        self.group = group
        self.start = start
        self.end = end
        self.serviced = False

    def __str__(self):
        return f"{self.order_id}( {self.group} ) : \n {self.start} - {self.end}, {self.terminal_id} -> {self.dest_id}\n"


class OrderTable:
    def __init__(self, file_dir=None, graph=None):
        self.table = [[] for _ in range(ORDER_GROUP_SIZE)]
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
                    group = int(data[11])

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