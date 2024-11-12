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

    conf_random_graphs = [
        ig.Graph.Degree_Sequence(
            graph.degree(loops=False)
        ).as_undirected().simplify() 
        for graph in graphs]
    
    er_random_graphs = [
        ig.Graph.Erdos_Renyi(n=graph.vcount(), m=graph.ecount()).simplify() 
        for graph in graphs]
    
    ba_random_graphs = [
        ig.Graph.Barabasi(n=graph.vcount(), m=graph.ecount()).simplify() 
        for graph in graphs]
    
    motif_counts = [0] * len(motifs)
    for i, motif in enumerate(motifs):
        for j, graph in enumerate(ba_random_graphs):
            if graph.subisomorphic_vf2(motif):
                motif_counts[i] += 1
        # if (1 - (motif_counts[i] / motif['support'])) * 100 >= 33:
        print(f'Motif {i} found in {motif_counts[i]} random graphs and {motif["support"]} original graphs')
