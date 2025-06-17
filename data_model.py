from abc import ABC
from typing import List
import uuid
import random


class Node(ABC):
    """
    Abstract base class for a node in the generated database.

    Each node has a unique ID and a name.
    Examples:
    - Component nodes might have the component name as the name.
    - Manufacturer nodes might use the company name.
    """

    def __init__(self, name):
        """
        Initialize a Node with a name.

        :param name: The label or identifier of the node.
        """
        self.id = str(uuid.uuid4())
        self.name = name


class Component(Node):
    """
    Represents a physical component in the system.

    Includes attributes like dimensions and cost, as well as reliability metrics.
    """

    def __init__(
        self,
        name: str,
        dimensions: List[int],
        cost: float,
        criticality: float,
        failure_rate: float,
        substitutions: List[str],
        breakability: float,
    ):
        """
        Initialize a Component with specific attributes.

        :param name: Name of the component.
        :param dimensions: A list of three integers [length, width, height].
        :param cost: Monetary cost of the component (float).
        :param criticality: Value (0–1) indicating component importance.
        :param failure_rate: Expected failure rate (e.g., failures/hour).
        :param substitutions: List of substitute component IDs.
        :param breakability: Value (0–1) indicating likelihood of breakage.
        """
        super().__init__(name)

        #  Runtime validation
        #  prevents garbage data
        if len(dimensions) != 3:
            raise ValueError("dimensions must be a list of three integers [L, W, H]")
        if not all(isinstance(x, int) for x in dimensions):
            raise TypeError("each dimension must be an integer")
        if cost < 0:
            raise ValueError("cost must be non-negative")
        if not (0 <= criticality <= 1):
            raise ValueError("criticality must be in [0, 1]")
        if not (0 <= failure_rate):
            raise ValueError("failure_rate must be non-negative")
        if not all(isinstance(sub_id, str) for sub_id in substitutions):
            raise TypeError("substitutions must be a list of strings (IDs)")
        if not (0 <= breakability <= 1):
            raise ValueError("breakability must be in [0, 1]")

        self.dimensions = dimensions
        self.cost = cost
        self.criticality = criticality
        self.failure_rate = failure_rate
        self.substitutions = substitutions
        self.breakability = breakability


class Manufacturer(Node):
    """
    Represents a manufacturer / company / supplier / etc. in the supply chain.

    Name represents the name of the organization.
    """

    def __init__(self, name: str):
        """
        Initialize a manufacturer with name attribute.

        :param name: Name of the manufacturer.
        """
        super().__init__(name)


class Plant(Node):
    """
    Represents a physical plant / factory in the system.

    Includes attributes like whether or not the plant is within restricted territory.
    """

    def __init__(self, name: str, restricted_territory: bool):
        """
        Initialize a plant with specific attributes.

        :param name: Name of the plant.
        :param restricted_territory: Whether or not the plant is within restricted territory (boolean). What restricted territory is considered is up to the end user.
        """
        super().__init__(name)
        self.restricted_territory = restricted_territory


class Edge(ABC):
    """
    Abstract class representing a relationship (edge) between two nodes.

    Used to define directional links in the graph.
    """

    def __init__(self, start_node: Node, end_node: Node):
        """
        Create a directed edge from one node to another.

        :param start_node: The source node (must be a Node subclass).
        :param end_node: The target node (must be a Node subclass).
        """
        self.start_node = start_node
        self.end_node = end_node


class Produces(Edge):
    """
    :PRODUCES is the relationship that relates a plant to the components it produces.
    This relationship should start at a plant and end at a component.

    Includes attributes like quality grade of those components it produces, as well as the daily capacity of the plant to produce that component.
    """

    def __init__(
        self,
        start_node: Plant,
        end_node: Component,
        daily_capacity: int,
        quality_grade: str,
    ):
        """
        Create a directed edge from one node to another.

        :param start_node: The source node (must be a Node subclass).
        :param end_node: The target node (must be a Node subclass).
        """

        super().__init__(start_node, end_node)
        self.daily_capacity = daily_capacity
        self.quality_grade = quality_grade

    def add_to_sql(self, database):

    def to_csv_row(self):
        """
        Convert this PRODUCES edge into a dictionary suitable for Memgraph CSV export.

        Returns:
            dict: A dictionary with keys matching Memgraph's required edge format,
                including start and end node IDs, relationship type, and edge properties.

        CSV Format:
            :START_ID(Plant)     - The ID of the producing Plant node
            :END_ID(Component)   - The ID of the produced Component node
            :TYPE                - Always 'PRODUCES' for this edge type
            daily_capacity       - Number of component units the plant can produce per day
            quality_grade        - Letter grade (e.g., A, B) indicating quality of output
        """

        return {
            ":START_ID(Plant)": self.start_node.id,
            ":END_ID(Component)": self.end_node.id,
            ":TYPE": "PRODUCES",
            "daily_capacity": self.daily_capacity,
            "quality_grade": self.quality_grade,
        }


# Example edge subclasses (not yet implemented):
# class RequiredFor(Edge):
#     pass

# class ManufacturedBy(Edge):
#     pass


def main():
    """
    Example generator for random components.
    """
    components = []

    for i in range(5):
        name = f"Component-{i}"
        dims = [random.randint(1, 10) for _ in range(3)]
        cost = random.uniform(10, 100)
        criticality = random.uniform(0, 1)
        failure_rate = random.uniform(0.001, 0.1)
        substitutions = []
        breakability = random.uniform(0, 1)

        comp = Component(
            name=name,
            dimensions=dims,
            cost=cost,
            criticality=criticality,
            failure_rate=failure_rate,
            substitutions=substitutions,
            breakability=breakability,
        )
        components.append(comp)

        print(f"{components[i].name} has ID: {components[i].id}")


if __name__ == "__main__":
    main()
