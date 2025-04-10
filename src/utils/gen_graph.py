# Generate a random directed graph with a given number of nodes and edges
import random
import networkx as nx
import math
import matplotlib.pyplot as plt

# Generate random hierarchical quantum network directional graph with capacities for each edge
def generate_random_hqnw(num_clients: int, num_repeaters: int, rep_coeff: float, gen_coeff: float, client_coeff: float, mean_cap: int):
    """
    Generate a random hierarchical quantum network directional graph with capacities for each edge.

    Parameters:
        num_clients (int): Number of clients.
        num_repeaters (int): Number of repeaters.
        rep_coeff (float): Coefficient for the number of repeaters.
        gen_coeff (float): Coefficient for the number of generators.
        client_coeff (float): Coefficient for the number of clients.
        mean_cap (int): Mean capacity for the edges.

    Notes:
    - Coefficients are a measure of controlling the number of edges in the graph.

    Returns:
        nx.DiGraph: A directed graph with capacities for each edge.
    """

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes for clients, repeaters, and generators
    for i in range(num_clients):
        G.add_node(f"client_{i}", type="client")
    for i in range(num_repeaters):
        G.add_node(f"repeater_{i}", type="repeater")
    G.add_node("generator", type="generator")

    # Add edges from generator to repeaters
    for i in range(num_repeaters):
        if random.random() < gen_coeff:
            capacity = math.ceil(random.gauss(mean_cap, mean_cap/2))
            if capacity > 0:
                G.add_edge("generator", f"repeater_{i}", capacity=capacity)

    # Add edges from repeaters to other repeaters
    for i in range(num_repeaters):
        for j in range(num_repeaters):
            if i != j and random.random() < rep_coeff:
                capacity = math.ceil(random.gauss(mean_cap, mean_cap/2))
                if capacity > 0:
                    G.add_edge(f"repeater_{i}", f"repeater_{j}", capacity=capacity)

    # Add edges from repeaters to clients
    for i in range(num_clients):
        isolated = True
        while isolated:
            for j in range(num_repeaters):
                if random.random() < client_coeff:
                    isolated = False
                    capacity = math.ceil(random.gauss(mean_cap, mean_cap/2))
                    if capacity > 0:
                        G.add_edge(f"repeater_{j}", f"client_{i}", capacity=capacity)

    # Remove self-loops
    G.remove_edges_from(nx.selfloop_edges(G))

    # Remove repeater nodes with no paths to clients
    for node in list(G.nodes):
        if G.nodes[node]["type"] == "repeater" and not any(G.has_edge(node, f"client_{j}") for j in range(num_clients)):
            G.remove_node(node)

    # Return the generated graph
    return G

# Draw the graph
def draw_graph(G: nx.DiGraph, filename: str | None = None):
    """
    Draw the graph with node labels and edge capacities.

    Parameters:
    G (nx.DiGraph): The directed graph to draw.
    """
    # Create shells
    rep_nodes = [n for n in G.nodes if G.nodes[n]["type"] == "repeater"]
    client_nodes = [n for n in G.nodes if G.nodes[n]["type"] == "client"]
    gen_nodes = [n for n in G.nodes if G.nodes[n]["type"] == "generator"]
    shells = [gen_nodes, rep_nodes, client_nodes]

    # Draw the graph
    pos = nx.shell_layout(G, nlist=shells)
    labels = nx.get_edge_attributes(G, 'capacity')
    nx.draw(G, pos, with_labels=True, node_size=700, node_color='lightblue', font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.title("Hierarchical Quantum Network")
    plt.show()

    # Save the graph to a file if filename is provided
    if filename:
        plt.savefig(filename)
        plt.close()
    else:
        plt.show()

    # Return
    return

# Save the graph to a file
def save_graph(G: nx.DiGraph, filename: str):
    """
    Save the graph to a file.

    Parameters:
    G (nx.DiGraph): The directed graph to save.
    filename (str): The filename to save the graph to.
    """
    nx.write_gml(G, filename)
    return

# Example usage
if __name__ == "__main__":
    num_clients = 3
    num_repeaters = 7
    rep_coeff = 0.25
    gen_coeff = 0.40
    client_coeff = 0.20
    mean_cap = 10

    # Generate the graph
    G = generate_random_hqnw(num_clients, num_repeaters, rep_coeff, gen_coeff, client_coeff, mean_cap)
    draw_graph(G, filename="hqnw_graph.png")    

    # Save the graph to a GML file
    save_graph(G, filename="hqnw_graph.gml")
