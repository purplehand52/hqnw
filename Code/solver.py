# Define and solve flow problem on a quantum hierarchical network
import networkx as nx
import cvxpy as cp
import numpy as np

# Define Problem class
def define_flow_problem(G: nx.DiGraph, demand: list[tuple[int, int], int, int]):
    """
    Define the flow problem on a quantum hierarchical network.

    Parameters:
    G (nx.DiGraph): 
        Directed graph representing the quantum network.
    demand (List[(int, int), int, int]): 
        Contains source, destination clients, qubit demand between them, and distance threshold
        for each demand.

    Returns:
        A tuple containing variables and the defined problem.

    """
    # Variables
    # Indicator variables for each demand (chi)
    demand_vars = cp.Variable(len(demand), boolean=True)

    # Flow variables for each demand and each edge (f)
    flow_vars = cp.Variable((len(demand), len(G.edges())), nonneg=True)

    # Indicator variable for flow for a demand and each edge (delta)
    edge_deltas = cp.Variable((len(demand), len(G.edges())), boolean=True)

    # Potential variables for every demand and node (p)
    potentials = cp.Variable((len(demand), len(G.nodes())), nonneg=True)

    # Objective function
    # Maximize the number of demands satisfied
    objective = cp.Maximize(cp.sum(demand_vars))

    # Mapping edges to indices
    edge_indices = {edge: i for i, edge in enumerate(G.edges())}
    # Mapping nodes to indices
    node_indices = {node: i for i, node in enumerate(G.nodes())}

    # Constraints
    constraints = []

    # Superimposed flow on each edge
    superimposed_constraints = []
    for i, edge in enumerate(G.edges()):
        # chi_d * f_d,e <= capacity_e
        for j, (src, dst, _, _) in enumerate(demand):
            superimposed_constraints.append(
                    demand_vars[j] * flow_vars[j, i] <= G.edges[edge]['capacity']
                    )
    constraints += superimposed_constraints

    # Flow conservation constraints for each demand
    for j, (src, dst, qubits, _) in enumerate(demand):
        # Flow conservation at repeaters
        for node in G.nodes():
            if G.nodes[node]['type'] == 'repeater':
                # Get all indices of edges connected to the node
                in_edges = [edge_indices[edge] for edge in G.in_edges(node)]
                out_edges = [edge_indices[edge] for edge in G.out_edges(node)]

                flow_in = cp.sum(flow_vars[j, in_edges])
                flow_out = cp.sum(flow_vars[j, out_edges])
                constraints.append(flow_in == flow_out)

        # Flow conservation at clients
        in_src_edges = [edge_indices[edge] for edge in G.in_edges(f"client_{src}")]
        in_dst_edges = [edge_indices[edge] for edge in G.in_edges(f"client_{dst}")]

        flow_in_src = cp.sum(flow_vars[j, in_src_edges])
        flow_in_dst = cp.sum(flow_vars[j, in_dst_edges])
        constraints.append(flow_in_src == qubits)
        constraints.append(flow_in_dst == qubits)

        # Indicator flow constraints
        for k, edge in enumerate(G.edges()):
            constraints.append(flow_vars[j, k] <= edge_deltas[j, k] * G.edges[edge]['capacity'])

    # Potential constraints
    for j, (src, dst, _, thres) in enumerate(demand):
        # Potential difference constraints
        for node in G.nodes():
            node_idx = node_indices[node]
            if G.nodes[node]['type'] == 'generator':
                constraints.append(potentials[j, node_idx] == 0)
            elif G.nodes[node]['type'] == 'client':
                if node == f"client_{src}" or node == f"client_{dst}":
                    constraints.append(potentials[j, node_idx] <= thres)

        for edge in G.edges():
            node_id0 = node_indices[edge[0]]
            node_id1 = node_indices[edge[1]]
            edge_id = edge_indices[edge]
            constraints.append(potentials[j, node_id1] >= potentials[j, node_id0] + G.edges[edge]['capacity'] * edge_deltas[j, edge_id])

    # Return the all variables and the problem
    problem = cp.Problem(objective, constraints)
    return demand_vars, flow_vars, edge_deltas, potentials, problem

def solve_flow_problem(problem: cp.Problem):
    """
    Solve the flow problem on a quantum hierarchical network.

    Parameters:
    problem (cp.Problem): 
        The defined flow problem.

    Returns:
        A tuple containing the optimal value and the optimal variables.
    """
    # Solve the problem
    problem.solve()

    # Get the optimal value and variables
    optimal_value = problem.value
    demand_vars = problem.variables()[0].value
    flow_vars = problem.variables()[1].value
    edge_deltas = problem.variables()[2].value
    potentials = problem.variables()[3].value

    return optimal_value, demand_vars, flow_vars, edge_deltas, potentials

# Example usage
if __name__ == "__main__":
    # Load graph from file (gml file)
    G = nx.read_gml("hqnw_graph.gml")

    # Define demand (source, destination, qubit demand, distance threshold)
    demand = [
        (0, 1, 10, 3),
        (1, 2, 5, 2),
        (0, 2, 8, 4)
        ]

    # Define the flow problem
    demand_vars, flow_vars, edge_deltas, potentials, problem = define_flow_problem(G, demand)

    # Solve the flow problem
    optimal_value, demand_vars, flow_vars, edge_deltas, potentials = solve_flow_problem(problem)
    print("Optimal value:", optimal_value)
    print("Demand variables:", demand_vars)
    print("Flow variables:", flow_vars)
    print("Edge deltas:", edge_deltas)
    print("Potentials:", potentials)



    
