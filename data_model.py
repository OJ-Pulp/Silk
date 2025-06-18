from abc import ABC
from typing import List, Optional
import uuid
import random


class Node(ABC):
    """
    Abstract base class for a node in the generated database.

    Each node has a unique ID and a name.
    Examples:
    - Component nodes might have the component name as the name.
    - Manufacturer nodes might use the name of the company (ex. "Ford Motor Company").
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
        full_product: bool,
        manufacturer: str,
        locations: List[str],
        designation: Optional[str] = None,
        popular_name: Optional[str] = None,
        dimensions: Optional[List[int]] = None,
        cost: Optional[float] = None,
        criticality: Optional[float] = None,
        failure_rate: Optional[float] = None,
        substitutions: Optional[List[str]] = None,
        breakability: Optional[float] = None,
        year_range: Optional[List[int]] = None,
    ):
        """
        Initialize a Component with specific attributes.

        :param name: Name of the component.
        :param full_product: Whether or not this component is a full product to be sold to customers.
        :param manufacturer: The manufacturer that produces this component.
        :param locations: The locations that this component is produced in.
        :param designation: A specific designation of the component used for any external purposes.
        :param popular_name: The popular name, or more generally used name, of this component.
        :param dimensions: A list of three integers [length, width, height]. Dimensions are determined by user.
        :param cost: Monetary cost of the component (float). Currency used determined by user.
        :param criticality: Value (0–1) indicating component importance.
        :param failure_rate: Expected failure rate (e.g., failures/hour). Rate determined by user.
        :param substitutions: List of substitute component IDs.
        :param breakability: Value (0–1) indicating likelihood of breakage.
        :param year_range: The range of years this component was produced. Each year must be in the list.
        """
        super().__init__(name)

        # PLAIN NODE DATA
        # These attributes of each component are NOT OPTIONAL
        self.full_product = full_product
        self.manufacturer = manufacturer
        self.locations = locations

        # Empty components list that will be filled when the REQUIRES edges are created.
        self.components = []

        # METADATA
        # All metadata is completely OPTIONAL
        # Include runtime validation for supported arguments
        self.metadata = {}
        if designation is not None:
            self.metadata["designation"] = designation
        if popular_name is not None:
            self.metadata["popular_name"] = popular_name
        if dimensions is not None:
            if len(dimensions) != 3:
                raise ValueError(
                    "dimensions must be a list of three integers [L, W, H]"
                )
            if not all(isinstance(x, int) for x in dimensions):
                raise TypeError("each dimension must be an integer")
            self.metadata["dimensions"] = dimensions
        if cost is not None:
            if cost < 0:
                raise ValueError("cost must be non-negative")
            self.metadata["cost"] = cost
        if criticality is not None:
            if not (0 <= criticality <= 1):
                raise ValueError("criticality must be in [0, 1]")
            self.metadata["criticality"] = criticality
        if failure_rate is not None:
            if not (0 <= failure_rate):
                raise ValueError("failure_rate must be non-negative")
            self.metadata["failure_rate"] = failure_rate
        if substitutions is not None:
            if not all(isinstance(sub_id, str) for sub_id in substitutions):
                raise TypeError("substitutions must be a list of strings (IDs)")
            self.metadata["substitutions"] = substitutions
        if breakability is not None:
            if not (0 <= breakability <= 1):
                raise ValueError("breakability must be in [0, 1]")
            self.metadata["breakability"] = breakability
        if year_range is not None:
            self.metadata["year_range"] = year_range


# class Manufacturer(Node):
#     """
#     Represents a manufacturer / company / supplier / etc. in the supply chain.
#
#     Name represents the name of the organization.
#     """
#
#     def __init__(self, name: str):
#         """
#         Initialize a manufacturer with name attribute.
#
#         :param name: Name of the manufacturer.
#         """
#         super().__init__(name)


# class Plant(Node):
#     """
#     Represents a physical plant / factory in the system.
#
#     Includes attributes like whether or not the plant is within restricted territory.
#     """
#
#     def __init__(self, name: str, restricted_territory: bool):
#         """
#         Initialize a plant with specific attributes.
#
#         :param name: Name of the plant.
#         :param restricted_territory: Whether or not the plant is within restricted territory (boolean). What restricted territory is considered is up to the end user.
#         """
#         super().__init__(name)
#         self.restricted_territory = restricted_territory


class Edge(ABC):
    """
    Abstract class representing a relationship (edge) between two nodes.

    Each edge has a unique ID.
    Used to define directional links in the graph.
    """

    def __init__(self, start_node: Node, end_node: Node):
        """
        Create a directed edge from one node to another.

        :param start_node: The source node (must be a Node subclass).
        :param end_node: The target node (must be a Node subclass).
        """
        self.id = str(uuid.uuid4())
        self.start_node = start_node
        self.end_node = end_node


