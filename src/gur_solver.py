# Define and solve flow problem on a quantum hierarchical network using gurobi
import itertools
import gurobipy as gp
from gurobipy import GRB
import networkx as nx
from utils.gen_graph import generate_random_hqnw
from utils.demand import Demand

# Define Problem class

def edge_formulation(G: nx.DiGraph, demands: list[tuple[int, int], int, int]):
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
    demand_vars = model.addVars(len(demands), vtype=GRB.BINARY, name="demand_vars")

    # Flow variables for each demand and each edge (f)
    flow_vars = model.addVars(len(demands), len(G.edges()), vtype=GRB.INTEGER, name="flow_vars", lb=0)

    # Potential variables for every demand and node (p)
    potentials = model.addVars(len(demands), len(G.nodes()), vtype=GRB.CONTINUOUS, name="potentials")

    # Delta variables for each demand and each edge (delta)
    edge_deltas = model.addVars(len(demands), len(G.edges()), vtype=GRB.BINARY, name="edge_deltas")

    # Objective function
    # Maximize the number of demands satisfied
    model.setObjective(gp.quicksum(demand_vars[i] for i in range(len(demands))), GRB.MAXIMIZE)

    # Mapping edges to indices
    edge_indices = {edge: i for i, edge in enumerate(G.edges())}
    # Mapping nodes to indices
    node_indices = {node: i for i, node in enumerate(G.nodes())}

    # Constraints
    # Superimposed flow on each edge
    for i, edge in enumerate(G.edges()):
        # SUM_OVER_DEMANDS[f_d,e] <= capacity_e
        # This is a change from the original code
        # Basically, we set flow into a client to be zero if `chi_d` is 0, so that propagates across the graph to make
        # the flow zero everywhere.
        model.addConstr(gp.quicksum(flow_vars[j, i] for j in range(len(demands))) <= G.edges[edge]['capacity'], name=f"superimposed_flow_{i}")

    # Flow conservation constraints
    for i, node in enumerate(G.nodes()):
        # Check if node is not a repeater
        # Generator has no constraints and clients are sinks. 
        if G.nodes[node]['type'] != 'repeater':
            continue
        for j, _ in enumerate(demands):
            # Flow conservation: incoming flow = outgoing flow
            model.addConstr(
                gp.quicksum(flow_vars[j, edge_indices[edge]] for edge in G.in_edges(node)) -
                gp.quicksum(flow_vars[j, edge_indices[edge]] for edge in G.out_edges(node)) == 0,
                name=f"flow_conservation_{i}_{j}"
            )

    # Capacity constraints
    for i, edge in enumerate(G.edges()):
        for j, _ in enumerate(demands):
            # Flow on edge is less than capacity
            model.addConstr(flow_vars[j, i] <= edge_deltas[j, i] * G.edges[edge]['capacity'], name=f"flow_capacity_{i}_{j}")

    # Sink constraints
    for i, (src, dst, qubits, _) in enumerate(demands):
        # Flow conservation at src
        # This is a change from the original code
        # Refer to capacity constraint. Flow is zero if `chi_d` is 0.
        # This makes the program linear, which is a good improvement over bilinear.
        # Even for ILP, this is faster than the path stuff.
        model.addConstr(
            gp.quicksum(flow_vars[i, edge_indices[edge]] for edge in G.in_edges(f"client_{src}")) == qubits * demand_vars[i],
            name=f"flow_conservation_src_{i}"
        )
        # Flow conservation at dst
        model.addConstr(
            gp.quicksum(flow_vars[i, edge_indices[edge]] for edge in G.in_edges(f"client_{dst}")) == qubits * demand_vars[i],
            name=f"flow_conservation_dst_{i}"
        )

    # Potential constraints
    for i, (src, dst, _, thres) in enumerate(demands):
        for j, node in enumerate(G.nodes()):
            # If the node is a generator, set potential to 0
            if G.nodes[node]['type'] == 'generator':
                model.addConstr(potentials[i, j] == 0, name=f"potential_generator_{i}_{j}")

            # If the node is src or dst, set potential <= threshold
            elif node == f"client_{src}" or node == f"client_{dst}":
                model.addConstr(potentials[i, j] <= thres, name=f"potential_client_{i}_{j}")

        for k, edge in enumerate(G.edges()):
            # Potential difference constraints
            # p_v - p_u >= delta
            model.addConstr(potentials[i, node_indices[edge[1]]] - potentials[i, node_indices[edge[0]]] >= edge_deltas[i, k], name=f"potential_difference_{i}_{k}")

    # Return the model and variables
    return model, demand_vars, flow_vars, potentials, edge_deltas


