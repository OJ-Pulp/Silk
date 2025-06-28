import numpy as np
from typing import List, Tuple

class Network:
    def __init__(self, size: int, growth: int = 50):
        self.index = 0
        self.size = size
        self.growth = growth
        self.node_weights = np.zeros(size, dtype=np.float32)
        self.edge_weights = np.zeros((size, size), dtype=np.float32)

    def add_node(self, weight: float = 1.0) -> int:
        """Add a node to the network and returns the index of the node."""
        if self.index >= self.size:
            self._resize(self.size + self.growth)
        index = self.index
        self.node_weights[index] = weight
        self.index += 1
        return index
    
    def add_edge(self, from_node: int, to_node: int, weight: float):
        """Add an edge to the network and returns the index of the edge."""
        self.edge_weights[from_node][to_node] = weight
    
    def delete_node(self, node_index: int):
        """Delete a node from the network by shifting up/left and zeroing the last row/col."""
        if node_index < 0 or node_index >= self.index:
            raise IndexError("Node index out of range.")

        # Get number of nodes
        n = self.index
        
        # If it is not the last node, shift node_weights
        if node_index < n - 1:
            self.node_weights[node_index:-1] = self.node_weights[node_index + 1:]
        self.node_weights[-1] = 0

        # If it is not the last node, shift edge_weights rows up and shift edge_weights columns left
        if node_index < n - 1:
            self.edge_weights[node_index:-1, :] = self.edge_weights[node_index + 1:, :]
        self.edge_weights[-1, :] = 0

        if node_index < n - 1:
            self.edge_weights[:, node_index:-1] = self.edge_weights[:, node_index + 1:]
        self.edge_weights[:, -1] = 0

        self.index -= 1

    def delete_edge(self, from_node: int, to_node: int):
        """Delete an edge from the network."""
        if from_node < 0 or from_node >= self.size or to_node < 0 or to_node >= self.size:
            raise IndexError("Node index out of range.")
        self.edge_weights[from_node][to_node] = 0.0
    
    def filtered_subgraph(self, node_indices: List[int], edge_indices: List[Tuple[int]]):
        """Returns a subgraph as an adjacency matrix based on the provided node and edge indices."""
        subgraph_size = len(node_indices)
        subgraph = np.zeros((subgraph_size, subgraph_size), dtype=np.float32)

        for i, from_node in enumerate(node_indices):
            for j, to_node in enumerate(node_indices):
                if (from_node, to_node) in edge_indices:
                    subgraph[i][j] = self.edge_weights[from_node][to_node]

        edges_matrix = subgraph
        node_weights = self.node_weights[node_indices]
        return edges_matrix, node_weights
    
    def weight_network(self, node_weights: np.ndarray, edge_weights: np.ndarray):
        """Set the weights of the network."""
        if len(node_weights) != self.size:
            raise ValueError("Node weights size does not match network size.")
        if edge_weights.shape != (self.size, self.size):
            raise ValueError("Edge weights shape does not match network size.")
        
        self.node_weights = node_weights
        self.edge_weights = edge_weights
    
    def unweight_network(self):
        """Reset the weights of the network to zero if zero and 1 if not zero."""
        self.node_weights = np.where(self.node_weights == 0, 0, 1)
        self.edge_weights = np.where(self.edge_weights == 0, 0, 1)

    def _resize(self, new_size: int):
        """Resize the network to a new size."""
        new_node_weights = np.zeros(new_size, dtype=np.float32)
        new_edge_weights = np.zeros((new_size, new_size), dtype=np.float32)
        new_node_weights[:self.size] = self.node_weights
        new_edge_weights[:self.size, :self.size] = self.edge_weights
        self.node_weights = new_node_weights
        self.edge_weights = new_edge_weights
        self.size = new_size