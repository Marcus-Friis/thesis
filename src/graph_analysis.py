from graph_utils import get_all_video_graphs, get_all_user_graphs, degree_centralization, closeness_centralization, betweenness_centralization
import igraph as ig
import numpy as np
import pandas as pd

if __name__ == '__main__':
    # load graphs
    video_graphs = get_all_video_graphs()
    user_graphs = get_all_user_graphs()
    video_lccs = [g.components(mode='weak').giant() for g in video_graphs]
    user_lccs = [g.components(mode='weak').giant() for g in user_graphs]
    all_graphs = {
        'video': video_graphs,
        'user': user_graphs,
        'video_lcc': video_lccs,
        'user_lcc': user_lccs
    }

    # basic graph statistics
    for label, graphs in all_graphs.items():
        graph_labels = [g['name'] for g in graphs]
        num_nodes = [g.vcount() for g in graphs]
        num_edges = [g.ecount() for g in graphs]
        num_self_loops = [sum(g.is_loop()) for g in graphs]
        num_multiple_edges = [sum(g.is_multiple()) for g in graphs]
        num_components = [g.components().n for g in graphs]
        density = [g.density() for g in graphs]
        diameter = [g.diameter() for g in graphs]
        diameter_un = [g.diameter(directed=False) for g in graphs]
        avg_path_length = [g.average_path_length() for g in graphs]
        avg_path_length_un = [g.average_path_length(directed=False) for g in graphs]
        degree_assortativity = [g.assortativity_degree() for g in graphs]
        clustering_coeff = [g.transitivity_undirected() for g in graphs]
        reciprocity = [g.reciprocity() for g in graphs]
        degree_cent = [degree_centralization(g.as_undirected().simplify()) if g.vcount() > 2 else None for g in graphs]
        closeness_cent = [closeness_centralization(g.as_undirected().simplify()) if g.vcount() > 2 else None for g in graphs]
        betweenness_cent = [betweenness_centralization(g.as_undirected().simplify()) if g.vcount() > 2 else None for g in graphs]

        df = pd.DataFrame({
            'label': graph_labels,
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'num_self_loops': num_self_loops,
            'num_multiple_edges': num_multiple_edges,
            'num_components': num_components,
            'density': density,
            'diameter': diameter,
            'diameter_un': diameter_un,
            'avg_path_length': avg_path_length,
            'avg_path_length_un': avg_path_length_un,
            'degree_assortativity': degree_assortativity,
            'clustering_coeff': clustering_coeff,
            'reciprocity': reciprocity,
            'degree_cent': degree_cent,
            'closeness_cent': closeness_cent,
            'betweenness_cent': betweenness_cent
        })
        print(df)

