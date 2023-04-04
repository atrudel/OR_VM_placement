import pandas as pd

from vm_placement.algorithms.approximation.approx_algo import ApproxAlgo


def test_vm_fits_in_server_when_empty():
    # Given
    algo = ApproxAlgo()
    vm = pd.Series({
        'vCPU': 4,
        'Memory': 8,
        'Storage': 10,
        'Class': 1
    })
    server_capacity = pd.Series({
        'vCPU': 10,
        'Memory':20,
        'Storage': 100
    })
    server_filling = pd.Series({
        'vCPU': 0,
        'Memory': 0,
        'Storage': 0
    })

    # When
    fits = algo._vm_fits_in_server(vm, server_capacity, server_filling)

    # Then
    assert fits == True

def test_vm_fits_in_server_not_when_short_one_resource():
    # Given
    algo = ApproxAlgo()
    vm = pd.Series({
        'vCPU': 4,
        'Memory': 8,
        'Storage': 10,
        'Class': 1
    })
    server_capacity = pd.Series({
        'vCPU': 10,
        'Memory':20,
        'Storage': 7
    })
    server_filling = pd.Series({
        'vCPU': 0,
        'Memory': 0,
        'Storage': 0
    })

    # When
    fits = algo._vm_fits_in_server(vm, server_capacity, server_filling)

    # Then
    assert fits == False

def test_vm_fits_in_server_not_when_server_filled():
    # Given
    algo = ApproxAlgo()
    vm = pd.Series({
        'vCPU': 4,
        'Memory': 8,
        'Storage': 100,
        'Class': 1
    })
    server_capacity = pd.Series({
        'vCPU': 10,
        'Memory':20,
        'Storage': 7
    })
    server_filling = pd.Series({
        'vCPU': 7,
        'Memory': 12,
        'Storage': 50
    })

    # When
    fits = algo._vm_fits_in_server(vm, server_capacity, server_filling)

    # Then
    assert fits == False

def test_add_vm_to_server_correctly_adds_when_empty():
    # Given
    algo: ApproxAlgo = ApproxAlgo()
    vm = pd.Series({
        'vCPU': 4,
        'Memory': 8,
        'Storage': 100,
        'Class': 1
    })
    server_fillings = pd.DataFrame({
        'vCPU': [10, 0, 0,],
        'Memory': [14, 0, 0],
        'Storage': [50, 0, 0]
    })
    current_server: int = 1

    # When
    algo._add_vm_to_server(vm, server_fillings, current_server)

    # Then
    expected_filling = pd.DataFrame({
        'vCPU': [10, 4, 0,],
        'Memory': [14, 8, 0],
        'Storage': [50, 100, 0]
    })

    pd.testing.assert_frame_equal(expected_filling, server_fillings)


def test_add_vm_to_server_correctly_adds_when_partially_filled():
    # Given
    algo: ApproxAlgo = ApproxAlgo()
    vm = pd.Series({
        'vCPU': 4,
        'Memory': 8,
        'Storage': 100,
        'Class': 1
    })
    server_fillings = pd.DataFrame({
        'vCPU': [10, 12, 0, ],
        'Memory': [14, 2, 0],
        'Storage': [50, 8, 0]
    })
    current_server: int = 1

    # When
    algo._add_vm_to_server(vm, server_fillings, current_server)

    # Then
    expected_filling = pd.DataFrame({
        'vCPU': [10, 12+4, 0, ],
        'Memory': [14, 2+8, 0],
        'Storage': [50, 8+100, 0]
    })

    pd.testing.assert_frame_equal(expected_filling, server_fillings)


