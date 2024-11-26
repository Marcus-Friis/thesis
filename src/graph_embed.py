import os
import sys

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.lines import Line2D
from sklearn.cluster import HDBSCAN
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from umap import UMAP


from sklearn.metrics import silhouette_score, davies_bouldin_score  # Import scoring functions

def construct_graphs(hashtags, directed, lcc_only=False):
    """Constructs graphs from hashtag edge files."""
    names = []
    graphs = []

    for hashtag in hashtags:
        names.append(hashtag)
        with open(f'../data/hashtags/edges/{hashtag}_edges.txt', 'r') as f:
            edges = f.readlines()

        users = []
        for edge in edges:
            u, v = edge.strip().split(',')
            if 'None' in v:
                continue
            u_user = u.split('/')[-3]
            v_user = v.split('/')[-3]
            users.append((u_user, v_user))

        all_users = set(user for edge in users for user in edge)
        user_to_id = {user: i for i, user in enumerate(all_users)}
        user_edges = [(user_to_id[src], user_to_id[dst]) for src, dst in users]

        G = nx.DiGraph() if directed else nx.Graph()
        G.add_edges_from(user_edges)

        if lcc_only:
            # Extract the largest connected component
            if directed:
                # Weakly connected component for directed graph
                largest_cc = max(nx.weakly_connected_components(G), key=len)
            else:
                # Connected component for undirected graph
                largest_cc = max(nx.connected_components(G), key=len)
            
            # Create subgraph from the largest connected component
            G = G.subgraph(largest_cc).copy()

        G = nx.convert_node_labels_to_integers(G)
        graphs.append(G)

    return names, graphs

def construct_configuration_models(names, graphs, directed):
    """Constructs configuration model graphs based on the LCC of the current graphs."""
    print("Creating configuration model graphs")
    config_names = []
    config_graphs = []

    for name, G in zip(names, graphs):
        config_name = f'{name}_config'
        config_names.append(config_name)

        if directed:
            # For directed graphs, use both in-degree and out-degree sequences
            in_degrees = [d for n, d in G.in_degree()]
            out_degrees = [d for n, d in G.out_degree()]
            CM = nx.directed_configuration_model(in_degrees, out_degrees)
            # Convert to DiGraph and remove self-loops and parallel edges
            CM = nx.DiGraph(CM)
            #CM.remove_edges_from(nx.selfloop_edges(CM))
        else:
            degrees = [d for n, d in G.degree()]
            CM = nx.configuration_model(degrees)
            # Convert to Graph and remove self-loops and parallel edges
            CM = nx.Graph(CM)
            #CM.remove_edges_from(nx.selfloop_edges(CM))

        CM = nx.convert_node_labels_to_integers(CM)
        config_graphs.append(CM)

    return config_names, config_graphs

def cluster_graphs(embeddings, min_cluster_size=3, min_samples=None):  # Add parameters
    """Clusters graph embeddings using HDBSCAN."""
    print("Clustering embeddings with HDBSCAN")

    clusterer = HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples) # Initialize HDBSCAN
    clusterer.fit(embeddings)

    cluster_labels = clusterer.labels_
    return cluster_labels

def embed_graphs(graphs, algorithm):
    """Embeds graphs using the specified algorithm."""
    from karateclub import (FGSD, GL2Vec, FeatherGraph, Graph2Vec, LDP, SF)

    algorithm_classes = {
        'graph2vec': Graph2Vec,
        'feathergraph': FeatherGraph,
        'sf': SF,
        'fgsd': FGSD,
        'gl2vec': GL2Vec,
        'ldp': LDP
    }

    if algorithm not in algorithm_classes:
        raise ValueError(f'Algorithm "{algorithm}" not implemented.')

    print(f'Using "{algorithm}" to create embeddings')
    model = algorithm_classes[algorithm]()
    model.fit(graphs)
    embeddings = model.get_embedding()

    pca = PCA(n_components=2)
    pca.fit(embeddings)
    explained_variance = sum(pca.explained_variance_ratio_)
    print(f'Explained variance (2 components) of PCA embeddings: {explained_variance:.4f}')

    return embeddings

