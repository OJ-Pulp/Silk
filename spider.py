"""
SPIDER.PY

This file is the main interface that is used for interacting with the Silk framework.
It includes wrapper function for the Hybrid SQL Graph Database (WebDB) and provides
tool functions for answering network questions.
"""

from config import DEFAULT_PATH, SCHEMA_FILE, join_paths
from Web.db import WebDB
from Web.webmath import markov_chain, max_profit_route, mcl, mcc
import numpy as np
from typing import Dict

class Spider:
    def __init__(self, db_name: str, db_path: str = None):
        # Initialize the WebDB with the provided paths.
        if db_path is None:
            self.web = self.load_web(join_paths(DEFAULT_PATH, db_name))
        else:
            self.web = self.load_web(join_paths(db_path, db_name))

    # TOOL FUNCTIONS
    # NOTE: These are our base tools for answering network questions. 
    #       If we need more complex tools, we can add them later.
    # For the tool functions, I need to use the get node and get edge functions to make sure that the data and not the index
    # are returned.

    def get_web(self, node_filter: str, edge_filter: str):
        """
        Get a subgraph from the web database based on node and edge filters.
        Args:
            node_filter: a dictionary where keys are node attributes and values are the values to filter by.
            edge_filter: a dictionary where keys are edge attributes and values are the values to filter by.
        
        returns:
            edges_matrix: a 2D numpy array representing the edges of the subgraph.
            node_weights: a 1D numpy array representing the weights of the nodes in the subgraph.
            key: a list of original node indexes where the list index corresponds 
                 to the location in the subgraph and the value is the original index.
        """
        edge_matrix, node_vector, index_keys = self.web.get_web(node_filter, edge_filter)
        return edge_matrix, node_vector, index_keys

    def weight_nodes(self, 
                     node_filter: str, 
                     edge_filter: str) -> np.ndarray:
        """Implement a node weighting algorithm (PageRank) and return the weighted node array."""

        # Create a subgraph based on the filters provided.
        edge_matrix, _node_vector, index_keys = self.get_web(node_filter, edge_filter)

        # If the edge matrix or node vector is None, return None.
        if edge_matrix is None or edge_matrix.size == 0:
            return None
        
        # Use the Markov chain algorithm to compute the node weights.      
        node_weights = markov_chain(edge_matrix)

        return list(zip(index_keys, node_weights))


    def weight_edges(self, 
                     node_filter: str, 
                     edge_filter: str) -> np.ndarray:
        """Implement an edge weighting algorithm (betweenness/gravity) and return the weighted edge array."""
        # Create a subgraph based on the filters provided.
        edge_matrix, node_vector, index_keys = self.get_web(node_filter, edge_filter)
        # If the edge matrix or node vector is None, return None.
        if edge_matrix is None or edge_matrix.size == 0:
            return None
        
        # Use the Markov chain algorithm to compute the edge weights.
        edge_weights = mcc(edge_matrix, node_vector)
        # Return the edge weights as a list of tuples ((from_node, to_node), weight).
        return [((index_keys[i], index_keys[j]), edge_weights[i, j])
                for i in range(edge_weights.shape[0])
                for j in range(edge_weights.shape[1])
                if not np.isinf(edge_weights[i, j]) and edge_weights[i, j] != 0]
        

    def cluster(self, 
                node_filter: str, 
                edge_filter: str) -> list:
        """Implement a graph clustering algorithm and return the index of the clusters."""
        # Create a subgraph based on the filters provided.
        edge_matrix, node_vector, index_keys = self.get_web(node_filter, edge_filter)

        # If the edge matrix or node vector is None, return None.
        if edge_matrix is None or edge_matrix.size == 0:
            return None
        
        # Use the Markov chain algorithm to compute the clusters.
        clusters = mcl(edge_matrix)
        # Convert the clusters from the subgraph index to the original index.
        if clusters is None or len(clusters) == 0:
            return None
        return [[index_keys[i] for i in cluster] for cluster in clusters if len(cluster) > 0]


    def traverse(self, 
                  start: int, end: int, 
                  node_filter: str, 
                  edge_filter: str,
                  num_hops: int = None) -> list:
        """Implement a cost-benefit analysis algorithm to find the best path."""
        # Create a subgraph based on the filters provided.
        edge_matrix, node_vector, index_keys = self.get_web(node_filter, edge_filter)

        route = max_profit_route(
            cost_matrix=edge_matrix, 
            reward=node_vector, 
            start=start, 
            end=end,
            K=num_hops
        )
        # Convert the route from the subgraph index to the original index.
        if route is None or len(route) == 0:
            return None
        else:
            return [index_keys[i] for i in route]

    # WRAPPER FUNCTIONS FOR WEBDB
    def add_node(self, **kwargs) -> int:
        """Add a node to the web database and return the index of the node."""
        return self.web.add_node(**kwargs)
    
    def delete_node(self, node_index: int):
        """Delete a node from the web database."""
        self.web.delete_node(node_index)

    def add_edge(self, from_node: int, to_node: int, **kwargs) -> int:
        """Add an edge to the web database and return the index of the edge."""
        return self.web.add_edge(from_node, to_node, **kwargs)
    
    def delete_edge(self, from_node: int, to_node: int):
        """Delete an edge from the web database."""
        self.web.delete_edge(from_node, to_node)
    
    def get_node(self, node_index: list = None) -> np.ndarray:
        """Get nodes from the web database. If no indices are provided, return all nodes."""
        return self.web.get_node(node_index)

    def get_edge(self, from_node: int, to_node: int) -> np.ndarray:
        """Get an edge from the web database."""
        return self.web.get_edge(from_node, to_node)

    def get_schema(self) -> dict:
        """Returns the schema of the web database from the sql schema file."""
        return self.web.get_schema()

    def change_schema(self, new_schema: str):
        """Change the schema of the web database."""
        self.web.change_schema(new_schema)

    def delete_web(self):
        """Delete the web database."""
        self.web.delete_db()
        self.web = None
    
    def change_web(self, web_path: str):
        """Change the current web database to a new one."""
        self.web.close()
        self.load_web(web_path)
    
    def load_web(self, web_path: str):
        """Load a web database by name."""
        return WebDB(web_path, SCHEMA_FILE)