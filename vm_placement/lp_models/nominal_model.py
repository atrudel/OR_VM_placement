import pyomo.environ as pyo
from pyomo.environ import AbstractModel

from vm_placement.data_handling.data_loader import Data

import numpy as np


class NominalModel:
    def __init__(self, linear_relaxation: bool = False, solver: str = 'glpk', verbose: int = 1):
        self.linear_relaxation: bool = linear_relaxation
        self.solver: str = solver
        self.verbose: int = verbose
        self.model = AbstractModel()
        self.model = self._add_variables(self.model)
        self.model = self._add_constraints(self.model)
        self.model = self._add_objective(self.model)
        self.model_instance = None

    def _add_variables(self, model: AbstractModel) -> AbstractModel:

        # Indices
        model.n_vms = pyo.Param(within=pyo.NonNegativeIntegers)
        model.m_servers = pyo.Param(within=pyo.NonNegativeIntegers)

        model.I_vm = pyo.RangeSet(1, model.n_vms)
        model.J_server = pyo.RangeSet(1, model.m_servers)

        # Server resource capacities
        model.cpu_capacity = pyo.Param(model.J_server, domain=pyo.NonNegativeReals)
        model.memory_capacity = pyo.Param(model.J_server, domain=pyo.NonNegativeReals)
        model.storage_capacity = pyo.Param(model.J_server, domain=pyo.NonNegativeReals)

        # VM resource requirements
        model.cpu_requirement = pyo.Param(model.I_vm, domain=pyo.NonNegativeReals)
        model.memory_requirement = pyo.Param(model.I_vm, domain=pyo.NonNegativeReals)
        model.storage_requirement = pyo.Param(model.I_vm, domain=pyo.NonNegativeReals)

        # Decision variables
        x_domain = pyo.PercentFraction if self.linear_relaxation else pyo.Binary
        model.x = pyo.Var(model.I_vm, model.J_server, domain=x_domain)
        model.y = pyo.Var(model.J_server, domain=pyo.NonNegativeIntegers)

        return model

    def _add_constraints(self, model) -> AbstractModel:
        def constraint_rule_vm_demand(model: AbstractModel, i_vm: int):
            """Each VM must be located in exactly ONE server"""
            return sum(model.x[i_vm, j] for j in model.J_server) == 1

        def constraint_rule_cpu_capacity(model: AbstractModel, j_server: int):
            """The sum of the vCPU requirements of all VMs deployed in a server must not exceed its capacity."""
            return sum(
                model.cpu_requirement[i] * model.x[i, j_server]
                for i in model.I_vm
            ) <= model.cpu_capacity[j_server]

        def constraint_rule_memory_capacity(model: AbstractModel, j_server: int):
            """The sum of the Memory requirements of all VMs deployed in a server must not exceed its capacity."""
            return sum(
                model.memory_requirement[i] * model.x[i, j_server]
                for i in model.I_vm
            ) <= model.memory_capacity[j_server]

        def constraint_rule_storage_capacity(model: AbstractModel, j_server: int):
            """The sum of the Storage requirements of all VMs deployed in a server must not exceed its capacity."""
            return sum(
                model.storage_requirement[i] * model.x[i, j_server]
                for i in model.I_vm
            ) <= model.storage_capacity[j_server]

        def constraint_rule_server_count(model: AbstractModel, i_vm, j_server):
            """A server is considered used when at least one VM is deployed on it."""
            return model.x[i_vm, j_server] <= model.y[j_server]

        # Meeting VM demand
        model.DemandConstraint = pyo.Constraint(model.I_vm, rule=constraint_rule_vm_demand)

        # Not going over server capacities
        model.CPUCapacityConstraint = pyo.Constraint(model.J_server, rule=constraint_rule_cpu_capacity)
        model.MemoryCapacityConstraint = pyo.Constraint(model.J_server, rule=constraint_rule_memory_capacity)
        model.StorageCapacityConstraint = pyo.Constraint(model.J_server, rule=constraint_rule_storage_capacity)

        # Counting the number of active servers
        model.ServerCountConstraint = pyo.Constraint(model.I_vm, model.J_server, rule=constraint_rule_server_count)
        return model

    def _add_objective(self, model: AbstractModel) -> AbstractModel:
        def objective_expression(model):
            return pyo.summation(model.y)

        model.OBJ = pyo.Objective(rule=objective_expression, sense=pyo.minimize)
        return model

    def solve(self, data: Data):
        self._print(self._ascii_art())
        data_dict = self._format_data(data)
        self._print(f"Instianting model with {len(data.vm_data)} VMs and {len(data.server_data)} server specification(s)...")
        model_instance = self.model.create_instance(data_dict)
        opt = pyo.SolverFactory(self.solver)
        self._print(f"Launching solving with {self.solver}...{' [verbose off]' if self.verbose < 2 else ''}")
        solution = opt.solve(model_instance, tee=(self.verbose >= 2))
        self._print(f"Best solution found: {pyo.value(model_instance.OBJ)}")
        self.model_instance = model_instance
        return model_instance, solution

    def _format_data(self, data: Data) -> dict:

        # VM data
        data_dict = {
            None: {
                'n_vms': {None: len(data.vm_data)},
                'cpu_requirement': {i_vm+1: cpu_requirement for i_vm, cpu_requirement in data.vm_data['vCPU'].items()},
                'memory_requirement': {i_vm+1: memory_requirement for i_vm, memory_requirement in data.vm_data['Memory'].items()},
                'storage_requirement': {i_vm+1: storage_requirement for i_vm, storage_requirement in data.vm_data['Storage'].items()},
            }
        }

        # Server data
        if len(data.server_data) == 1:
            # Initialize with as many servers as vms
            m_servers = len(data.vm_data) // 2
            data_dict[None].update({
                'm_servers': {None: m_servers},
                'cpu_capacity': {j_server+1: data.server_data['vCPU'][0] for j_server in range(m_servers)},
                'memory_capacity': {j_server+1: data.server_data['Memory'][0] for j_server in range(m_servers)},
                'storage_capacity': {j_server+1: data.server_data['Storage'][0] for j_server in range(m_servers)}
            })
        else:
            raise NotImplemented("Case with multiple server capacities not yet implemented")
        return data_dict

    def _print(self, message: str):
        if self.verbose > 0:
            print(message)

    def _ascii_art(self) -> str:
        return """
██╗   ██╗███╗   ███╗    ██████╗ ██╗      █████╗  ██████╗███████╗███╗   ███╗███████╗███╗   ██╗████████╗
██║   ██║████╗ ████║    ██╔══██╗██║     ██╔══██╗██╔════╝██╔════╝████╗ ████║██╔════╝████╗  ██║╚══██╔══╝
██║   ██║██╔████╔██║    ██████╔╝██║     ███████║██║     █████╗  ██╔████╔██║█████╗  ██╔██╗ ██║   ██║   
╚██╗ ██╔╝██║╚██╔╝██║    ██╔═══╝ ██║     ██╔══██║██║     ██╔══╝  ██║╚██╔╝██║██╔══╝  ██║╚██╗██║   ██║   
 ╚████╔╝ ██║ ╚═╝ ██║    ██║     ███████╗██║  ██║╚██████╗███████╗██║ ╚═╝ ██║███████╗██║ ╚████║   ██║   
  ╚═══╝  ╚═╝     ╚═╝    ╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝╚══════╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝      
        """



if __name__ == '__main__':
    import pandas as pd

    # Specify server capacity
    server_capacity = pd.DataFrame({
        'vCPU': [64],
        'Memory': [512],
        'Storage': [2048]
    })
    data = Data('data/vm_data.csv', server_capacity, 1)
    # Remove oversize VMs
    data.filter_vms_by_resource('Storage', 2048)
    # Use a subset of the VMs
    data.subset_vms(10, seed=42)

    # Launch MIP solver
    model = NominalModel(linear_relaxation=True)
    model, solution = model.solve(data)
    print(solution)


