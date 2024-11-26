from graph_utils import get_all_user_graphs
import igraph as ig
import os

def igraph_to_gspan(graphs: list) -> str:
    """
    t # 0
    v 1 a
    v 2 b
    e 1 2 a
    """
    output = ''
    for i, g in enumerate(graphs):
        g = g.as_undirected()  # gspan only works with undirected graphs
        output += f't # {i}\n'
        for v in g.vs:
            output += f'v {v.index} 0\n'
        for e in g.es:
            output += f'e {e.source} {e.target} 0\n'
    return output

def igraph_to_nel(graphs: list) -> str:
    """
    v 1
    v 2
    e 1 2
    g 1
    x 0
    """
    output = ''
    for i, g in enumerate(graphs):
        for v in g.vs:
            output += f'v {v.index + 1}\n'
        for e in g.es:
            output += f'e {e.source + 1} {e.target + 1}\n'
        output += f'g {i+1}\n'
        output += 'x 0\n\n'
    output = output.strip() + '\n'
    return output

def gspan_to_igraph(gspan_content: str) -> list:
    graphs = []
    edges = []
    support = None
    lines = gspan_content.strip().split('\n')
    for line in lines:
        if line.startswith('e'):
            u, v = int(line.split(' ')[1]), int(line.split(' ')[2])
            edges.append((u, v))
        elif line.startswith('t') and not line.startswith('t # 0'):
            g = ig.Graph.TupleList(edges, directed=False)
            if support is not None:
                g['support'] = support
            graphs.append(g)
            edges = []
            if len(line.split(' ')) > 3 and line.split(' ')[3] == '*':
                support = int(line.split(' ')[4])
        elif line.startswith('t # 0'):
            parts = line.split(' ')
            if len(parts) > 3 and parts[3] == '*':
                support = int(parts[4])
            else:
                support = None
    g = ig.Graph.TupleList(edges, directed=False)
    g['support'] = support
    graphs.append(g)
    return graphs

def nel_to_igraph(nel_content: str) -> list:
    graphs = []
    vertices = set()
    edges = []
    lines = nel_content.strip().split('\n')
    for line in lines:
        if line.startswith('v') or line.startswith('n'):
            u = int(line.split(' ')[1]) - 1
            vertices.add(u)
        elif line.startswith('e') or line.startswith('d'):
            u, v = int(line.split(' ')[1]) - 1, int(line.split(' ')[2]) - 1
            edges.append((u, v))
        elif line.startswith('g'):
            g = ig.Graph(directed=True)
            for v in vertices:
                g.add_vertex(v)
            for u, v in edges:
                g.add_edge(u, v)
            graphs.append(g)
            vertices = set()
            edges = []
        elif line.startswith('s'):
            support = int(line.split(' ')[3])
            graphs[-1]['support'] = support
    return graphs


