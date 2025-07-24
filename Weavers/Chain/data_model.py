"""Data model for components and their requirement relationships in the supply chain."""

from dataclasses import dataclass
from typing import List, Optional

from Weavers.graph_model import Node, Edge

# This JSON schema defines the structure for this specific data model.
# It changes depending on which Weaver is being used.
# This should only be touched by engineers who are familiar with the
# data model and its requirements, and not by end users.
# It is used to validate the data before it is saved to the database,
# and defines how the end user is expected to enter the data.
DATA_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "Designations": {
            "type": "object",
            "minProperties": 1,
            "patternProperties": {
                "^[A-Z]$": {
                    "type": "object",
                    "properties": {
                        "Type": {"type": ["string", "null"]},
                        "Number of Parts": {"type": ["integer", "null"]},
                        "Vital Parts": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1,
                        },
                        "Parts": {
                            "type": "object",
                            "minProperties": 1,
                            "additionalProperties": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 1,
                            },
                        },
                    },
                    "required": ["Vital Parts", "Parts"],
                    "additionalProperties": False,
                }
            },
        },
        "Manufacturers": {
            "type": "object",
            "minProperties": 1,
            "patternProperties": {
                ".*": {
                    "type": "object",
                    "properties": {
                        "ID": {
                            "type": "string",
                            "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
                        },
                        "Locations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1,
                        },
                    },
                    "required": ["Locations"],
                    "additionalProperties": False,
                }
            },
        },
    },
    "required": ["Designations", "Manufacturers"],
    "additionalProperties": False,
}

@dataclass
class Component(Node):
    """
    Represents a physical component in the system.

    Includes attributes like dimensions, cost, failure rate, and more. 
    """

    # id: str 
    # field(init=False) 
    # """Unique identifier for the component, generated if not provided."""

    name: str 
    """Name of the node to be displayed in GUI tools."""

    manufacturer: str 
    """The manufacturer that produces this component."""

    locations: str | List[str] 
    """The location(s) that this component is produced in."""

    full_product: bool 
    """Whether or not this component is a full product to be sold to customers."""

    component_type: Optional[str] = None 
    """Level of the component in relation to other components (e.g., sprue, part, assembly)"""
    
    product: Optional[str] = None
    """The product that the non full_product component is a component of. If full_product is True, this is None."""

    variant: Optional[bool] = None 
    """Whether or not this component is a variant of another component. False if it is the base model."""

    variant_base_product: Optional[str] = None 
    """The base product that the variant is a subset of"""

    vital: Optional[bool] = None 
    """Indicates whether the component is vital for a variant"""

    designation: Optional[str] = None 
    """Specific designation of the component used for any external purposes"""

    popular_name: Optional[str] = None 
    """More commonly used name for the component"""

    category: Optional[str] = None 
    """Category of the component (e.g., electronics, mechanical)"""

    part_type: Optional[str] = None 
    """General type of the component"""

    dimensions: Optional[List[int]] = None  
    """List of [length, width, height]"""

    cost: Optional[float] = None  
    """Monetary cost of the component"""

    failure_rate: Optional[float] = None  
    """Expected failure rate (e.g., failures/hour)"""

    substitutions: Optional[List[str]] = None  
    """List of substitute component IDs"""

    breakability: Optional[float] = None  
    """Likelihood of breakage (0–1)"""

    year_range: Optional[List[int]] = None  
    """Range of years this component was produced"""


    #     """
    #     Initialize a Component with specific attributes.
    #
    #     :param name: Name of the component.
    #     :param manufacturer: The manufacturer that produces this component.
    #     :param locations: The location(s) that this component is produced in.
    #     :param full_product: Whether or not this component is a full product to be sold to customers.
    #     :param id: If the user wants to input an id instead of having a randomly generated one.
    #     :param component_type: Level of the component in relation to other components.
    #     :param product: The product that the non full_product component is a component of.
    #     :param variant: Whether or not this component is a variant of another or is the base_model.
    #     :param variant_base_product: The base_product that the variant is a subset of.
    #     :param vital: Indicates whether or not the component is vital for a variant.
    #     :param designation: A specific designation of the component used for any external purposes.
    #     :param popular_name: The popular name, or more generally used name, of this component.
    #     :param category: The category of this component. Definition of category determined by user.
    #     :param part_type: The general type of the component. Specific definition of part type is determined by user.
    #     :param dimensions: A list of three integers [length, width, height]. Dimensions are determined by user.
    #     :param cost: Monetary cost of the component (float). Currency used determined by user.
    #     :param failure_rate: Expected failure rate (e.g., failures/hour). Rate determined by user.
    #     :param substitutions: List of substitute component IDs.
    #     :param breakability: Value (0–1) indicating likelihood of breakage.
    #     :param year_range: The range of years this component was produced. Each year must be in the list.
    #     """
@dataclass
class Requires(Edge):
    """
    :REQUIRES is the relationship that relates components to components.
    It states that the source component requires the target component along the supply chain.

    Includes if a component is a part of the base model of another component.
    Additionally includes lead time variable, specific use case determined by the user.
    """
    
    start_node: Node
    """The source node of the edge (must be a Node subclass)."""

    end_node: Node
    """The target node of the edge (must be a Node subclass)."""

    base_model: bool
    """Indicates if the target component is in the base model of the source component."""

    lead_time: int
    """The time it takes for the target component to be shipped & fabricated into the source component (in hours, days, business days)."""
    #     Creates a :REQUIRES relationship from one component to another.
    #     The start node requires the target node.
    #
    #     :param start_node: The source node (must be a Component).
    #     :param end_node: The target node (must be a Component).
    #     :param base_model: The target component is in the base model of the source component. When the target component can be replaced by a different component, it is interchangeable and those parts that can replace the base model component have this property set to False. If the source component comes with the target component by default, say when you purchase that component as a customer, this property is set to True. (Ex. In a Ford F-150, the engine that comes in the car when you buy it from a dealership is considered the base model, and the REQUIRES relationship between the car and the engine has the base_model property set to True. If the engine is able to be replaced with a different engine, it is interchangeable, and the REQUIRES relationship between the car and that different engine has base_model set to False.)
    #     :param lead_time: The time it takes for the target component to be shipped & fabricated into the source component. (hours, days, business days)
