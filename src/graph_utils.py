import igraph as ig
import numpy as np

def degree_centralization(G: ig.Graph) -> float:
    if G.is_directed():
        raise ValueError('Centralization is only defined for undirected graphs')

    if G.vcount() < 3:
        raise ValueError('Centralization is only defined for graphs with at least 3 vertices')

    if not G.is_simple():
        raise ValueError('Centralization is only defined for simple graphs')

    if G.ecount() == 0:
        raise ValueError('Centralization is only defined for graphs with at least 1 edge')
    
    num_nodes = len(G.vs)
    star = ig.Graph.Star(num_nodes, mode = 'undirected')

    degrees = np.array(G.degree())
    degrees_star = np.array(star.degree())

    max_degree = np.max(degrees)
    max_degree_star = np.max(degrees_star)

    centrality = max_degree - degrees
    centrality_star = np.where(degrees_star > 0, max_degree_star - degrees_star , 0)

    degree_centralization = np.sum(centrality) / np.sum(centrality_star)
    
    return degree_centralization
