import sqlite3
import uuid
import numpy as np
import os
import re
import json
from typing import Dict, Any, List


class GraphDB:
    def __init__(self, db_name: str, schema_path: str):
        self.db_path = db_name
        self.schema_path = schema_path
        # Initialize the database connection and schema.
        if not os.path.exists(db_name):
            self.connection = sqlite3.connect(db_name)
            self.cursor = self.connection.cursor()
            self._initialize_db(schema_path)
        else:
            self.connection = sqlite3.connect(db_name)
            self.cursor = self.connection.cursor()

    def _initialize_db(self, schema_path: str):
        """Load and apply schema from an external SQL file."""
        with open(schema_path, "r") as f:
            schema_sql = f.read()
            self.cursor.executescript(schema_sql)
        self.connection.commit()

    def add_graph(
        self,
        graph_id: str | None = None,
        node_ids: List[str] | None = None,
        **kwargs,
    ) -> int:
        """
        Add a new graph to the web database and return its ID.

        Parameters:
            graph_id (str, optional): ID of the graph. If None, a new UUID will be generated.
            node_ids (List[str], optional): List of node IDs to associate with the graph.
            **kwargs: Entity and value pairs of the graph following the schema.
                    Example: name="Graph1", description="A sample graph", etc.
        Returns:
            int: ID of the newly added graph.
        """
        if graph_id is None:
            graph_id = str(uuid.uuid4())
        if not node_ids:
            node_ids = []
            self.cursor.execute(
                "INSERT INTO Graph_Nodes (Graph_ID) VALUES (?)", (graph_id,)
            )
        else:
            for node_id in node_ids:
                self.cursor.execute(
                    "INSERT INTO Graph_Nodes (Graph_ID, Node_ID) VALUES (?, ?)",
                    (graph_id, node_id),
                )
        self.connection.commit()
        # Insert kwargs into the Graph_Entities Table
        self._add_entities(graph_id, "graph", **kwargs)
        return graph_id

    def delete_graph(self, graph_id: str):
        """
        Delete a graph and its associated node links.
        Only remove nodes if they are not shared with other graphs.
        Assumes delete_node handles cleanup (edges, entities, etc.)
        """
        # Step 1: Get all nodes associated with this graph
        self.cursor.execute(
            "SELECT Node_ID FROM Graph_Nodes WHERE Graph_ID = ?", (graph_id,)
        )
        node_ids = [row[0] for row in self.cursor.fetchall() if row[0] is not None]

        # Step 2: For each node, check if it belongs only to this graph
        for node_id in node_ids:
            self.cursor.execute(
                """
                SELECT COUNT(*) FROM Graph_Nodes
                WHERE Node_ID = ? AND Graph_ID != ?
                """,
                (node_id, graph_id),
            )
            count = self.cursor.fetchone()[0]
            if count == 0:
                self.delete_node(node_id)

        # Step 3: Remove the graph-node links
        self.cursor.execute("DELETE FROM Graph_Nodes WHERE Graph_ID = ?", (graph_id,))

        self.connection.commit()

    def get_graphs(self) -> List[str]:
        """
        Retrieve all graph IDs from the database.
        Returns:
            List[str]: A list of graph IDs.
        """
        self.cursor.execute("SELECT DISTINCT Graph_ID FROM Graph_Nodes")
        return [row[0] for row in self.cursor.fetchall() if row[0] is not None]

    def add_node(
        self, graph_ids: List[str], node_id: str | None = None, **kwargs
    ) -> int:
        """
        Add a node to the web database.

        Parameters:
            graph_ids (List[str]): List of graph IDs to which the node belongs.
            node_id (str, optional): ID of the node. If None, a new UUID will be generated.
            **kwargs: Entity and value pairs of nodes following the schema.
                    Example: name="Node1", location="USA", company="Acme", etc.

        Returns:
            str: ID of the newly added node.
        """
        if node_id is None:
            node_id = str(uuid.uuid4())

        for graph_id in graph_ids:
            self.cursor.execute(
                "INSERT INTO Graph_Nodes (Graph_ID, Node_ID) VALUES (?, ?)",
                (graph_id, node_id),
            )
        self.connection.commit()
        # Insert kwargs into the Node_Entities Table
        self._add_entities(node_id, "node", **kwargs)
        return node_id

    def delete_node(self, node_id: str):
        """
        Delete a node from the web database.

        Parameters:
            node_id (str): ID of the node to delete.
        """
        # Delete the node from the Nodes table
        self.cursor.execute(
            "DELETE FROM Graph_Nodes WHERE Node_ID = ?",
            (node_id,),
        )
        # Delete all related entities from each of the Node_Entities tables
        self._delete_entities(node_id, "node")

        # Delete all edges associated with this node
        self.cursor.execute(
            "DELETE FROM Edges WHERE SourceID = ? OR TargetID = ?", (node_id, node_id)
        )

        self.connection.commit()

    def edit_node(self, node_id: str, **kwargs):
        """
        Edit a node in the web database.

        Parameters:
            node_id (str): ID of the node to edit.
            **kwargs: Updated entity and value pairs for the node.
        """
        # Delete all related entities from each of the Node_Entities tables
        self._delete_entities(node_id, "node")
        self.connection.commit()
        # Re-add the node with updated values
        self._add_entities(node_id, "node", **kwargs)

    def get_node(self, node_id: str) -> Dict[str, Any]:
        """
        Retrieve a node from the web database.

        Parameters:
            node_id (str): ID of the node to retrieve.

        Returns:
            dict: A dictionary containing node attributes and values.
        """
        self.cursor.execute(
            "SELECT Graph_ID FROM Graph_Nodes WHERE Node_ID = ?",
            (node_id,),
        )
        if not self.cursor.fetchone():
            return {}

        # Get the node entities
        entities = self._get_entities(node_id, "node")
        return {
            "graph_ids": [row[0] for row in self.cursor.fetchall()],
            "node_id": node_id,
            **entities,
        }

    def add_edge(self, from_node: str, to_node: str, **kwargs) -> str:
        """
        Add an edge to the web database and return the edge ID.

        Parameters:
            from_node (str): ID of the source node
            to_node (str): ID of the target node
            **kwargs: Any additional edge attributes (e.g., weight=2.5, type="friendship")

        Returns:
            str: ID of the newly added edge.
        """
        edge_id = str(uuid.uuid4())
        self.cursor.execute(
            "INSERT INTO Edges (ID, SourceID, TargetID) VALUES (?, ?, ?)",
            (edge_id, from_node, to_node),
        )
        self.connection.commit()
        # Insert kwargs into the Edge_Entities Table
        self._add_entities(edge_id, "edge", **kwargs)
        return edge_id

    def delete_edge(self, edge_id: str):
        """
        Delete an edge from the web database.

        Parameters:
            edge_id (str): ID of the edge to delete.
        """
        # Delete the edge from the Edges table
        self.cursor.execute("DELETE FROM Edges WHERE ID = ?", (edge_id,))
        # Delete all related entities from each of the Edge_Entities tables
        self._delete_entities(edge_id, "edge")
        self.connection.commit()

    def edit_edge(self, edge_id: str, **kwargs):
        """
        Edit an edge in the web database.

        Parameters:
            edge_id (str): ID of the edge to edit.
            **kwargs: Updated edge attributes (e.g., weight=2.5, type="friendship")
        """
        # Delete all related entities from each of the Edge_Entities tables
        self._delete_entities(edge_id, "edge")
        self.connection.commit()
        # Re-add the edge with updated values
        self._add_entities(edge_id, "edge", **kwargs)

    def get_edge(self, source: str, target: str) -> Dict[str, Any]:
        """
        Retrieve an edge between two nodes.

        Parameters:
            source (str): ID of the source node.
            target (str): ID of the target node.

        Returns:
            dict: A dictionary containing edge attributes and values.
        """
        self.cursor.execute(
            "SELECT ID FROM Edges WHERE SourceID = ? AND TargetID = ?",
            (source, target),
        )

        edge_id = self.cursor.fetchone()

        if not edge_id:
            return {}

        # Get the edge entities
        entities = self._get_entities(edge_id, "edge")
        return {"id": edge_id, "source": source, "target": target, **entities}

    def create_graph(
        self,
        graph_filter: List[str] | None = None,
        node_filter: Dict[str, List[str]] | None = None,
        edge_filter: Dict[str, List[str]] | None = None,
    ):
        """
        Create a network based on the specified graph IDs and conditions.

        Parameters:
            graph_ids (list[str], optional): List of graph IDs to include in the network.
            node_conditions (dict[str, list[str]], optional): Dictionary of SQL conditions to filter nodes.
            Example: {"age": ["<= 30", "> 10"]} to filter nodes by age between 10 and 30.
            edge_conditions (dict[str, list[str]], optional): Dictionary of SQL conditions to filter edges.

        Returns:
            Node_Weights: np.ndarray
            Edge_Weights: np.ndarray
            Node_Ids: List[str]
        """
        node_weights, node_ids = self._weight_nodes(node_filter, graph_filter)
        edge_weights, _ = self._weight_edges(edge_filter, node_ids)
        return node_weights, edge_weights, node_ids

    def _weight_nodes(
        self,
        node_conditions: Dict[str, List[str]],
        graph_ids: List[str] | None = None,
    ) -> np.ndarray:
        """
        Calculate weights for nodes based on specified conditions. If no conditions are provided,
        equal weights are assigned to all nodes. If no graph IDs are provided, all graphs are considered.

        Parameters:
            node_conditions (dict[str, list[str]]): Dictionary of conditions for filtering nodes.
            graph_ids (list[str], optional): List of graph IDs to filter nodes. If None, all graphs are considered.

        Returns:
            Tuple[np.ndarray, List[str]]: A tuple containing an array of node weights and a list of node IDs.
        """
        if not graph_ids:
            self.cursor.execute("SELECT DISTINCT Graph_ID FROM Graph_Nodes")
            graph_ids = [row[0] for row in self.cursor.fetchall()]

        if not node_conditions:
            # Return equal weights if no conditions
            self.cursor.execute(
                f"SELECT DISTINCT Node_ID FROM Graph_Nodes WHERE Graph_ID IN ({','.join(repr(g) for g in graph_ids)})"
            )
            node_ids = [row[0] for row in self.cursor.fetchall() if row[0] is not None]
            node_ids = list(set(node_ids))
            return (
                (np.ones(len(node_ids)), node_ids) if node_ids else (np.array([]), [])
            )

        node_weights = {}
        for entity, conditions in node_conditions.items():
            # Get entity ID and type
            self.cursor.execute(
                f"SELECT ID, Type FROM Entities WHERE Name = {repr(entity)}"
            )
            result = self.cursor.fetchone()
            if not result:
                continue

            entity_id, entity_type = result
            value_table = f"{entity_type}_Entity_Values"

            for condition in conditions:
                condition = condition.strip()
                match = re.match(
                    r"^(=|!=|>=|<=|>|<|LIKE|NOT LIKE|IN|NOT IN|BETWEEN)\s+(.*)$",
                    condition,
                    re.IGNORECASE,
                )
                if not match:
                    print(f"Skipping invalid condition: {condition}")
                    continue

                operator, value = match.groups()
                operator = operator.upper()
                value = value.strip()

                if operator in ("IN", "NOT IN"):
                    items = [
                        f"'{item.strip().strip('"\'')}'"
                        for item in re.split(r"[,\s]+", value.strip("()[]"))
                        if item
                    ]
                    value_clause = f"{operator} ({', '.join(items)})"
                elif operator == "BETWEEN":
                    parts = re.split(r"\s+AND\s+", value, flags=re.IGNORECASE)
                    if len(parts) != 2:
                        print(f"Skipping malformed BETWEEN: {value}")
                        continue
                    value_clause = f"BETWEEN {parts[0]} AND {parts[1]}"
                else:
                    # Sanitize string value
                    if not value.replace(".", "", 1).isdigit():
                        value = f"'{value.strip('"\'')}'"
                    value_clause = f"{operator} {value}"

                # Build query with inline values
                query = f"""
                    SELECT ev.Target_ID,
                        CASE
                            WHEN '{entity_type}' = 'Text' THEN 1.0 / COUNT(*) OVER ()
                            ELSE CAST(ev.Value AS FLOAT) / SUM(CAST(ev.Value AS FLOAT)) OVER ()
                        END AS weight
                    FROM {value_table} ev
                    JOIN Graph_Nodes gn ON ev.Target_ID = gn.Node_ID
                    WHERE ev.Entity_ID = '{entity_id}'
                    AND ev.Target_Type = 'node'
                    AND ev.Value {value_clause}
                    AND gn.Graph_ID IN ({", ".join(repr(gid) for gid in graph_ids)})
                """

                self.cursor.execute(query)
                for node_id, weight in self.cursor.fetchall():
                    node_weights.setdefault(node_id, []).append(weight)

        # Average weights
        for node_id, weights in node_weights.items():
            node_weights[node_id] = sum(weights) / len(weights)

        return np.array(list(node_weights.values())), list(node_weights.keys())

    def _weight_edges(
        self,
        edge_conditions: Dict[str, List[str]],
        node_ids: List[str] | None = None,
    ) -> np.ndarray:
        """
        Calculate weights for edges based on specified conditions. If no conditions are provided,
        equal weights are assigned to all edges. Additionally, if no node IDs are provided,
        all nodes are considered.
        Parameters:
            edge_conditions (dict[str, list[str]]): Dictionary of conditions for filtering edges.
            node_ids (list[str], optional): List of node IDs to filter edges. If None, all nodes are considered.
        Returns:
            Tuple[np.ndarray, List[str]]: A tuple containing an array of edge weights and a list of node IDs.
        """
        if not node_ids:
            return np.array([]), []

        if not node_ids:
            self.cursor.execute("SELECT DISTINCT Node_ID FROM Graph_Nodes")
            node_ids = [row[0] for row in self.cursor.fetchall()]

        node_index_map = {node_id: i for i, node_id in enumerate(node_ids)}
        N = len(node_ids)
        matrix = np.zeros((N, N))

        if not edge_conditions:
            # If no conditions are provided, return equal weights for all edges
            self.cursor.execute(
                "SELECT SourceID, TargetID FROM Edges WHERE SourceID IN ({}) AND TargetID IN ({})".format(
                    ",".join(["?"] * len(node_ids)), ",".join(["?"] * len(node_ids))
                ),
                (*node_ids, *node_ids),
            )
            for source_id, target_id in self.cursor.fetchall():
                if source_id in node_index_map and target_id in node_index_map:
                    i = node_index_map[source_id]
                    j = node_index_map[target_id]
                    matrix[i][j] = 1.0

            return matrix, node_ids
        else:
            edge_weights = {}  # edge_id → list of weights
            for entity, conditions in edge_conditions.items():
                self.cursor.execute(
                    "SELECT ID, Type FROM Entities WHERE Name = ?", (entity,)
                )
                entity_id, entity_type = self.cursor.fetchone()
                value_table = f"{entity_type}_Entity_Values"

                for condition in conditions:
                    operator, condition_value = condition.strip().split(" ", 1)
                    placeholders = ",".join(["?"] * len(node_ids))

                    query = f"""
                        SELECT ge.SourceID, ge.TargetID,
                            CASE 
                                WHEN ? = 'Text' THEN 1.0 / COUNT(*) OVER ()
                                ELSE CAST(ev.Value AS FLOAT) / SUM(CAST(ev.Value AS FLOAT)) OVER ()
                            END AS weight
                        FROM {value_table} ev
                        JOIN Edges ge ON ev.Target_ID = ge.ID
                        WHERE ev.Entity_ID = ?
                        AND ev.Target_Type = 'edge'
                        AND ev.Value {operator} ?
                        AND ge.SourceID IN ({placeholders})
                        AND ge.TargetID IN ({placeholders})
                    """

                    self.cursor.execute(
                        query,
                        (entity_type, entity_id, condition_value, *node_ids, *node_ids),
                    )

                    for source_id, target_id, weight in self.cursor.fetchall():
                        edge_weights.setdefault((source_id, target_id), []).append(
                            weight
                        )

            # Average weights and fill the matrix
            for (source_id, target_id), weights in edge_weights.items():
                if source_id in node_index_map and target_id in node_index_map:
                    i = node_index_map[source_id]
                    j = node_index_map[target_id]
                    matrix[i][j] = sum(weights) / len(weights)

            return matrix, node_ids

    def _add_entities(self, target_id: str, target_type: str, **kwargs) -> None:
        for key, value in kwargs.items():
            # Skip None values
            if value is None:
                continue
            # Convert bools to int
            if isinstance(value, bool):
                value = int(value)
            # Serialize lists and dicts as JSON strings
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            self.cursor.execute(
                "SELECT ID, Name, Type FROM Entities WHERE Name = ?", (key,)
            )
            row = self.cursor.fetchone()

            if row:
                entity_id, entity_name, entity_type = row
            else:
                py_type = type(value).__name__

                if py_type == "str":
                    entity_type = "Text"
                elif py_type == "int":
                    entity_type = "Int"
                elif py_type == "float":
                    entity_type = "Real"
                else:
                    raise ValueError(
                        f"Unsupported value type: {py_type} for key '{key}'"
                    )

                entity_id = str(uuid.uuid4())
                entity_name = key.lower()

                self.cursor.execute(
                    "INSERT INTO Entities (ID, Name, Type) VALUES (?, ?, ?)",
                    (entity_id, entity_name, entity_type),
                )

            # Build table name dynamically using entity_type
            value_table = f"{entity_type}_Entity_Values"

            if entity_type == "Text":
                value = str(value)
            elif entity_type == "Int":
                value = int(value)
            elif entity_type == "Real":
                value = float(value)
            else:
                raise ValueError(f"Unsupported entity type: {entity_type}")

            self.cursor.execute(
                f"INSERT INTO {value_table} (Entity_ID, Target_Type, Target_ID, Value) VALUES (?, ?, ?, ?)",
                (entity_id, target_type, target_id, value),
            )

        self.connection.commit()

    def _delete_entities(self, target_id: str, target_type: str) -> None:
        """
        Delete all entity values associated with a target, and delete the entity itself
        if it is no longer referenced elsewhere.
        Parameters:
            target_id (str): The ID of the target (graph, node, or edge).
            target_type (str): The type of the target (e.g., 'graph', 'node', 'edge').
        """
        entity_ids = set()

        # Step 1: Collect all Entity_IDs related to the target across all value tables
        for table in ["Real_Entity_Values", "Int_Entity_Values", "Text_Entity_Values"]:
            self.cursor.execute(
                f"SELECT Entity_ID FROM {table} WHERE Target_ID = ? AND Target_Type = ?",
                (target_id, target_type),
            )
            entity_ids.update(row[0] for row in self.cursor.fetchall())

        if not entity_ids:
            raise ValueError("No entities found for the given target ID and type.")

        # Step 2: Delete value records for this target
        for table in ["Real_Entity_Values", "Int_Entity_Values", "Text_Entity_Values"]:
            self.cursor.execute(
                f"DELETE FROM {table} WHERE Target_ID = ? AND Target_Type = ?",
                (target_id, target_type),
            )

        # Step 3: Remove unreferenced Entity_IDs from Entities table
        for entity_id in entity_ids:
            self.cursor.execute(
                """
                SELECT 1 FROM (
                    SELECT Entity_ID FROM Real_Entity_Values
                    UNION ALL
                    SELECT Entity_ID FROM Int_Entity_Values
                    UNION ALL
                    SELECT Entity_ID FROM Text_Entity_Values
                ) WHERE Entity_ID = ? LIMIT 1
            """,
                (entity_id,),
            )
            still_referenced = self.cursor.fetchone()
            if not still_referenced:
                self.cursor.execute("DELETE FROM Entities WHERE ID = ?", (entity_id,))

        self.connection.commit()

    def _get_entities(self, target_id: str, target_type: str) -> Dict[str, Any]:
        """
        Retrieve all entity values associated with a target (graph, node, or edge).

        Parameters:
            target_id (str): The ID of the target.
            target_type (str): The type of the target (e.g., 'graph', 'node', 'edge').

        Returns:
            dict: A dictionary where keys are entity names and values are their corresponding values.
        """
        entities = {}

        for table in ["Real_Entity_Values", "Int_Entity_Values", "Text_Entity_Values"]:
            self.cursor.execute(
                f"""
                SELECT Entity_ID, Value FROM {table}
                WHERE Target_ID = ? AND Target_Type = ?
            """,
                (target_id, target_type),
            )
            for entity_id, value in self.cursor.fetchall():
                self.cursor.execute(
                    "SELECT Name FROM Entities WHERE ID = ?", (entity_id,)
                )
                entity_name = self.cursor.fetchone()[0]
                entities[entity_name] = value

        return entities

    def check_id(self, id: str) -> bool:
        """
        Check if an ID exists in the current database.

        Parameters:
            id (str): The ID to check.

        Returns:
            bool: True if the ID exists, False otherwise.
        """
        self.cursor.execute(
            "SELECT 1 FROM Graph_Nodes WHERE Node_ID = ? OR Graph_ID = ?",
            (id, id),
        )
        return self.cursor.fetchone() is not None

    def get_all_entities(self, target_type: str) -> List[Dict[str, Any]]:
        """
        Retrieve all entities of a specific type (graph, node, or edge).

        Parameters:
            target_type (str): The type of the target (e.g., 'graph', 'node', 'edge').

        Returns:
            List[Dict[str, Any]]: A list of entity metadata dictionaries (ID, Name, Type).
        """
        if target_type not in ("graph", "node", "edge"):
            raise ValueError("target_type must be 'graph', 'node', or 'edge'.")

        query = """
            SELECT DISTINCT E.ID, E.Name, E.Type
            FROM Entities E
            WHERE E.ID IN (
                SELECT Entity_ID FROM Real_Entity_Values WHERE Target_Type = ?
                UNION
                SELECT Entity_ID FROM Int_Entity_Values WHERE Target_Type = ?
                UNION
                SELECT Entity_ID FROM Text_Entity_Values WHERE Target_Type = ?
            )
            ORDER BY E.Name
            """

        cursor = self.connection.execute(query, (target_type, target_type, target_type))
        return [
            {"ID": row[0], "Name": row[1], "Type": row[2]}
            for row in cursor.fetchall()
            if row[0] is not None and row[1] is not None and row[2] is not None
        ]

    def delete_db(self):
        """Delete the database file."""
        self.connection.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def close(self):
        self.connection.close()
