import sys
import os
import json
import faker
import logging
import pandas as pd
from typing import List, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data_model import Component, Requires

logging.basicConfig(
    level=logging.DEBUG,  # Show DEBUG and above messages
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# Suppress debug messages from Faker library
logging.getLogger("faker").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Program Start")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "inputdata.json"), "r") as f:
    INPUTDATA = json.load(f)
DESIGNATIONS = INPUTDATA["Designations"]
MANUFACTURERS = INPUTDATA["Manufacturers"]
faker_gen = faker.Faker()
logger.info("Opening Variables Set")


def random_upper():
    return str(faker_gen.random_letter().upper())


# -------------------------------------------------------------------------------------------
#                                      BASE_PRODUCTS
# -------------------------------------------------------------------------------------------
# region BASE_PRODUCTS


def create_base_products(num_base_products) -> List[Component]:
    """
    Minor Function to generate a fake set of base_products.
    :param num_products: The total number of unique model aircraft products to include in the supply chain.
                         Defaults to 40.
    :param variant_distribution: A float (0.0 to 1.0) controlling the proportion of products that will have variants.
                         Defaults to 0.25, meaning roughly 25% of products will be variations.
    :return: A an integer defining the number of variants and a list of Components representing all base_products.
    """

    base_products = []
    designation_keys = list(DESIGNATIONS.keys())
    manufacturer_keys = list(MANUFACTURERS.keys())

    designation_num = {designation_type: 0 for designation_type in designation_keys}

    logger_count = 0

    # Creates a list of Components that are base_products
    for _ in range(num_base_products):
        logger_count += 1
        logger.debug(f"Base Product {logger_count}:")

        # Assigns base_product designation
        designation_mm = faker_gen.random_element(elements=designation_keys)
        designation_num[designation_mm] += 1
        base_product_designation_num = designation_num[designation_mm]
        base_product_designation = f"{designation_mm}-{base_product_designation_num}"
        logger.debug(f"Base Product Designation:        {base_product_designation}")

        # Assigns base_product popular_name and name
        base_product_popular_name = faker_gen.word(part_of_speech="noun").capitalize()
        logger.debug(f"Base Product Popular Name:       {base_product_popular_name}")

        # Assigns base_product manufacturer and manufacturer_location
        base_product_manufacturer = faker_gen.random_element(elements=manufacturer_keys)
        logger.debug(f"Base Product Manufacturer:       {base_product_manufacturer}")
        possible_manufacturer_locations = list(
            MANUFACTURERS[base_product_manufacturer]["Locations"]
        )
        base_product_manufacturer_location = faker_gen.random_element(
            elements=possible_manufacturer_locations
        )

        # Creates base_product node
        base_product = Component(
            name=f"{base_product_popular_name} {base_product_designation}",
            full_product=True,
            variant=False,
            manufacturer=base_product_manufacturer,
            locations=base_product_manufacturer_location,
            designation=designation_mm,
            popular_name=base_product_popular_name,
        )

        # Appends base_product to the overall list of base_products
        base_products.append(base_product)

        logger.debug("\n")

    return base_products

    # endregion


# -------------------------------------------------------------------------------------------
#                                   BASE_PRODUCT_SPRUES
# -------------------------------------------------------------------------------------------
# region BASE_PRODUCT_SPRUES


def create_base_product_sprues(
    base_products: List[Component],
) -> Tuple[List[Component], List[Requires]]:
    # Sets base_product_sprues variables
    base_product_sprues = []
    base_product_sprue_edges = []

    logger_count = 0

    for base_product in base_products:
        logger_count += 1
        logger.debug(f"Base Product {logger_count}:\n")

        for manufacturer in MANUFACTURERS:
            # Creates base_product_sprue node
            base_product_sprue = Component(
                name=f"Sprue {random_upper()}{random_upper()}{random_upper()}{str(faker_gen.random_int(10, 1000000000))}",
                full_product=False,
                product=base_product.id,
                manufacturer=manufacturer,
                locations=faker_gen.random_element(
                    elements=MANUFACTURERS[manufacturer]["Locations"]
                ),
                variant=False,
            )
            logger.debug(f"Base Product Sprue:{base_product_sprue}\n")

            # Appends part to the overall list of parts for this product
            base_product_sprues.append(base_product_sprue)

            # Creates base_product to base_product_sprue edge
            base_product_sprue_edge = Requires(
                start_node=base_product,
                end_node=base_product_sprue,
                base_model=True,
                # In Business Days
                lead_time=faker_gen.random_int(1, 1000),
            )

            logger.debug(f"Base Product Sprue Edge:{base_product_sprue_edge}\n")

            base_product_sprue_edges.append(base_product_sprue_edge)

    return base_product_sprues, base_product_sprue_edges


# endregion

# -------------------------------------------------------------------------------------------
#                                   BASE_PRODUCT_PARTS
# -------------------------------------------------------------------------------------------
# region BASE_PRODUCT_PARTS


def create_base_product_parts(
    base_products: List[Component], base_product_sprues: List[Component]
) -> Tuple[List[Component], List[Requires]]:
    # Sets base_product_parts variables
    base_product_parts = []
    base_product_part_edges = []

    for base_product in base_products:
        PARTS_CATEGORIES = DESIGNATIONS[base_product.metadata["designation"]]["Parts"]

        for part_category, part_list in PARTS_CATEGORIES.items():
            # According to the inputdata.json list of desired parts for that product
            for part_type in part_list:
                # Assigns part manufacturer and manufacturer location
                base_product_part_manufacturer = faker_gen.random_element(
                    elements=list(MANUFACTURERS.keys())
                )

                # Creates part node
                base_product_part = Component(
                    name=f"{part_type} {random_upper()}{random_upper()}{random_upper()}{str(faker_gen.random_int(10, 10000))}",
                    full_product=False,
                    manufacturer=base_product_part_manufacturer,
                    locations=faker_gen.random_element(
                        elements=MANUFACTURERS[base_product_part_manufacturer][
                            "Locations"
                        ]
                    ),
                    product=base_product.id,
                    variant=False,
                    category=part_category,
                    part_type=part_type,
                )

                logger.debug("Base Product Part:")
                logger.debug(base_product_part)
                logger.debug("")

                # Appends part to the overall list of parts for this product
                base_product_parts.append(base_product_part)

                for base_product_sprue in base_product_sprues:
                    if (
                        base_product_part.metadata["product"]
                        == base_product_sprue.metadata["product"]
                        and base_product_part.manufacturer
                        == base_product_sprue.manufacturer
                    ):
                        # Creates base_product to base_product_sprue edge
                        base_product_part_edge = Requires(
                            start_node=base_product_sprue,
                            end_node=base_product_part,
                            base_model=True,
                            # In Business Days
                            lead_time=faker_gen.random_int(1, 1000),
                        )

                        logger.debug("Base Product Part Edge:")
                        logger.debug(base_product_part_edge)
                        logger.debug("")

                        base_product_part_edges.append(base_product_part_edge)

    return base_product_parts, base_product_part_edges


# endregion


# -------------------------------------------------------------------------------------------
#                               RESOLVE_BASE_PRODUCT_SPRUES
# -------------------------------------------------------------------------------------------
# region RESOLVE_SPRUES
def resolve_base_product_sprues(
    base_product_sprues: List[Component],
    base_product_sprue_edges: List[Requires],
    base_product_part_edges: List[Requires],
):
    for base_product_sprue in base_product_sprues:
        edge_count = 0

        for base_product_part_edge in base_product_part_edges:
            assert isinstance(base_product_part_edge, Requires)

            if base_product_part_edge.start_node == base_product_sprue:
                edge_count += 1

        if edge_count == 0:
            base_product_sprues.remove(base_product_sprue)

            logger.debug("Removed Sprue:")
            logger.debug(base_product_sprue)
            logger.debug("")

            for base_product_sprue_edge in base_product_sprue_edges:
                if base_product_sprue_edge.end_node == base_product_sprue:
                    base_product_sprue_edges.remove(base_product_sprue_edge)

                    logger.debug("Removed Sprue Edge:")
                    logger.debug(base_product_sprue)
                    logger.debug("")

    return base_product_sprues, base_product_sprue_edges


# endregion

# -------------------------------------------------------------------------------------------
#                                NODES_AND_EDGES_TO_ROWS
# -------------------------------------------------------------------------------------------
# region NODES_AND_EDGES_TO_ROWS


def component_to_row(component: Component) -> dict:
    metadata = component.metadata
    return {
        "id": component.id,
        "name": component.name,
        "manufacturer": component.manufacturer,
        "locations": component.locations,
        "components": ";".join(component.components) if component.components else "",
        "full_product": component.full_product,
        "component_type": (
            "Product"
            if component.full_product
            else "Sprue"
            if metadata.get("category") is None
            else "Part"
        ),
        "variant": metadata.get("variant", ""),
        "variant_base_product": metadata.get("variant_base_product", ""),
        "designation": metadata.get("designation", ""),
        "popular_name": metadata.get("popular_name", ""),
        "category": metadata.get("category", ""),
        "part_type": metadata.get("part_type", ""),
        "dimensions": metadata.get("dimensions", ""),
        "cost": metadata.get("cost", ""),
        "criticality": metadata.get("criticality", ""),
        "failure_rate": metadata.get("failure_rate", ""),
        "substitutions": metadata.get("substitutions", ""),
        "breakability": metadata.get("breakability", ""),
        "year_range": metadata.get("year_range", ""),
    }


def requires_to_row(edge: Requires) -> dict:
    return {
        "start_node": edge.start_node.id,
        "end_node": edge.end_node.id,
        "lead_time": edge.lead_time,
        "base_model": edge.base_model,
    }


# endregion

# -------------------------------------------------------------------------------------------
#                                NODES_AND_EDGES_TO_CSV
# -------------------------------------------------------------------------------------------
# region NODES_AND_EDGES_TO_CSV


def write_nodes_to_csv(nodes: List[Component], filename: str):
    rows = [component_to_row(c) for c in nodes]
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)


