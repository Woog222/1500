from pyasn1.codec import der

from object.graph import Graph
from object.order import Order
from object.vehicle import Vehicle


class Temporal_bundle:
    def __init__(self, orders:list[Order], vehicle:Vehicle, graph:Graph):
        self.graph = graph
        self.orders = orders
        self.vehicle = vehicle
        self.terminal = orders[0].terminal_id

class Spatial_bundle:
    def __init__(self, orders:list[Order], vehicle:Vehicle, graph:Graph):
        self.graph = graph
        self.orders = orders
        self.vehicle = vehicle
        self.terminal = orders[0].terminal_id