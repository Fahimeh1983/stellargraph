# -*- coding: utf-8 -*-
#
# Copyright 2019-2020 Data61, CSIRO
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
`stellargraph.datasets` contains classes to download sample network datasets.

The default download path of ``stellargraph-datasets`` within the user's home directory can be changed by setting the
``STELLARGRAPH_DATASETS_PATH`` environment variable, and each dataset will be downloaded to a subdirectory within this path.
"""

from .dataset_loader import DatasetLoader
from ..core.graph import StellarGraph, StellarDiGraph
import logging
import os
import pandas as pd
import numpy as np
from sklearn import preprocessing


log = logging.getLogger(__name__)


class Cora(
    DatasetLoader,
    name="Cora",
    directory_name="cora",
    url="https://linqs-data.soe.ucsc.edu/public/lbc/cora.tgz",
    url_archive_format="gztar",
    expected_files=["cora.cites", "cora.content"],
    description="The Cora dataset consists of 2708 scientific publications classified into one of seven classes. "
    "The citation network consists of 5429 links. Each publication in the dataset is described by a 0/1-valued word vector "
    "indicating the absence/presence of the corresponding word from the dictionary. The dictionary consists of 1433 unique words.",
    source="https://linqs.soe.ucsc.edu/data",
):
    def load(self, directed=False, largest_connected_component_only=False):
        """
        Load this dataset into a homogeneous graph that is directed or undirected, downloading it if
        required.

        The node feature vectors are included, and the edges are treated as directed or undirected
        depending on the ``directed`` parameter.

        Args:
            directed (bool): if True, return a directed graph, otherwise return an undirected one.
            largest_connected_component_only (bool): if True, returns only the largest connected
                component, not the whole graph.

        Returns:
            A tuple where the first element is the :class:`StellarGraph` object (or
            :class:`StellarDiGraph`, if ``directed == True``) with the nodes, node feature vectors
            and edges, and the second element is a pandas Series of the node subject class labels.
        """
        self.download()
        edgelist = pd.read_csv(
            self._resolve_path("cora.cites"),
            sep="\t",
            header=None,
            names=["target", "source"],
        )

        feature_names = ["w_{}".format(ii) for ii in range(1433)]
        subject = "subject"
        column_names = feature_names + [subject]
        node_data = pd.read_csv(
            self._resolve_path("cora.content"),
            sep="\t",
            header=None,
            names=column_names,
        )

        cls = StellarDiGraph if directed else StellarGraph
        graph = cls({"paper": node_data[feature_names]}, {"cites": edgelist})

        if largest_connected_component_only:
            cc_ids = next(graph.connected_components())
            return graph.subgraph(cc_ids), node_data[subject][cc_ids]

        return graph, node_data[subject]


class CiteSeer(
    DatasetLoader,
    name="CiteSeer",
    directory_name="citeseer",
    url="https://linqs-data.soe.ucsc.edu/public/lbc/citeseer.tgz",
    url_archive_format="gztar",
    expected_files=["citeseer.cites", "citeseer.content"],
    description="The CiteSeer dataset consists of 3312 scientific publications classified into one of six classes. "
    "The citation network consists of 4732 links. Each publication in the dataset is described by a 0/1-valued word vector "
    "indicating the absence/presence of the corresponding word from the dictionary. The dictionary consists of 3703 unique words.",
    source="https://linqs.soe.ucsc.edu/data",
):
    pass


class PubMedDiabetes(
    DatasetLoader,
    name="PubMed Diabetes",
    directory_name="Pubmed-Diabetes",
    url="https://linqs-data.soe.ucsc.edu/public/Pubmed-Diabetes.tgz",
    url_archive_format="gztar",
    expected_files=[
        "data/Pubmed-Diabetes.DIRECTED.cites.tab",
        "data/Pubmed-Diabetes.GRAPH.pubmed.tab",
        "data/Pubmed-Diabetes.NODE.paper.tab",
    ],
    description="The PubMed Diabetes dataset consists of 19717 scientific publications from PubMed database "
    "pertaining to diabetes classified into one of three classes. The citation network consists of 44338 links. "
    "Each publication in the dataset is described by a TF/IDF weighted word vector from a dictionary which consists of 500 unique words.",
    source="https://linqs.soe.ucsc.edu/data",
    data_subdirectory_name="data",
):
    pass


class BlogCatalog3(
    DatasetLoader,
    name="BlogCatalog3",
    directory_name="BlogCatalog-dataset",
    url="http://socialcomputing.asu.edu/uploads/1283153973/BlogCatalog-dataset.zip",
    url_archive_format="zip",
    expected_files=[
        "data/edges.csv",
        "data/group-edges.csv",
        "data/groups.csv",
        "data/nodes.csv",
    ],
    description="This dataset is crawled from a social blog directory website BlogCatalog "
    "http://www.blogcatalog.com and contains the friendship network crawled and group memberships.",
    source="http://socialcomputing.asu.edu/datasets/BlogCatalog3",
    data_subdirectory_name="data",
):
    def load(self):
        """
        Load this dataset into an undirected heterogeneous graph, downloading it if required.

        The graph has two types of nodes, 'user' and 'group', and two types of edges, 'friend' and 'belongs'.
        The 'friend' edges connect two 'user' nodes and the 'belongs' edges connects 'user' and 'group' nodes.

        The node and edge types are not included in the dataset that is a collection of node and group ids along with
        the list of edges in the graph.

        Important note about the node IDs: The dataset uses integers for node ids. However, the integers from 1 to 39 are
        used as IDs for both users and groups. This would cause a confusion when constructing the graph object.
        As a result, we convert all IDs to string and append the character 'u' to the integer ID for user nodes and the
        character 'g' to the integer ID for group nodes.

        Returns:
            A :class:`StellarGraph` object.
        """
        self.download()

        # load the raw data
        edges, group_edges, groups, nodes = [
            self._resolve_path(name) for name in self.expected_files
        ]

        user_node_ids = pd.read_csv(nodes, header=None)
        group_ids = pd.read_csv(groups, header=None)
        edges = pd.read_csv(edges, header=None, names=["source", "target"])
        group_edges = pd.read_csv(group_edges, header=None, names=["source", "target"])

        # The dataset uses integers for node ids. However, the integers from 1 to 39 are used as IDs
        # for both users and groups. This is disambiguated by converting everything to strings and
        # prepending u to user IDs, and g to group IDs.
        def u(users):
            return "u" + users.astype(str)

        def g(groups):
            return "g" + groups.astype(str)

        # nodes:
        user_node_ids = u(user_node_ids)
        group_ids = g(group_ids)

        # node IDs in each edge:
        edges = u(edges)
        group_edges["source"] = u(group_edges["source"])
        group_edges["target"] = g(group_edges["target"])

        # arrange the DataFrame indices appropriately: nodes use their node IDs, which have
        # been made distinct above, and the group edges have IDs after the other edges
        user_node_ids.set_index(0, inplace=True)
        group_ids.set_index(0, inplace=True)

        start = len(edges)
        group_edges.index = range(start, start + len(group_edges))

        return StellarGraph(
            nodes={"user": user_node_ids, "group": group_ids},
            edges={"friend": edges, "belongs": group_edges},
        )


class MovieLens(
    DatasetLoader,
    name="MovieLens",
    directory_name="ml-100k",
    url="http://files.grouplens.org/datasets/movielens/ml-100k.zip",
    url_archive_format="zip",
    expected_files=["u.data", "u.user", "u.item", "u.genre", "u.occupation"],
    description="The MovieLens 100K dataset contains 100,000 ratings from 943 users on 1682 movies.",
    source="https://grouplens.org/datasets/movielens/100k/",
):
    def load(self):
        """
        Load this dataset into an undirected heterogeneous graph, downloading it if required.

        The graph has two types of nodes (``user`` and ``movie``) and one type of edge (``rating``).

        The dataset includes some node features on both users and movies: on users, they consist of
        categorical features (``gender`` and ``job``) which are one-hot encoded into binary
        features, and an ``age`` feature that is scaled to have mean = 0 and standard deviation = 1.

        Returns:
            A tuple where the first element is a :class:`StellarGraph` instance containing the graph
            data and features, and the second element is a pandas DataFrame of edges, with columns
            ``user_id``, ``movie_id`` and ``rating`` (a label from 1 to 5).
        """
        self.download()

        ratings, users, movies, *_ = [
            self._resolve_path(path) for path in self.expected_files
        ]

        edges = pd.read_csv(
            ratings,
            sep="\t",
            header=None,
            names=["user_id", "movie_id", "rating", "timestamp"],
            usecols=["user_id", "movie_id", "rating"],
        )

        users = pd.read_csv(
            users,
            sep="|",
            header=None,
            names=["user_id", "age", "gender", "job", "zipcode"],
            usecols=["user_id", "age", "gender", "job"],
        )

        movie_columns = [
            "movie_id",
            "title",
            "release_date",
            "video_release_date",
            "imdb_url",
            # features from here:
            "unknown",
            "action",
            "adventure",
            "animation",
            "childrens",
            "comedy",
            "crime",
            "documentary",
            "drama",
            "fantasy",
            "film_noir",
            "horror",
            "musical",
            "mystery",
            "romance",
            "sci_fi",
            "thriller",
            "war",
            "western",
        ]
        movies = pd.read_csv(
            movies,
            sep="|",
            header=None,
            names=movie_columns,
            usecols=["movie_id"] + movie_columns[5:],
        )

        # manage the IDs
        def u(users):
            return "u_" + users.astype(str)

        def m(movies):
            return "m_" + movies.astype(str)

        users_ids = u(users["user_id"])

        movies["movie_id"] = m(movies["movie_id"])
        movies.set_index("movie_id", inplace=True)

        edges["user_id"] = u(edges["user_id"])
        edges["movie_id"] = m(edges["movie_id"])

        # convert categorical user features to numeric, and normalize age
        feature_encoding = preprocessing.OneHotEncoder(sparse=False)
        onehot = feature_encoding.fit_transform(users[["gender", "job"]])
        scaled_age = preprocessing.scale(users["age"])
        encoded_users = pd.DataFrame(onehot, index=users_ids).assign(
            scaled_age=scaled_age
        )

        g = StellarGraph(
            {"user": encoded_users, "movie": movies},
            {"rating": edges[["user_id", "movie_id"]]},
            source_column="user_id",
            target_column="movie_id",
        )
        return g, edges


class AIFB(
    DatasetLoader,
    name="AIFB",
    directory_name="aifb",
    url="https://ndownloader.figshare.com/files/1118822",
    url_archive_format=None,
    expected_files=["aifbfixed_complete.n3"],
    description="The AIFB dataset describes the AIFB research institute in terms of its staff, research group, and publications. "
    'First used for machine learning with RDF in Bloehdorn, Stephan and Sure, York, "Kernel Methods for Mining Instance Data in Ontologies", '
    "The Semantic Web (2008), http://dx.doi.org/10.1007/978-3-540-76298-0_5. "
    "It contains ~8k entities, ~29k edges, and 45 different relationships or edge types. In (Bloehdorn et al 2007) the dataset "
    "was first used to predict the affiliation (i.e., research group) for people in the dataset. The dataset contains 178 "
    "members of a research group with 5 different research groups. The goal is to predict which research group a researcher belongs to.",
    source="https://figshare.com/articles/AIFB_DataSet/745364",
):
    pass


class MUTAG(
    DatasetLoader,
    name="MUTAG",
    directory_name="MUTAG",
    url="https://ls11-www.cs.tu-dortmund.de/people/morris/graphkerneldatasets/MUTAG.zip",
    url_archive_format="zip",
    expected_files=[
        "MUTAG_A.txt",
        "MUTAG_graph_indicator.txt",
        "MUTAG_node_labels.txt",
        "MUTAG_edge_labels.txt",
        "MUTAG_graph_labels.txt",
        "README.txt",
    ],
    description="Each graph represents a chemical compound and graph labels represent 'their mutagenic effect on a specific gram negative bacterium.'"
    "The dataset includes 188 graphs with 18 nodes and 20 edges on average for each graph. Graph nodes have 7 labels and each graph is labelled as belonging to 1 of 2 classes.",
    source="https://ls11-www.cs.tu-dortmund.de/staff/morris/graphkerneldatasets",
):
    def _load_from_txt_file(
        self, filename, names=None, dtype=None, index_increment=None
    ):
        df = pd.read_csv(
            self._resolve_path(filename=filename),
            header=None,
            index_col=False,
            dtype=dtype,
            names=names,
        )
        # We optional increment the index by 1 because indexing, e.g. node IDs, for this dataset starts
        # at 1 whereas the Pandas DataFrame implicit index starts at 0 potentially causing confusion selecting
        # rows later on.
        if index_increment:
            df.index = df.index + index_increment
        return df

    def load(self):
        """
        Load this dataset into a list of StellarGraph objects with corresponding labels, downloading it if required.

        Note: Edges in MUTAG are labelled as one of 4 values: aromatic, single, double, and triple indicated by integers
        0, 1, 2, 3 respectively. The edge labels are included in the  :class:`StellarGraph` objects as edge weights in
        integer representation.

        Returns:
            A tuple that is a list of :class:`StellarGraph` objects and a Pandas Series of labels one for each graph.
        """
        self.download()

        df_graph = self._load_from_txt_file(
            filename="MUTAG_A.txt", names=["source", "target"]
        )
        df_edge_labels = self._load_from_txt_file(
            filename="MUTAG_edge_labels.txt", names=["weight"], dtype=int
        )
        df_graph = pd.concat([df_graph, df_edge_labels], axis=1)  # add edge weights
        df_graph_ids = self._load_from_txt_file(
            filename="MUTAG_graph_indicator.txt", names=["graph_id"], index_increment=1
        )
        df_graph_labels = self._load_from_txt_file(
            filename="MUTAG_graph_labels.txt",
            dtype="category",
            names=["label"],
            index_increment=1,
        )  # binary labels {-1, 1}
        df_node_labels = self._load_from_txt_file(
            filename="MUTAG_node_labels.txt", dtype="category", index_increment=1
        )

        # Let us one-hot encode the node labels because these are used as node features
        # in graph classification tasks.
        df_node_labels = pd.get_dummies(df_node_labels)

        graphs = []
        for graph_id in np.unique(df_graph_ids):
            # find the subgraph with nodes that correspond to graph_id
            node_ids = list(
                df_graph_ids.loc[df_graph_ids["graph_id"] == graph_id].index
            )

            df_subgraph = df_graph[df_graph["source"].isin(node_ids)]
            # nodes should be DataFrame with node features; DataFrame index indicates node IDs
            # edges should be DataFrame of edges, 2 columns "source" and "target"
            graph = StellarGraph(nodes=df_node_labels.loc[node_ids], edges=df_subgraph)
            graphs.append(graph)

        return graphs, df_graph_labels["label"]
