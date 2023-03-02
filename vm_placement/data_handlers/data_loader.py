import pandas as pd
import numpy as np



class Data:
    def __init__(self, vm_filepath, server_filepath, demand_max=3, seed=42):
        np.random.seed(seed)
        self.vm_data: pd.DataFrame = pd.read_csv(vm_filepath, sep=';')
        self.demands: np.ndarray = np.random.randint(0, demand_max, len(self.vm_data), )
        self.server_data: pd.DataFrame = pd.read_csv(server_filepath, sep=';')
