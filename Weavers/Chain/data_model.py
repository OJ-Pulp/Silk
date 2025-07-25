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
    """Category of the component (e.g., electronics, mechanical). Definition of category determined by user."""

    part_type: Optional[str] = None 
    """The general type of the component. Specific definition of part type is determined by user."""

    dimensions: Optional[List[int]] = None  
    """List of [length, width, height]"""

    cost: Optional[float] = None  
    """Monetary cost of the component. Currency used determined by user."""

    failure_rate: Optional[float] = None  
    """Expected failure rate (e.g., failures/hour). Rate determined by user."""

    substitutions: Optional[List[str]] = None  
    """List of substitute component IDs"""

    breakability: Optional[float] = None  
    """Likelihood of breakage (0–1)"""

    year_range: Optional[List[int]] = None  
    """The range of years this component was produced. Each year must be in the list."""


@dataclass
class Requires(Edge):
    """
    :REQUIRES is the relationship that relates components to components.
    It states that the source component requires the target component along the supply chain.

    Includes if a component is a part of the base model of another component.
    Additionally includes lead time variable, specific use case determined by the user.
    """
    
    start_node: str
    """The source node of the edge (must be a Node subclass)."""

    end_node: str
    """The target node of the edge (must be a Node subclass)."""

    base_model: bool
    """The target component is in the base model of the source component. When the target component can be replaced by a different component, it is interchangeable and those parts that can replace the base model component have this property set to False. If the source component comes with the target component by default, say when you purchase that component as a customer, this property is set to True. (Ex. In a Ford F-150, the engine that comes in the car when you buy it from a dealership is considered the base model, and the REQUIRES relationship between the car and the engine has the base_model property set to True. If the engine is able to be replaced with a different engine, it is interchangeable, and the REQUIRES relationship between the car and that different engine has base_model set to False.)"""

    lead_time: int
    """The time it takes for the target component to be shipped & fabricated into the source component (in hours, days, business days)."""
