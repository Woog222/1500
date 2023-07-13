from typing import Dict
from collections import defaultdict
from object.objects import edge

class Graph:
    def __init__(self, file_dir):
        self.table = None
        self.IDX = {}
        self.ID = {}

        # table reset with {-1, -1}
        init_value = edge(-1)
        self.table = [[init_value for _ in range(GRAPH_SIZE)] for _ in range(GRAPH_SIZE)]
        for i in range(GRAPH_SIZE):
            self.table[i][i] = edge(0)

        # input
        with open(file_dir, 'r') as fs:
            idx = 0
            for line in fs:
                origin, dest, length, time = line.split()
                # index setting
                if origin not in self.IDX:
                    self.IDX[origin] = idx
                    idx += 1
                if dest not in self.IDX:
                    self.IDX[dest] = idx
                    idx += 1
                from_, to = self.IDX[origin], self.IDX[dest]

                # adj matrix
                self.table[from_][to] = edge(float(time))

        # ID setting
        self.ID = {v: k for k, v in self.IDX.items()}

    def id2idx(self, id):
        if id not in self.IDX:
            print(id, "is not in od_matrix")
            exit(1)
        return self.IDX[id]

    def idx2id(self, idx):
        if idx not in self.ID:
            print(idx, "is not a valid index.")
            exit(1)
        return self.ID[idx]
