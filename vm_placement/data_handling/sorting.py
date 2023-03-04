from typing import List

import pandas as pd

from vm_placement.data_handling import Data
from vm_placement.data_handling.processing import resource_columns


def calculate_scarcity_ratio(data: Data) -> dict:
    mean_resource_requirement = data.vm_data[resource_columns].mean()
    mean_resource_availability = data.server_data[resource_columns].mean()
    return mean_resource_requirement / mean_resource_availability


def compute_and_add_weighted_resources(data: pd.DataFrame, scarcity_ratio: pd.Series):
    data_scaled = data[resource_columns] / data[resource_columns].max()
    weighted_resources = (data_scaled * scarcity_ratio).sum(axis=1)
    data['weighted_resources'] = weighted_resources
    return data

def sort_by_scarcity_ratio(data: pd.DataFrame, scarcity_ratio: pd.Series):
    data_scaled = data[resource_columns] / data[resource_columns].max()
    weighted_resources = (data_scaled * scarcity_ratio).sum(axis=1)
    data['weighted_resources'] = weighted_resources
    data = data.sort_values(by='weighted_resources', ascending=False)
    data = data.drop('weighted_resources', axis=1)
    return data