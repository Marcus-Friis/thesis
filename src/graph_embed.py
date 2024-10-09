import networkx as nx
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from sys import argv
import random
import os

from sklearn.manifold import TSNE
from sklearn.cluster import HDBSCAN
from sklearn.decomposition import PCA
from umap import UMAP

from karateclub import Graph2Vec, FeatherGraph, SF, FGSD, GeoScattering, GL2Vec, IGE, LDP, NetLSD

def construct_graphs(hashtags, directed):
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

        all_users = set([user for edge in users for user in edge])
        user_to_id = {user: i for i, user in enumerate(all_users)}
        users = [(user_to_id[src], user_to_id[dst]) for src, dst in users]

        G = nx.Graph()
        G.add_edges_from(users)

        if directed:
            G = nx.DiGraph(G)

        graphs.append(G)
    return names, graphs

def construct_random_graphs(num_graphs, num_nodes, directed):
    random_names = [f'G_random_{i}' for i in range(num_graphs)]
    random_graphs = []
    
    for _ in range(num_graphs):
        G = nx.gnp_random_graph(num_nodes, random.uniform(0.1, 0.3), directed=directed)
        random_graphs.append(G)

    return random_names, random_graphs

#cluser with hdbscan
def cluster_graphs(embeddings):
    pass
    # hdbscan = HDBSCAN(min_cluster_size=5)
    # cluster_labels = hdbscan.fit_predict(embeddings)
    # return cluster_labels

    


def embed_graphs(graphs, algorithm, three_d):
    algorithm_classes = {
        'graph2vec': Graph2Vec,
        'feathergraph': FeatherGraph,
        'sf': SF,
        'fgsd': FGSD,
        'gl2vec': GL2Vec,
        'ldp' : LDP
        
        #'geoscattering': GeoScattering,   --->  Found infinite path length because the graph is not connected
        #'ige' : IGE, ---> Not implemented yet (slow af)
        #'netlsd' : NetLSD ---> Not implemented yet (slow af)
        #'waveletcharacteristic' : waveletcharacteristic ---> Not implemented yet (slow af)

    }

    # Check if the algorithm is in the accepted list and create the model
    if algorithm in algorithm_classes:
        model = algorithm_classes[algorithm]()
    else:
        raise ValueError(f'Algorithm "{algorithm}" not implemented yet')

    print(f'Using "{algorithm}" to create embeddings')

    
    model.fit(graphs)
    embeddings = model.get_embedding()

    if three_d: print(f'Explained variance (3 components) of PCA embeddings: {sum(PCA(n_components=3).fit(embeddings).explained_variance_ratio_)}')
    else: print(f'Explained variance (2 components) of PCA embeddings: {sum(PCA(n_components=2).fit(embeddings).explained_variance_ratio_)}')

    return embeddings

def categorize_hashtags(names):
    categories = {
        'Shared interest/subculture': ['anime', 'booktok', 'football', 'gym', 'jazz', 'kpop', 'lgbt', 'makeup', 'minecraft', 'plantsoftiktok'],
        'Political discussion': ['biden2024', 'blacklivesmatter', 'climatechange', 'conspiracy', 'election', 'gaza', 'israel', 'maga', 'palestine', 'trump2024'],
        'Entertainment/knowledge': ['asmr', 'challenge', 'comedy', 'learnontiktok', 'movie', 'news', 'science', 'storytime', 'tiktoknews', 'watermelon'],
        'Random Graphs': ['G_random_0', 'G_random_1', 'G_random_2', 'G_random_3', 'G_random_4', 'G_random_5', 'G_random_6', 'G_random_7']
    }
    
    name_to_category = {}
    for category, tags in categories.items():
        for tag in tags:
            name_to_category[tag] = category

    return [name_to_category.get(name, 'Unknown') for name in names]

