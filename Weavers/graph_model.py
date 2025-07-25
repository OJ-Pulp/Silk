"""
Graph model for representing nodes and edges in a database.
"""

from abc import ABC
import uuid
from dataclasses import dataclass, field, asdict


@dataclass
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

    name: str 
    """Name of the node to be displayed in GUI tools."""

    id: str = field(default_factory=lambda:str(uuid.uuid4()), init=False)
    """Unique identifier for the node, generated with UUID4 if not provided."""

    def to_dict(self) -> dict:
        """
        Convert any Node subclass to a flat dictionary.
        """
        return asdict(self)

@dataclass
class Edge(ABC):
    """
    Abstract class representing a relationship (edge) between two nodes.

    Each edge has a unique ID.
    Used to define directional links in the graph.

    Class attributes listed here are used to define the fields that will be exported to CSV.
    These fields are NOT inherited by subclasses, so each subclass must define its own attributes.
    This allows for flexibility in defining edges with different properties, say if you want an unweighted graph, you can exclude the weight attribute.
    """

    start_node: str
    """The source node of the edge (must be a Node subclass)."""

    end_node: str
    """The target node of the edge (must be a Node subclass)."""

    def to_dict(self) -> dict:
        """
        Convert any Edge subclass to a flat dictionary.
        """
        return asdict(self)
