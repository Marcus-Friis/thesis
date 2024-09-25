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

def output_summary_statistics(G: ig.Graph) -> dict:
    G_un = G.as_undirected()
    G_simple = G_un.simplify()

    metrics = {}
    metrics['Vertices'] = G.vcount()
    metrics['Edges'] = G.ecount()
    metrics['Components'] = len(G_un.components())
    metrics['Largest component size'] = max(G_un.components().sizes())
    metrics['Degree Assortativity'] = G.assortativity_degree(directed=True)
    metrics['Clustering Coefficient'] = G.transitivity_undirected()
    metrics['Diameter'] = G.diameter()
    metrics['Undirected Diameter'] = G_un.diameter()
    #metrics['Reciprocity'] = G.reciprocity()
    metrics['% of vertices in the largest component'] = max(G_un.components().sizes()) / G.vcount()

    components = G_simple.components()
    c_sizes = [len(c) for c in components if len(c) > 2]
    if len(c_sizes) > 0:

        degree_centralizations = [degree_centralization(G_simple.subgraph(c)) for c in components if len(c) > 2]
        closeness_centralizations = [closeness_centralization(G_simple.subgraph(c)) for c in components if len(c) > 2]
        betweenness_centralizations = [betweenness_centralization(G_simple.subgraph(c)) for c in components if len(c) > 2]

        lcc_degree_centralization = degree_centralizations[np.argmax(c_sizes)]
        lcc_closeness_centralization = closeness_centralizations[np.argmax(c_sizes)]
        lcc_betweenness_centralization = betweenness_centralizations[np.argmax(c_sizes)]

        metrics['Global degree centralization'] = degree_centralization(G_simple.as_undirected())
        metrics['Largest component degree centralization'] = lcc_degree_centralization
        #metrics['Avg. local degree centralization'] = np.mean(degree_centralizations)
        #metrics['Weighted avg. local degree centralization'] = np.average(degree_centralizations, weights=c_sizes)

        metrics['Global closeness centralization'] = closeness_centralization(G_simple.as_undirected())
        metrics['Largest component closeness centralization'] = lcc_closeness_centralization
        #metrics['Avg. local closeness centralization'] = np.mean(closeness_centralizations)
        #metrics['Weighted avg. local closeness centralization'] = np.average(closeness_centralizations, weights=c_sizes)

        metrics['Global betweenness centralization'] = betweenness_centralization(G_simple.as_undirected())
        metrics['Largest component betweenness centralization'] = lcc_betweenness_centralization
        #metrics['Avg. local betweenness centralization'] = np.mean(betweenness_centralizations)
        #metrics['Weighted avg. local betweenness centralization'] = np.average(betweenness_centralizations, weights=c_sizes)

    return metrics


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
    plt.close(fig)


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
    plt.close(fig)

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
    plt.close(fig)

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
    plt.close(fig)

