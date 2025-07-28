"""
SPIDER.PY

This file is the main interface that is used for interacting with the Silk framework.
It includes wrapper function for the Hybrid SQL Graph Database (WebDB) and provides
tool functions for answering network questions.
"""

from config import DEFAULT_PATH, SCHEMA_FILE, join_paths
from Web.db import GraphDB
from Web.webmath.math import markov_chain, max_profit_route, mcl, mcc, list_algorithms
import numpy as np
from typing import List


class Spider:
    def __init__(self, db_name: str = None, db_path: str = None):
        self.current_state = {
            "graph": {
                "graph_filter": [],
                "node_filter": {},
                "edge_filter": {},
            },
            "Tools": {
                "Weight Nodes": None,
                "Weight Edges": None,
                "Traverse Graph": None,
                "Cluster Graph": None,
                "Compare Graphs": None,
            },
        }
        if db_path is None:
            self.current_db_path = None
            self.graph = None
        else:
            self.current_db_path = join_paths(db_path, db_name)
            self.graph = GraphDB(self.current_db_path, SCHEMA_FILE)

    # ----------------------------
    # Persistence Methods
    # ----------------------------
    def create_database(self, filepath):
        self.current_db_path = filepath
        self.graph = GraphDB(self.current_db_path, SCHEMA_FILE)

    def change_database(self, filepath):
        self.current_db_path = filepath
        self.graph = GraphDB(self.current_db_path, SCHEMA_FILE)

    def disconnect(self):
        if self.graph is not None:
            self.graph.close()
            self.graph = None
        else:
            print("No active database connection to close.")

    def reconnect(self):
        if self.current_db_path is not None:
            self.graph = GraphDB(self.current_db_path, SCHEMA_FILE)
        else:
            print("No active database connection to reconnect.")

    def is_database(self):
        return self.graph is not None and self.current_db_path is not None

    def check_id(self, id):
        """
        Check if an ID exists in the current database.
        """
        if self.graph is None:
            print("No active database connection.")
            return True
        return self.graph.check_id(id)

    def get_graphs(self):
        """
        Get all graphs in the current database.
        """
        if self.graph is None:
            print("No active database connection.")
            return []
        return self.graph.get_graphs()

    # ----------------------------
    # Entity/Node/Edge Creation
    # ----------------------------
    def create_node(self, graph_ids, node_id, **kwargs):
        self.graph.add_node(graph_ids, node_id, **kwargs)

    def create_edge(self, source, target, **kwargs):
        self.graph.add_edge(source, target, **kwargs)

    def change_node(self, node_id, **kwargs):
        self.graph.edit_node(node_id, **kwargs)

    def change_edge(self, edge_id, **kwargs):
        self.graph.edit_edge(edge_id, **kwargs)

    def delete_node(self, node_id):
        self.graph.delete_node(node_id)

    def delete_edge(self, edge_id):
        self.graph.delete_edge(edge_id)

    def get_node(self, node_id):
        return self.graph.get_node(node_id)

    def get_edge(self, source: str, target: str):
        return self.graph.get_edge(source, target)

    def get_node_entities(self):
        """
        Get all node entities in the current graph.
        """
        return [ent["Name"] for ent in self.graph.get_all_entities("node")]

    def get_edge_entities(self):
        """
        Get all edge entities in the current graph.
        """
        return [ent["Name"] for ent in self.graph.get_all_entities("edge")]

    # ----------------------------
    # Graph Management
    # ----------------------------
    def create_graph(self, id):
        self.graph.add_graph(id)

    def delete_graph(self, id):
        self.graph.delete_graph(id)

    def get_current_graph(self):
        return self.filter_graphs(**self.current_state["graph"])

    def save_current_graph(self, graph_id):
        """
        Save the current graph state to the database.
        """
        _edge_matrix, _node_weights, node_idxs = self.filter_graphs(
            **self.current_state["graph"]
        )
        print(f"Saving current graph as '{graph_id}' with nodes: {node_idxs}")
        self.graph.add_graph(graph_id, node_idxs)

    def filter_graphs(
        self,
        graph_filter: List[str] | None = None,
        node_filter: str | None = None,
        edge_filter: str | None = None,
    ):

        self.current_state["graph"]["graph_filter"] = graph_filter or []
        self.current_state["graph"]["node_filter"] = node_filter or {}
        self.current_state["graph"]["edge_filter"] = edge_filter or {}
        edge_matrix, node_weights, node_idxs = self.graph.create_graph(
            graph_filter=graph_filter, node_filter=node_filter, edge_filter=edge_filter
        )
        return edge_matrix, node_weights, node_idxs

    # ----------------------------
    # Tool Methods (Graph Algorithms)
    # ----------------------------

    def weight_nodes(self, edge_matrix, node_vector, index_keys):
        if edge_matrix is None or edge_matrix.size == 0:
            return None
        weights = markov_chain(edge_matrix)
        return list(zip(index_keys, weights))

    def weight_edges(self, edge_matrix, node_vector, index_keys):
        if edge_matrix is None or edge_matrix.size == 0:
            return None
        edge_weights = mcc(edge_matrix, node_vector)
        return [
            ((index_keys[i], index_keys[j]), edge_weights[i, j])
            for i in range(edge_weights.shape[0])
            for j in range(edge_weights.shape[1])
            if not np.isinf(edge_weights[i, j]) and edge_weights[i, j] != 0
        ]

    def traverse_graph(self, edge_matrix, node_vector, index_keys, **kwargs):
        start = kwargs.get("start")
        end = kwargs.get("end")
        K = kwargs.get("num_hops")
        route = max_profit_route(edge_matrix, node_vector, start, end, K)
        if route is None:
            return None
        return [index_keys[i] for i in route]

    def cluster_graph(self, edge_matrix, index_keys):
        clusters = mcl(edge_matrix)
        if clusters is None or len(clusters) == 0:
            return None
        return [
            [index_keys[i] for i in cluster] for cluster in clusters if len(cluster) > 0
        ]

    def compare_graphs(self, graph1_id, graph2_id):
        return self.graph.compare_graphs(graph1_id, graph2_id)

    def get_all_tools(self):
        # Placeholder; implement dynamic tool discovery if needed
        return list_algorithms()

    def get_current_tools(self):
        return self.current_state["Tools"]
