# Define and solve flow problem on a quantum hierarchical network using gurobi
import gurobipy as gp
from gurobipy import GRB
import networkx as nx
import numpy as np
from utils.demand import Demand

# Define Problem class

def define_flow_problem(G: nx.DiGraph, demand: list[Demand]):
    """
    Define the flow problem on a quantum hierarchical network.

    Parameters:
        G (nx.DiGraph): 
            Directed graph representing the quantum network.
        demand (List[Demand]): 
            Contains source, destination clients, qubit demand between them, and distance threshold
            for each demand.

    Returns:
        A tuple containing variables and the defined problem.

    """
    # Create a new model
    model = gp.Model("QuantumFlowProblem")

    # Variables
    # Indicator variables for each demand (chi)
    demand_vars = model.addVars(len(demand), vtype=GRB.BINARY, name="demand_vars")

    # Flow variables for each demand and each edge (f)
    flow_vars = model.addVars(len(demand), len(G.edges()), vtype=GRB.CONTINUOUS, name="flow_vars")

    # Potential variables for every demand and node (p)
    potentials = model.addVars(len(demand), len(G.nodes()), vtype=GRB.CONTINUOUS, name="potentials")

    # Delta variables for each demand and each edge (delta)
    edge_deltas = model.addVars(len(demand), len(G.edges()), vtype=GRB.BINARY, name="edge_deltas")

    # Objective function
    # Maximize the number of demands satisfied
    model.setObjective(gp.quicksum(demand_vars[i] for i in range(len(demand))), GRB.MAXIMIZE)

    # Mapping edges to indices
    edge_indices = {edge: i for i, edge in enumerate(G.edges())}
    # Mapping nodes to indices
    node_indices = {node: i for i, node in enumerate(G.nodes())}

    # Constraints
    # Superimposed flow on each edge
    for i, edge in enumerate(G.edges()):
        # SUM_OVER_DEMANDS[chi_d * f_d,e] <= capacity_e
        for j, _ in enumerate(demand):
            model.addConstr(gp.quicksum(demand_vars[j] * flow_vars[j, i] for j in range(len(demand))) <= G.edges[edge]['capacity'], name=f"superimposed_flow_{i}")

    # Flow conservation constraints
    for i, node in enumerate(G.nodes()):
        # Check if node is not a repeater
        if G.nodes[node]['type'] != 'repeater':
            continue
        for j, _ in enumerate(demand):
            # Flow conservation: incoming flow = outgoing flow
            model.addConstr(
                gp.quicksum(flow_vars[j, edge_indices[edge]] for edge in G.in_edges(node)) -
                gp.quicksum(flow_vars[j, edge_indices[edge]] for edge in G.out_edges(node)) == 0,
                name=f"flow_conservation_{i}_{j}"
            )

    # Capacity constraints
    for i, edge in enumerate(G.edges()):
        for j, _ in enumerate(demand):
            # Flow on edge is positive
            model.addConstr(flow_vars[j, i] >= 0, name=f"flow_positive_{i}_{j}")
            # Flow on edge is less than capacity
            model.addConstr(flow_vars[j, i] <= edge_deltas[j, i] * G.edges[edge]['capacity'], name=f"flow_capacity_{i}_{j}")

    # Sink constraints
    for i, (src, dst, qubits, _) in enumerate(demand):
        # Flow conservation at src
        model.addConstr(
            gp.quicksum(flow_vars[i, edge_indices[edge]] for edge in G.in_edges(f"client_{src}")) == qubits,
            name=f"flow_conservation_src_{i}"
            )
        # Flow conservation at dst
        model.addConstr(
            gp.quicksum(flow_vars[i, edge_indices[edge]] for edge in G.in_edges(f"client_{dst}")) == qubits,
            name=f"flow_conservation_dst_{i}"
            )

    # Potential constraints
    for i, (src, dst, _, thres) in enumerate(demand):
        for j, node in enumerate(G.nodes()):
            # If the node is a generator, set potential to 0
            if G.nodes[node]['type'] == 'generator':
                model.addConstr(potentials[i, j] == 0, name=f"potential_generator_{i}_{j}")

            # If the node is src or dst, set potential <= threshold
            elif node == f"client_{src}" or node == f"client_{dst}":
                model.addConstr(potentials[i, j] <= thres, name=f"potential_client_{i}_{j}")

        for k, edge in enumerate(G.edges()):
            # Potential difference constraints
            model.addConstr(potentials[i, node_indices[edge[1]]] - potentials[i, node_indices[edge[0]]] >= edge_deltas[i, k], name=f"potential_difference_{i}_{k}")

    # Objective function (sum of chis)
    model.setObjective(gp.quicksum(demand_vars[i] for i in range(len(demand))), GRB.MAXIMIZE)

    # Return the model and variables
    return model, demand_vars, flow_vars, potentials, edge_deltas

# Solve function
def solve_flow_problem(model):
    """
    Solve the flow problem using Gurobi.

    Parameters:
    model (gurobipy.Model): 
        The Gurobi model to be solved.

    Returns:
        The solution of the model.
    """
    # Optimize the model
    model.optimize()

    # Check if the model is feasible
    if model.status == GRB.OPTIMAL:
        return model
    else:
        print("No optimal solution found.")
        return None

# Example usage
if __name__ == "__main__":
    # Load the graph from gml
    # G = nx.read_gml("hqnw_graph.gml")

    # Create an example directed graph
    G = nx.DiGraph()
    G.add_node("generator_0", type="generator")
    G.add_node("repeater_0", type="repeater")
    G.add_node("repeater_1", type="repeater")
    G.add_node("client_0", type="client")
    G.add_node("client_1", type="client")

    G.add_edge("generator_0", "repeater_0", capacity=10)
    G.add_edge("generator_0", "repeater_1", capacity=5)
    G.add_edge("repeater_0", "repeater_1", capacity=5)
    G.add_edge("repeater_0", "client_0", capacity=5)
    G.add_edge("repeater_1", "client_1", capacity=4)


    # Define demand (source, destination, qubit demand, threshold)
    demand = [
        Demand(0, 1, 4, 3),
    ]

    # Define the flow problem
    model, demand_vars, flow_vars, potentials, edge_deltas = define_flow_problem(G, demand)

    # Solve the flow problem
    solution = solve_flow_problem(model)

    # Print the solution
    if solution:
        print("Optimal solution found:")
        for var in model.getVars():
            print(f"{var.VarName}: {var.X}")
        print(f"Objective value: {model.objVal}")
    else:
        print("No optimal solution found.")



    
