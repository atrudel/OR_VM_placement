from typing import Optional

import pandas as pd

from vm_placement.algorithms.first_fit import FirstFitDivideAlgo



def test_fit_and_partition_vm_returns_remainder():
    # Given
    algo = FirstFitDivideAlgo()
    vm = pd.Series({
        'vCPU': 4,
        'Memory': 8,
        'Storage': 100,
        'Class': 1
    })
    server_capacities = pd.DataFrame({
        'vCPU': [5]*4,
        'Memory': [20]*4,
        'Storage': [1000]*4
    })
    server_fillings = pd.DataFrame({
        'vCPU': [4, 4, 4, 0],
        'Memory': [20, 8, 8, 0],
        'Storage': [100, 100, 100, 0]
    })
    current_server: int = 1

    # When
    remainder: Optional[pd.Series] = algo._fit_and_partition_vm(vm, server_capacities, server_fillings, current_server)

    # Then
    expected_filling = pd.DataFrame({
        'vCPU': [4, 5, 4, 0],
        'Memory': [20, 10, 8, 0],
        'Storage': [100, 125, 100, 0]
    })
    expected_remainder = pd.Series({
        'vCPU': 3,
        'Memory': 6,
        'Storage': 75,
        'Class': 1
    })
    pd.testing.assert_frame_equal(expected_filling, server_fillings)
    pd.testing.assert_series_equal(expected_remainder, remainder)


def test_fit_and_partition_vm_returns_full_vm_if_doesnt_fit_at_all():
    # Given
    algo = FirstFitDivideAlgo()
    vm = pd.Series({
        'vCPU': 4,
        'Memory': 8,
        'Storage': 100,
        'Class': 1
    })
    server_capacities = pd.DataFrame({
        'vCPU': [5]*4,
        'Memory': [20]*4,
        'Storage': [1000]*4
    })
    server_fillings = pd.DataFrame({
        'vCPU': [4, 4, 4, 0],
        'Memory': [20, 8, 8, 0],
        'Storage': [100, 100, 100, 0]
    })
    current_server: int = 0

    # When
    remainder: Optional[pd.Series] = algo._fit_and_partition_vm(vm, server_capacities, server_fillings, current_server)

    # Then
    expected_filling = pd.DataFrame({
        'vCPU': [4, 4, 4, 0],
        'Memory': [20, 8, 8, 0],
        'Storage': [100, 100, 100, 0]
    })
    expected_remainder = pd.Series({
        'vCPU': 4.,
        'Memory': 8.,
        'Storage': 100.,
        'Class': 1
    })
    pd.testing.assert_frame_equal(expected_filling, server_fillings)
    pd.testing.assert_series_equal(expected_remainder, remainder)


def test_fit_and_partition_vm_returns_none_if_fits_entirely():
    # Given
    algo = FirstFitDivideAlgo()
    vm = pd.Series({
        'vCPU': 4,
        'Memory': 8,
        'Storage': 100,
        'Class': 1
    })
    server_capacities = pd.DataFrame({
        'vCPU': [5]*4,
        'Memory': [20]*4,
        'Storage': [1000]*4
    })
    server_fillings = pd.DataFrame({
        'vCPU': [4, 4, 4, 0],
        'Memory': [20, 8, 8, 0],
        'Storage': [100, 100, 100, 0]
    })
    current_server: int = 3

    # When
    remainder: Optional[pd.Series] = algo._fit_and_partition_vm(vm, server_capacities, server_fillings, current_server)

    # Then
    expected_filling = pd.DataFrame({
        'vCPU': [4, 4, 4, 4],
        'Memory': [20, 8, 8, 8],
        'Storage': [100, 100, 100, 100]
    })
    pd.testing.assert_frame_equal(expected_filling, server_fillings)
    assert remainder is None



def test_fit_and_partition_large_vm_returns_none_if_fits_entirely():
    # Given
    algo = FirstFitDivideAlgo()
    vm = pd.Series({
        'vCPU': 16,
        'Memory': 32,
        'Storage': 2074,
        'Class': 2
    })
    server_capacities = pd.DataFrame({
        'vCPU': [64]*2,
        'Memory': [512]*2,
        'Storage': [2048]*2
    })
    server_fillings = pd.DataFrame({
        'vCPU': [0, 0],
        'Memory': [0, 0],
        'Storage': [0, 0]
    })
    current_server: int = 0

    # When
    remainder: Optional[pd.Series] = algo._fit_and_partition_vm(vm, server_capacities, server_fillings, current_server)

    # Then
    expected_filling = pd.DataFrame({
        'vCPU': [2048/2074 * 16, 0],
        'Memory': [2048/2074 * 32, 0],
        'Storage': [2048, 0]
    })
    expected_remainder = pd.Series({
        'vCPU': 16 - 2048/2074 * 16,
        'Memory': 32 - 2048/2074 * 32,
        'Storage': 2074 - 2048,
        'Class': 2
    })
    pd.testing.assert_frame_equal(expected_filling, server_fillings)
    pd.testing.assert_series_equal(expected_remainder, remainder)

