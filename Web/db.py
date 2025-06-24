import sqlite3
import uuid
import numpy as np
import pickle
import os
from typing import Dict, Any, List, Tuple

class WebDB:
    def __init__(self, db_name: str, schema_path: str, web_size: int = 100, growth: int = 50):
        self.db_path = db_name
        self.schema_path = schema_path
        self.network_path = db_name + '_network.pkl'
        # Initialize the database connection and schema.
        if not os.path.exists(db_name):
            self.connection = sqlite3.connect(db_name)
            self._initialize_db(schema_path)
            self.cursor = self.connection.cursor()
            self.network =  Network(size=web_size, growth=growth)  # Initialize a network with specified size and growth
        else:
            self.connection = sqlite3.connect(db_name)
            self.cursor = self.connection.cursor()
            # Load the existing network from the pickle file
            with open(self.network_path, 'rb') as f:
                self.network = pickle.load(f)

        # Define the filter operations for the web database
        self.filter_ops = {
            "==": "!=",
            "!=": "==",
            ">=": "<",
            "<=": ">",
            ">": "<=",
            "<": ">="
        }
        self.nodes_entities = {col[1]: col[2] for col in self.cursor.execute("PRAGMA table_info(Nodes)")}
        self.edges_entities = {col[1]: col[2] for col in self.cursor.execute("PRAGMA table_info(Edges)")}

    def _initialize_db(self, schema_path: str):
        """Load and apply schema from an external SQL file."""
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            self.cursor.executescript(schema_sql)
        self.connection.commit()

    def add_node(self, **kwargs) -> int:
        """
        Add a node to the web database and return its index in the network.

        Parameters:
            **kwargs: Entity and value pairs of nodes following the schema.
                    Example: name="Node1", location="USA", company="Acme", etc.

        Returns:
            int: The index of the newly added node in the network.
        """
        node_id = str(uuid.uuid4())
        node_index = self.network.add_node(kwargs.get("weight", 1.0))

        columns = ', '.join(['ID', 'Index'] + list(kwargs.keys()))
        placeholders = ', '.join(['?'] * (2 + len(kwargs)))
        values = [node_id, node_index] + list(kwargs.values())

        self.cursor.execute(f"INSERT INTO Nodes ({columns}) VALUES ({placeholders})", values)
        self.connection.commit()

        return node_index
    
    def add_edge(self, from_node: int, to_node: int, **kwargs) -> int:
        """
        Add an edge to the web database and return the edge index.

        Parameters:
            from_node (int): Index of the source node
            to_node (int): Index of the target node
            **kwargs: Any additional edge attributes (e.g., Base_Model=True)

        Returns:
            int: Index of the newly added edge (optional — or just return nothing)
        """
        if from_node < 0 or from_node >= self.network.index or to_node < 0 or to_node >= self.network.index:
            raise IndexError("Node index out of range.")

        self.network.add_edge(from_node, to_node, kwargs.get("weight", 1.0))

        # Insert the edge into the Edges table
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join('?' for _ in kwargs)
        
        sql_columns = "SourceID, TargetID" + (", " + columns if columns else "")
        sql_placeholders = "?, ?" + (", " + placeholders if placeholders else "")
        values = [from_node, to_node] + list(kwargs.values())

        self.cursor.execute(
            f"INSERT INTO Edges ({sql_columns}) VALUES ({sql_placeholders})",
            values
        )
        self.connection.commit()

    def delete_node(self, node_index: int):
        """Delete a node from the web database."""
        # Delete the node from the network
        self.network.delete_node(node_index)

        # Delete the node from the Nodes table
        self.cursor.execute("DELETE FROM Nodes WHERE Index = ?", (node_index,))

        # Decrement the index of all nodes with a higher index
        self.cursor.execute("UPDATE Nodes SET Index = Index - 1 WHERE Index > ?", (node_index,))

        # Delete edges associated with the node
        self.cursor.execute("DELETE FROM Edges WHERE SourceID = ? OR TargetID = ?", (node_index, node_index))

        self.connection.commit()


    def delete_edge(self, from_node: int, to_node: int):
        """Delete an edge from the web database."""
        if from_node < 0 or from_node >= self.network.index or to_node < 0 or to_node >= self.network.index:
            raise IndexError("Node index out of range.")
        
        # Delete the edge from the network
        self.network.delete_edge(from_node, to_node)

        # Delete the edge from the Edges table
        self.cursor.execute("DELETE FROM Edges WHERE SourceID = ? AND TargetID = ?", (from_node, to_node))

        self.connection.commit()


    def get_node(self, node_index: list = None) -> np.ndarray:
        """
        Get nodes from the web database.
        If no indices are provided, return all nodes.
        """
        if node_index is None:
            self.cursor.execute("SELECT * FROM Nodes")
            rows = self.cursor.fetchall()
        else:
            placeholders = ', '.join('?' for _ in node_index)
            query = f"SELECT * FROM Nodes WHERE Index IN ({placeholders})"
            self.cursor.execute(query, tuple(node_index))
            rows = self.cursor.fetchall()

        return np.array(rows, dtype=object)

    def get_edge(self, from_node: int, to_node: int) -> np.ndarray:
        """
        Get an edge from the web database using source and target node indices.
        """
        if from_node < 0 or from_node >= self.network.index or to_node < 0 or to_node >= self.network.index:
            raise IndexError("Node index out of range.")

        self.cursor.execute(
            "SELECT * FROM Edges WHERE SourceID = ? AND TargetID = ?",
            (from_node, to_node)
        )
        row = self.cursor.fetchone()
        return np.array(row, dtype=object) if row else None
        
    def _build_conditions(self, filter_dict, valid_cols):
        conditions = []
        values = []

        for column, filters in filter_dict.items():
            if column not in valid_cols:
                raise ValueError(f"Invalid column name: '{column}'")

            if isinstance(filters, tuple):
                filters = [filters]

            for op, val in filters:
                if op not in self.filter_ops:
                    raise ValueError(f"Unsupported operator '{op}' for column '{column}'")

                inverse_op = self.filter_ops[op]
                conditions.append(f"{column} {inverse_op} ?")
                values.append(val)

        return conditions, values
        
    def _filter_nodes(self, node_filter: dict):
        """
        Returns a list of valid nodes based on the node_filter conditions.

        Parameters:
            node_filter (dict): {column_name: (operator, value) or list of such tuples}
                                Conditions for filtering nodes.

        Returns:
            List[tuple]: A list of nodes that meet the node_filter conditions.
        """
        node_conditions, node_values = self._build_conditions(node_filter, self.nodes_entities) if node_filter else ([], [])
        node_sql = "SELECT Index FROM Nodes"
        if node_conditions:
            node_sql += " WHERE " + " AND ".join(node_conditions)

        self.cursor.execute(node_sql, node_values)
        valid_nodes = [row[0] for row in self.cursor.fetchall()]

        return valid_nodes
    
    def _filter_edges(self, edge_filter: dict):
        """
        Returns a list of valid edges (SourceID, TargetID) based on the edge_filter conditions.

        Parameters:
            edge_filter (dict): {column_name: (operator, value) or list of such tuples}
                                Conditions for filtering edges.

        Returns:
            List[tuple]: A list of edges (SourceID, TargetID) that meet the edge_filter conditions.
        """
        edge_conditions, edge_values = self._build_conditions(edge_filter, self.edges_entities) if edge_filter else ([], [])
        edge_sql = "SELECT SourceID, TargetID FROM Edges"
        if edge_conditions:
            edge_sql += " WHERE " + " AND ".join(edge_conditions)

        self.cursor.execute(edge_sql, edge_values)
        valid_edges = [(row[0], row[1]) for row in self.cursor.fetchall()]

        return valid_edges
    
    def get_web(self, node_filter: dict = None, edge_filter: dict = None) -> np.ndarray:
        """
        Returns a subgraph as an adjacency matrix based on the provided node and edge filters.

        Parameters:
            node_filter (dict): {column_name: (operator, value) or list of such tuples}
                                Conditions for filtering nodes.
            edge_filter (dict): {column_name: (operator, value) or list of such tuples}
                                Conditions for filtering edges.

        Returns:
            np.ndarray: Adjacency matrix of the filtered subgraph.
        """
        # Filter nodes and edges
        node_indicies = self._filter_nodes(node_filter)
        edge_indicies = self._filter_edges(edge_filter)
        # Get Sub-Network
        edge_matrix, node_weights = self.network.filtered_subgraph(node_indicies, edge_indicies)
        # Return the network edge matrix, node weights, and node indicies (keys)
        return edge_matrix, node_weights, node_indicies

    def delete_db(self):
        """Delete the database file."""
        self.connection.close()
        if os.path.exists(self.db_path) and os.path.exists(self.network_path):
            os.remove(self.db_path)
            os.remove(self.network_path)
    
    def change_schema(self, new_schema: str):
        """Change the schema of the web database."""
        with open(self.schema_path, 'w') as f:
            f.write(new_schema)
    
    def get_schema(self) -> Dict[str, Any]:
        """Returns the schema of the web database from the SQL schema file."""
        with open(self.schema_path, 'r') as f:
            schema_sql = f.read()
        return schema_sql

    def close(self):
        # Pickle the network to save its state
        with open(self.network_path, 'wb') as f:
            pickle.dump(self.network, f)
        self.connection.close()

class Network:
    def __init__(self, size: int, growth: int = 50):
        self.index = 0
        self.size = size
        self.growth = growth
        self.node_weights = np.zeros(size, dtype=np.float32)
        self.edge_weights = np.zeros((size, size), dtype=np.float32)

    def add_node(self, weight: float) -> int:
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

    def _resize(self, new_size: int):
        """Resize the network to a new size."""
        new_node_weights = np.zeros(new_size, dtype=np.float32)
        new_edge_weights = np.zeros((new_size, new_size), dtype=np.float32)
        new_node_weights[:self.size] = self.node_weights
        new_edge_weights[:self.size, :self.size] = self.edge_weights
        self.node_weights = new_node_weights
        self.edge_weights = new_edge_weights
        self.size = new_size