if __name__ == '__main__':
    plt.style.use('ggplot')
    from sys import argv

    if len(argv) < 2:
        raise ValueError('At least one hashtag must be provided as argument')

    # Separate hashtags from the plot flag
    hashtag_args = [arg for arg in argv[1:] if arg.lower() not in ['true', 'false']]
    create_plots = 'true' in map(str.lower, argv[1:])
    print(f'Processing {len(hashtag_args)} hashtags:\n')

    # Initialize a DataFrame to store all hashtag metrics
    all_video_metrics_df = pd.DataFrame()
    all_user_metrics_df = pd.DataFrame()

    for hashtag in hashtag_args:
        print(f'\nProcessing hashtag: {hashtag}\n')
        
        # read vertex data
        with open(f'../data/hashtags/stitch/vertices/{hashtag}.json', 'r') as f:
            vertices = json.load(f)

            if isinstance(vertices, list):
                # Convert list to a dictionary using 'id' as the key
                vertices = {str(item['id']): item for item in vertices if 'id' in item}


        # read edges from file
        edges = pd.read_csv(f'../data/hashtags/stitch/edges/{hashtag}_edges.txt', header=None)

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
        # Get metrics
        video_metrics = output_summary_statistics(G)

        # Convert the metrics dictionary to a DataFrame, transpose it to make metrics rows
        video_metrics_df = pd.DataFrame(video_metrics, index=[hashtag])
        
  


        if create_plots:
            # plot degree distribution
            plot_degree_distributions(G, hashtag)

            # plot graph
            target = f'../figures/video_graphs/{hashtag}-graph.svg'
            layout = G.layout_graphopt(niter=1000)
            print(f"Plotting video graph for {hashtag}")
            ig.plot(G, layout=layout, vertex_size=2, vertex_label=G.vs["name"], vertex_frame_width=0.01, 
                    edge_arrow_size=0.01, edge_width=0.2, target=target, vertex_label_size=0.1)

        # Repeat for user graph
        G = get_usergraph(edges)
        print(f'\nUser Graph for {hashtag}')
        user_metrics = output_summary_statistics(G)

        # Convert user graph metrics to a DataFrame, transpose it to make metrics rows
        user_metrics_df = pd.DataFrame(user_metrics, index=[f'{hashtag}-user'])

        if create_plots:
            plot_degree_distributions(G, hashtag + '-user')
            target = f'../figures/user_graphs/{hashtag}-user-graph.svg'
            layout = G.layout_graphopt(niter=1000)
            print(f"Plotting user graph for {hashtag}")
            ig.plot(G, layout=layout, vertex_size=2, vertex_label=None, vertex_frame_width=0.01, 
                    edge_arrow_size=0.01, edge_width=0.2, target=target)
            
            # plot user graph with component size > 2
            components = G.as_undirected().components()
            sizes = [len(c) for c in components]
            components_filtered = [c for c in components if len(c) > 2]
            G_sub = G.subgraph(sum(components_filtered, []))
            target = f'../figures/user_graphs_filtered/{hashtag}-user-graph-filtered.svg'
            layout = G_sub.layout_graphopt(niter=1000)
            ig.plot(G_sub, layout=layout, vertex_size=2, vertex_label=None, vertex_frame_width=0.01, 
                    edge_arrow_size=0.01, edge_width=0.2, target=target)
            
        all_video_metrics_df = pd.concat([all_video_metrics_df.copy(), video_metrics_df], axis=0)
        all_user_metrics_df = pd.concat([all_user_metrics_df.copy(), user_metrics_df], axis=0)

    # Format the metrics DataFrames as LaTeX strings
    # video_formatted_latex = all_video_metrics_df.style.format("{:.2f}").to_latex()
    # user_formatted_latex = all_user_metrics_df.style.format("{:.2f}").to_latex()

    # # Output the formatted LaTeX string
    # print('\n\n')
    # print('Video Metrics')
    # print(video_formatted_latex)
    # print('\n\n')
    # print('User Metrics')
    # print(user_formatted_latex)


    #Convert cols to ints
    all_video_metrics_df[['Vertices', 'Edges', 'Components', 'Largest component size']] = all_video_metrics_df[['Vertices', 'Edges', 'Components', 'Largest component size']].astype(int)
    #Convert rest of cols to floats with 2 decimal places
    all_video_metrics_df[[col for col in all_video_metrics_df.columns if col not in ['Vertices', 'Edges', 'Components', 'Largest component size']]] = (
        all_video_metrics_df[[col for col in all_video_metrics_df.columns if col not in ['Vertices', 'Edges', 'Components', 'Largest component size']]].astype(float).round(2)
    )

    #Repeat for user metrics
    all_user_metrics_df[['Vertices', 'Edges', 'Components', 'Largest component size']] = all_user_metrics_df[['Vertices', 'Edges', 'Components', 'Largest component size']].astype(int)
    all_user_metrics_df[[col for col in all_user_metrics_df.columns if col not in ['Vertices', 'Edges', 'Components', 'Largest component size']]] = (
        all_user_metrics_df[[col for col in all_user_metrics_df.columns if col not in ['Vertices', 'Edges', 'Components', 'Largest component size']]].astype(float).round(2)
    )
    

    #Save the metrics to a csv file
    
    all_video_metrics_df.fillna('NA').to_csv('../data/all_video_metrics_df.csv', index=True, index_label='hashtag')
    all_user_metrics_df.fillna('NA').to_csv('../data/all_user_metrics_df.csv', index=True, index_label='hashtag')

    print(all_video_metrics_df)
    print('Done')