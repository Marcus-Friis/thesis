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
    data_path = '../data/hashtags/edges/'
    edge_files = [file for file in os.listdir(data_path) if file.endswith('.txt')]

    # load and process graphs
    graphs = []
    lcc_graphs = []
    conf_graphs = []
    conf_lcc_graphs = []
    er_graphs = []
    er_lcc_graphs = []
    for i, edge_file in enumerate(edge_files):
        # read edge file
        edge_file_path = os.path.join(data_path, edge_file)
        edges = load_edges(edge_file_path)
        g = get_user_graph(edges)

        # get lcc
        g_lcc = g.components(mode='weak').giant()

        # get configuration models for both graphs
        indeg_sequence  = g.degree(mode='in', loops=False)
        outdeg_sequence = g.degree(mode='out', loops=False)
        g_conf = ig.Graph.Degree_Sequence(indeg_sequence, outdeg_sequence)

        indeg_sequence_lcc  = g_lcc.degree(mode='in', loops=False)
        outdeg_sequence_lcc = g_lcc.degree(mode='out', loops=False)
        g_lcc_conf = ig.Graph.Degree_Sequence(indeg_sequence_lcc, outdeg_sequence_lcc)

        # get erdos-renyi random graphs
        g_er = ig.Graph.Erdos_Renyi(n=g.vcount(), m=g.ecount()).simplify()
        g_lcc_er = ig.Graph.Erdos_Renyi(n=g_lcc.vcount(), m=g_lcc.ecount()).simplify()
        
        # append graphs
        graphs.append(g)
        lcc_graphs.append(g_lcc)
        conf_graphs.append(g_conf)
        conf_lcc_graphs.append(g_lcc_conf)
        er_graphs.append(g_er)
        er_lcc_graphs.append(g_lcc_er)

    # format into gspan and nel files
    gspan = igraph_to_gspan(graphs)
    nel = igraph_to_nel(graphs)
    gspan_lcc = igraph_to_gspan(lcc_graphs)
    nel_lcc = igraph_to_nel(lcc_graphs)
    gspan_conf = igraph_to_gspan(conf_graphs)
    nel_conf = igraph_to_nel(conf_graphs)
    gspan_lcc_conf = igraph_to_gspan(conf_lcc_graphs)
    nel_lcc_conf = igraph_to_nel(conf_lcc_graphs)
    gspan_er = igraph_to_gspan(er_graphs)
    nel_er = igraph_to_nel(er_graphs)
    gspan_lcc_er = igraph_to_gspan(er_lcc_graphs)
    nel_lcc_er = igraph_to_nel(er_lcc_graphs)

    # dump data files
    data_path = '../data/fsm/graphs'
    with open(os.path.join(data_path, 'graph.gspan'), 'w') as f:
        f.write(gspan)
    with open(os.path.join(data_path, 'graph.nel'), 'w') as f:
        f.write(nel)
    with open(os.path.join(data_path, 'lcc.gspan'), 'w') as f:
        f.write(gspan_lcc)
    with open(os.path.join(data_path, 'lcc.nel'), 'w') as f:
        f.write(nel_lcc)
    with open(os.path.join(data_path, 'conf.gspan'), 'w') as f:
        f.write(gspan_conf)
    with open(os.path.join(data_path, 'conf.nel'), 'w') as f:
        f.write(nel_conf)
    with open(os.path.join(data_path, 'conf_lcc.gspan'), 'w') as f:
        f.write(gspan_lcc_conf)
    with open(os.path.join(data_path, 'conf_lcc.nel'), 'w') as f:
        f.write(nel_lcc_conf)
    with open(os.path.join(data_path, 'er.gspan'), 'w') as f:
        f.write(gspan_er)
    with open(os.path.join(data_path, 'er.nel'), 'w') as f:
        f.write(nel_er)
    with open(os.path.join(data_path, 'er_lcc.gspan'), 'w') as f:
        f.write(gspan_lcc_er)
    with open(os.path.join(data_path, 'er_lcc.nel'), 'w') as f:
        f.write(nel_lcc_er)