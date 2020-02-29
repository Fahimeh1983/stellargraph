import os

import pandas as pd
import networkx as nx

from stellargraph.data.explorer import BiasedRandomWalk, BiasedDirectedRandomWalk
from stellargraph.core.graph import StellarDiGraph, StellarGraph

#############################################################
################### Initialization ##########################
#############################################################

# Normalize the edge weights
# change the node choice from naive to numpy


tmp_edge = pd.read_csv("edges.csv", index_col="Unnamed: 0")
tmp_edge['source'] = tmp_edge['source'].astype(str)
tmp_edge['target'] = tmp_edge['target'].astype(str)
g = nx.DiGraph()
g.add_weighted_edges_from([tuple(x) for x in tmp_edge.values])
print(g.number_of_edges())
print(g.number_of_nodes())

sdg = StellarDiGraph(g)
rw = BiasedDirectedRandomWalk(sdg)
walks = rw.run(nodes=sdg.nodes(), length=10, n=1, p=1,q=1, weighted=True, directed=True)
print(sdg.nodes())
print(sdg)