if __name__ == '__main__':
    import json
    import random
    random.seed(42)

    # load and preprocess data
    print('Loading graphs...')
    graphs = get_all_user_graphs()
    graphs = [g.simplify() for g in graphs]  # remove self loops and multi-edges for computational efficiency
    lccs = [g.components(mode='weak').giant() for g in graphs]

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
        'conf_graph': confs,
        'conf_lcc': conf_lccs,
        'er_graph': ers,
        'er_lcc': er_lccs
    }
    graphs_to_mine = ['graph', 'lcc']

    # convert to gspan and nel format
    for key in graphs_to_mine:
        value = graph_dict[key]
        gspan = igraph_to_gspan(value)
        nel = igraph_to_nel(value)
        with open(f'../data/fsm/graphs/{key}.gspan', 'w') as f:
            f.write(gspan)
        with open(f'../data/fsm/graphs/{key}.nel', 'w') as f:
            f.write(nel)

    # perform frequent subgraph mining
    print('Mining frequent undirected subgraphs...')
    for key in graphs_to_mine:
        print(f'\t Mining {key}...')
        command = f'./gSpan6/gSpan -f ../data/fsm/graphs/{key}.gspan -s 0.6 -o -i'
        os.system(command)

        # move output to subgraphs directory
        if os.path.exists(f'../data/fsm/graphs/{key}.gspan.fp'):
            os.rename(f'../data/fsm/graphs/{key}.gspan.fp', f'../data/fsm/subgraphs/{key}.gspan.fp')

    print('Mining frequent directed subgraphs...')
    for key in graphs_to_mine:
        print(f'\t Mining {key}...')
        command = f'java -Xmx6g -cp dmoss/moss.jar moss.Miner -inel -onel -x -D -m2 -n4 -s10 -C -A ../data/fsm/graphs/{key}.nel ../data/fsm/subgraphs/{key}.nel.moss'
        os.system(command)

    # analyse significant motifs
    print('Analysing significant motifs...')
    for key in graphs_to_mine:
        print(f'\t Analysing {key}...')
        data = []
        with open(f'../data/fsm/subgraphs/{key}.gspan.fp') as f:
            gspan = f.read()
        motifs = gspan_to_igraph(gspan)
        graphs = graph_dict[key]
        confs = graph_dict[f'conf_{key}']
        ers = graph_dict[f'er_{key}']

        for i, motif in enumerate(motifs):
            print(f'\t\t Analysing motif {i}...')
            occurrences = [g.as_undirected().subisomorphic_vf2(motif) for g in graphs]
            indeces = [i for i, o in enumerate(occurrences) if o]
            graph_labels = [g['name'] for g, o in zip(graphs, occurrences) if o]
            graph_support = sum(occurrences)
            gspan_support = motif['support']
            conf_support = sum([1 for g in confs if g.as_undirected().subisomorphic_vf2(motif)]) / BOOTSTRAPS
            er_support = sum([1 for g in ers if g.as_undirected().subisomorphic_vf2(motif)]) / BOOTSTRAPS
            
            motif_data = {
                'vertices': [v.index for v in motif.vs],
                'edges': [(e.source, e.target) for e in motif.es],
                'graph_indeces': indeces,
                'graph_labels': graph_labels,
                'graph_support': graph_support,
                'conf_support': conf_support,
                'er_support': er_support,
                'gspan_support': gspan_support
            }
            data.append(motif_data)

        with open(f'../data/fsm/subgraph_data/{key}.json', 'w') as f:
            json.dump(data, f, indent=2)

    # analyse significant motifs in directed graphs
    print('Analysing significant motifs in directed graphs...')
    for key in graphs_to_mine:
        print(f'\t Analysing {key}...')
        data = []
        with open(f'../data/fsm/subgraphs/{key}.nel.moss') as f:
            nel = f.read()
        motifs = nel_to_igraph(nel)
        graphs = graph_dict[key]
        confs = graph_dict[f'conf_{key}']
        ers = graph_dict[f'er_{key}']

        for i, motif in enumerate(motifs):
            print(f'\t\t Analysing motif {i}...')
            occurrences = [g.subisomorphic_vf2(motif) for g in graphs]
            indeces = [i for i, o in enumerate(occurrences) if o]
            graph_labels = [g['name'] for g, o in zip(graphs, occurrences) if o]
            graph_support = sum(occurrences)
            gspan_support = motif['support']
            conf_support = sum([1 for g in confs if g.subisomorphic_vf2(motif)]) / BOOTSTRAPS
            er_support = sum([1 for g in ers if g.subisomorphic_vf2(motif)]) / BOOTSTRAPS
            
            motif_data = {
                'vertices': [v.index for v in motif.vs],
                'edges': [(e.source, e.target) for e in motif.es],
                'graph_indeces': indeces,
                'graph_labels': graph_labels,
                'graph_support': graph_support,
                'conf_support': conf_support,
                'er_support': er_support,
                'gspan_support': gspan_support
            }
            data.append(motif_data)

        with open(f'../data/fsm/subgraph_data/{key}_directed.json', 'w') as f:
            json.dump(data, f, indent=2)