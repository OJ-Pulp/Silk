"""
Graph model for representing nodes and edges in a database.
"""

from abc import ABC
from typing import List, Optional
import uuid
from pathlib import Path
import pandas as pd


class Node(ABC):
    """
    Abstract base class for a node in the generated database.

    Each node has a unique ID and a name.
    Examples:
    - Component nodes might have the component name as the name.
    - Manufacturer nodes might use the name of the company (ex. "Ford Motor Company").
    """

    # Must be overridden in subclasses to specify which fields to export
    __csv_fields__: List[str]

    def __init__(self, name: str, id: Optional[str] = None):
        """
        Initialize a Node with a name.

        :param name: The label or identifier of the node.
        """
        self.id = id if id is not None else str(uuid.uuid4())
        self.name = name
        self.metadata: dict

    def __eq__(self, other):
        return isinstance(other, Node) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def to_dict(self) -> dict:
        """
        Convert any Node subclass to a flat dictionary.
        If __csv_fields__ is defined, it controls which fields are exported.
        Otherwise, export all simple attributes + metadata.
        """
        row = {"id": self.id, "name": self.name}

        # Get instance dict without private/internal
        base_attrs = {
            k: v
            for k, v in self.__dict__.items()
            if not k.startswith("_") and k not in {"id", "name", "metadata"}
        }

        # Flatten flat lists and basic types
        for k, v in base_attrs.items():
            if isinstance(v, list):
                row[k] = ";".join(map(str, v))
            else:
                row[k] = v

        # Add metadata
        if hasattr(self, "metadata"):
            for k, v in self.metadata.items():
                row[k] = v

        # Optionally prune to __csv_fields__
        if self.__csv_fields__:
            row = {k: row.get(k, "") for k in self.__csv_fields__}

        return row


class Edge(ABC):
    """
    Abstract class representing a relationship (edge) between two nodes.

    Each edge has a unique ID.
    Used to define directional links in the graph.
    """

    def __init__(self, start_node: Node, end_node: Node, weight: float = 1.0):
        """
        Create a directed edge from one node to another.

        :param start_node: The source node (must be a Node subclass).
        :param end_node: The target node (must be a Node subclass).
        :param weight: The weight of the edge, default is 1.0.
        """
        self.id = str(uuid.uuid4())
        self.start_node = start_node
        self.end_node = end_node
        self.weight = weight

    def __eq__(self, other):
        """
        Check equality with another Edge instance.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if 'other' is an Edge and has the same id, False otherwise.
        """
        return isinstance(other, Edge) and self.id == other.id

    def __hash__(self):
        """
        Compute the hash value for the Edge instance.

        Returns:
            int: The hash of the Edge's id.
        """
        return hash(self.id)

    def to_dict(self) -> dict:
        """
        Convert any Edge subclass to a flat dictionary.
        If __csv_fields__ is defined, it controls which fields are exported.
        Otherwise, export all simple attributes.
        """
        # Get instance dict without private/internal
        base_attrs = {
            k: v
            for k, v in self.__dict__.items()
            if not k.startswith("_") and k not in {"start_node", "end_node"}
        }

        # Start with start_id, end_id (omit 'id')
        row = {
            "start_id": getattr(self.start_node, "id", None),
            "end_id": getattr(self.end_node, "id", None),
        }

        for k, v in base_attrs.items():
            row[k] = v

        # Optionally prune to __csv_fields__
        if hasattr(self, "__csv_fields__") and getattr(self, "__csv_fields__"):
            row = {k: row.get(k, "") for k in getattr(self, "__csv_fields__")}

        return row

    @staticmethod
    def write_to_csv(edges, filename: Path):
        """
        Converts the passed Edges to a CSV file.

        :param edges: A list of Edge instances to write to CSV.
        :type edges: List[Edge]
        :param filename: The path to the CSV file to write.
        :type filename: Path
        :raises FileNotFoundError: If the directory for the filename does not exist.
        """
        filename.parent.mkdir(parents=True, exist_ok=True)
        rows = [e.to_dict() for e in edges]
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False)
