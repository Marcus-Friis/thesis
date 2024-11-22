import igraph as ig
import numpy as np
from scipy.sparse import lil_matrix
import re
import pandas as pd
import os

def load_edges(filepath: str) -> pd.DataFrame:
    # read edges from file
    edges = pd.read_csv(filepath, header=None)

    edges.columns = ['stitcher_url', 'stitchee_url']
    edges = edges[edges['stitcher_url'].str.contains('None') == False]
    edges = edges[edges['stitchee_url'].str.contains('None') == False]

    edges['stitcher'] = edges['stitcher_url'].apply(lambda x: x.split('/')[-1]).astype(np.int64)
    edges['stitchee'] = edges['stitchee_url'].apply(lambda x: x.split('/')[-1]).astype(np.int64)

    expression = re.compile(r'@[\w\d\.]+')
    edges['stitcher_user'] = edges['stitcher_url'].apply(lambda x: re.findall(expression, x)[0])
    edges['stitchee_user'] = edges['stitchee_url'].apply(lambda x: re.findall(expression, x)[0])

    return edges

def get_video_graph(edges: pd.DataFrame) -> ig.Graph:
    G = ig.Graph.TupleList(edges[['stitcher', 'stitchee']].values, directed=True)
    return G

def get_user_graph(edges: pd.DataFrame) -> ig.Graph:
    G = ig.Graph.TupleList(edges[['stitcher_user', 'stitchee_user']].values, directed=True)
    return G

def get_all_video_graphs() -> list:
    data_path = '../data/hashtags/edges/'
    edge_files = [file for file in os.listdir(data_path) if file.endswith('.txt')]
    graphs = []
    for edge_file in edge_files:
        # read edge file
        edge_file_path = os.path.join(data_path, edge_file)
        edges = load_edges(edge_file_path)
        g = get_video_graph(edges)
        graphs.append(g)
    return graphs

def get_all_user_graphs() -> list:
    data_path = '../data/hashtags/edges/'
    edge_files = [file for file in os.listdir(data_path) if file.endswith('.txt')]
    graphs = []
    for edge_file in edge_files:
        # read edge file
        edge_file_path = os.path.join(data_path, edge_file)
        edges = load_edges(edge_file_path)
        g = get_user_graph(edges)
        graphs.append(g)
    return graphs

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
