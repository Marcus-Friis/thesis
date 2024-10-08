import networkx as nx
import matplotlib.pyplot as plt

from sys import argv
import os

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

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

def embed_graphs(graphs, algorithm):
    algorithm_classes = {
        'graph2vec': Graph2Vec,
        'feathergraph': FeatherGraph,
        'sf': SF,
        'fgsd': FGSD,
        #'geoscattering': GeoScattering,   --->  Found infinite path length because the graph is not connected
        'gl2vec': GL2Vec,
        'ldp' : LDP
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

    return embeddings

def plot_embeddings(embeddings, names, algorithm, three_d):

    if three_d: 
    
        tsne_embeddings = TSNE(n_components=3, perplexity=10).fit_transform(embeddings)
        pca_embeddings = PCA(n_components=3).fit_transform(embeddings)
        
        #Explained variance
        print(f'Explained variance of PCA embeddings: {sum(PCA(n_components=3).fit(embeddings).explained_variance_ratio_)}')

        #3d pca plot and 3d tsne plot
        fig = plt.figure(figsize=(12, 6))
        ax1 = fig.add_subplot(121, projection='3d')
        ax2 = fig.add_subplot(122, projection='3d')
        for i, (embedding, title) in enumerate(zip([pca_embeddings, tsne_embeddings], ['PCA', 'TSNE'])):
            ax = ax1 if i == 0 else ax2
            ax.scatter(embedding[:, 0], embedding[:, 1], embedding[:, 2])
            for j, name in enumerate(names):
                ax.text(embedding[j, 0], embedding[j, 1], embedding[j, 2], name)
            ax.set_title(title)
        plt.suptitle(f'{algorithm} embeddings')
        plt.show()
        return


    tsne_embeddings = TSNE(n_components=2, perplexity=10, random_state=42).fit_transform(embeddings)
    pca_embeddings = PCA(n_components=2, random_state=42).fit_transform(embeddings)

    #Explained variance
    print(f'Explained variance of PCA embeddings: {sum(PCA(n_components=2).fit(embeddings).explained_variance_ratio_)}')

    fig, ax = plt.subplots(1, 2, figsize=(12, 6))

    for i, (embedding, title) in enumerate(zip([pca_embeddings, tsne_embeddings], ['PCA', 'TSNE'])):
        ax[i].scatter(embedding[:, 0], embedding[:, 1])
        for j, name in enumerate(names):
            ax[i].annotate(name, (embedding[j, 0], embedding[j, 1]))
        ax[i].set_title(title)
    plt.suptitle(f'{algorithm} embeddings')
    plt.show()

    
def main():
    
    if len(argv) < 2:
        raise ValueError('At least one embedding algorithm must be provided as argument')
    
    args_lower = [arg.lower() for arg in argv[1:]]

    directed = 'directed' in args_lower
    do_plot = 'plot' in args_lower
    three_d = '3d' in args_lower


    accepted_algorithms = ['graph2vec', 'feathergraph', 'sf', 'fgsd', 'geoscattering', 'gl2vec', 'ige', 'ldp', 'netlsd', 'waveletcharacteristic']
    algorithm = next((arg for arg in args_lower if arg in accepted_algorithms), None)
    if algorithm is None:
        raise ValueError(f"No valid algorithm provided. Accepted algorithms are: {', '.join(accepted_algorithms)}")
    

    hashtag_path = "../data/hashtags/vertices"
    hashtags = [f[:-5] for f in os.listdir(hashtag_path) if f.endswith('.json')]

    names, graphs = construct_graphs(hashtags, directed)
    embeddings = embed_graphs(graphs, algorithm)
    
    if do_plot:
        plot_embeddings(embeddings, names, algorithm, three_d)




if __name__ == "__main__":
    main()