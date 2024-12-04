import os
from igraph import Graph, plot
import matplotlib.pyplot as plt

def parse_gspan_output(filepath):
    graphs = []
    current_graph = None

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('t '):
                if current_graph is not None:
                    graphs.append(current_graph)

                # Start a new graph
                parts = line.split()
                graph_id = int(parts[2])

                # Extract support value if available
                support = None
                if '*' in line:
                    # Line format: 't # <id> * <support>'
                    support_index = parts.index('*') + 1
                    if support_index < len(parts):
                        support = int(parts[support_index])
                    else:
                        support = 0  # Default support if not specified
                else:
                    support = 0  # Default support if not specified

                current_graph = {
                    'id': graph_id,
                    'vertices': [],
                    'edges': [],
                    'support': support
                }
            elif line.startswith('v '):
                # Vertex line: 'v <id> <label>'
                parts = line.split()
                vertex_id = int(parts[1])
                label = parts[2]  # Label is optional; modify if necessary
                current_graph['vertices'].append(vertex_id)
            elif line.startswith('e '):
                # Edge line: 'e <from> <to> <label>'
                parts = line.split()
                from_vertex = int(parts[1])
                to_vertex = int(parts[2])
                label = parts[3]  # Label is optional; modify if necessary
                current_graph['edges'].append((from_vertex, to_vertex))
            else:
                pass

        if current_graph is not None:
            graphs.append(current_graph)

    return graphs

def visualize_graphs(graphs):
    output_dir = "../data/motifs/test"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    else:
        print(f"Output directory already exists: {output_dir}")
    
    for i, graph_data in enumerate(graphs):
        if len(graph_data['vertices']) == 0:
            print(f"Graph {i} is empty, skipping visualization.")
            continue

        g = Graph()
        g.add_vertices(len(graph_data['vertices']))
        g.add_edges(graph_data['edges'])

        layout = g.layout_graphopt(niter=2)

        support = graph_data.get('support', 0)

        print(f"Saving Graph {i} with support {support} to file.")

        output_path = os.path.join(output_dir, f"motif_{i}_support_{support}.jpg")

        fig, ax = plt.subplots(figsize=(8, 6))

        plot(
            g,
            layout=layout,
            target=ax,
            backend='matplotlib',
            margin=50
        )

        ax.set_title(f"Motif {i} (Support: {support})")

        fig.savefig(output_path, format='jpg', bbox_inches='tight')
        plt.close(fig) 

    print("All graphs have been saved.")

input_filepath = "../data/bitch.fp"
graphs = parse_gspan_output(input_filepath)

if not graphs:
    print("No graphs found in the input file.")
else:
    visualize_graphs(graphs)
