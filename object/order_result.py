class OrderResult:
    def __init__(self, vehicle_id, ord_no, site_code, arrival_time, waiting_time, service_time, departure_time, sequence):
        self.VehicleID = vehicle_id
        self.ORD_NO = ord_no
        self.SiteCode = site_code
        self.ArrivalTime = arrival_time
        self.WaitingTime = waiting_time
        self.ServiceTime = service_time
        self.DepartureTime = departure_time
        self.Sequence = sequence
        self.ArrivalTime_print = -1
        self.WaitingTime_print = -1
        self.ServiceTime_print = -1
        self.DepartureTime_print = -1
        self.Delivered = 0

    def __str__(self):
        return f"{self.ORD_NO},{self.VehicleID},{self.Sequence},{self.SiteCode},{self.ArrivalTime_print},{self.WaitingTime_print},{self.ServiceTime_print},{self.DepartureTime_print},{self.Delivered}\n"

    def update(self, cur_time):
        if self.DepartureTime <= cur_time:
            self.ArrivalTime_print = self.ArrivalTime
            self.WaitingTime_print = self.WaitingTime
            self.ServiceTime_print = self.ServiceTime
            self.DepartureTime_print = self.DepartureTime
            self.Delivered = 1