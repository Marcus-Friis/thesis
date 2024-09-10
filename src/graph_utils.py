import igraph as ig
import numpy as np

def centralization(G: ig.Graph) -> float:
    num_nodes = len(G.vs)
    
    # Get degrees and compute centrality
    degrees = np.array(G.degree())
    denominator = num_nodes - 1
    centrality = np.where(denominator > 0, degrees / denominator, 0)

    # Compute values for centralization
    n_val = float(len(centrality))
    c_denominator = (n_val - 1) * (n_val - 2)
    c_node_max = np.max(centrality)
    c_node_max_n_val_minus_1 = c_node_max * (n_val - 1)

    # Compute centralization
    c_numerator = np.sum(c_node_max_n_val_minus_1 - centrality * (n_val - 1))
    network_centralization = float(c_numerator / c_denominator)
    
    return network_centralization
