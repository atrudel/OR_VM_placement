from __future__ import annotations
from typing import Optional
import pandas as pd

from vm_placement.data_handling.processing import duplicate_entry


class Data:
    def __init__(self, vm_filepath: str, server_specs: Optional[pd.DataFrame], n_servers: Optional[int] = None):
        self.vm_data: pd.DataFrame = pd.read_csv(vm_filepath, sep=';')
        n_servers = len(self.vm_data) if n_servers is None else n_servers
        self.server_data = duplicate_entry(server_specs, n_times=n_servers)

    def filter_vms_by_resource(self, resource: str, max: float) -> Data:
        filtered_vms = self.vm_data[self.vm_data[resource] <= max].reset_index(drop=True)
        print(f"Filtered out {len(self.vm_data) - len(filtered_vms)} VMs with {resource} > {max}")
        self.vm_data = filtered_vms
        return self

    def subset_vms(self, n_vms: int, seed: int = None) -> Data:
        self.vm_data = self.vm_data.sample(n_vms, random_state=seed).reset_index()
        print(f"Sampled {n_vms} VMs from the dataset (with seed={seed})")
        return self

    def __repr__(self) -> str:
        return f"Data[{len(self.vm_data)} VMs, {len(self.server_data)} server]"
