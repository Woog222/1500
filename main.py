import copy
import os.path

import config

from checker import checker
from simulator.program import Program
from preproc.preprocessing import preprocessing

if __name__ == "__main__":

    preprocessing()
    program = Program()
    program.simulator()

    ch = checker(dir_final=config.FINAL_ORDER_RESULT_DIR,
            dir_vehicles=os.path.join("data", "real_raw", "vehicles.csv"),
            dir_id2idx=config.IDX2ID_DIR,
            dir_od_matrix= os.path.join("data", "real_raw", "od_matrix.csv"),
            dir_vehicle_result= config.VEH_RESULT_DIR)
    ch.get_summary()
