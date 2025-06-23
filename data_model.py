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

    def __init__(self, name: str):
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

    def _validate_metadata_entry(self, key: str, value):
        """
        Internal method to validate a single metadata key-value pair.

        Raises:
            ValueError, TypeError, or KeyError if validation fails.
        """
        if key == "variant":
            if not (isinstance(value, bool)):
                raise ValueError("variant must be boolean data type")
        elif key == "dimensions":
            if not (
                isinstance(value, list)
                and len(value) == 3
                and all(isinstance(x, int) for x in value)
            ):
                raise ValueError("dimensions must be a list of 3 integers")
        elif key == "cost":
            if not (isinstance(value, (int, float)) and value >= 0):
                raise ValueError("cost must be a non-negative number")
        elif key == "criticality":
            if not (0 <= value <= 1):
                raise ValueError("criticality must be between 0 and 1")
        elif key == "failure_rate":
            if not (isinstance(value, (int, float)) and value >= 0):
                raise ValueError("failure_rate must be a non-negative number")
        elif key == "substitutions":
            if not (isinstance(value, list) and all(isinstance(x, str) for x in value)):
                raise TypeError("substitutions must be a list of strings")
        elif key == "breakability":
            if not (0 <= value <= 1):
                raise ValueError("breakability must be between 0 and 1")
        elif key == "year_range":
            if not (isinstance(value, list) and all(isinstance(x, int) for x in value)):
                raise TypeError("year_range must be a list of integers")
        else:
            return True

    def __init__(
        self,
        name: str,
        full_product: bool,
        manufacturer: str,
        locations: List[str],
        product: Optional[str] = None,
        variant: Optional[bool] = None,
        variant_base_product: Optional[str] = None,
        designation: Optional[str] = None,
        popular_name: Optional[str] = None,
        category: Optional[str] = None,
        part_type: Optional[str] = None,
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
        :param product: The product that the non full_product component is a component of.
        :param variant: Whether or not this component is a variant of another or is the base_model.
        :param variant_base_product: The base_product that the variant is a subset of.
        :param designation: A specific designation of the component used for any external purposes.
        :param popular_name: The popular name, or more generally used name, of this component.
        :param category: The category of this component. Definition of category determined by user.
        :param part_type: The general type of the component. Specific definition of part type is determined by user.
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

        for k, v in {
            "product": product,
            "variant": variant,
            "variant_base_product": variant_base_product,
            "designation": designation,
            "popular_name": popular_name,
            "category": category,
            "type": part_type,
            "dimensions": dimensions,
            "cost": cost,
            "criticality": criticality,
            "failure_rate": failure_rate,
            "substitutions": substitutions,
            "breakability": breakability,
            "year_range": year_range,
        }.items():
            if v is not None:
                self._validate_metadata_entry(k, v)
                self.metadata[k] = v

    def set_metadata(self, key: str, value):
        """
        Add or update a metadata entry for the component.

        Valid keys:
            - "product": str
            - "variant": bool
            - "variant_base_product": str
            - "designation": str
            - "popular_name": str
            - "category": str
            - "type": str
            - "dimensions": List[int] of length 3
            - "cost": float >= 0
            - "criticality": float in [0, 1]
            - "failure_rate": float >= 0
            - "substitutions": List[str]
            - "breakability": float in [0, 1]
            - "year_range": List[int]

        :param key: The metadata key to add or update.
        :param value: The value to assign for the given key.
        :raises ValueError, TypeError: If the value is invalid for the given key.
        """

        self._validate_metadata_entry(key, value)
        self.metadata[key] = value

    def get_metadata(self, key: Optional[str] = None, default=None):
        """
        Retrieve metadata from the component.

        If a key is provided, return the corresponding value or a default if the key is missing.
        If no key is provided, return the entire metadata dictionary.

        :param key: Optional metadata key to look up.
        :param default: Value to return if the key is not found (only used if key is given).
        :return: Metadata value, full metadata dict, or default fallback.
        """
        if key is None:
            return self.metadata
        return self.metadata.get(key, default)


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

    Includes if a component is a part of the base model of another component.
    Additionally includes lead time variable, specific use case determined by the user.
    """

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
        :param base_model: The target component is in the base model of the source component. When the target component can be replaced by a different component, it is interchangeable and those parts that can replace the base model component have this property set to False. If the source component comes with the target component by default, say when you purchase that component as a customer, this property is set to True. (Ex. In a Ford F-150, the engine that comes in the car when you buy it from a dealership is considered the base model, and the REQUIRES relationship between the car and the engine has the base_model property set to True. If the engine is able to be replaced with a different engine, it is interchangeable, and the REQUIRES relationship between the car and that different engine has base_model set to False.)
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
