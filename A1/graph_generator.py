import networkx as nx
import random
import matplotlib.pyplot as plt

def generate_random_graph(num_nodes):
    # Create an empty graph
    G = nx.Graph()

    # Add nodes to the graph
    G.add_nodes_from(range(num_nodes))

    # Add edges to achieve desired degree distribution
    for node in G.nodes():
        degree = random.randint(3, 6)
        while G.degree(node) < degree:
            # Choose a random node to connect to
            neighbor = random.choice(list(G.nodes()))
            
            # Avoid self-loops and parallel edges
            if neighbor != node and not G.has_edge(node, neighbor):
                if G.degree(neighbor) < 6:
                    G.add_edge(node, neighbor)

    return G

# Number of nodes in the graph
num_nodes = 400

# Generate the random graph
random_graph = generate_random_graph(num_nodes)
is_connected = nx.is_connected(random_graph)
num_edges = random_graph.number_of_edges()
print(is_connected, num_edges)
# Visualize the graph (optional)
pos = nx.spring_layout(random_graph)
nx.draw(random_graph, pos, with_labels=True, node_size=100, node_color='skyblue', font_size=8, font_color='black', font_weight='bold', edge_color='gray')
plt.show()
