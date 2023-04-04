# OR_VM_placement
Operational Research: bin packing problem applied to VM placement in servers

## Problem to solve
Consider a data file containing requests for some virtual machines (VMs) corresponding to specific virtual network functions of services.These VMs are to be run onto servers in DataCenters. Each VM is characterized by (name, nb vCPU, Memory (GB), DiskSpace (GB), class of service (S1, S2, S3)), whereas each server is characterized by (name, nb vCPU available, Memory (GB) available, DiskSpace available (GB)).
What would be the optimal packing of VMs into servers so as to minimize the number of servers needed ?
Propose a mathematical formulation and algorithms providing a feasible solution. Explain, and give some ways to derive upper and lower bounds on the optimal solution for each of the following VMs placement variants:
1. nominal case
2. anti-affinity rules between some set of VMs, some VMs are responsible for services that can’t be shared with some others.
3. all servers are partiallly loaded vs totally empty and all with the same characteristics
4. VMs could be splitted over several servers
5. Consider VMs families, each family is given a criticity level between 1 to 3 (Class 1 can’t share physical infra with VMs of class 3).
6. Are these algorithms adaptable to online cases ?

## Installation
Clone the repository and install the package `vm_placement` developed in it
```shell
git clone https://github.com/atrudel/OR_VM_placement.git
cd OR_VM_placement
pip install -e .
```

## Demo Notebooks
Two demo notebooks are present at the root of the repository:  
- The first one is named `demo_fit_algos.ipynb` and calls the algorithmic functions developed in the `vm_placement` package and displays the results.  
- [NEW!] The second one is `demo_linear_prog.ipynb` and calls the linear programming solver to find linear relaxation solutions for lower bounds.

## Upper-bound algorithms
First-fit and Best-fit algorithms were implemented with heuristics to pack the VMs in the servers.
They are implemented in the folder `vm_placement/algorithms`.

## Linear programming
The nominal problem was modeled with Pyomo to obtain the linear relaxation. It can also perform integer programming 
with the keyword argument `linear_relaxation=False`. It is implemented in the folder `vm_placement/lp_models`.

