import igraph as ig
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re


def get_usergraph(edges: pd.DataFrame) -> ig.Graph:
    expression = re.compile(r'@[\w\d\.]+')
    edges['stitcher'] = edges['stitcher_url'].apply(lambda x: re.findall(expression, x)[0])
    edges['stitchee'] = edges['stitchee_url'].apply(lambda x: re.findall(expression, x)[0])

    edges = edges.groupby(['stitcher', 'stitchee']).size().reset_index()

    G = ig.Graph.TupleList(edges[['stitcher', 'stitchee']].values, directed=True, edge_attrs=['weight'])
    G.es['weight'] = edges[0]

    return G

if __name__ == '__main__':
    plt.style.use('ggplot')
    from sys import argv

    # get hashtag from command line argument
    if len(argv) < 2:
        raise ValueError('Hashtag must be provided as argument')
    hashtag = argv[1]

    # read edges from file
    edges = pd.read_csv(f'../data/{hashtag}_edges_repair.txt', header=None)
    edges.columns = ['stitcher_url', 'stitchee_url']

    # remove all None edges
    edges = edges.dropna()

    # clean dataset
    edges['stitcher'] = edges['stitcher_url'].apply(lambda x: x.split('/')[-1])
    edges['stitchee'] = edges['stitchee_url'].apply(lambda x: x.split('/')[-1])

    # construct graph
    G = ig.Graph.TupleList(edges[['stitcher', 'stitchee']].values, directed=True, edge_attrs=['weight'])
    G.es['weight'] = 1

    # output summary statistics
    print('Video Graph')
    print('Number of vertices:', G.vcount())
    print('Number of edges:', G.ecount())
    print('Number of components:', len(G.as_undirected().components()))
    print('Largest component size:', max(G.as_undirected().components().sizes()))

    # plot degree distribution
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
    fig, ax = plt.subplots(figsize=[6.4*0.75, 4.8*0.75])
    ax.scatter(d_in, v_in, s=dot_size)
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')
    # ax.set_title(f'{PLOT_TITLES}in-degree distribution')
    ax.set_xlim(-10, x_upper_bound + 10)
    ax.set_ylim(-0.01, y_upper_bound + 0.01)
    plt.tight_layout()
    fig.savefig(f'../figures/degree_distributions/{hashtag}-in-degree.svg')

    # plot out-degree
    fig, ax = plt.subplots(figsize=[6.4*0.75, 4.8*0.75])
    ax.scatter(d_out, v_out, s=dot_size)
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')
    # ax.set_title(f'{PLOT_TITLES}out-degree distribution')
    ax.set_xlim(-10, x_upper_bound + 10)
    ax.set_ylim(-0.01, y_upper_bound + 0.01)
    plt.tight_layout()
    fig.savefig(f'../figures/degree_distributions/{hashtag}-out-degree.svg')

    # plot in-degree log-log
    fig, ax = plt.subplots(figsize=[6.4*0.75, 4.8*0.75])
    ax.scatter(d_in, v_in, s=dot_size)
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')
    # ax.set_title(f'{PLOT_TITLES}in-degree distribution')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.9, x_upper_bound*2)
    ax.set_ylim(0.0001, y_upper_bound*2)
    plt.tight_layout()
    fig.savefig(f'../figures/degree_distributions/{hashtag}-log-in-degree.svg')

    # plot out-degree log-log
    fig, ax = plt.subplots(figsize=[6.4*0.75, 4.8*0.75])
    d_out, v_out = np.unique(out_degrees, return_counts=True)
    v_out = v_out / v_out.sum()
    ax.scatter(d_out, v_out, s=dot_size)
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')
    # ax.set_title(f'{PLOT_TITLES}out-degree distribution')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.9, x_upper_bound*2)
    ax.set_ylim(0.0001, y_upper_bound*2)
    plt.tight_layout()
    fig.savefig(f'../figures/degree_distributions/{hashtag}-log-out-degree.svg')

    # plot graph
    target = f'../figures/video_graphs/{hashtag}-graph.svg'
    # layout = G.layout("kk")
    layout = G.layout_graphopt(niter=1000)
    ig.plot(G, layout=layout, vertex_size=2, vertex_label=None, vertex_frame_width=0, 
            edge_arrow_size=0, edge_width=0.2, target=target)


    # repeat for user graph
    G = get_usergraph(edges)

    # output summary statistics
    print('\nUser Graph')
    print('Number of vertices:', G.vcount())
    print('Number of edges:', G.ecount())
    print('Number of components:', len(G.as_undirected().components()))
    print('Largest component size:', max(G.as_undirected().components().sizes()))

    # plot degree distribution
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
    fig, ax = plt.subplots(figsize=[6.4*0.75, 4.8*0.75])
    ax.scatter(d_in, v_in, s=dot_size)
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')
    # ax.set_title(f'{PLOT_TITLES}in-degree distribution')
    ax.set_xlim(-10, x_upper_bound + 10)
    ax.set_ylim(-0.01, y_upper_bound + 0.01)
    plt.tight_layout()
    fig.savefig(f'../figures/degree_distributions/{hashtag}-user-in-degree.svg')

    # plot out-degree
    fig, ax = plt.subplots(figsize=[6.4*0.75, 4.8*0.75])
    ax.scatter(d_out, v_out, s=dot_size)
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')
    # ax.set_title(f'{PLOT_TITLES}out-degree distribution')
    ax.set_xlim(-10, x_upper_bound + 10)
    ax.set_ylim(-0.01, y_upper_bound + 0.01)
    plt.tight_layout()
    fig.savefig(f'../figures/degree_distributions/{hashtag}-user-out-degree.svg')

    # plot in-degree log-log
    fig, ax = plt.subplots(figsize=[6.4*0.75, 4.8*0.75])
    ax.scatter(d_in, v_in, s=dot_size)
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')
    # ax.set_title(f'{PLOT_TITLES}in-degree distribution')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.9, x_upper_bound*2)
    ax.set_ylim(0.0001, y_upper_bound*2)
    plt.tight_layout()
    fig.savefig(f'../figures/degree_distributions/{hashtag}-user-log-in-degree.svg')

    # plot out-degree log-log
    fig, ax = plt.subplots(figsize=[6.4*0.75, 4.8*0.75])
    d_out, v_out = np.unique(out_degrees, return_counts=True)
    v_out = v_out / v_out.sum()
    ax.scatter(d_out, v_out, s=dot_size)
    ax.set_xlabel('k')
    ax.set_ylabel('p(k)')
    # ax.set_title(f'{PLOT_TITLES}out-degree distribution')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.9, x_upper_bound*2)
    ax.set_ylim(0.0001, y_upper_bound*2)
    plt.tight_layout()
    fig.savefig(f'../figures/degree_distributions/{hashtag}-user-log-out-degree.svg')

    # plot graph
    target = f'../figures/user_graphs/{hashtag}-user-graph.svg'
    layout = G.layout_graphopt(niter=1000)
    ig.plot(G, layout=layout, vertex_size=2, vertex_label=None, vertex_frame_width=0, 
            edge_arrow_size=0, edge_width=0.2, target=target)
    
    # plot user graph with component size > 2
    components = G.as_undirected().components()
    sizes = [len(c) for c in components]
    components_filtered = [c for c in components if len(c) > 2]
    G_sub = G.subgraph(sum(components_filtered, []))
    target = f'../figures/user_graphs_filtered/{hashtag}-user-graph-filtered.svg'
    layout = G_sub.layout_graphopt(niter=1000)
    ig.plot(G_sub, layout=layout, vertex_size=2, vertex_label=None, vertex_frame_width=0, 
            edge_arrow_size=0, edge_width=0.2, target=target)
