import pandas as pd

from vm_placement.algorithms.algo import Algo
from vm_placement.algorithms.fit_algos import BestFitAlgo
from vm_placement.data_handling.sorting import calculate_scarcity_ratio


def test_find_best_fitting_server():
    # Given
    best_fit: BestFitAlgo = BestFitAlgo(sorting_criterion='weighted_resources')
    vm = pd.Series({
        'vCPU': 4,
        'Memory': 8,
        'Storage': 100,
        'Class': 1
    })
    server_capacities = pd.DataFrame({
        'vCPU': [10] * 4,
        'Memory': [14] * 4,
        'Storage': [100] * 4
    })
    server_fillings = pd.DataFrame({
        'vCPU': [0, 6, 4, 0],
        'Memory': [0, 2, 2, 0],
        'Storage': [8, 0, 0, 0]
    })
    current_server: int = 2
    scarcity_ratio = pd.Series({
        'vCPU': 0.1,
        'Memory': 0.1,
        'Storage': 0.1
    })

    # When
    best_server_index = best_fit._find_best_fitting_server(
        vm,
        server_capacities,
        server_fillings,
        current_server,
        scarcity_ratio=scarcity_ratio
    )

    # Then
    expected_index = 1
    assert best_server_index == expected_index

def test_find_best_fitting_server_returns_none_if_no_fit():
    # Given
    best_fit: BestFitAlgo = BestFitAlgo(sorting_criterion='weighted_resources')
    vm = pd.Series({
        'vCPU': 4,
        'Memory': 8,
        'Storage': 100,
        'Class': 1
    })
    server_capacities = pd.DataFrame({
        'vCPU': [10] * 4,
        'Memory': [14] * 4,
        'Storage': [100] * 4
    })
    server_fillings = pd.DataFrame({
        'vCPU': [0, 6, 7, 0],
        'Memory': [0, 7, 2, 0],
        'Storage': [8, 0, 0, 0]
    })
    current_server: int = 2
    scarcity_ratio = pd.Series({
        'vCPU': 0.1,
        'Memory': 0.1,
        'Storage': 0.1
    })

    # When
    best_server_index = best_fit._find_best_fitting_server(
        vm,
        server_capacities,
        server_fillings,
        current_server,
        scarcity_ratio=scarcity_ratio
    )

    # Then
    assert best_server_index is None