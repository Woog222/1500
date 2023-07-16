from config import *

class Logger:
    def __init__(self):
        self.orderResults = []
        self.cur_time = 0
        self.sequence = 0
        self.order_result_dir = ""

    def add_order(self, vehicleId, ordNo, siteCode, arrivalTime, waitingTime, serviceTime, departureTime):
        self.orderResults.append(
            (vehicleId, ordNo, siteCode, arrivalTime, waitingTime, serviceTime, departureTime, self.sequence))
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
                    f.write(order)
            else:
                print(order_result_dir + " is not a valid result directory.")
