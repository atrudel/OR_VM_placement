from typing import Optional

import pandas as pd

from vm_placement.data_handling.processing import resource_columns

class ApproxAlgo:
    """This is a generic class that contains helper methods useful for all its child classes."""
    def _vm_fits_in_space_left(self, vm: pd.Series, space_left: pd.Series):
        return (space_left[resource_columns] >= vm[resource_columns]).all()
    def _vm_fits_in_server(self, vm: pd.Series, server_capacity: pd.Series, server_filling: pd.Series) -> bool:
        space_left = server_capacity - server_filling
        return (space_left >= vm[resource_columns]).all()

    def _add_vm_to_server(self, vm: pd.Series, server_fillings: pd.DataFrame, server_index: int) -> None:
        server_fillings.loc[server_index] += vm[resource_columns]

    def _find_next_fitting_server(self, server_index: int, vm: pd.Series, server_capacities: pd.DataFrame,
                                  server_fillings: pd.DataFrame) -> Optional[int]:
        """Returns the index of the next server, starting at server_index, where the VM can fit entirely."""
        curr_server_idx: int = server_index

        # Try to fit the VM in each server one at a time
        while curr_server_idx < len(server_capacities) and \
                not self._vm_fits_in_server(vm, server_capacities.loc[curr_server_idx], server_fillings.loc[curr_server_idx]):
            curr_server_idx += 1

        # Return index, or None if we went beyond the number of available servers
        if curr_server_idx < len(server_capacities):
            return curr_server_idx
        else:
            return None

    def __repr__(self):
        return self.__class__.__name__



