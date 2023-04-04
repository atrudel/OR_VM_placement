from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd

from vm_placement.data_handling.processing import resource_columns


class Solution:
    def __init__(self,
                 server_capacities: pd.DataFrame,
                 server_fillings: pd.DataFrame,
                 overize_vms: Optional[pd.DataFrame] = None,
                 algo_name: Optional[str] = None
                 ):
        # Drop zero rows of non-used servers
        used_server_fillings = server_fillings.loc[(server_fillings != 0).any(axis=1)]
        self.server_fillings: pd.DataFrame = used_server_fillings
        self.n_servers: int = len(used_server_fillings)
        self.server_capacities: pd.DataFrame = server_capacities[:][:self.n_servers]
        self.oversize_vms: Optional[pd.DataFrame] = overize_vms
        self.algo_name: str = algo_name if algo_name is not None else ""

    def display(self):

        filling_rates = self.server_fillings / self.server_capacities
        global_filling_rate = self.filling_rate()
        n_plots = len(resource_columns)
        fig, axs = plt.subplots(ncols=1, nrows=n_plots, figsize=(7, 1.5 * n_plots),
                                sharex=True, sharey=True)
        for i, resource in enumerate(resource_columns):
            axs[i].bar(filling_rates.index, filling_rates[resource],
                       label=f"{resource}\n{global_filling_rate[resource]*100:.1f}%")
            axs[i].legend(loc='upper right')
        axs[-1].set_xlabel('Server index')
        axs[n_plots//2].set_ylabel('% resource usage')
        fig.suptitle(self)
        plt.tight_layout()
        plt.show()
        if self.oversize_vms is not None:
            print()
            print("Oversize VMs:")
            print(self.oversize_vms)

    def filling_rate(self) -> float:
        total_resource_usage = self.server_fillings.sum()
        total_resource_mobilized = self.server_capacities.sum()
        return total_resource_usage / total_resource_mobilized

    def __repr__(self) -> str:
        oversize: str = f"<{len(self.oversize_vms)} oversize VMs>" if self.oversize_vms is not None else ""
        return f"Solution {self.algo_name}: [{self.n_servers} servers]" \
               f"<{self.filling_rate().mean()*100:.1f}% full>{oversize}"

    def __int__(self) -> int:
        return self.n_servers
