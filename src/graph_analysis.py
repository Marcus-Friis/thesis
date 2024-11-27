from graph_utils import get_all_video_graphs, get_all_user_graphs, get_all_twtter_user_graphs, degree_centralization, closeness_centralization, betweenness_centralization
import igraph as ig
import numpy as np
import pandas as pd

if __name__ == '__main__':
    # load graphs
    video_graphs = get_all_video_graphs()
    user_graphs = get_all_user_graphs()
    video_lccs = [g.components(mode='weak').giant() for g in video_graphs]
    user_lccs = [g.components(mode='weak').giant() for g in user_graphs]
    twitter_graphs = get_all_twtter_user_graphs()
    twitter_lccs = [g.components(mode='weak').giant() for g in twitter_graphs]

    all_graphs = {
        'video': video_graphs,
        'user': user_graphs,
        'video_lcc': video_lccs,
        'user_lcc': user_lccs,
        'twitter': twitter_graphs,
        'twitter_lcc': twitter_lccs
    }

    # categorization of hashtags
    category_dict = {
        'anime': 'Shared interest/subculture',
        'booktok': 'Shared interest/subculture',
        'football': 'Shared interest/subculture',
        'gym': 'Shared interest/subculture',
        'jazz': 'Shared interest/subculture',
        'kpop': 'Shared interest/subculture',
        'lgbt': 'Shared interest/subculture',
        'makeup': 'Shared interest/subculture',
        'minecraft': 'Shared interest/subculture',
        'plantsoftiktok': 'Shared interest/subculture',
        'biden2024': 'Political discussion',
        'blacklivesmatter': 'Political discussion',
        'climatechange': 'Political discussion',
        'conspiracy': 'Political discussion',
        'election': 'Political discussion',
        'gaza': 'Political discussion',
        'israel': 'Political discussion',
        'maga': 'Political discussion',
        'palestine': 'Political discussion',
        'trump2024': 'Political discussion',
        'asmr': 'Entertainment/knowledge',
        'challenge': 'Entertainment/knowledge',
        'comedy': 'Entertainment/knowledge',
        'learnontiktok': 'Entertainment/knowledge',
        'movie': 'Entertainment/knowledge',
        'news': 'Entertainment/knowledge',
        'science': 'Entertainment/knowledge',
        'storytime': 'Entertainment/knowledge',
        'tiktoknews': 'Entertainment/knowledge',
        'watermelon': 'Entertainment/knowledge'
    }

    # basic graph statistics
    for label, graphs in all_graphs.items():
        graph_labels = [g['name'] for g in graphs]
        category = [category_dict.get(g['name'], 'Other') for g in graphs]
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
            'category': category,
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
        }).sort_values(['category', 'label'])
        print(df)
