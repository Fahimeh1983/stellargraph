import os

import pandas as pd
import networkx as nx

from stellargraph.data.explorer import BiasedRandomWalk, BiasedDirectedRandomWalk, layer_node_importance
from stellargraph.core.graph import StellarDiGraph, StellarGraph

#############################################################
################### Initialization ##########################
#############################################################

# Normalize the edge weights
# change the node choice from naive to numpy
# Should we put the importance of the nodes with 0 outgoing edges to epsilon?

parrent_dir = "~/Documents/git-workspace/stellargraph/stellargraph/data/edges/VISp"

nx_G = {}
sd_G = {}
ln_imp = {}

for layer in ["Adcyap1-Adcyap1r1", "Adcyap1-Vipr1"]:
    file_name = os.path.join(parrent_dir, layer, "edges.csv")
    tmp_edge = pd.read_csv(file_name, index_col="Unnamed: 0")
    tmp_edge['source'] = tmp_edge['source'].astype(str)
    tmp_edge['target'] = tmp_edge['target'].astype(str)
    g = nx.DiGraph()
    g.add_weighted_edges_from([tuple(x) for x in tmp_edge.values])
    print(g.number_of_edges())
    print(g.number_of_nodes())
    nx_G[layer] = g

    #Convert them into stellarDigraphs
    sdg = StellarDiGraph(g)
    sd_G[layer] = sdg
    imp = layer_node_importance(sdg)
    ln_imp[layer] = imp.run()
    print("Done")

rw = BiasedDirectedRandomWalk(sdg)
walks = rw.run(nodes=sdg.nodes(), length=10, n=1, p=1,q=1, weighted=True, directed=True)
print(sdg.nodes())
print(sdg)
