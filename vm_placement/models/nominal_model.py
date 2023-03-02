import pyomo.environ as pyo
from pyomo.environ import AbstractModel

from vm_placement.data_handlers.data_loader import Data


class NominalModel:
    def __init__(self, linear_relaxation: bool = False):
        self.linear_relaxation: bool = linear_relaxation
        self.model = AbstractModel()
        self.model = self._add_variables(self.model)
        self.model = self._add_constraints(self.model)
        self.model = self._add_objective(self.model)

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
        domain = pyo.PercentFraction if self.linear_relaxation else pyo.Binary

        model.x = pyo.Var(model.I_vm, model.J_server, domain=domain)
        model.y = pyo.Var(model.J_server, domain=domain)

        return model

    def _add_constraints(self, model) -> AbstractModel:
        def constraint_rule_vm_demand(model: AbstractModel, i_vm: int):
            """Each copy of a demanded VM must be located in exactly ONE server"""
            return sum(model.x[i_vm, j] for j in model.J_server) == 1

        def constraint_rule_cpu_capacity(model: AbstractModel, j_server: int):
            return sum(
                model.cpu_requirement[i] * model.x[i, j_server]
                for i in model.I_vm
            ) <= model.cpu_capacity[j_server]

        def constraint_rule_memory_capacity(model: AbstractModel, j_server: int):
            return sum(
                model.memory_requirement[i] * model.x[i, j_server]
                for i in model.I_vm
            ) <= model.memory_capacity[j_server]

        def constraint_rule_storage_capacity(model: AbstractModel, j_server: int):
            return sum(
                model.storage_requirement[i] * model.x[i, j_server]
                for i in model.I_vm
            ) <= model.storage_capacity[j_server]

        def constraint_rule_server_count(model: AbstractModel, i_vm, j_server):
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
        data_dict = self._format_data(data)
        model_instance = self.model.create_instance(data_dict)
        opt = pyo.SolverFactory('glpk')
        solution = opt.solve(model_instance)
        return solution

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
        # return {
        #     None: {
        #         'n_vms': {None: 2},
        #         'cpu_requirement': {1: 10, 2:20},
        #         'memory_requirement': {1: 10, 2:20},
        #         'storage_requirement': {1: 10, 2:20},
        #         'm_servers': {None: 3},
        #         'cpu_capacity': {1:20, 2:20, 3: 20},
        #         'memory_capacity': {1:30, 2:30, 3: 30},
        #         'storage_capacity': {1:30, 2:30, 3: 30}
        #     }
        # }



if __name__ == '__main__':
    data = Data('data/vm_data.csv', 'data/unique_server_data.csv')
    model = NominalModel(linear_relaxation=True)
    solution = model.solve(data)
    print(solution)


