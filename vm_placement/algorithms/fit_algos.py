from typing import Union, List, Optional

import pandas as pd

from vm_placement.algorithms.algo import Algo
from vm_placement.algorithms.solution import Solution
from tqdm import tqdm

from vm_placement.data_handling.processing import resource_columns
from vm_placement.data_handling.sorting import compute_and_add_weighted_resources


class FirstFitAlgo(Algo):
    def solve(self, vms: pd.DataFrame, server_capacities: pd.DataFrame):
        curr_server: int = 0
        server_fillings = pd.DataFrame(0, index=server_capacities.index, columns=server_capacities.columns)

        for i, vm in tqdm(vms.iterrows()):
            while not self._vm_fits_in_server(vm, server_capacities.loc[curr_server], server_fillings.loc[curr_server]):
                curr_server += 1
            self._add_vm_to_server(vm, server_fillings, curr_server)
        return Solution(server_capacities, server_fillings)


class FirstFitDivideAlgo(Algo):

    def solve(self, vms: pd.DataFrame, server_capacities: pd.DataFrame):
        curr_server: int = 0
        server_fillings = pd.DataFrame(0, index=server_capacities.index, columns=server_capacities.columns)

        for i, vm in tqdm(vms.iterrows()):
            remainder: Optional[pd.Series] = vm
            while remainder is not None:
                remainder = self._fit_and_partition_vm(
                    vm,
                    server_capacities,
                    server_fillings,
                    curr_server
                )
                if remainder is not None:
                    curr_server += 1

        return Solution(server_capacities, server_fillings)

    def _fit_and_partition_vm(self, vm, server_capacities, server_fillings, curr_server) -> Optional[pd.Series]:
        if self._vm_fits_in_server(vm, server_capacities.loc[curr_server], server_fillings.loc[curr_server]):
            self._add_vm_to_server(vm, server_fillings, curr_server)
            return None
        else:
            space_left = server_capacities.loc[curr_server] - server_fillings.loc[curr_server]
            resource_criticity = space_left[resource_columns] / vm[resource_columns]
            cutting_fraction = resource_criticity.min()
            portion_to_fit = vm * cutting_fraction
            remainder = vm - portion_to_fit
            self._add_vm_to_server(portion_to_fit, server_fillings, curr_server)
            return remainder


class BestFitAlgo(Algo):
    def __init__(self, sorting_criterion: Union[str, List[str]]):
        self.sorting_criterion = sorting_criterion

    def solve(self, vms: pd.DataFrame, server_capacities: pd.DataFrame, scarcity_ratio=None):
        curr_server: int = 0
        server_fillings = pd.DataFrame(0, index=server_capacities.index, columns=server_capacities.columns)

        for i, vm in tqdm(vms.iterrows()):
            best_fitting_server = self._find_best_fitting_server(vm, server_capacities, server_fillings, curr_server, scarcity_ratio)
            if best_fitting_server is not None:
                self._add_vm_to_server(vm, server_fillings, best_fitting_server)
            else:
                while not self._vm_fits_in_server(vm, server_capacities.loc[curr_server], server_fillings.loc[curr_server]):
                    curr_server += 1
                self._add_vm_to_server(vm, server_fillings, curr_server)
        return Solution(server_capacities, server_fillings)

    def _find_best_fitting_server(self,
                                  vm: pd.Series,
                                  server_capacities: pd.DataFrame,
                                  server_fillings: pd.DataFrame,
                                  curr_server: int,
                                  scarcity_ratio: pd.Series
                                  ):
        space_left: pd.DataFrame = server_capacities[resource_columns] - server_fillings[resource_columns]
        space_left = space_left[:][:curr_server]
        if self.sorting_criterion == 'weighted_resources':
            space_left = compute_and_add_weighted_resources(space_left, scarcity_ratio)
        space_left = space_left.sort_values(self.sorting_criterion, ascending=True)

        for index, space_in_server in space_left.iterrows():
            if self._vm_fits_in_space_left(vm, space_in_server):
                return index
        return None


