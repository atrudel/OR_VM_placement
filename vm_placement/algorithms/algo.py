import pandas as pd

from vm_placement.data_handling.processing import resource_columns

class Algo:
    def _vm_fits_in_space_left(self, vm: pd.Series, space_left: pd.Series):
        return (space_left[resource_columns] >= vm[resource_columns]).all()
    def _vm_fits_in_server(self, vm: pd.Series, server_capacity: pd.Series, server_filling: pd.Series) -> bool:
        space_left = server_capacity - server_filling
        return (space_left >= vm[resource_columns]).all()

    def _add_vm_to_server(self, vm: pd.Series, server_fillings: pd.DataFrame, server_index: int) -> None:
        server_fillings.loc[server_index] += vm[resource_columns]


