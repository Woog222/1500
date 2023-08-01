import os

DEBUG = True



HOUR = 60
DAY = HOUR*24
WEEK = DAY*7

MAX = 987654321
GRAPH_SIZE = 2000
LAST_BATCH = 23
GROUP_INTERVAL = 360
MAX_START_TIME = WEEK - 60
INT_NULL = -1

ORDER_ID_NULL = "Null"
STRING_NULL = "Null"
TERMINAL_START_CHARACTER = "O"
DEST_START_CHARACTER = "D"


FINAL_ORDER_RESULT_DIR = os.path.join("results", "final.csv")
ORDER_RESULT_DIR = os.path.join("results", "order_result.csv")
VEH_RESULT_DIR = os.path.join("results", "vehicle_result.csv")
IDX2ID_DIR = os.path.join("results", "id2idx.csv")
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

VEH_COLUMNS = \
        "VehicleID," + \
        "Count," + \
        "Volume," + \
        "TravelDistance," + \
        "WorkTime," + \
        "TravelTime," + \
        "ServiceTime," + \
        "WaitingTime," + \
        "TotalCost," + \
        "FixedCost," + \
        "VariableCost\n"