def write_edges_to_csv(edges: List[Requires], filename: str):
    rows = [requires_to_row(e) for e in edges]
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)


# endregion

# -------------------------------------------------------------------------------------------
#                                    MAIN_FUNCTION
# -------------------------------------------------------------------------------------------
# region MAIN_FUNCTION


def main(num_products: int = 40, variant_distribution: float = 0.25):
    """
    Main Function to generate a fake supply chain for model aircrafts.
    :param num_products: The total number of unique model aircraft products to include in the supply chain.
                         Defaults to 40.
    :param variant_distribution: A float (0.0 to 1.0) controlling the proportion of products that will have variants.
                         Defaults to 0.25, meaning roughly 25% of products will be variations.
    :return: A dictionary representing the supply chain.
    """

    # Sets overall variables
    num_variants = int(num_products * variant_distribution)
    num_base_products = num_products - num_variants

    base_products = create_base_products(num_base_products)
    base_product_sprues, base_product_sprue_edges = create_base_product_sprues(
        base_products
    )
    base_product_parts, base_product_part_edges = create_base_product_parts(
        base_products, base_product_sprues
    )
    base_product_sprues, base_product_sprue_edges = resolve_base_product_sprues(
        base_product_sprues, base_product_sprue_edges, base_product_part_edges
    )

    # Collect all components and edges
    base_components = base_products + base_product_sprues + base_product_parts
    base_edges = base_product_sprue_edges + base_product_part_edges

    # Write to CSV
    write_nodes_to_csv(base_components, "output/test5_base_components.csv")
    write_edges_to_csv(base_edges, "output/test5_base_edges.csv")

if __name__ == "__main__":
    main()
