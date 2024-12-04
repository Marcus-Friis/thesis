from utils.graph_utils import get_all_user_graphs, get_all_twitter_user_graphs, get_all_sentiment_user_graphs, get_all_twitter_sentiment_user_graphs
from utils.fsm_utils import gspan, moss, igraph_to_gspan, igraph_to_nel, gspan_to_igraph, nel_to_igraph
import igraph as ig
import os

if __name__ == '__main__':
    import json
    import random
    random.seed(42)

    # load and preprocess data
    print('Loading graphs...')
    graphs = get_all_user_graphs()
    graphs = [g.simplify() for g in graphs]  # remove self loops and multi-edges for computational efficiency
    lccs = [g.components(mode='weak').giant() for g in graphs]
    
    # sentiment graphs
    sgraphs = get_all_sentiment_user_graphs()
    sgraphs = [g.simplify(multiple=False) for g in sgraphs]
    slccs = [g.components(mode='weak').giant() for g in sgraphs]
    
    # load twitter data
    twitter_graphs = get_all_twitter_user_graphs()
    twitter_graphs = [g.simplify() for g in twitter_graphs]
    twitter_lccs = [g.components(mode='weak').giant() for g in twitter_graphs]
    
    # twitter sentiment graphs
    stwitter_graphs = get_all_twitter_sentiment_user_graphs()
    stwitter_graphs = [g.simplify(multiple=False) for g in stwitter_graphs]
    stwitter_lccs = [g.components(mode='weak').giant() for g in stwitter_graphs]

    # create random graphs for comparison
    BOOTSTRAPS = 10
    confs = [
        ig.Graph.Degree_Sequence(g.degree(mode='in'), g.degree(mode='out')).simplify()
        for g in graphs for _ in range(BOOTSTRAPS)
    ]
    conf_lccs = [
        ig.Graph.Degree_Sequence(g.degree(mode='in'), g.degree(mode='out')).simplify()
        for g in lccs for _ in range(BOOTSTRAPS)
    ]
    ers = [
        ig.Graph.Erdos_Renyi(n=g.vcount(), m=g.ecount(), directed=True).simplify(multiple=False)
        for g in graphs for _ in range(BOOTSTRAPS)
    ]
    er_lccs = [
        ig.Graph.Erdos_Renyi(n=g.vcount(), m=g.ecount(), directed=True).simplify(multiple=False)
        for g in lccs for _ in range(BOOTSTRAPS)
    ]
    
    graph_dict = {
        'graph': graphs,
        'lcc': lccs,
        'sentiment_graph': sgraphs,
        'sentiment_lcc': slccs,
        'twitter_graph': twitter_graphs,
        'twitter_lcc': twitter_lccs,
        'twitter_sentiment_graph': stwitter_graphs,
        'twitter_sentiment_lcc': stwitter_lccs,
        'conf_graph': confs,
        'conf_lcc': conf_lccs,
        'er_graph': ers,
        'er_lcc': er_lccs
    }
    graphs_to_mine = ['graph', 'lcc', 'sentiment_graph', 'sentiment_lcc']

    # convert to gspan and nel format
    for key in graphs_to_mine:
        value = graph_dict[key]
        gspan_content = igraph_to_gspan(value)
        nel = igraph_to_nel(value)
        with open(f'../data/fsm/graphs/{key}.gspan', 'w') as f:
            f.write(gspan_content)
        with open(f'../data/fsm/graphs/{key}.nel', 'w') as f:
            f.write(nel)

    # perform frequent subgraph mining
    print('Mining frequent undirected subgraphs...')
    for key in graphs_to_mine:
        print(f'\t Mining {key}...')
        # run gspan - ./gSpan6/gSpan -f ../data/fsm/graphs/{key}.gspan -s 0.6 -o -i
        filepath = f'../data/fsm/graphs/{key}.gspan'
        gspan(filepath, support=0.6, verbose=True)

    print('Mining frequent directed subgraphs...')
    for key in graphs_to_mine:
        print(f'\t Mining {key}...')
        # run moss - java -Xmx6g -cp dmoss/moss.jar moss.Miner -inel -onel -x -D -m2 -n4 -s33 -C -A ../data/fsm/graphs/{key}.nel ../data/fsm/subgraphs/{key}.nel.moss
        filepath = f'../data/fsm/graphs/{key}.nel'
        moss(filepath, support=33, heap_size=6, directed=True, verbose=True)

    # analyse significant motifs
    def analyze_motif(motif: ig.Graph, graphs: list, twitter: list, use_edge_colors: bool, confs: list = None, ers: list = None) -> dict:
        fsm_support = motif['support']
        if use_edge_colors:
            motif_edge_color = 'sentiment_value'
            graphs_edge_color = 'stitcher_sentiment_value'
            twitter_edge_color = 'sentiment_value'
        else:
            motif_edge_color = None
            graphs_edge_color = None
            twitter_edge_color = None
            
        occurrences = [g.subisomorphic_vf2(motif, edge_color1=graphs_edge_color, edge_color2=motif_edge_color) for g in graphs]
        indeces = [i for i, o in enumerate(occurrences) if o]
        graph_labels = [g['name'] for g, o in zip(graphs, occurrences) if o]
        graph_support = sum(occurrences)

        twitter_occurences = [g.subisomorphic_vf2(motif, edge_color1=twitter_edge_color, edge_color2=motif_edge_color) for g in twitter]
        twitter_indeces = [i for i, o in enumerate(twitter_occurences) if o]
        twitter_support = sum(twitter_occurences)

        if confs is not None:
            conf_support = sum([1 for g in confs if g.subisomorphic_vf2(motif)]) / BOOTSTRAPS
        else:
            conf_support = None
        if ers is not None:
            er_support = sum([1 for g in ers if g.subisomorphic_vf2(motif)]) / BOOTSTRAPS
        else:
            er_support = None

        return {
            'vertices': [v.index for v in motif.vs],
            'edges': [(e.source, e.target) for e in motif.es],
            'edge_colors': [e['sentiment_value'] for e in motif.es] if motif.es.attributes() else None,
            'graph_occurrences': occurrences,
            'graph_indeces': indeces,
            'graph_labels': graph_labels,
            'graph_support': graph_support,
            'fsm_support': fsm_support,
            'twitter_occurences': twitter_occurences,
            'twitter_indeces': twitter_indeces,
            'twitter_support': twitter_support,
            'conf_support': conf_support,
            'er_support': er_support
        }

    print('Analysing significant motifs...')
    for key in graphs_to_mine:
        print(f'\t Analysing {key}...')
        use_edge_colors = 'sentiment' in key
        data = []
        with open(f'../data/fsm/subgraphs/{key}.gspan.fp') as f:
            gspan_content = f.read()
        motifs = gspan_to_igraph(gspan_content)
        graphs = graph_dict[key]
        graphs = [g.as_undirected(mode='each') for g in graphs]
        twitter = graph_dict[f'twitter_{key}']
        twitter = [g.as_undirected(mode='each') for g in twitter]
        confs = graph_dict.get(f'conf_{key}', None)
        confs = [g.as_undirected(mode='each') for g in confs] if confs is not None else None
        ers = graph_dict.get(f'er_{key}', None)
        ers = [g.as_undirected(mode='each') for g in ers] if ers is not None else None

        for i, motif in enumerate(motifs):
            print(f'\t\t Analysing motif {i}...')
            motif_data = analyze_motif(motif, graphs, twitter, use_edge_colors, confs, ers)
            data.append(motif_data)

        with open(f'../data/fsm/subgraph_data/{key}.json', 'w') as f:
            json.dump(data, f, indent=2)

    # analyse significant motifs in directed graphs
    print('Analysing significant motifs in directed graphs...')
    for key in graphs_to_mine:
        print(f'\t Analysing {key}...')
        use_edge_colors = 'sentiment' in key
        data = []
        with open(f'../data/fsm/subgraphs/{key}.nel.moss') as f:
            nel = f.read()
        motifs = nel_to_igraph(nel)
        graphs = graph_dict[key]
        twitter = graph_dict[f'twitter_{key}']
        confs = graph_dict.get(f'conf_{key}', None)
        ers = graph_dict.get(f'er_{key}', None)

        for i, motif in enumerate(motifs):
            print(f'\t\t Analysing motif {i}...')
            motif_data = analyze_motif(motif, graphs, twitter, use_edge_colors, confs, ers)
            data.append(motif_data)

        with open(f'../data/fsm/subgraph_data/{key}_directed.json', 'w') as f:
            json.dump(data, f, indent=2)