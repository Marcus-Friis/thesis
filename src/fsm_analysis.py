from fsm import gspan_to_igraph
import igraph as ig

if __name__ == '__main__':
    with open('../data/fsm/subgraphs/lcc.gspan.fp') as f:
        gspan = f.read()
    motifs = gspan_to_igraph(gspan)

    with open('../data/fsm/graphs/lcc.gspan') as f:
        gspan = f.read()
    graphs = gspan_to_igraph(gspan)
    graphs = [graph.simplify() for graph in graphs]

    random_graphs = [
        ig.Graph.Degree_Sequence(
            graph.degree(mode='in', loops=False), 
            graph.degree(mode='out', loops=False)
            ).as_undirected().simplify() 
            for graph in graphs]
    
    for i, motif in enumerate(motifs):
        for j, graph in enumerate(graphs):
            if graph.subisomorphic_vf2(motif):
                ...  # to be continued