def categorize_hashtags(names):
    """Categorizes hashtags into predefined categories."""
    categories = {
        'Shared interest/subculture': [
            'anime', 'booktok', 'football', 'gym', 'jazz',
            'kpop', 'lgbt', 'makeup', 'minecraft', 'plantsoftiktok'
        ],
        'Political discussion': [
            'biden2024', 'blacklivesmatter', 'climatechange', 'conspiracy',
            'election', 'gaza', 'israel', 'maga', 'palestine', 'trump2024'
        ],
        'Entertainment/knowledge': [
            'asmr', 'challenge', 'comedy', 'learnontiktok', 'movie',
            'news', 'science', 'storytime', 'tiktoknews', 'watermelon'
        ],
    }

    # Create a mapping from name to category
    name_to_category = {}
    for category, tags in categories.items():
        for tag in tags:
            name_to_category[tag] = category

    # Assign 'Configuration Models' category to configuration model graphs
    for name in names:
        if name not in name_to_category:
            if name.endswith('_config'):
                name_to_category[name] = 'Configuration Models'
            else:
                name_to_category[name] = 'Unknown'

    return [name_to_category.get(name, 'Unknown') for name in names]

def plot_embeddings(embeddings, names, algorithm, cluster_labels, save_plot, directed, add_random, cluster, lcc_only):
    """Plots the graph embeddings using PCA, TSNE, and UMAP."""
    import os
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    from umap import UMAP

    categories = categorize_hashtags(names)
    unique_categories = sorted(set(categories))

    # Dimensionality reduction methods
    reducers = {
        'PCA': PCA(n_components=2).fit_transform(embeddings),
        'TSNE': TSNE(n_components=2, perplexity=10, random_state=42).fit_transform(embeddings),
        'UMAP': UMAP(n_components=2).fit_transform(embeddings)
    }

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Assign markers to categories
    category_markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
    category_to_marker = {
        category: category_markers[i % len(category_markers)]
        for i, category in enumerate(unique_categories)
    }

    if cluster_labels is not None:
        # Prepare colors for clusters
        unique_clusters = sorted(set(cluster_labels))
        clusters = [cluster for cluster in unique_clusters if cluster != -1]
        n_clusters = len(clusters)
        n_clusters = max(n_clusters, 1)  # Ensure at least one color

        cmap = plt.get_cmap('tab10', n_clusters)
        cluster_colors = [cmap(i) for i in range(n_clusters)]

        # Map clusters to colors
        cluster_to_color = {
            cluster: cluster_colors[i]
            for i, cluster in enumerate(clusters)
        }
        cluster_to_color[-1] = 'grey'  # Noise points
    else:
        # Prepare colors for categories
        color_mapping = {
            'Shared interest/subculture': 'green',
            'Political discussion': 'orange',
            'Entertainment/knowledge': 'blue',
            'Configuration Models': 'grey',
            'Unknown': 'red'
        }
        category_to_color = {
            category: color_mapping.get(category, 'black')
            for category in unique_categories
        }

    for ax, (title, reduced_embeddings) in zip(axes, reducers.items()):
        for idx, name in enumerate(names):
            x, y = reduced_embeddings[idx, 0], reduced_embeddings[idx, 1]
            category = categories[idx]
            marker = category_to_marker.get(category, 'o')  # Default marker

            if cluster_labels is not None:
                cluster_label = cluster_labels[idx]
                color = cluster_to_color.get(cluster_label, 'grey')
            else:
                color = category_to_color.get(category, 'black')

            ax.scatter(x, y, color=color, marker=marker)
            ax.annotate(name, (x, y))

        ax.set_title(title)

    # Create legend handles
    handles = []

    # Category legend
    category_handles = [
        Line2D([0], [0], marker=category_to_marker[category], color='w', label=category,
               markerfacecolor='black', markeredgecolor='black', markersize=10)
        for category in unique_categories
    ]
    handles.extend(category_handles)

    if cluster_labels is not None:
        # Cluster legend
        cluster_handles = []
        for cluster in sorted(set(cluster_labels)):
            if cluster == -1:
                label = 'Outliers'
                color = 'grey'
            else:
                label = f'Cluster {cluster}'
                color = cluster_to_color.get(cluster, 'grey')
            cluster_handles.append(
                Line2D([0], [0], marker='o', color='w', label=label,
                       markerfacecolor=color, markeredgecolor='black', markersize=10)
            )
        handles.extend(cluster_handles)
    else:
        # Category color legend (only if clustering is not performed)
        color_handles = [
            Line2D([0], [0], marker='o', color='w', label=category,
                   markerfacecolor=color, markeredgecolor='black', markersize=10)
            for category, color in category_to_color.items()
        ]
        handles.extend(color_handles)

    # Place legend
    plt.legend(handles=handles, loc='upper left', bbox_to_anchor=(1, 1))

    # Add title and adjust layout
    used_arguments = [
        f'Algorithm: {algorithm}',
        f'Directed: {directed}',
        f'Add_Config_Models: {add_random}',
        f'LCC_Only: {lcc_only}'
    ]
    plot_title = ' // '.join(used_arguments)
    plt.suptitle(plot_title)
    plt.tight_layout()

    if save_plot:
        os.makedirs('../figures/embeddings', exist_ok=True)
        bools = [item.split(': ')[1].strip().lower() == 'true' for item in used_arguments]
        args = [item.split(': ')[0].strip().lower() for item in used_arguments]
        true_args = [args[i] for i in range(len(bools)) if bools[i]]
        plot_args = '_'.join(true_args)
        plt.savefig(f'../figures/embeddings/{algorithm}_embeddings_{plot_args}.png')
    else:
        plt.show()


