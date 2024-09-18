import igraph as ig
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import json
import numpy as np
from graph_utils import degree_centralization, closeness_centralization, betweenness_centralization

def get_usergraph(edges: pd.DataFrame) -> ig.Graph:
    expression = re.compile(r'@[\w\d\.]+')
    edges['stitcher'] = edges['stitcher_url'].apply(lambda x: re.findall(expression, x)[0])
    edges['stitchee'] = edges['stitchee_url'].apply(lambda x: re.findall(expression, x)[0])

    edges = edges.groupby(['stitcher', 'stitchee']).size().reset_index()

    G = ig.Graph.TupleList(edges[['stitcher', 'stitchee']].values, directed=True, edge_attrs=['weight'])
    G.es['weight'] = edges[0]

    return G

def output_summary_statistics(G: ig.Graph) -> None:
    G_un = G.as_undirected()
    G_simple = G_un.simplify()

    print('Number of vertices:', G.vcount())
    print('Number of edges:', G.ecount())
    print('Number of components:', len(G_un.components()))
    print('Largest component size:', max(G_un.components().sizes()))
    print('Degree assortativity:', G.assortativity_degree(directed=True))
    print('Clustering coefficient:', G.transitivity_undirected())
    print('Diameter:', G.diameter())
    print('Undirected diameter:', G_un.diameter())
    print('Reciprocity:', G.reciprocity())

    components = G_simple.components()
    c_sizes = [len(c) for c in components if len(c) > 2]
    if len(c_sizes) > 0:

        degree_centralizations = [degree_centralization(G_simple.subgraph(c)) for c in components if len(c) > 2]
        closeness_centralizations = [closeness_centralization(G_simple.subgraph(c)) for c in components if len(c) > 2]
        betweenness_centralizations = [betweenness_centralization(G_simple.subgraph(c)) for c in components if len(c) > 2]

        lcc_degree_centralization = degree_centralizations[np.argmax(c_sizes)]
        lcc_closeness_centralization = closeness_centralizations[np.argmax(c_sizes)]
        lcc_betweenness_centralization = betweenness_centralizations[np.argmax(c_sizes)]

        print("\n")
        #Degree centralization
        print('Global degree centralization:', degree_centralization(G_simple.as_undirected()))
        print('Largest component degree centralization:', lcc_degree_centralization)
        print('Avg local degree centralization:', np.mean(degree_centralizations))
        print('Weighted avg local degree centralization:', np.average(degree_centralizations, weights=c_sizes))
        print("\n")
        #Closeness centralization
        print('Global closeness centralization:', closeness_centralization(G_simple.as_undirected()))
        print('Largest component closeness centralization:', lcc_closeness_centralization)
        print('Avg local closeness centralization:', np.mean(closeness_centralizations))
        print('Weighted avg local closeness centralization:', np.average(closeness_centralizations, weights=c_sizes))
        print("\n")
        #Betweenness centralization
        print('Global betweenness centralization:', betweenness_centralization(G_simple.as_undirected()))
        print('Largest component betweenness centralization:', lcc_betweenness_centralization)
        print('Avg local betweenness centralization:', np.mean(betweenness_centralizations))
        print('Weighted avg local betweenness centralization:', np.average(betweenness_centralizations, weights=c_sizes))
        print("\n")

def plot_degree_distributions(G, label):
    in_degrees = G.indegree()
    out_degrees = G.outdegree()

    # get frequency of each degree and normalize to density
    d_in, v_in = np.unique(in_degrees, return_counts=True)
    v_in = v_in / v_in.sum()
    d_out, v_out = np.unique(out_degrees, return_counts=True)
    v_out = v_out / v_out.sum()

    x_upper_bound = max(np.max(d_in), np.max(d_out))
    y_upper_bound = max(np.max(v_in), np.max(v_out))

    dot_size = 15

    # plot in-degree
    print('Plotting in-degree distribution')
    fig, ax = plt.subplots(figsize=[6.4*0.75, 4.8*0.75])
    ax.scatter(d_in, v_in, s=dot_size)
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')
    ax.set_xlim(-10, x_upper_bound + 10)
    ax.set_ylim(-0.01, y_upper_bound + 0.01)
    plt.tight_layout()
    fig.savefig(f'../figures/degree_distributions/{label}-in-degree.svg')

    # plot out-degree
    print('Plotting out-degree distribution')
    fig, ax = plt.subplots(figsize=[6.4*0.75, 4.8*0.75])
    ax.scatter(d_out, v_out, s=dot_size)
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')
    ax.set_xlim(-10, x_upper_bound + 10)
    ax.set_ylim(-0.01, y_upper_bound + 0.01)
    plt.tight_layout()
    fig.savefig(f'../figures/degree_distributions/{label}-out-degree.svg')

    # plot in-degree log-log
    print('Plotting in-degree log-log distribution')
    fig, ax = plt.subplots(figsize=[6.4*0.75, 4.8*0.75])
    ax.scatter(d_in, v_in, s=dot_size)
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.9, x_upper_bound*2)
    ax.set_ylim(0.0001, y_upper_bound*2)
    plt.tight_layout()
    fig.savefig(f'../figures/degree_distributions/{label}-log-in-degree.svg')

    # plot out-degree log-log
    print('Plotting out-degree log-log distribution')
    fig, ax = plt.subplots(figsize=[6.4*0.75, 4.8*0.75])
    d_out, v_out = np.unique(out_degrees, return_counts=True)
    v_out = v_out / v_out.sum()
    ax.scatter(d_out, v_out, s=dot_size)
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.9, x_upper_bound*2)
    ax.set_ylim(0.0001, y_upper_bound*2)
    plt.tight_layout()
    fig.savefig(f'../figures/degree_distributions/{label}-log-out-degree.svg')

