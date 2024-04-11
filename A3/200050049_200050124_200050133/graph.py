import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np

# Define the parameters for the power law graph
num_nodes = 100
random.seed(42)

# Create the power law graph using the Barabasi-Albert model
while True:
    G = nx.barabasi_albert_graph(num_nodes, m=2, seed=42)
    if nx.is_connected(G):
        break
A = nx.adjacency_matrix(G).todense()
print(nx.is_connected(G))
nx.draw(G, with_labels=True)
plt.savefig("sexy.png")
print(A)

