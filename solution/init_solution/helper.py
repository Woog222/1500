from object.order import Order
from object.vehicle import Vehicle


class Order_helper:
    def __init__(self, order:Order):
        self.order = order
        self.allocated = False

class Veh_helper:
    def __init__(self, vehicle: Vehicle):
        self.vehicle = vehicle
        self.cur_loc = vehicle.start_loc
        self.cur_time = vehicle.free_time
        self.left = vehicle.capa
        self.allocated_order = []