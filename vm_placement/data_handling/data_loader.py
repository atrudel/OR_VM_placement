from typing import Optional

import pandas as pd

from vm_placement.data_handling.processing import duplicate_entry


class Data:
    def __init__(self, vm_filepath: str, server_specs: Optional[pd.DataFrame], n_servers: Optional[int] = None):
        self.vm_data: pd.DataFrame = pd.read_csv(vm_filepath, sep=';')
        n_servers = len(self.vm_data) if n_servers is None else n_servers
        self.server_data = duplicate_entry(server_specs, n_times=n_servers)
