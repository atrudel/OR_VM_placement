import matplotlib.pyplot as plt
import pandas as pd

from vm_placement.data_handling.processing import resource_columns


class Solution:
    def __init__(self, server_capacities: pd.DataFrame, server_fillings: pd.DataFrame):
        # Drop zero rows of non-used servers
        used_server_fillings = server_fillings.loc[(server_fillings != 0).any(axis=1)]
        self.server_fillings: pd.DataFrame = used_server_fillings
        self.n_servers: int = len(used_server_fillings)
        self.server_capacities: pd.DataFrame = server_capacities[:][:self.n_servers]

    def display(self):
        filling_rates = self.server_fillings / self.server_capacities
        for resource in resource_columns:
            plt.bar(filling_rates.index ,filling_rates[resource], alpha=0.5, label=resource)
        plt.xlabel('Server numero')
        plt.ylabel('% resource usage')
        plt.legend()
        plt.title(self)
        plt.show()
        print("Filling rates")
        print(self.filling_rate())

    def filling_rate(self) -> float:
        total_resource_usage = self.server_fillings.sum()
        total_resource_mobilized = self.server_capacities.sum()
        return total_resource_usage / total_resource_mobilized

    def __repr__(self) -> str:
        return f"SOLUTION[{self.n_servers} servers]<{self.filling_rate().mean()*100:.1f}% full>"

    def __int__(self) -> int:
        return self.n_servers
