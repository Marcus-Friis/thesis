from utils.graph_utils import get_all_video_graphs, get_all_user_graphs, get_all_twitter_user_graphs, degree_centralization, closeness_centralization, betweenness_centralization
import igraph as ig
import numpy as np
import pandas as pd

if __name__ == '__main__':
    # load graphs
    video_graphs = get_all_video_graphs()
    user_graphs = get_all_user_graphs()
    video_lccs = [g.components(mode='weak').giant() for g in video_graphs]
    user_lccs = [g.components(mode='weak').giant() for g in user_graphs]
    twitter_graphs = get_all_twitter_user_graphs()
    twitter_lccs = [g.components(mode='weak').giant() for g in twitter_graphs]

    all_graphs = {
        #'video': video_graphs,
        #'user': user_graphs,
        #'video_lcc': video_lccs,
        'user_lcc': user_lccs,
        #'twitter': twitter_graphs,
        #'twitter_lcc': twitter_lccs
    }

    # basic graph statistics
    for label, graphs in all_graphs.items():
        graph_labels = [g['name'] for g in graphs]
        category = [g['category'] for g in graphs]
        num_nodes = [g.vcount() for g in graphs]
        num_edges = [g.ecount() for g in graphs]
        avg_in_degree = [np.mean(g.indegree()) for g in graphs]
        avg_out_degree = [np.mean(g.outdegree()) for g in graphs]
        num_self_loops = [sum(g.is_loop()) for g in graphs]
        num_multiple_edges = [sum(g.is_multiple()) for g in graphs]
        num_components = [len(g.components(mode='weak')) for g in graphs]
        num_nodes_in_lcc = [g.components(mode='weak').giant().vcount() for g in graphs]
        density = [g.density() for g in graphs]
        diameter = [g.diameter() for g in graphs]
        diameter_un = [g.diameter(directed=False) for g in graphs]
        avg_path_length = [g.average_path_length() for g in graphs]
        avg_path_length_un = [g.average_path_length(directed=False) for g in graphs]
        degree_assortativity = [g.assortativity_degree() for g in graphs]
        degree_assortativity_un = [g.assortativity_degree(directed=False) for g in graphs]
        clustering_coeff = [g.transitivity_undirected(mode='zero') for g in graphs]
        reciprocity = [g.reciprocity() for g in graphs]
        degree_cent = [degree_centralization(g.as_undirected().simplify()) if g.vcount() > 2 else None for g in graphs]
        closeness_cent = [closeness_centralization(g.as_undirected().simplify()) if g.vcount() > 2 else None for g in graphs]
        betweenness_cent = [betweenness_centralization(g.as_undirected().simplify()) if g.vcount() > 2 else None for g in graphs]

        df = pd.DataFrame({
            'hashtag': graph_labels,
            'category': category,
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'num_self_loops': num_self_loops,
            'num_multi_edges': num_multiple_edges,
            'num_components': num_components,
            'num_nodes_in_lcc': num_nodes_in_lcc,
            'density': density,
            'diameter': diameter,
            'diameter_un': diameter_un,
            'avg_path_length': avg_path_length,
            'avg_path_length_un': avg_path_length_un,
            'degree_assortativty': degree_assortativity,
            # 'degree_assortativity_un': degree_assortativity_un,
            'clustering': clustering_coeff,
            'reciprocity': reciprocity,
            'degree_centralization': degree_cent,
            'closeness_centralization': closeness_cent,
            'betweenness_centralization': betweenness_cent
        }).sort_values('hashtag') #.sort_values(['num_nodes', 'num_edges'], ascending=False)

        latex_header_dict = {
            'hashtag': 'Hashtag',
            'category': 'Category',
            'num_nodes': '$|V|$',
            'num_edges': '$|E|$',
            'num_self_loops': '\makecell{\#Self-\\\\ loops}',
            'num_multi_edges': '\makecell{\#Multi-\\\\ edges}',
            'num_components': '\#Components',
            'num_nodes_in_lcc': '\makecell{$|V|$\\\\ in LCC}',
            'density': 'Density',
            'diameter': '$D$',
            'diameter_un': '$D_u$',
            'avg_path_length': '$L$',
            'avg_path_length_un': '$L_u$',
            'degree_assortativty': '\makecell{Degree\\\\ assortativity}',
            'degree_assortativity_un': '\makecell{Degree\\\\ assortativity\\\\ undirected}',
            'clustering': '$C_u$',
            'reciprocity': 'Reciprocity',
            'degree_centralization': '\makecell{Degree\\\\ centralization}',
            'closeness_centralization': '\makecell{Closeness\\\\ centralization}',
            'betweenness_centralization': '\makecell{Betweenness\\\\ centralization}'
        }
        
        cols_to_print = [
            'hashtag',
            # 'category', 
            'num_nodes', 
            'num_edges', 
            #'num_components', 
            #'diameter',
            #'diameter_un',
            'avg_path_length',
            'avg_path_length_un',
            'clustering',
            'reciprocity',
            'degree_centralization'
        ]
        
        # full table
        # cols_to_print = df.columns  # [col for col in df.columns if col != 'hashtag']
        
        # aggregate rows by category
        # df = df.groupby('category').mean().reset_index()
        
        latex = df[cols_to_print] \
            .rename(columns=latex_header_dict)\
            .to_latex(index=False, float_format='%.2f', escape=False)
        print(latex)
