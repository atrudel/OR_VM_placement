import pandas as pd
import numpy as np



class Data:
    def __init__(self,
                 vm_filepath: str = 'data/vm_data.csv',
                 server_filepath: str = 'data/unique_server_data.csv',
                 seed=42):
        np.random.seed(seed)
        self.vm_data: pd.DataFrame = pd.read_csv(vm_filepath, sep=';')
        self.server_data: pd.DataFrame = pd.read_csv(server_filepath, sep=';')
