import networkx as nx
import random
import matplotlib.pyplot as plt

def generate_random_graph(num_nodes):
    # Create an empty graph
    graph = nx.Graph()

    # Add nodes to the graph
    graph.add_nodes_from(range(num_nodes))
    deg_sequence = [random.randint(3,6) for i in range(num_nodes)]
    while not nx.is_graphical(deg_sequence):
        deg_sequence = [random.randint(3,6) for i in range(num_nodes)]
    while True:
        graph = nx.random_degree_sequence_graph(deg_sequence)
        if nx.is_connected(graph):
            break
    return list(graph.edges())


# Visualize the random graph
def show_random_graph(random_graph):
    num_edges = random_graph.number_of_edges()
    print(num_edges)
    # Visualize the graph (optional)
    pos = nx.spring_layout(random_graph)
    nx.draw(random_graph, pos, with_labels=True, node_size=100, node_color='skyblue', font_size=8, font_color='black', font_weight='bold', edge_color='gray')
    plt.show()