def plot_embeddings(embeddings, names, algorithm, three_d):
    categories = categorize_hashtags(names)
    unique_categories = sorted(list(set(categories)))  # Sort categories to ensure consistent ordering
    colors = {category: plt.cm.tab10(i % 10) for i, category in enumerate(unique_categories)}  # Ensure consistent colors
    
    # Setting a random seed for reproducibility
    random.seed(42)

    if three_d: 
        tsne_embeddings = TSNE(n_components=3, perplexity=10, random_state=42).fit_transform(embeddings)
        pca_embeddings = PCA(n_components=3).fit_transform(embeddings)
        umap_embeddings = UMAP(n_components=3).fit_transform(embeddings)
        
        # 3D PCA plot, 3D TSNE plot, and 3D UMAP plot
        fig = plt.figure(figsize=(18, 6))
        ax1 = fig.add_subplot(131, projection='3d')
        ax2 = fig.add_subplot(132, projection='3d')
        ax3 = fig.add_subplot(133, projection='3d')
        for i, (embedding, title) in enumerate(zip([pca_embeddings, tsne_embeddings, umap_embeddings], ['PCA', 'TSNE', 'UMAP'])):
            ax = [ax1, ax2, ax3][i]
            for j, name in enumerate(names):
                ax.scatter(embedding[j, 0], embedding[j, 1], embedding[j, 2], color=colors[categories[j]], label=categories[j] if j == 0 else "")
                ax.text(embedding[j, 0], embedding[j, 1], embedding[j, 2], name)
            ax.set_title(title)
        plt.suptitle(f'{algorithm} embeddings')
        plt.tight_layout()
        plt.show()
        return

    tsne_embeddings = TSNE(n_components=2, perplexity=10, random_state=42).fit_transform(embeddings)
    pca_embeddings = PCA(n_components=2).fit_transform(embeddings)
    umap_embeddings = UMAP(n_components=2).fit_transform(embeddings)
    
    fig, ax = plt.subplots(1, 3, figsize=(18, 6))

    for i, (embedding, title) in enumerate(zip([pca_embeddings, tsne_embeddings, umap_embeddings], ['PCA', 'TSNE', 'UMAP'])):
        for j, name in enumerate(names):
            ax[i].scatter(embedding[j, 0], embedding[j, 1], color=colors[categories[j]], label=categories[j] if j == 0 else "")
            ax[i].annotate(name, (embedding[j, 0], embedding[j, 1]))
        ax[i].set_title(title)
    plt.suptitle(f'{algorithm} embeddings')
    plt.tight_layout()
    plt.show()

    
def main():
    
    if len(argv) < 2:
        raise ValueError('At least one embedding algorithm must be provided as argument')
    
    args_lower = [arg.lower() for arg in argv[1:]]

    directed = 'directed' in args_lower
    do_plot = 'plot' in args_lower
    three_d = '3d' in args_lower
    add_random = 'random' in args_lower
    cluster = 'cluster' in args_lower

    if three_d and not do_plot:
        raise ValueError('Use the "plot" argument as well in order to plot 3D embeddings')

    accepted_algorithms = ['graph2vec', 'feathergraph', 'sf', 'fgsd', 'gl2vec', 'ldp']
    algorithm = next((arg for arg in args_lower if arg in accepted_algorithms), None)
    if algorithm is None:
        raise ValueError(f"No valid algorithm provided. Accepted algorithms are: {', '.join(accepted_algorithms)}")
    
    
    hashtag_path = "../data/hashtags/vertices"
    hashtags = [f[:-5] for f in os.listdir(hashtag_path) if f.endswith('.json')]

    names, graphs = construct_graphs(hashtags, directed)

    if add_random:
        random_names, random_graphs = construct_random_graphs(num_graphs=8, num_nodes=750, directed=directed)
        names.extend(random_names)
        graphs.extend(random_graphs)

    embeddings = embed_graphs(graphs, algorithm, three_d)
    
    
    if do_plot:
        plot_embeddings(embeddings, names, algorithm, three_d)

if __name__ == "__main__":
    main()