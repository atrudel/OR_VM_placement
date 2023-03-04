from typing import Optional

import pandas as pd
import numpy as np

from vm_placement.data_handling.processing import duplicate_entry


class Data:
    def __init__(self,
                 vm_filepath: str = 'data/vm_data.csv',
                 server_filepath: str = 'data/unique_server_data.csv',
                 unique_server: Optional[pd.DataFrame] = None,
                 seed=42):
        np.random.seed(seed)
        self.vm_data: pd.DataFrame = pd.read_csv(vm_filepath, sep=';')
        if unique_server is None:
            self.server_data: pd.DataFrame = pd.read_csv(server_filepath, sep=';')
        else:
            self.server_data = duplicate_entry(unique_server, n_times=len(self.vm_data))