# class Produces(Edge):
#     """
#     :PRODUCES is the relationship that relates a plant to the components it produces.
#     This relationship should start at a plant and end at a component.
#
#     Includes attributes like quality grade of those components it produces, as well as the daily capacity of the plant to produce that component.
#     """
#
#     def __init__(
#         self,
#         start_node: Plant,
#         end_node: Component,
#         daily_capacity: int,
#         quality_grade: str,
#     ):
#         """
#         Creates a :PRODUCES directed edge from a source Plant to a target Component.
#
#         :param start_node: The source node (must be a Plant).
#         :param end_node: The target node (must be a Component).
#         :param daily_capacity: The number of target components that the source plant can produce in a day.
#         :param quality_grade: A letter grade given to the quality of the product. Can be determined by the source plant's quality ranking.
#         """
#
#         super().__init__(start_node, end_node)
#         self.daily_capacity = daily_capacity
#         self.quality_grade = quality_grade
#
#     #   def add_to_sql(self, database):
#
#     def to_csv_row(self):
#         """
#         Convert this PRODUCES edge into a dictionary suitable for Memgraph CSV export.
#
#         Returns:
#             dict: A dictionary with keys matching Memgraph's required edge format,
#                 including start and end node IDs, relationship type, and edge properties.
#
#         CSV Format:
#             :START_ID(Plant)     - The ID of the producing Plant node
#             :END_ID(Component)   - The ID of the produced Component node
#             :TYPE                - Always 'PRODUCES' for this edge type
#             daily_capacity       - Number of component units the plant can produce per day
#             quality_grade        - Letter grade (e.g., A, B) indicating quality of output
#         """
#
#         return {
#             ":START_ID(Plant)": self.start_node.id,
#             ":END_ID(Component)": self.end_node.id,
#             ":TYPE": "PRODUCES",
#             "daily_capacity": self.daily_capacity,
#             "quality_grade": self.quality_grade,
#         }


class Requires(Edge):
    """
    :REQUIRES is the relationship that relates components to components.
    It states that the source component requires the target component along the supply chain.
    """

    # TODO: ask Cpt. Terry for more clarification on base model edge characteristic, for a better description in the docstring.

    def __append_components_lists(self):
        """
        Keeps the components list of the source components up to date by appending the target component's ID into it.
        Called upon creation of :REQUIRES edges.
        """

        # My type checker gets very angry at me if I don't do this
        assert isinstance(self.start_node, Component), "start_node must be a Component"
        assert isinstance(self.end_node, Component), "end_node must be a Component"

        self.start_node.components.append(self.end_node.id)

    def __init__(
        self,
        start_node: Component,
        end_node: Component,
        base_model: bool,
        lead_time: int,
    ):
        """
        Creates a :REQUIRES relationship from one component to another.
        The start node requires the target node.

        :param start_node: The source node (must be a Component).
        :param end_node: The target node (must be a Component).
        :param base_model:
        :param lead_time: The time it takes for the target component to be shipped & fabricated into the source component. (hours, days, business days)
        """

        super().__init__(start_node, end_node)
        self.base_model = base_model
        self.lead_time = lead_time

        self.__append_components_lists()

    def to_csv_row(self):
        """
        Convert this REQUIRES edge into a dictionary suitable for Memgraph CSV export.

        Returns:
            dict: A dictionary with keys matching Memgraph's required edge format,
                including start and end node IDs, relationship type, and edge properties.

        CSV Format:
            :START_ID(Plant)     - The ID of the producing Plant node
            :END_ID(Component)   - The ID of the produced Component node
            :TYPE                - Always 'REQUIRES' for this edge type
        """

        return {
            ":START_ID(Plant)": self.start_node.id,
            ":END_ID(Component)": self.end_node.id,
            ":TYPE": "REQUIRES",
            "base_model": self.base_model,
            "lead_time": self.lead_time,
        }


# class ManufacturedBy(Edge):
#     pass


def main():
    """
    Example generator for random components.
    """
    components = []
    for i in range(10):
        name = f"Component-{i}"
        dims = [random.randint(1, 10) for _ in range(3)]
        cost = random.uniform(10, 100)
        criticality = random.uniform(0, 1)
        failure_rate = random.uniform(0.001, 0.1)
        substitutions = []
        breakability = random.uniform(0, 1)

        comp = Component(
            name=name,
            full_product=False,
            manufacturer="Test Inc.",
            locations=["Singapore", "New York City, USA"],
            dimensions=dims,
            cost=cost,
            criticality=criticality,
            failure_rate=failure_rate,
            substitutions=substitutions,
            breakability=breakability,
        )
        components.append(comp)

        print(
            f"{components[i].name} has ID: {components[i].id} and criticality of {components[i].metadata['criticality']} and costs {components[i].metadata['cost']}"
        )


if __name__ == "__main__":
    main()