def path_formulation(G: nx.DiGraph, demands: list[tuple[int, int], int, int]):
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
    # Create a new model
    model = gp.Model("QuantumFlowProblem")
    
    # Variables
    # Indicator variables for each demand (chi)
    demand_vars = model.addVars(len(demands), vtype=GRB.BINARY, name="demand_vars", ub=1)
    
    # clients = list(filter(lambda x: x["type"] == "client", G.nodes))
    # print(f"Number of clients: {len(clients)}")
    
    paths = {i: (
        list(nx.all_simple_paths(G, source="generator", target=f"client_{src}", cutoff=h)), 
        list(nx.all_simple_paths(G, source="generator", target=f"client_{dst}", cutoff=h))) 
        for i, (src, dst, _, h) in enumerate(demands)
    }
    
    paths_e = {e: [] for e in G.edges()}
    for i, p in enumerate(paths.values()):
        for a in itertools.pairwise(p[0]):
            paths_e[a].append(i)
        for b in itertools.pairwise(p[1]):
            paths_e[b].append(i)
            
    print("Pathsed")
            
    # Flow variables for each demand and each path (f)
    flow_vars = model.addVars(len(demands), sum(len(a) + len(b) for a, b in paths.values()), vtype=GRB.INTEGER, name="flow_vars", lb=0)
    
    # Objective function
    # Maximize the number of demands satisfied
    model.setObjective(gp.quicksum(demand_vars[i] for i in range(len(demand))), GRB.MAXIMIZE)
    
    # Constraints
    # Superimposed flow on each edge from all paths that contain it
    for i, edge in enumerate(G.edges()):
        # SUM_OVER_DEMANDS[chi_d * f_d,e] <= capacity_e
        model.addConstr(gp.quicksum(flow_vars[j, k] for j in range(len(demand)) for k in paths_e[edge]) <= G.edges[edge]['capacity'], name=f"superimposed_flow_{i}")
        
    # Demand atomicity
    for j, (_, _, qubits, _) in enumerate(demands):
        p = paths[j]
        model.addConstr(gp.quicksum(flow_vars[j, k] for k in range(len(p[0]))) == demand_vars[j] * qubits, name=f"flow_conservation_src_{j}")
        model.addConstr(gp.quicksum(flow_vars[j, k] for k in range(len(p[1]))) == demand_vars[j] * qubits, name=f"flow_conservation_dst_{j}")
            
    return model, demand_vars, flow_vars, paths, paths_e
    
# Solve function
def solve_flow_problem(model: gp.Model):
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
        print("Optimal solution found:")
        with open("solution.txt", "w") as f:
            for var in model.getVars():
                print(f"{var.varName}: {var.x}", file=f)
            print(f"Objective value: {model.objVal}", file=f)
    else:
        print("No optimal solution found.")
        return None

# Example usage
if __name__ == "__main__":
    G = generate_random_hqnw(15, 250, 0.06, 0.3, 0.3, 10)
    print(f"Generated graph with {len(G.nodes)} nodes and {len(G.edges)} edges.")


    # Define demand (source, destination, qubit demand, threshold)
    demand = [
        (0, 1, 4, 25),
        (1, 2, 3, 25),
        (2, 3, 2, 25),
        (3, 4, 1, 25),
        (4, 5, 2, 25),
        (5, 6, 3, 25),
        (6, 7, 4, 25),
        (7, 8, 5, 25),
        (8, 9, 6, 25),
        (9, 10, 7, 25),
        (10, 11, 8, 25),
        (11, 12, 9, 25),
        (12, 13, 10, 25),
        (0, 13, 10, 1),
    ]

    # Define the flow problem
    model, demand_vars, flow_vars, potentials, edge_deltas = edge_formulation(G, demand)
    # Solve the flow problem
    solve_flow_problem(model)
        
    # Taking too long
    # path_model, path_demand_vars, path_flow_vars, paths, paths_e = path_formulation(G, demand)
    # solve_flow_problem(path_model)



    