def main():
    if len(sys.argv) < 2:
        raise ValueError('At least one embedding algorithm must be provided as an argument')

    args_lower = [arg.lower() for arg in sys.argv[1:]]

    if 'help' in args_lower:
        print('Usage: python graph_embed.py [embedding_algorithm] [options]')
        print('Accepted embedding algorithms: graph2vec, feathergraph, sf, fgsd, gl2vec, ldp')
        print('Optional arguments:')
        print('  directed : Use directed graphs')
        print('  plot     : Plot 2D embeddings')
        print('  config   : Add configuration model graphs to the dataset')
        print('  cluster  : Cluster the embeddings with HDBSCAN')
        print('  save     : Save the plot instead of displaying it')
        print('  lcc      : Use only the largest connected component of each graph')
        return

    directed = 'directed' in args_lower
    do_plot = 'plot' in args_lower
    add_random = 'config' in args_lower 
    cluster = 'cluster' in args_lower
    save_plot = 'save' in args_lower
    lcc_only = 'lcc' in args_lower

    accepted_algorithms = ['graph2vec', 'feathergraph', 'sf', 'fgsd', 'gl2vec', 'ldp']
    algorithm = next((arg for arg in args_lower if arg in accepted_algorithms), None)
    if algorithm is None:
        raise ValueError(f"No valid algorithm provided. Accepted algorithms are: {', '.join(accepted_algorithms)}")

    hashtag_path = "../data/hashtags/vertices"
    hashtags = [f[:-5] for f in os.listdir(hashtag_path) if f.endswith('.json')]

    names, graphs = construct_graphs(hashtags, directed, lcc_only)

    if add_random:
        config_names, config_graphs = construct_configuration_models(names, graphs, directed)
        names.extend(config_names)
        graphs.extend(config_graphs)

    embeddings = embed_graphs(graphs, algorithm)


    if cluster:
        #umap before clustering
        umap = UMAP(n_components=2).fit_transform(embeddings)
        cluster_labels = cluster_graphs(umap) if cluster else None
        # cluster_labels = cluster_graphs(embeddings) if cluster else None

        #make a dictionary to group the hashtags
        cluster_dict = {}
        for i in range(len(names)):
            if cluster_labels[i] in cluster_dict:
                cluster_dict[cluster_labels[i]].append(names[i])
            else:
                cluster_dict[cluster_labels[i]] = [names[i]]

        for key in cluster_dict:
            print(f"Cluster {key}: {cluster_dict[key]}")
        





        # Filter out noise points
        mask = cluster_labels != -1
        filtered_embeddings = embeddings[mask]
        filtered_labels = cluster_labels[mask]

        # Check if there are at least 2 clusters
        n_clusters = len(set(filtered_labels))
        if n_clusters > 1:
            # Calculate Silhouette Score and Davies-Bouldin Index
            silhouette_avg = silhouette_score(filtered_embeddings, filtered_labels)
            db_score = davies_bouldin_score(filtered_embeddings, filtered_labels)

            print(f"Silhouette Score: {silhouette_avg:.4f}")
            print(f"Davies-Bouldin Index: {db_score:.4f}")
        else:
            print("Not enough clusters to compute silhouette score or Davies-Bouldin Index.")


    if do_plot:
        plot_embeddings(embeddings, names, algorithm, cluster_labels, save_plot, directed, add_random, cluster, lcc_only)


if __name__ == "__main__":
    main()