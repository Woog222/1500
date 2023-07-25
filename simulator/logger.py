from config import *
from object.objects import *

class Logger:
    def __init__(self):
        self.orderResults = []
        self.vehResults = []
        self.cur_time = 0
        self.sequence = 0
        self.order_result_dir = ""
        self.veh_result_dir = ""

    def add_order(self, vehicleId, ordNo, siteCode, arrivalTime, waitingTime, serviceTime, departureTime):
        self.orderResults.append(
            OrderResult(vehicleId, ordNo, siteCode, arrivalTime, waitingTime, serviceTime, departureTime, self.sequence))
        self.sequence += 1

    def update_logs(self, cur_time_):
        self.cur_time = cur_time_
        for order in self.orderResults:
            order.update(self.cur_time)

    def order_result_init(self, file_dir):
        self.order_result_dir = file_dir
        with open(self.order_result_dir, 'w') as f:
            f.write(ORDER_COLUMNS)

    def write_order(self, cur_time):
        with open(self.order_result_dir, 'a') as f:
            self.update_logs(cur_time)
            if f:
                for order in self.orderResults:
                    f.write(str(order))
            else:
                print(ORDER_RESULT_DIR + " is not a valid result directory.")

    def init_veh_result(self, veh_result_dir):
        self.veh_result_dir = veh_result_dir
        with open(self.veh_result_dir, 'w') as f:
            f.write(VEH_COLUMNS)

    def write_veh_result(self, veh, vehicleID):
        distance = veh.travel_distance
        fc = veh.fc if distance > 0 else 0
        vc = veh.vc * distance
        tc = fc + vc
        with open(self.veh_result_dir, "a") as f:
            if f:
                f.write(f"\n{vehicleID}, {distance}, {tc}, {fc}, {vc}")
            else:
                print(self.veh_result_dir + " is not a valid result directory.")