from utils.fsm_utils import gspan_to_igraph, nel_to_igraph
import igraph as ig

def graph_to_tikz(g: ig.Graph, layout, scaling: float = 1) -> str:
    is_directed = g.is_directed()
    edge_direct = ',Direct' if is_directed else ''
    max_coord = max([abs(x) for coor in layout for x in coor])
    
    sentiment_dict = {0: 'gray', 1: 'green', 2: 'red', 3: 'blue'}

    tikz_code = '\\begin{tikzpicture}\n'
    for i, (x, y) in enumerate(layout):
        x = x * scaling / max_coord
        y = y * scaling / max_coord
        tikz_code += f'\t\\Vertex[x={x:.2f}, y={y:.2f}]{{{i}}}\n'

    for i, j in g.get_edgelist():
        sentiment = g.es[g.get_eid(i, j)]['sentiment_value']
        edge_color = sentiment_dict[sentiment]
        edge_style = f'[color={edge_color}{edge_direct}]'
        tikz_code += f'\t\\Edge{edge_style}({i})({j})\n'
    tikz_code += '\\end{tikzpicture}'
    return tikz_code

def graphs_to_tikz(graphs: list, 
                   layout_algo: str = 'kamada_kawai', 
                   scaling: float = 1, 
                   support: bool = True, 
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
        if support:
            tikz_code += f"\\\\ $s$: {g['support']}\n"
        tikz_code += "\\end{center}\n"
        tikz_code += "\\end{minipage}\n"
        tikz_code += f"\\hspace{{{horizontal_space}\\textwidth}}\n"
    return tikz_code

if __name__ == '__main__':
    from sys import argv

    if len(argv) < 2:
        print(f"Usage: {argv[0]} <nel or gspan file> [min support] [layout algo]")
        exit(1)
    filepath = argv[1]

    min_support = None
    if len(argv) > 2:
        min_support = int(argv[2])

    layout = 'kamada_kawai'
    if len(argv) > 3:
        layout = argv[3]

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
    graphs = [g for g in graphs if g.vcount() > 0]
    graphs = [g for g in graphs if min_support is None or g['support'] >= min_support]
    tikz = graphs_to_tikz(graphs, layout_algo=layout, support=True)
    print(tikz)