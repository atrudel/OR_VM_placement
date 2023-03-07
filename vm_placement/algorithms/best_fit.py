from typing import Union, List, Optional

import pandas as pd
from tqdm import tqdm

from vm_placement.algorithms.algo import Algo
from vm_placement.algorithms.solution import Solution
from vm_placement.data_handling.processing import resource_columns
from vm_placement.data_handling.sorting import compute_and_add_weighted_resources


class BestFitAlgo(Algo):
    def __init__(self, criterion: Union[str, List[str]]):
        self.sorting_criterion = criterion

    def solve(self, vms: pd.DataFrame, server_capacities: pd.DataFrame, scarcity_ratio=None):
        curr_server: int = 0
        server_fillings = pd.DataFrame(0, index=server_capacities.index, columns=server_capacities.columns)
        oversize_vms = pd.DataFrame(columns=vms.columns)

        for i, vm in tqdm(vms.iterrows()):
            # Find the best already visited server where the VM fits
            best_fitting_server = self._find_best_fitting_server(vm, server_capacities, server_fillings, curr_server, scarcity_ratio)
            if best_fitting_server is not None:
                self._add_vm_to_server(vm, server_fillings, best_fitting_server)
            else:
                # Find a server where the VM fits in the non-visited servers.
                next_fit_index: Optional[int] = self._find_next_fitting_server(curr_server, vm, server_capacities, server_fillings)
                if next_fit_index is not None:
                    curr_server = next_fit_index
                    self._add_vm_to_server(vm, server_fillings, curr_server)
                else:
                    oversize_vms = pd.concat([oversize_vms, vm.to_frame().T])
        return Solution(server_capacities, server_fillings, oversize_vms, algo_name=str(self))

    def _find_best_fitting_server(self,
                                  vm: pd.Series,
                                  server_capacities: pd.DataFrame,
                                  server_fillings: pd.DataFrame,
                                  curr_server: int,
                                  scarcity_ratio: pd.Series
                                  ) -> Optional[int]:
        space_left: pd.DataFrame = server_capacities[resource_columns] - server_fillings[resource_columns]
        space_left = space_left[:][:curr_server]
        if self.sorting_criterion == 'weighted_resources':
            space_left = compute_and_add_weighted_resources(space_left, scarcity_ratio)
        space_left = space_left.sort_values(self.sorting_criterion, ascending=True)

        for index, space_in_server in space_left.iterrows():
            if self._vm_fits_in_space_left(vm, space_in_server):
                return index
        return None

if __name__ == '__main__':
    from vm_placement.data_handling.data_loader import Data

    server_capacity = pd.DataFrame({
        'vCPU': [64],
        'Memory': [512],
        'Storage': [2048]
    })
    data = Data(
        vm_filepath='data/vm_data.csv',
        server_specs=server_capacity
    )
    best_fit = BestFitAlgo(criterion='Storage')
    solution = best_fit.solve(data.vm_data, data.server_data,)
    solution.display()