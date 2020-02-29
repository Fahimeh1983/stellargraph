import os

import pandas as pd
import networkx as nx

from stellargraph.data.explorer import BiasedRandomWalk, BiasedDirectedRandomWalk
from stellargraph.core.graph import StellarDiGraph, StellarGraph

#############################################################
################### Initialization ##########################
#############################################################

graph_dir = "/home/pogo/work_dir/NPP-GNN-project/dat/graphs/"
w_dir = "/home/pogo/work_dir/NPP-GNN-project/dat/Interaction_mats/VISp/Adcyap1-Adcyap1r1.csv"
region = "VISp"


w_mat = pd.read_csv(w_dir, index_col="Unnamed: 0")
edge_dir = os.path.join(graph_dir, region, 'Adcyap1-Adcyap1r1', "edges.csv")
tmp_edge = pd.read_csv(edge_dir, index_col="Unnamed: 0")
tmp_edge['source'] = tmp_edge['source'].astype(str)
tmp_edge['target'] = tmp_edge['target'].astype(str)
g = nx.DiGraph()
g.add_weighted_edges_from([tuple(x) for x in tmp_edge.values])
print(g.number_of_edges())
print(g.number_of_nodes())

sdg = StellarDiGraph(g)
rw = BiasedDirectedRandomWalk(sdg)
walks = rw.run(nodes=sdg.nodes(), length=5, n=1, p=1,q=1, weighted=True, directed=True)
print(sdg.nodes())
print(sdg)
