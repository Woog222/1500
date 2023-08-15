import os

DEBUG = True
INTEGER = False


HOUR = 60
DAY = HOUR*24
WEEK = DAY*7

MAX = 987654321
GRAPH_SIZE = 2000
LAST_BATCH = 24
GROUP_INTERVAL = 360
MAX_START_TIME = WEEK - 60
TIME_CRITERION = DAY * 3
TEMPORAL_BUNDLE_CRITERION = 100
SPATIAL_BUNDLE_CRITERION = 100

TIMELIMIT_SEC = 60*3
NUM_ITER = 30

ORDER_ID_NULL = "Null"
STRING_NULL = "Null"
TERMINAL_START_CHARACTER = "O"
DEST_START_CHARACTER = "D"

"""
        RESULT_FILE
"""
FINAL_ORDER_RESULT_DIR = os.path.join("results", "final.csv")
ORDER_RESULT_DIR = os.path.join("results", "order_result.csv")
VEH_RESULT_DIR = os.path.join("results", "vehicle_result.csv")
IDX2ID_DIR = os.path.join("results", "id2idx.csv")
COORDINAES_DIR = os.path.join("results", "coordinates.csv")
"""
        DATA
"""
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
        "Delivered," + \
        "cbm," + \
        "start," + \
        "end," + \
        "group\n" \
        if DEBUG else \
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

