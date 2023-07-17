import pandas as pd

class Terminal:
    def __init__(self, latitude, longitude, region):
        self.loc = (latitude, longitude)
        self.region = region

    def __str__(self):
        return f"loc: ({self.loc[0]}, {self.loc[1]}), region: {self.region}"


class Terminal_Table:
    def __init__(self, file_dir=None, graph=None):
        self.table = {}

        if file_dir is not None and graph is not None:
            # Read file using pandas
            data = pd.read_csv(file_dir, sep='\s+', header=None)

            for i in range(len(data)):
                id, latitude, longitude, region = data.iloc[i, :]

                idx = graph.id2idx(id)

                if idx not in self.table:
                    self.table[idx] = Terminal(latitude, longitude, region)
                else:
                    print("duplicates in terminals.csv")
                    exit(1)