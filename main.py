import copy

from simulator.program import Program
from preproc.preprocessing import preprocessing

if __name__ == "__main__":

    preprocessing()
    program = Program()
    program.simulator()


