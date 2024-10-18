import igraph as ig
import networkx as nx
import os

def igraph_to_gspan(graphs: list) -> str:
    output = ''
    for i, g in enumerate(graphs):
        g = g.as_undirected()  # gspan only works with undirected graphs
        output += f't # {i}\n'
        for v in g.vs:
            output += f'v {v.index} 0\n'
        for e in g.es:
            output += f'e {e.source} {e.target} 0\n'
    return output
    
def gspan_to_igraph(gspan_content: str) -> list:
    graphs = []
    current_graph_edges = []
    in_graph = False
    for line in gspan_content.strip().splitlines():
        if line.startswith('t'):
            if in_graph:
                # Create a graph for the previous block
                g = ig.Graph.TupleList(current_graph_edges, directed=False)
                graphs.append(g)
                current_graph_edges = []  # Reset for the next graph
            in_graph = True
        elif line.startswith('v'):
            # Vertex information can be ignored for igraph
            continue
        elif line.startswith('e'):
            # Extract edge information
            _, source, target, _ = line.split()
            current_graph_edges.append((int(source), int(target)))
    if current_graph_edges:
        # Add the final graph
        g = ig.Graph.TupleList(current_graph_edges, directed=False)
        graphs.append(g)
    return graphs

def igraph_to_nel(graphs: list) -> str:
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

def nel_to_igraph(nel_content: str) -> list:
    graphs = []
    current_graph_edges = []
    in_graph = False
    for line in nel_content.strip().splitlines():
        if line.startswith('e'):
            _, source, target = line.split()
            current_graph_edges.append((int(source) - 1, int(target) - 1))
        elif line.startswith('g'):
            if in_graph and current_graph_edges:
                g = ig.Graph.TupleList(current_graph_edges, directed=True)
                graphs.append(g)
                current_graph_edges = []  # Reset for the next graph
            in_graph = True
    if current_graph_edges:
        # Add the final graph as directed
        g = ig.Graph.TupleList(current_graph_edges, directed=True)
        graphs.append(g)
    return graphs


if __name__ == '__main__':
    data_path = '../data/hashtags/edges/'
    edge_files = [file for file in os.listdir(data_path) if file.endswith('.txt')]

    # load and process graphs
    graphs = []
    for i, edge_file in enumerate(edge_files):
        # read edge file
        edge_file_path = os.path.join(data_path, edge_file)
        with open(edge_file_path, 'r') as f:
            edges = f.readlines()

        # construct user graph edgelist
        users = []
        for edge in edges:
            u, v = edge.strip().split(',')
            if 'None' in v:
                continue
            u_user = u.split('/')[-3]
            v_user = v.split('/')[-3]
            if (u_user, v_user) not in users:
                users.append((u_user, v_user))

        # construct lcc graph
        g = ig.Graph.TupleList(users, directed=True)
        lcc = g.as_undirected().components().giant()
        largest_components_nodes = lcc.vs.indices
        g_lcc = g.subgraph(largest_components_nodes)
        g_lcc = g_lcc.simplify()
        graphs.append(g_lcc)

    # format into gspan and nel files
    gspan = igraph_to_gspan(graphs)
    nel = igraph_to_nel(graphs)

    graphs = gspan_to_igraph(gspan)

    data_path = '../data'
    with open(os.path.join(data_path, 'lcc.gspan'), 'w') as f:
        f.write(gspan)
    with open(os.path.join(data_path, 'lcc.nel'), 'w') as f:
        f.write(nel)
