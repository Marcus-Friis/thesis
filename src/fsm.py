from graph_utils import load_edges, get_user_graph
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
    lines = gspan_content.strip().split('\n')
    for line in lines:
        if line.startswith('e'):
            u, v = int(line.split(' ')[1]), int(line.split(' ')[2])
            edges.append((u, v))
        elif line.startswith('t') and line != 't # 0':
            g = ig.Graph.TupleList(edges, directed=False)
            graphs.append(g)
            edges = []
    g = ig.Graph.TupleList(edges, directed=False)
    graphs.append(g)
    return graphs

def nel_to_igraph(nel_content: str) -> list:
    graphs = []
    edges = []
    lines = nel_content.strip().split('\n')
    for line in lines:
        if line.startswith('e'):
            u, v = int(line.split(' ')[1]), int(line.split(' ')[2])
            edges.append((u, v))
        elif line.startswith('g'):
            g = ig.Graph.TupleList(edges, directed=True)
            graphs.append(g)
            edges = []
    return graphs            


if __name__ == '__main__':
    data_path = '../data/hashtags/edges/'
    edge_files = [file for file in os.listdir(data_path) if file.endswith('.txt')]

    # load and process graphs
    graphs = []
    lcc_graphs = []
    for i, edge_file in enumerate(edge_files):
        # read edge file
        edge_file_path = os.path.join(data_path, edge_file)
        edges = load_edges(edge_file_path)
        g = get_user_graph(edges)

        # get lcc
        lcc = g.as_undirected().components().giant()
        g_lcc = g.subgraph(lcc.vs.indices)

        # append graphs
        graphs.append(g)
        lcc_graphs.append(g_lcc)

    # format into gspan and nel files
    gspan = igraph_to_gspan(graphs)
    nel = igraph_to_nel(graphs)
    gspan_lcc = igraph_to_gspan(lcc_graphs)
    nel_lcc = igraph_to_nel(lcc_graphs)

    # dump data files
    data_path = '../data'
    with open(os.path.join(data_path, 'graph.gspan'), 'w') as f:
        f.write(gspan)
    with open(os.path.join(data_path, 'graph.nel'), 'w') as f:
        f.write(nel)
    with open(os.path.join(data_path, 'lcc.gspan'), 'w') as f:
        f.write(gspan_lcc)
    with open(os.path.join(data_path, 'lcc.nel'), 'w') as f:
        f.write(nel_lcc)
