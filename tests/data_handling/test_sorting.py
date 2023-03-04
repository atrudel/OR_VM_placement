from unittest.mock import Mock

import pandas as pd
from pandas.core.indexes.numeric import Int64Index

from vm_placement.data_handling import Data
from vm_placement.data_handling.sorting import calculate_scarcity_ratio, sort_by_scarcity_ratio


def test_calculate_scarcity_ratio():
    # Given
    data: Data = Mock(Data)
    data.vm_data = pd.DataFrame({
        'vCPU': [1, 3],
        'Memory': [4,6],
        'Storage': [9, 11],
        'Class': [1,2]
    })
    data.server_data = pd.DataFrame({
        'vCPU': [9, 11],
        'Memory': [9, 11],
        'Storage': [9, 11]
    })

    # When
    scarcity_ratio = calculate_scarcity_ratio(data)

    # Then
    expected_scarcity_ratio = pd.Series({
        'vCPU': 0.2,
        'Memory': 0.5,
        'Storage': 1.
    })
    pd.testing.assert_series_equal(expected_scarcity_ratio, scarcity_ratio)


def test_sort_by_scarcity_ratio():
    # Given
    vm_data = pd.DataFrame({
        'vCPU':     [1, 4, 2, 10],
        'Memory':   [2, 3, 2, 10],
        'Storage':  [3, 2, 2, 10],
        'Class':    [1, 2, 3, 4]
    })
    scarcity_ratio = pd.Series({
        'vCPU': 0.5,
        'Memory': 0.1,
        'Storage': 0.1,
    })

    # When
    sorted_vm = sort_by_scarcity_ratio(vm_data, scarcity_ratio)

    # Then
    expected_sorted_vms = pd.DataFrame({
        'vCPU':     [10, 4, 2, 1],
        'Memory':   [10, 3, 2, 2],
        'Storage':  [10, 2, 2, 3],
        'Class':    [4, 2, 3, 1]
    }, index=Int64Index([3,1,2,0]))
    pd.testing.assert_frame_equal(expected_sorted_vms, sorted_vm)

def test_sort_by_scarcity_ratio_handles_diff_unit_scales():
    # Given
    vm_data = pd.DataFrame({
        'vCPU':     [1, 4, 2, 10],
        'Memory':   [2, 2, 2, 2],
        'Storage':  [300, 200, 100, 10],
        'Class':    [1, 2, 3, 4]
    })
    scarcity_ratio = pd.Series({
        'vCPU': 0.8,
        'Memory': 0.1,
        'Storage': 0.1,
    })

    # When
    sorted_vm = sort_by_scarcity_ratio(vm_data, scarcity_ratio)

    # Then
    expected_sorted_vms = pd.DataFrame({
        'vCPU':     [10, 4, 2, 1],
        'Memory':   [2, 2, 2, 2],
        'Storage':  [10, 200, 100, 300],
        'Class':    [4, 2, 3, 1]
    }, index=Int64Index([3,1,2,0]))
    pd.testing.assert_frame_equal(expected_sorted_vms, sorted_vm)