from fsm import gspan_to_igraph, nel_to_igraph
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
    with open('../data/lcc.gspan.fp', 'r') as f:
        gspan = f.read()

    graphs = gspan_to_igraph(gspan)
    graphs = sorted(graphs, key=lambda x: (-x[1], x[0].vcount()))
    for g, support in graphs:
        if support >= 20:
            g_nx = g.to_networkx()
            pos = nx.kamada_kawai_layout(g_nx, scale=0.5)
            print(graph_to_tikz(g_nx, pos, support=support, minipage_width=0.15))
    