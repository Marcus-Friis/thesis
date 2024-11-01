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


def cluster_graphs(embeddings):
    """Clusters graph embeddings using HDBSCAN."""
    print("Clustering embeddings with HDBSCAN")
    hdbscan = HDBSCAN(min_cluster_size=3, metric='cosine')
    cluster_labels = hdbscan.fit_predict(embeddings)
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


def plot_embeddings(embeddings, names, algorithm, cluster_labels, save_plot, directed, do_plot, add_random, cluster, lcc_only):
    """Plots the graph embeddings using PCA, TSNE, and UMAP."""
    categories = categorize_hashtags(names)
    unique_categories = sorted(set(categories))

    # Dimensionality reduction methods
    reducers = {
        'PCA': PCA(n_components=2).fit_transform(embeddings),
        'TSNE': TSNE(n_components=2, perplexity=10, random_state=42).fit_transform(embeddings),
        'UMAP': UMAP(n_components=2).fit_transform(embeddings)
    }

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    if cluster_labels is not None:
        # When clustering is performed
        # Assign markers to categories
        category_markers = ['o', 's', '^', '+']
        category_to_marker = {category: category_markers[i % len(category_markers)] for i, category in enumerate(unique_categories)}

        # Assign colors to clusters
        unique_clusters = sorted(set(cluster_labels))
        n_clusters = len(unique_clusters)
        cmap = plt.get_cmap('tab10_r', n_clusters)
        cluster_to_color = {cluster: cmap(i) for i, cluster in enumerate(unique_clusters)}

        for ax, (title, reduced_embeddings) in zip(axes, reducers.items()):
            for idx, name in enumerate(names):
                category = categories[idx]
                marker = category_to_marker.get(category, '+')  # Default to 'o' if category not found
                cluster_label = cluster_labels[idx]
                color = cluster_to_color.get(cluster_label, 'grey')
                ax.scatter(reduced_embeddings[idx, 0], reduced_embeddings[idx, 1],
                           color=color, marker=marker)
                ax.annotate(name, (reduced_embeddings[idx, 0], reduced_embeddings[idx, 1]))
            ax.set_title(title)

        # Create legend handles for categories only
        category_handles = [
            Line2D([0], [0], marker=category_to_marker[category], color='w', label=category,
                   markerfacecolor='black', markeredgecolor='black', markersize=10)
            for category in unique_categories
        ]

    else:
        # When clustering is not performed
        # Assign colors to categories
        color_mapping = {
            'Shared interest/subculture': 'green',
            'Political discussion': 'orange',
            'Entertainment/knowledge': 'blue',
            'Configuration Models': 'grey',
            'Unknown': 'red'
        }
        category_to_color = {category: color_mapping.get(category, 'grey') for category in unique_categories}

        # Use the same marker for all points
        marker = 'o'

        for ax, (title, reduced_embeddings) in zip(axes, reducers.items()):
            for idx, name in enumerate(names):
                category = categories[idx]
                color = category_to_color.get(category, 'grey')
                ax.scatter(reduced_embeddings[idx, 0], reduced_embeddings[idx, 1],
                           color=color, marker=marker)
                ax.annotate(name, (reduced_embeddings[idx, 0], reduced_embeddings[idx, 1]))
            ax.set_title(title)

        # Create legend handles for categories with colors
        category_handles = [
            Line2D([0], [0], marker='o', color='w', label=category,
                   markerfacecolor=color, markeredgecolor='black', markersize=10)
            for category, color in category_to_color.items()
        ]

    # Place legend
    plt.legend(handles=category_handles, loc='upper left', bbox_to_anchor=(1, 1))
    used_arguments = [
        f'Algorithm: {algorithm}',
        f'Directed: {directed}',
        f'Add_Config_Models: {add_random}',
        f'Clustering: {cluster}',
        f'LCC_Only: {lcc_only}'
    ]
    plot_title = ' // '.join(used_arguments)
    plt.suptitle(plot_title)
    plt.tight_layout()

    if save_plot:
        os.makedirs('../figures/embeddings', exist_ok=True)
        bools = [True if item.split(': ')[1].strip().lower() == 'true' else False for item in used_arguments]
        args = [item.split(': ')[0].strip().lower() for item in used_arguments]
        true_args = [args[i] for i in range(len(bools)) if bools[i] == True]
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
        return

    directed = 'directed' in args_lower
    do_plot = 'plot' in args_lower
    add_random = 'config' in args_lower  # Changed from 'random' to 'config'
    cluster = 'cluster' in args_lower
    save_plot = 'save' in args_lower
    lcc_only = 'lcc' in args_lower

    accepted_algorithms = ['graph2vec', 'feathergraph', 'sf', 'fgsd', 'gl2vec', 'ldp']
    algorithm = next((arg for arg in args_lower if arg in accepted_algorithms), None)
    if algorithm is None:
        raise ValueError(f"No valid algorithm provided. Accepted algorithms are: {', '.join(accepted_algorithms)}")

    hashtag_path = "../data/hashtags/vertices"
    hashtags = [f[:-5] for f in os.listdir(hashtag_path) if f.endswith('.json')]

    #hashtags = hashtags[:10]  # Limit to first N hashtags for testing

    names, graphs = construct_graphs(hashtags, directed, lcc_only)

    if add_random:
        config_names, config_graphs = construct_configuration_models(names, graphs, directed)
        names.extend(config_names)
        graphs.extend(config_graphs)

    embeddings = embed_graphs(graphs, algorithm)

    cluster_labels = cluster_graphs(embeddings) if cluster else None

    if do_plot:
        plot_embeddings(embeddings, names, algorithm, cluster_labels, save_plot, directed, do_plot, add_random, cluster, lcc_only)


if __name__ == "__main__":
    main()
