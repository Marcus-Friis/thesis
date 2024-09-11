import igraph as ig
import numpy as np

def centralization(G: ig.Graph) -> float:
    if G.is_directed():
        raise ValueError('Centralization is only defined for undirected graphs')
    
    num_nodes = len(G.vs)
    G2 = ig.Graph.Star(num_nodes, mode = 'undirected')

    degrees_nominator = np.array(G.degree())
    degrees_denominator = np.array(G2.degree())

    max_centrality_nominator = np.max(degrees_nominator)
    max_centrality_denominator = np.max(degrees_denominator)

    centrality_nominator = max_centrality_nominator - degrees_nominator
    centrality_denominator = np.where(degrees_denominator > 0, max_centrality_denominator - degrees_denominator , 0)

    network_centralization = np.sum(centrality_nominator) / np.sum(centrality_denominator)
    
    return network_centralization
