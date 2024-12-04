from utils.fsm_utils import gspan_to_igraph, nel_to_igraph
import networkx as nx

def graph_to_tikz(g, pos, support=None, minipage_width=0.23, horizontal_space=0.02):
    # Start with minipage
    tikz_code = f"\\begin{{minipage}}{{{minipage_width}\\textwidth}}\\begin{{center}}\n"
    tikz_code += "\\begin{tikzpicture}\n"

    # Add nodes
    for node, (x, y) in pos.items():
        tikz_code += f"    \\Vertex[x={x:.2f}, y={y:.2f}]{{{node}}}\n"

    # Add edges
    edge = '\\Edge[Direct]' if g.is_directed() else '\\Edge'
    for u, v in g.edges():
        tikz_code += f"    {edge}({u})({v})\n"

    tikz_code += "\\end{tikzpicture}\n"

    # Add support number on a separate line below the graph
    if support:
        tikz_code += f"\\\\ $s$: {support}\\end{{center}}\n"
    else:
        tikz_code += "\\end{center}\n"

    # Close the minipage
    tikz_code += "\\end{minipage}\n"

    # Add horizontal space between minipages
    tikz_code += f"\\hspace{{{horizontal_space}\\textwidth}}"

    return tikz_code

if __name__ == '__main__':
    from sys import argv

    if len(argv) < 2:
        print(f"Usage: {argv[0]} <nel or gspan file>")
        exit(1)
    filepath = argv[1]

    min_support = None
    if len(argv) > 2:
        min_support = int(argv[2])

    layout = 'kamada_kawai'
    if len(argv) > 3:
        layout = argv[3]

    with open(f'../data/{filepath}', 'r') as f:
        content = f.read()

    if '.gspan' in filepath:
        graphs = gspan_to_igraph(content)
    elif '.nel' in filepath:
        graphs = nel_to_igraph(content)
    else:
        print("File format not supported")
        exit(1)

    graphs = sorted(graphs, key=lambda x: (-x['support'], x.vcount()))
    for g in graphs:
        support = g['support']
        if min_support is not None and support < min_support:
            continue
        g_nx = g.to_networkx()
        
        if layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(nx.to_undirected(g_nx), scale=0.5)
        elif layout == 'planar':
            pos = nx.planar_layout(g_nx)
            
        print(graph_to_tikz(g_nx, pos, support=support, minipage_width=0.15))
    