if __name__ == '__main__':
    plt.style.use('ggplot')
    from sys import argv

    if len(argv) < 2:
        raise ValueError('At least one hashtag must be provided as argument')

    # Separate hashtags from the plot flag
    hashtag_args = [arg for arg in argv[1:] if arg.lower() not in ['true', 'false']]
    create_plots = 'true' in map(str.lower, argv[1:])

    for hashtag in hashtag_args:
        print(f'\nProcessing hashtag: {hashtag}\n')
        
        # read vertex data
        with open(f'../data/stitch/vertices/{hashtag}.json', 'r') as f:
            vertices = json.load(f)

        # read edges from file
        edges = pd.read_csv(f'../data/stitch/edges/{hashtag}_edges.txt', header=None)

        edges.columns = ['stitcher_url', 'stitchee_url']
        edges = edges[edges['stitcher_url'].str.contains('None') == False]
        edges = edges[edges['stitchee_url'].str.contains('None') == False]

        edges['stitcher'] = edges['stitcher_url'].apply(lambda x: x.split('/')[-1]).astype(np.int64)
        edges['stitchee'] = edges['stitchee_url'].apply(lambda x: x.split('/')[-1]).astype(np.int64)
        
        # construct graph
        G = ig.Graph.TupleList(edges[['stitcher', 'stitchee']].values, directed=True, edge_attrs=['weight'])
        G.es['weight'] = 1

        # add vertex attributes
        G.vs['username'] = [vertices[str(v)]['username'] if str(v) in vertices else None for v in G.vs['name'] if str(v) in vertices]
        G.vs['create_time'] = [vertices[str(v)]['create_time'] if str(v) in vertices else None for v in G.vs['name'] if str(v) in vertices]

        # output summary statistics
        print(f'Video Graph for {hashtag}')
        output_summary_statistics(G)

        if create_plots:
            # plot degree distribution
            plot_degree_distributions(G, hashtag)

            # plot graph
            target = f'../figures/video_graphs/{hashtag}-graph.svg'
            layout = G.layout_graphopt(niter=1000)
            print(f"Plotting video graph for {hashtag}")
            ig.plot(G, layout=layout, vertex_size=2, vertex_label=None, vertex_frame_width=0, 
                    edge_arrow_size=0, edge_width=0.2, target=target)

        # Repeat for user graph
        G = get_usergraph(edges)
        print(f'\nUser Graph for {hashtag}')
        output_summary_statistics(G)

        if create_plots:
            plot_degree_distributions(G, hashtag + '-user')
            target = f'../figures/user_graphs/{hashtag}-user-graph.svg'
            layout = G.layout_graphopt(niter=1000)
            print(f"Plotting user graph for {hashtag}")
            ig.plot(G, layout=layout, vertex_size=2, vertex_label=None, vertex_frame_width=0, 
                    edge_arrow_size=0.1, edge_width=0.2, target=target)
            
                # plot user graph with component size > 2
            components = G.as_undirected().components()
            sizes = [len(c) for c in components]
            components_filtered = [c for c in components if len(c) > 2]
            G_sub = G.subgraph(sum(components_filtered, []))
            target = f'../figures/user_graphs_filtered/{hashtag}-user-graph-filtered.svg'
            layout = G_sub.layout_graphopt(niter=1000)
            ig.plot(G_sub, layout=layout, vertex_size=2, vertex_label=None, vertex_frame_width=0, 
                    edge_arrow_size=0.1, edge_width=0.2, target=target)
