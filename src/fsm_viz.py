from utils.fsm_utils import gspan_to_igraph, nel_to_igraph, json_to_igraph
import igraph as ig
import json
from collections import Counter, defaultdict

def graph_to_tikz(g: ig.Graph, layout, scaling: float = 1, twitter: bool = False) -> str:
    is_directed = g.is_directed()
    edge_direct = ',Direct' if is_directed else ''
    max_coord = max([abs(x) for coor in layout for x in coor])
    
    sentiment_dict = {0: 'gray', 1: 'green', 2: 'red', 3: 'blue'}

    tikz_code = '\\begin{tikzpicture}\n'
    for i, (x, y) in enumerate(layout):
        x = x * scaling / max_coord
        y = y * scaling / max_coord
        tikz_code += f'\t\\Vertex[x={x:.2f}, y={y:.2f}]{{{i}}}\n'

    edge_list = g.get_edgelist()
    edge_counter = Counter(edge_list)
    edge_bend_dict = defaultdict(lambda : -33)
    for i, j in edge_list:
        edge_count = edge_counter[(i, j)]
        bend_bool = edge_count > 1
        if bend_bool:
            edge_bend = edge_bend_dict[(i, j)]
            edge_bend_dict[(i, j)] += 66
        sentiment = g.es[g.get_eid(i, j)]['sentiment_value']
        edge_color = sentiment_dict[sentiment]
        edge_bend_style = f',bend={edge_bend}' if bend_bool else ''
        edge_style = f'[color={edge_color}{edge_direct}{edge_bend_style}]'
        tikz_code += f'\t\\Edge{edge_style}({i})({j})\n'
    tikz_code += '\\end{tikzpicture}'
    return tikz_code

def graphs_to_tikz(graphs: list,
                   layout_algo: str = 'kamada_kawai',
                   scaling: float = 1,
                   support: bool = True,
                   twitter: bool = False,
                   n_cols: int = 5,
                   tabcolsep: int = 9,
                   row_spacing: float = 0.9) -> str:
    tikz_code = f'\setlength{{\\tabcolsep}}{{{tabcolsep}pt}}\n'
    tikz_code += '\\begin{tabular}{'
    for _ in range(n_cols):
        tikz_code += 'c'
    tikz_code += '}\n'
    for i in range(0, len(graphs), n_cols):
        for j in range(n_cols):
            if i + j >= len(graphs):
                break
            g = graphs[i + j]
            if layout_algo == 'kamada_kawai':
                layout = g.layout_kamada_kawai()
            elif layout_algo == 'graphopt':
                layout = g.layout_graphopt()
            elif layout_algo == 'fruchterman_reingold':
                layout = g.layout_fruchterman_reingold()
            else:
                raise ValueError('Invalid layout algorithm')
            tikz_code += '\\makecell{'
            tikz_code += graph_to_tikz(g, layout, scaling) + '\n'
            if support and twitter:
                tikz_code += f"\\\\${g['support']} \\hspace{{4pt}} | \\hspace{{4pt}} \\textcolor{{TwitterBlue}}{{{g['twitter_support']}}}$\n"
            elif support:
                tikz_code += f"\\\\${g['support']}$\n"
            tikz_code += '}\n'
            if j < n_cols - 1:
                tikz_code += '&'
        tikz_code += f'\\\\[{row_spacing}cm]\n'
    tikz_code += '\\end{tabular}'
    return tikz_code

