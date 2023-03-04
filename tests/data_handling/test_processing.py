import pandas as pd

from vm_placement.data_handling.processing import duplicate_entry


def test_duplicate_entry():
    # Given
    server_data = pd.DataFrame({
        'vCPU': [10],
        'Memory': [20],
        'Storage': [30]
    })
    n_times = 20

    # When
    duplicated_server_data = duplicate_entry(server_data, n_times)

    # Then
    expected_duplicated_data = pd.DataFrame({
        'vCPU': [10] * n_times,
        'Memory': [20] * n_times,
        'Storage': [30] * n_times
    })
    pd.testing.assert_frame_equal(expected_duplicated_data, duplicated_server_data)