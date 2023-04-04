from typing import Optional

import pandas as pd

from vm_placement.algorithms.approximation.approx_algo import ApproxAlgo
from vm_placement.algorithms.solution import Solution
from tqdm import tqdm

from vm_placement.data_handling.processing import resource_columns


class FirstFitAlgo(ApproxAlgo):
    def solve(self, vms: pd.DataFrame, server_capacities: pd.DataFrame):

        server_fillings = pd.DataFrame(0, index=server_capacities.index, columns=server_capacities.columns)
        oversize_vms = pd.DataFrame(columns=vms.columns)

        for i, vm in tqdm(vms.iterrows()):
            first_fit_index: Optional[int] = self._find_next_fitting_server(0, vm, server_capacities, server_fillings)

            # Insert VM in the server if a server with space was found
            if first_fit_index is not None:
                self._add_vm_to_server(vm, server_fillings, first_fit_index)
            # If it doesn't fit, add the VM to the list of oversize
            else:
                oversize_vms = pd.concat([oversize_vms, vm.to_frame().T])
        return Solution(server_capacities, server_fillings, oversize_vms, algo_name=str(self))


class FirstFitDivideAlgo(ApproxAlgo):

    def solve(self, vms: pd.DataFrame, server_capacities: pd.DataFrame):
        curr_server: int = 0
        server_fillings = pd.DataFrame(0, index=server_capacities.index, columns=server_capacities.columns)

        for i, vm in tqdm(vms.iterrows()):
            remainder: Optional[pd.Series] = vm
            while remainder is not None:
                remainder = self._fit_and_partition_vm(
                    remainder,
                    server_capacities,
                    server_fillings,
                    curr_server
                )
                if remainder is not None:
                    curr_server += 1

        return Solution(server_capacities, server_fillings, algo_name=str(self))

    def _fit_and_partition_vm(self, vm, server_capacities, server_fillings, curr_server) -> Optional[pd.Series]:
        # If the VM fits in the current server, add it to the server and return None as a remainder
        if self._vm_fits_in_server(vm, server_capacities.loc[curr_server], server_fillings.loc[curr_server]):
            self._add_vm_to_server(vm, server_fillings, curr_server)
            return None

        # Otherwise,
        else:
            # Calculate what fraction of the VM can fit in te server
            space_left = server_capacities.loc[curr_server] - server_fillings.loc[curr_server]
            resource_criticity = space_left[resource_columns] / vm[resource_columns]
            cutting_fraction = min(resource_criticity.min(), 1.)

            # Calculate the amount of ech resource corresponds to that fraction and add it
            resource_portion_that_fits = vm[resource_columns] * cutting_fraction
            resource_portion_that_remains = vm[resource_columns] - resource_portion_that_fits
            vm_portion_that_fits = vm.copy()
            vm_portion_that_fits[resource_columns] = resource_portion_that_fits
            self._add_vm_to_server(resource_portion_that_fits, server_fillings, curr_server)

            # Calculate the remainder that needs to be fit to another VM
            remainder = vm.copy()
            remainder[resource_columns] = resource_portion_that_remains
            return remainder




if __name__ == '__main__':
    from vm_placement.data_handling.data_loader import Data

    server_capacity = pd.DataFrame({
        'vCPU': [64],
        'Memory': [512],
        'Storage': [2048]
    })
    data = Data(
        vm_filepath='data/vm_data.csv',
        server_specs=server_capacity,
        n_servers=10000
    )
    first_fit_divide = FirstFitDivideAlgo()
    solution = first_fit_divide.solve(data.vm_data, data.server_data)
    solution.display()