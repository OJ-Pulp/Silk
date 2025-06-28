import sqlite3
import uuid
import numpy as np
import pickle
import os
from Web.network import Network
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
        node_index = self.network.add_node()

        # Insert the node into the Nodes table
        self.cursor.execute("INSERT INTO Nodes (ID, Index) VALUES (?, ?)", (node_id, node_index))

        # Search Node_Entities Table for each key in kwargs if it is not found then add it
        for key in kwargs.keys():
            self.cursor.execute("SELECT id, Entity, Type FROM Node_Entities WHERE Entity = ?", (key,))            
            if not self.cursor.fetchone():
                # Make new entity if it does not exist
                entity_id, entity_name, entity_type = self.make_entity(key, kwargs[key])
                self.cursor.execute(
                    "INSERT INTO Node_Entities (ID, Entity, Type) VALUES (?, ?, ?)",
                    (entity_id, entity_name, entity_type)
                )

            else:
                entity_id, entity_name, entity_type = self.cursor.fetchone()

            # Insert into the Node_Entity table based on the entity type
            if entity_type == "str":
                # Text_Node_Entities
                self.cursor.execute(
                    "INSERT INTO Text_Node_Entities (Node_ID, Node_Entity_ID, Value) VALUES (?, ?, ?)",
                    (node_id, entity_id, kwargs[key])
                )
            elif entity_type == "int":
                # Int_Node_Entities
                self.cursor.execute(
                    "INSERT INTO Int_Node_Entities (Node_ID, Node_Entity_ID, Value) VALUES (?, ?, ?)",
                    (node_id, entity_id, int(kwargs[key]))
                )
            elif entity_type == "float":
                # Real_Node_Entities
                self.cursor.execute(
                    "INSERT INTO Real_Node_Entities (Node_ID, Node_Entity_ID, Value) VALUES (?, ?, ?)",
                    (node_id, entity_id, float(kwargs[key]))
                )
            else:
                raise ValueError(f"Unsupported entity type: {entity_type}")
        # Commit the changes to the database
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
        # Add into Edges table
        if from_node < 0 or from_node >= self.network.index or to_node < 0 or to_node >= self.network.index:
            raise IndexError("Node index out of range.")
        
        edge_id = str(uuid.uuid4())

        self.network.add_edge(from_node, to_node)
        
        self.cursor.execute(
            "INSERT INTO Edges (ID, SourceID, TargetID) VALUES (?, ?, ?)",
            (edge_id, from_node, to_node)
        )

        # Commit the changes to the database
        self.connection.commit()

        # Search Edge_Entities Table for each key in kwargs if it is not found then add it
        for key in kwargs.keys():
            self.cursor.execute("SELECT id, Entity, Type FROM Edge_Entities WHERE Entity = ?", (key,))
            if not self.cursor.fetchone():
                # Make new entity if it does not exist
                entity_id, entity_name, entity_type = self.make_entity(key, kwargs[key])
                self.cursor.execute(
                    "INSERT INTO Edge_Entities (ID, Entity, Type) VALUES (?, ?, ?)",
                    (entity_id, entity_name, entity_type)
                )

            else:
                entity_id, entity_name, entity_type = self.cursor.fetchone()

            # Insert into the Edge_Entity table based on the entity type
            if entity_type == "str":
                self.cursor.execute(
                    "INSERT INTO Text_Edge_Entities (Edge_ID, Edge_Entity_ID, Value) VALUES (?, ?, ?)",
                    (edge_id, entity_id, kwargs[key])
                )
            elif entity_type == "int":
                self.cursor.execute(
                    "INSERT INTO Int_Edge_Entities (Edge_ID, Edge_Entity_ID, Value) VALUES (?, ?, ?)",
                    (edge_id, entity_id, int(kwargs[key]))
                )
            elif entity_type == "float":
                self.cursor.execute(
                    "INSERT INTO Real_Edge_Entities (Edge_ID, Edge_Entity_ID, Value) VALUES (?, ?, ?)",
                    (edge_id, entity_id, float(kwargs[key]))
                )
            else:
                raise ValueError(f"Unsupported entity type: {entity_type}")
            

    def delete_node(self, node_index: int):
        """Delete a node from the web database."""
        # Delete the node from the network
        self.network.delete_node(node_index)
        # Delete the node from the Nodes table and get the node ID
        self.cursor.execute("SELECT ID FROM Nodes WHERE Index = ?", (node_index,))
        row = self.cursor.fetchone()
        if row is None:
            raise IndexError("Node index out of range.")
        node_id = row[0]

        # Delete the node from the Nodes table
        self.cursor.execute("DELETE FROM Nodes WHERE Index = ?", (node_index,))
        # Delete all related entities from each of the Node_Entities tables
        self.cursor.execute("DELETE FROM Text_Node_Entities WHERE Node_ID = ?", (node_id,))
        self.cursor.execute("DELETE FROM Int_Node_Entities WHERE Node_ID = ?", (node_id,))
        self.cursor.execute("DELETE FROM Real_Node_Entities WHERE Node_ID = ?", (node_id,))

        self.connection.commit()

    def delete_edge(self, from_node: int, to_node: int):
        """Delete an edge from the web database."""
        if from_node < 0 or from_node >= self.network.index or to_node < 0 or to_node >= self.network.index:
            raise IndexError("Node index out of range.")
        
        # Delete the edge from the network
        self.network.delete_edge(from_node, to_node)

        # Get the edge ID from the Edges table
        self.cursor.execute(
            "SELECT ID FROM Edges WHERE SourceID = ? AND TargetID = ?",
            (from_node, to_node)
        )
        edge_id = self.cursor.fetchone()
        if edge_id is None:
            raise IndexError("Edge not found.")
        edge_id = edge_id[0]

        # Delete the edge from the Edges table
        self.cursor.execute(
            "DELETE FROM Edges WHERE SourceID = ? AND TargetID = ?",
            (from_node, to_node)
        )
        # Delete all related entities from each of the Edge_Entities tables
        self.cursor.execute("DELETE FROM Text_Edge_Entities WHERE Edge_ID = ?", (edge_id,))
        self.cursor.execute("DELETE FROM Int_Edge_Entities WHERE Edge_ID = ?", (edge_id,))
        self.cursor.execute("DELETE FROM Real_Edge_Entities WHERE Edge_ID = ?", (edge_id,))

        self.connection.commit()

    def change_node(self, node_index: int, **kwargs):
        """
        Change the attributes of a node in the web database.

        Parameters:
            node_index (int): Index of the node to change.
            **kwargs: Entity and value pairs to update the node's attributes.
                    Example: name="NewNode", location="Canada", company="NewCo", etc.
        """
        if node_index < 0 or node_index >= self.network.index:
            raise IndexError("Node index out of range.")

        # Update the Node_Entities table with new values
        for key, value in kwargs.items():
            self.cursor.execute("SELECT id, Entity, Type FROM Node_Entities WHERE Entity = ?", (key,))
            row = self.cursor.fetchone()
            if row is None:
                # Make new entity if it does not exist
                entity_id, entity_name, entity_type = self.make_entity(key, value)
                self.cursor.execute(
                    "INSERT INTO Node_Entities (ID, Entity, Type) VALUES (?, ?, ?)",
                    (entity_id, entity_name, entity_type)
                )
            else:
                entity_id, entity_name, entity_type = row

            # Update the corresponding Node_Entity table based on the entity type
            if entity_type == "str":
                self.cursor.execute(
                    "INSERT INTO Text_Node_Entities (Node_ID, Node_Entity_ID, Value) VALUES (?, ?, ?) "
                    "ON CONFLICT(Node_ID, Node_Entity_ID) DO UPDATE SET Value = excluded.Value",
                    (node_index, entity_id, value)
                )
            elif entity_type == "int":
                self.cursor.execute(
                    "INSERT INTO Int_Node_Entities (Node_ID, Node_Entity_ID, Value) VALUES (?, ?, ?) "
                    "ON CONFLICT(Node_ID, Node_Entity_ID) DO UPDATE SET Value = excluded.Value",
                    (node_index, entity_id, int(value))
                )
            elif entity_type == "float":
                self.cursor.execute(
                    "INSERT INTO Real_Node_Entities (Node_ID, Node_Entity_ID, Value) VALUES (?, ?, ?) "
                    "ON CONFLICT(Node_ID, Node_Entity_ID) DO UPDATE SET Value = excluded.Value",
                    (node_index, entity_id, float(value))
                )
            else:
                raise ValueError(f"Unsupported entity type: {entity_type}")

        # Commit the changes to the database
        self.connection.commit()
    
    def change_edge(self, from_node: int, to_node: int, **kwargs):
        """
        Change the attributes of an edge in the web database.

        Parameters:
            from_node (int): Index of the source node.
            to_node (int): Index of the target node.
            **kwargs: Entity and value pairs to update the edge's attributes.
                    Example: weight=2.5, type="friendship", etc.
        """

        if from_node < 0 or from_node >= self.network.index or to_node < 0 or to_node >= self.network.index:
            raise IndexError("Node index out of range.")
        
        # Get the edge ID from the Edges table
        self.cursor.execute(
            "SELECT ID FROM Edges WHERE SourceID = ? AND TargetID = ?",
            (from_node, to_node)
        )
        edge_row = self.cursor.fetchone()
        if edge_row is None:
            raise IndexError("Edge not found.")
        edge_id = edge_row[0]

        # Update the Edge_Entities table with new values
        for key, value in kwargs.items():
            self.cursor.execute("SELECT ID, Entity, Type FROM Edge_Entities WHERE Entity = ?", (key,))
            row = self.cursor.fetchone()
            if row is None:
                # Make new entity if it does not exist
                entity_id, entity_name, entity_type = self.make_entity(key, value)
                self.cursor.execute(
                    "INSERT INTO Edge_Entities (ID, Entity, Type) VALUES (?, ?, ?)",
                    (entity_id, entity_name, entity_type)
                )
            else:
                entity_id, entity_name, entity_type = row
            # Update the corresponding Edge_Entity table based on the entity type
            if entity_type == "str":
                self.cursor.execute(
                    "INSERT INTO Text_Edge_Entities (Edge_ID, Edge_Entity_ID, Value) VALUES (?, ?, ?) "
                    "ON CONFLICT(Edge_ID, Edge_Entity_ID) DO UPDATE SET Value = excluded.Value",
                    (edge_id, entity_id, value)
                )
            elif entity_type == "int":
                self.cursor.execute(
                    "INSERT INTO Int_Edge_Entities (Edge_ID, Edge_Entity_ID, Value) VALUES (?, ?, ?) "
                    "ON CONFLICT(Edge_ID, Edge_Entity_ID) DO UPDATE SET Value = excluded.Value",
                    (edge_id, entity_id, int(value))
                )
            elif entity_type == "float":
                self.cursor.execute(
                    "INSERT INTO Real_Edge_Entities (Edge_ID, Edge_Entity_ID, Value) VALUES (?, ?, ?) "
                    "ON CONFLICT(Edge_ID, Edge_Entity_ID) DO UPDATE SET Value = excluded.Value",
                    (edge_id, entity_id, float(value))
                )
            else:
                raise ValueError(f"Unsupported entity type: {entity_type}")
            
        # Commit the changes to the database
        self.connection.commit()

    def get_node(self, node_index: int) -> np.ndarray:
        """
        Get nodes from the web database.
        """
        # Get node id
        if node_index < 0 or node_index >= self.network.index:
            raise IndexError("Node index out of range.")

        self.cursor.execute("SELECT ID FROM Nodes WHERE Index = ?", (node_index,))
        row = self.cursor.fetchone()
        if row is None:
            raise IndexError("Node index not found.")
        node_id = row[0]
        # Get all node entities for the given node ID
        self.cursor.execute(
            "SELECT Node_Entities.Entity, "
            "COALESCE(Text_Node_Entities.Value, Int_Node_Entities.Value, Real_Node_Entities.Value) AS Value "
            "FROM Node_Entities "
            "LEFT JOIN Text_Node_Entities ON Node_Entities.ID = Text_Node_Entities.Node_Entity_ID AND Text_Node_Entities.Node_ID = ? "
            "LEFT JOIN Int_Node_Entities ON Node_Entities.ID = Int_Node_Entities.Node_Entity_ID AND Int_Node_Entities.Node_ID = ? "
            "LEFT JOIN Real_Node_Entities ON Node_Entities.ID = Real_Node_Entities.Node_Entity_ID AND Real_Node_Entities.Node_ID = ?",
            (node_id, node_id, node_id)
        )
        rows = self.cursor.fetchall()
        if not rows:
            raise IndexError("No entities found for the node.")
        # Convert the rows to a structured numpy array
        entity_names = [row[0] for row in rows]
        entity_values = [row[1] for row in rows]
        node_array = np.array(list(zip(entity_names, entity_values)), dtype=object)
        return node_array

    def get_edge(self, from_node: int, to_node: int) -> np.ndarray:
        """
        Get an edge from the web database using source and target node indices.
        """
        if from_node < 0 or from_node >= self.network.index or to_node < 0 or to_node >= self.network.index:
            raise IndexError("Node index out of range.")
        # Get edge id
        self.cursor.execute(
            "SELECT ID FROM Edges WHERE SourceID = ? AND TargetID = ?",
            (from_node, to_node)
        )
        row = self.cursor.fetchone()
        if row is None:
            raise IndexError("Edge not found.")
        edge_id = row[0]
        # Get all edge entities for the given edge ID
        self.cursor.execute(
            "SELECT Edge_Entities.Entity, "
            "COALESCE(Text_Edge_Entities.Value, Int_Edge_Entities.Value, Real_Edge_Entities.Value) AS Value "
            "FROM Edge_Entities "
            "LEFT JOIN Text_Edge_Entities ON Edge_Entities.ID = Text_Edge_Entities.Edge_Entity_ID AND Text_Edge_Entities.Edge_ID = ? "
            "LEFT JOIN Int_Edge_Entities ON Edge_Entities.ID = Int_Edge_Entities.Edge_Entity_ID AND Int_Edge_Entities.Edge_ID = ? "
            "LEFT JOIN Real_Edge_Entities ON Edge_Entities.ID = Real_Edge_Entities.Edge_Entity_ID AND Real_Edge_Entities.Edge_ID = ?",
            (edge_id, edge_id, edge_id)
        )
        rows = self.cursor.fetchall()
        if not rows:
            raise IndexError("No entities found for the edge.")
        # Convert the rows to a structured numpy array
        entity_names = [row[0] for row in rows]
        entity_values = [row[1] for row in rows]
        edge_array = np.array(list(zip(entity_names, entity_values)), dtype=object)
        return edge_array
    
    def _filter_nodes(self, conditions: Dict[str, str]) -> List[int]:
        """
        Retrieve node indexes from the Nodes table that satisfy a set of attribute-based conditions.

        Parameters:
            conditions (dict[str, str]): A dictionary of attribute conditions where:
                - Keys are attribute names from the Node_Entities table (e.g., 'height', 'name').
                - Values are raw SQL condition strings to apply to the `value` field
                (e.g., ">= 180", "= 'John'", "< 30").

        Returns:
            list[int]: A list of `Index` values from the Nodes table for nodes that satisfy all conditions.

        Notes:
            - Conditions must be correctly formatted as raw SQL fragments.
            - No SQL injection protection is applied—do not pass unsanitized user input.
            - Each entity key must exist in the Node_Entities table.
        """
        # Step 1: Find types for all entities
        entity_names = tuple(conditions.keys())
        placeholders = ','.join('?' for _ in entity_names)

        self.cursor.execute(
            f"SELECT Entity, Type FROM Node_Entities WHERE Entity IN ({placeholders})",
            entity_names
        )
        entity_type_map = dict(self.cursor.fetchall())  # { 'height': 'Real', 'name': 'Text', ... }

        # Step 2: Create subqueries for each condition
        subqueries = []
        for entity, condition in conditions.items():
            entity_type = entity_type_map.get(entity)
            if not entity_type:
                raise ValueError(f"Unknown entity: {entity}")

            if entity_type == 'Real':
                table = 'Real_Node_Entities'
            elif entity_type == 'Int':
                table = 'Int_Node_Entities'
            elif entity_type == 'Text':
                table = 'Text_Node_Entities'
            else:
                raise ValueError(f"Unsupported type: {entity_type}")

            subqueries.append(f"""
                SELECT {table}.Node_ID
                FROM {table}
                JOIN Node_Entities ne ON {table}.Node_Entity_ID = ne.ID
                WHERE ne.Entity = '{entity}' AND {table}.value {condition}
            """)

        # Step 3: Combine with INTERSECT
        if not subqueries:
            return []

        intersect_query = "\nINTERSECT\n".join(subqueries)

        final_query = f"""
            SELECT Index FROM Nodes
            WHERE ID IN (
                {intersect_query}
            )
        """

        self.cursor.execute(final_query)
        return [row[0] for row in self.cursor.fetchall()]
    
    def _filter_edges(self, conditions: Dict[str, str]) -> List[Tuple[int, int]]:
        """
        Retrieve (SourceID, TargetID) edge pairs from the Edges table that meet a set of attribute-based conditions.

        Parameters:
            conditions (dict[str, str]): A dictionary of attribute conditions where:
                - Keys are attribute names from the Edge_Entities table (e.g., 'distance', 'label').
                - Values are raw SQL condition strings to apply to the `value` field
                (e.g., ">= 5.0", "= 'highway'", "<= 60").

        Returns:
            list[tuple[int, int]]: A list of `(SourceID, TargetID)` pairs for edges matching all conditions.

        Notes:
            - Conditions must be correctly formatted as raw SQL fragments.
            - No SQL injection protection is applied—do not pass unsanitized user input.
            - Each entity key must exist in the Edge_Entities table.
        """
        # Step 1: Find types for all entities
        entity_names = tuple(conditions.keys())
        placeholders = ','.join('?' for _ in entity_names)

        self.cursor.execute(
            f"SELECT Entity, Type FROM Edge_Entities WHERE Entity IN ({placeholders})",
            entity_names
        )
        entity_type_map = dict(self.cursor.fetchall())  # e.g., { 'distance': 'Real', 'label': 'Text' }

        # Step 2: Create subqueries for each condition
        subqueries = []
        for entity, condition in conditions.items():
            entity_type = entity_type_map.get(entity)
            if not entity_type:
                raise ValueError(f"Unknown entity: {entity}")

            if entity_type == 'Real':
                table = 'Real_Edge_Entities'
            elif entity_type == 'Int':
                table = 'Int_Edge_Entities'
            elif entity_type == 'Text':
                table = 'Text_Edge_Entities'
            else:
                raise ValueError(f"Unsupported type: {entity_type}")

            subqueries.append(f"""
                SELECT {table}.Edge_ID
                FROM {table}
                JOIN Edge_Entities ee ON {table}.Edge_Entity_ID = ee.ID
                WHERE ee.Entity = '{entity}' AND {table}.value {condition}
            """)

        # Step 3: Combine with INTERSECT
        if not subqueries:
            return []

        intersect_query = "\nINTERSECT\n".join(subqueries)

        final_query = f"""
            SELECT SourceID, TargetID FROM Edges
            WHERE ID IN (
                {intersect_query}
            )
        """

        self.cursor.execute(final_query)
        return self.cursor.fetchall()  # list of (SourceID, TargetID) tuples

    def get_web(self, node_conditions: Dict[str, str], edge_conditions: Dict[str, str]) -> np.ndarray:
        # Get Node Indicies
        node_indicies = self._filter_nodes(node_conditions)
        if not node_indicies:
            raise ValueError("No nodes found matching the given conditions.")

        # Get Edge Indicies
        edge_indicies = self._filter_edges(edge_conditions)
        if not edge_indicies:
            raise ValueError("No edges found matching the given conditions.")
 
        # Get Sub-Network
        edge_matrix, node_weights = self.network.filtered_subgraph(node_indicies, edge_indicies)
        # Return the network edge matrix, node weights, and node indicies (keys)
        return edge_matrix, node_weights, node_indicies

    def make_entity(self, entity: str, value: Any) -> str:
        """
        Create the data for a new entity in the database and return its ID, name, and type.
        """
        entity = entity.lower()
        entity_id = str(uuid.uuid4())
        entity_type = type(value).__name__
        return entity_id, entity, entity_type
    
    def delete_db(self):
        """Delete the database file."""
        self.connection.close()
        if os.path.exists(self.db_path) and os.path.exists(self.network_path):
            os.remove(self.db_path)
            os.remove(self.network_path)

    def close(self):
        # Pickle the network to save its state
        with open(self.network_path, 'wb') as f:
            pickle.dump(self.network, f)
        self.connection.close()