def graphs_to_tikz_hierarchical(graphs: list,
                               layout_algo: str = 'kamada_kawai',
                               scaling: float = 1,
                               max_cols: int = 9,
                               support: bool = True,
                               twitter: bool = False,
                               tabcolsep: int = 9,
                               row_spacing: float = 0.9) -> str:
    graph_sizes = sorted(list(set([g.vcount() for g in graphs])))
    graphs = [[g for g in graphs if g.vcount() == size] for size in graph_sizes]
    tikz_code = f'\setlength{{\\tabcolsep}}{{{tabcolsep}pt}}\n'
    max_cols = min(max_cols, max([len(subgraphs) for subgraphs in graphs]))
    tikz_code += '\\begin{tabular}{c' + 'c' * max_cols + '}\n'
    for i in range(len(graph_sizes)):
        subgraphs = graphs[i]
        if twitter:
            subgraphs = sorted(subgraphs, key=lambda x: (-x['support'], -x['twitter_support']))
        else:
            subgraphs = sorted(subgraphs, key=lambda x: (-x['support']))
        size = graph_sizes[i]
        tikz_code += f'$|V| = {size}$'
        for j, g in enumerate(subgraphs):
            if layout_algo == 'kamada_kawai':
                layout = g.layout_kamada_kawai()
            elif layout_algo == 'graphopt':
                layout = g.layout_graphopt()
            elif layout_algo == 'fruchterman_reingold':
                layout = g.layout_fruchterman_reingold()
            else:
                raise ValueError('Invalid layout algorithm')
            if j % max_cols == 0 and j > 0:
                tikz_code += '&'
            tikz_code += '&\\makecell{'
            tikz_code += graph_to_tikz(g, layout, scaling) + '\n'
            if support and twitter:
                tikz_code += f"\\\\${g['support']} \\hspace{{4pt}} | \\hspace{{4pt}} \\textcolor{{TwitterBlue}}{{{g['twitter_support']}}}$\n"
            elif support:
                tikz_code += f"\\\\${g['support']}$\n"
            tikz_code += '}\n'
        tikz_code += f'\\\\[{row_spacing}cm]\n'
    tikz_code += '\\end{tabular}'
    return tikz_code

def graphs_to_tikz_minipage(graphs: list, 
                   layout_algo: str = 'kamada_kawai', 
                   scaling: float = 1, 
                   support: bool = True, 
                   twitter: bool = False,
                   minipage_width: float = 0.15,
                   horizontal_space: float = 0.05) -> str:
    tikz_code = ''
    for g in graphs:
        if layout_algo == 'kamada_kawai':
            layout = g.layout_kamada_kawai()
        elif layout_algo == 'graphopt':
            layout = g.layout_graphopt()
        elif layout_algo == 'fruchterman_reingold':
            layout = g.layout_fruchterman_reingold()
        else:
            raise ValueError('Invalid layout algorithm')
        
        tikz_code += f"\\begin{{minipage}}{{{minipage_width}\\textwidth}}\\begin{{center}}\n"    
        tikz_code += graph_to_tikz(g, layout, scaling) + '\n'
        if support and twitter:
            tikz_code += f"\\\\${g['support']} \\hspace{{4pt}} | \\hspace{{4pt}} \\textcolor{{TwitterBlue}}{{{g['twitter_support']}}}$\n"
        elif support:
            tikz_code += f"\\\\${g['support']}$\n"
        tikz_code += "\\end{center}\n"
        tikz_code += "\\end{minipage}\n"
        tikz_code += f"\\hspace{{{horizontal_space}\\textwidth}}\n"
    return tikz_code

if __name__ == '__main__':
    from sys import argv

    if len(argv) < 2:
        print(f"Usage: {argv[0]} <nel or gspan file> [min support] [layout algo] [twitter support]")
        exit(1)
    filepath = argv[1]

    min_support = None
    if len(argv) > 2:
        min_support = int(argv[2])

    layout = 'kamada_kawai'
    if len(argv) > 3:
        layout = argv[3]
        
    twitter = False
    if len(argv) > 4:
        twitter = bool(argv[4])

    if '.json' in filepath:
        data = json.load(open(f'../data/fsm/subgraph_data/{filepath}', 'r'))
        directed = 'directed' in filepath
        graphs = json_to_igraph(data, directed=directed)
    elif '.gspan' in filepath or '.nel' in filepath:
        with open(f'../data/fsm/subgraphs/{filepath}', 'r') as f:
            content = f.read()
        if '.gspan' in filepath:
            graphs = gspan_to_igraph(content)
        elif '.nel' in filepath:
            graphs = nel_to_igraph(content)
    else:
        print("File format not supported")
        exit(1)

    graphs = sorted(graphs, key=lambda x: (-x['support'], x.vcount()))
    graphs = [g for g in graphs if g.vcount() > 1]
    graphs = [g for g in graphs if min_support is None or g['support'] >= min_support]
    #tikz = graphs_to_tikz(graphs, layout_algo=layout, support=True, scaling=0.5, n_cols=7, twitter=twitter)
    tikz = graphs_to_tikz_hierarchical(graphs, layout_algo=layout, support=True, scaling=0.5, row_spacing=0.9, max_cols=9, twitter=twitter)
    print(tikz)