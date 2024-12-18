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
    is_sentiment_graph = 'stitcher_sentiment' in graphs[0].es.attributes()
    for i, g in enumerate(graphs):
        if g.is_directed():
            g = g.as_undirected(mode='each')  # gspan only works with undirected graphs
        output += f't # {i}\n'
        for v in g.vs:
            output += f'v {v.index} 0\n'
        for e in g.es:
            if is_sentiment_graph:
                sentiment = e['stitcher_sentiment_value']
            else:
                sentiment = 0
            output += f'e {e.source} {e.target} {sentiment}\n'
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
    is_sentiment_graph = 'stitcher_sentiment' in graphs[0].es.attributes()
    for i, g in enumerate(graphs):
        for v in g.vs:
            output += f'v {v.index + 1}\n'
        for e in g.es:
            if is_sentiment_graph:
                sentiment = e['stitcher_sentiment_value']
            else:
                sentiment = 0
            output += f'e {e.source + 1} {e.target + 1} {sentiment}\n'
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
            u, v, s = map(int, line.split(' ')[1:4])
            edges.append((u, v, s))
        elif line.startswith('t') and not line.startswith('t # 0'):
            g = ig.Graph.TupleList(edges, directed=False, edge_attrs=['sentiment_value'])
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
    g = ig.Graph.TupleList(edges, directed=False, edge_attrs=['sentiment_value'])
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
            u, v, s = int(line.split(' ')[1]) - 1, int(line.split(' ')[2]) - 1, int(line.split(' ')[3])
            edges.append((u, v, s))
        elif line.startswith('g'):
            g = ig.Graph(directed=True)
            for v in vertices:
                g.add_vertex(v)
            for u, v, s in edges:
                g.add_edge(u, v, sentiment_value=s)
            graphs.append(g)
            vertices = set()
            edges = []
        elif line.startswith('s'):
            support = int(line.split(' ')[3])
            graphs[-1]['support'] = support
    return graphs

def gspan(filepath, 
          support: float = 0.5, 
          output_graph_ids: bool = True,
          output_discovered_patterns: bool = True, 
          negative_data_filepath=None, 
          input_pattern_filepath=None, 
          output_dfs_codes: bool = False, 
          min_length: int = None, 
          lower_bound: float = None, 
          num_threads: int = None, 
          move_output_file: bool = True,
          verbose: bool = False
          ):
    command = f'./gSpan6/gSpan -f {filepath} -s {support}'
    if negative_data_filepath:
        command += f' -n {negative_data_filepath}'
    if input_pattern_filepath:
        command += f' -p {input_pattern_filepath}'
    if output_discovered_patterns:
        command += ' -o'
    if output_graph_ids:
        command += ' -i'
    if output_dfs_codes:
        command += ' -d'
    if min_length is not None:
        command += f' -m {min_length}'
    if lower_bound is not None:
        command += f' -v {lower_bound}'
    if num_threads is not None:
        command += f' -t {num_threads}'
    filename = os.path.basename(filepath)
    if verbose:
        print(command)
    os.system(command)
    
    if move_output_file:
        filename = os.path.basename(filepath)
        os.rename(f'{filepath}.fp', f'../data/fsm/subgraphs/{filename}.fp')
        
def moss(filepath,
         support: int = 50,
         directed: bool = True,
         heap_size: int = 6,
         restrict_to_closed_substrucutres: bool = False,
         generate_all_possible_extensions: bool = True,
         maximum_substrucutre_size: int = 4,
         verbose: bool = False
         ):
    filename = os.path.basename(filepath)
    heap_size = f'-Xmx{heap_size}g' if heap_size else ''
    directed = '-D' if directed else ''
    restrict_to_closed_substrucutres = '-C' if not restrict_to_closed_substrucutres else ''
    generate_all_possible_extensions = '-A' if generate_all_possible_extensions else ''
    command = f'java {heap_size} -cp dmoss/moss.jar moss.Miner -inel -onel -x {directed} -m2 -n{maximum_substrucutre_size} -s{support} {restrict_to_closed_substrucutres} {generate_all_possible_extensions} {filepath} ../data/fsm/subgraphs/{filename}.moss'
    if verbose:
        print(command)
    os.system(command)

def json_to_igraph(json_content: list) -> list:
    graphs = []
    for sub in json_content:
        edges = sub['edges']
        g = ig.Graph.TupleList(edges)
        g.es['sentiment_value'] = sub['edge_colors']
        g['support'] = sub['graph_support']
        g['fsm_support'] = sub['fsm_support']
        g['twitter_support'] = sub['twitter_support']
        g['conf_support'] = sub['conf_support']
        graphs.append(g)
    return graphs