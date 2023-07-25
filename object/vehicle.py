from operator import itemgetter

class Vehicle:
    def __init__(self, capa, fc, vc, veh_ton, start_center, veh_num):
        self.capa = capa
        self.fc = fc
        self.vc = vc
        self.veh_ton = veh_ton
        self.veh_num = veh_num
        self.start_center = start_center
        self.free_time = 0

        self.travel_distance = 0

    def __str__(self):
        return f"capa: {self.capa}, vc: {self.vc}, veh_num: {self.veh_num}, free_time: {self.free_time}"

    def __lt__(self, other):
        if self.free_time == other.free_time:
            if self.capa == other.capa:
                return self.vc < other.vc
            return self.capa > other.capa
        return self.free_time < other.free_time


class Vehicle_Table:
    def __init__(self, file_dir, graph):
        self.table = []
        with open(file_dir) as f:
            for line in f:
                veh_num, veh_ton, _, _, capa, start_center, fc, vc = line.split()
                capa, fc, vc, veh_ton = map(float, [capa, fc, vc, veh_ton])
                start_center = graph.id2idx(start_center)
                vehicle = Vehicle(capa, fc, vc, veh_ton, start_center, veh_num)
                self.table.append(vehicle)

        self.table.sort()

    def __str__(self):
        return '\n'.join(str(vehicle) for vehicle in self.table)