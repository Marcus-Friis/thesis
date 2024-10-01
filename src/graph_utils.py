import igraph as ig
import numpy as np
from scipy.sparse import lil_matrix

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
    centrality_star = max_degree_star - degrees_star
    #used to be: np.where(degrees_star > 0, max_degree_star - degrees_star, 0)
    degree_centralization = np.sum(centrality) / np.sum(centrality_star)
    
    return degree_centralization


def closeness_centralization(G: ig.Graph) -> float:
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

    closeness = np.array(G.closeness())
    closeness_star = np.array(star.closeness())
    

    max_closeness = np.max(closeness)
    max_closeness_star = np.max(closeness_star)


    centrality = max_closeness - closeness
    centrality_star = max_closeness_star - closeness_star
    closeness_centralization = np.sum(centrality) / np.sum(centrality_star)
    
    return closeness_centralization

def betweenness_centralization(G: ig.Graph) -> float:
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

    betweenness = np.array(G.betweenness())
    betweenness_star = np.array(star.betweenness())

    max_betweenness = np.max(betweenness)
    max_betweenness_star = np.max(betweenness_star)

    centrality = max_betweenness - betweenness
    centrality_star = max_betweenness_star - betweenness_star


    betweenness_centralization = np.sum(centrality) / np.sum(centrality_star)


    return betweenness_centralization    


def project_graph(G: ig.Graph) -> ig.Graph:
    A = G.get_adjacency_sparse()
    A_proj = A @ A.T
    A_proj = lil_matrix(A_proj)  # Convert to lil_matrix for efficient modification
    A_proj.setdiag(0)  # Set diagonal to 0
    A_proj = A_proj.tocsr()  # Convert back to csr_matrix for efficient operations
    G_proj = ig.Graph.Adjacency(A_proj, mode='undirected')
    return G_proj

    
if __name__ == '__main__':
    pass
