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
    
    Class attributes listed here are used to define the fields that will be exported to CSV.
    These fields are NOT inherited by subclasses, so each subclass must define its own attributes.
    This allows for flexibility in defining edges with different properties, say if you want an unweighted graph, you can exclude the weight attribute.
    """

    id: str 
    """Unique identifier for the node, generated if not provided."""

    name: str 
    """Name of the node to be displayed in GUI tools."""

    weight: float = 1.0
    """Weight of the node, default is 1.0."""

    def __init__(self, name: str, id: Optional[str] = None, weight: Optional[float] = 1.0):
        """
        Initialize a Node with a name.

        :param name: The label or identifier of the node.
        """
        self.id = id if id is not None else str(uuid.uuid4())
        self.name = name
        # if weight is not None:
            # self.weight = weight
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

        return row


class Edge(ABC):
    """
    Abstract class representing a relationship (edge) between two nodes.

    Each edge has a unique ID.
    Used to define directional links in the graph.

    Class attributes listed here are used to define the fields that will be exported to CSV.
    These fields are NOT inherited by subclasses, so each subclass must define its own attributes.
    This allows for flexibility in defining edges with different properties, say if you want an unweighted graph, you can exclude the weight attribute.
    """

    start_node: Node
    """The source node of the edge (must be a Node subclass)."""

    end_node: Node
    """The target node of the edge (must be a Node subclass)."""

    # weight: Optional[float] = 1.0
    # """The weight of the edge, default is 1.0."""

    def __init__(self, start_node: Node, end_node: Node):
        """
        Create a directed edge from one node to another.

        :param start_node: The source node (must be a Node subclass).
        :param end_node: The target node (must be a Node subclass).
        :param weight: The weight of the edge, default is 1.0.
        """
        self.start_node = start_node
        self.end_node = end_node
        # self.weight = weight if not None else 1.0

    def __eq__(self, other):
        """
        Check equality with another Edge instance.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if 'other' is an Edge and has the same start and end nodes, as well as weight, False otherwise.
        """
        return isinstance(other, Edge) and \
        self.start_node.id == other.start_node.id and \
        self.end_node.id == other.end_node.id and \
        self.weight == other.weight

    def __hash__(self):
        """
        Compute the hash value for the Edge instance.

        Returns:
            int: The hash of the start_node ID, end_node ID, and weight.
        """
        return hash(self.start_node.id + self.end_node.id + str(self.weight))

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
            "start_node": getattr(self.start_node, "id", None),
            "end_node": getattr(self.end_node, "id", None),
        }

        for k, v in base_attrs.items():
            row[k] = v

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
