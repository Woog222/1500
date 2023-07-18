import os

HOUR = 60
DAY = HOUR*24
WEEK = DAY*7

GRAPH_SIZE = 2000
ORDER_GROUP_SIZE = 40
LAST_BATCH = 23
GROUP_INTERVAL = 360
MAX_START_TIME = WEEK - 60
INT_NULL = -1

STRING_NULL = "-1"
ORDERS = os.path.join("data", "orders.txt")
OD_MATRIX = os.path.join("data", "od_matrix.txt")
TERMINALS = os.path.join("data", "terminals.txt")
VEHICLES = os.path.join("data", "vehicles.txt")

ORDER_COLUMNS =\
        "ORD_NO," + \
        "VehicleID," + \
        "Sequence," + \
        "SiteCode," + \
        "ArrivalTime," + \
        "WaitingTime," + \
        "ServiceTime," + \
        "DepartureTime," + \
        "Delivered\n"
ORDER_RESULT_DIR = os.path.join("results", "order_result.csv")