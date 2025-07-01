"""
OVERALL CHAINWEAVER
"""

# Standard
import copy
import json
import logging
import traceback
import uuid
from pathlib import Path
from typing import List, Tuple

# -------------------------------------------------------------------------------------------
#                                   LOGGING_SETTINGS
# -------------------------------------------------------------------------------------------
# region LOGGING_SETTINGS

SUCCESS = 0
FAILURE = 1
INTERRUPTED = 130

# Configures for logging showing messages level INFO and above
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Suppresses debug messages from faker library
logging.getLogger("faker").setLevel(logging.INFO)

# endregion

# Third-Party
try:
    import faker
    import pandas as pd
    from jsonschema import validate, ValidationError
except ModuleNotFoundError as e:
    logger.critical(f"{type(e).__name__}: Missing Required Module '{e.name}' -- Try 'python -m pip install {e.name}' -- Exiting")
    raise SystemExit(FAILURE)

# Local
try:
    from Weavers.Chain.data_model import Component, Requires
    #import input_utils
except ModuleNotFoundError as e:
    logger.critical(f"{type(e).__name__}: Missing Required Local Module '{e.name}' -- Check that '{e.name}.py' is in the Same Directory as 'ChainWeaver.py' -- Exiting")
    raise SystemExit(FAILURE)

logger.info("Program Start")

FAKER_GEN = faker.Faker()
logger.info("Global Variables Set")

# -------------------------------------------------------------------------------------------
#                                      BASE_PRODUCTS
# -------------------------------------------------------------------------------------------
# region BASE_PRODUCTS

def create_base_products(
    num_base_products: int, 
    designations_dict: dict, 
    manufacturers_dict: dict
) -> List[Component]:
    """
    Generates a fake dataset of base products and their data.

    :param `num_base_products`: The total number of unique base products to include in the supply chain.
    :type `num_base_products`: int
    :param `designations_dict`: The 'Designation' category of 'resolved_inputdata'.
    :type `designations_dict`: dict
    :param `manufacturers_dict`: The 'Manufacturer' category of 'resolved_inputdata'.
    :type `manufacturers_dict`: dict

    :return: A list of base products.
    :rtype: List[Component]
    """

    # Sets empty lists to collect products along with other necessary variables
    base_products = []
    designation_keys = list(designations_dict.keys())
    manufacturer_keys = list(manufacturers_dict.keys())
    designation_counter = {designation_type: 0 for designation_type in designation_keys}

    # Creates all base products
    for i in range(num_base_products):
        logger.debug(f"Base Product {i}:")

        # Generates base product data
        selected_designation = FAKER_GEN.random_element(elements=designation_keys)
        designation_counter[selected_designation] += 1
        designation = f"{selected_designation}-{designation_counter[selected_designation]}"
        popular_name = FAKER_GEN.word(part_of_speech="noun").capitalize()
        manufacturer = FAKER_GEN.random_element(elements=manufacturer_keys)

        # Creates 'base_product' Component(Node)
        base_product = Component(
            name=f"{popular_name} {designation}",
            full_product=True,
            variant=False,
            manufacturer=manufacturer,
            locations=FAKER_GEN.random_element(elements=list(manufacturers_dict[manufacturer]["Locations"])),
            designation=selected_designation,
            popular_name=popular_name,
        )

        # Appends 'base_product' Component(Node) to the overall list of 'base_products'
        base_products.append(base_product)
        logger.debug(base_product)
        logger.debug("")

    return base_products

# endregion

# -------------------------------------------------------------------------------------------
#                                   BASE_PRODUCT_SPRUES
# -------------------------------------------------------------------------------------------
# region BASE_PRODUCT_SPRUES

def create_base_product_sprues(
    base_products: List[Component], 
    manufacturers_dict: dict
) -> Tuple[List[Component], List[Requires]]:
    """
    Generates a fake dataset of base product sprues and sprue edges and their data.

    :param `base_products`: A list of base products and their data.
    :type `base_products`: List[Component]
    :param `manufacturers_dict`: The 'Manufacturer' category of 'resolved_inputdata'.
    :type `manufacturers_dict`: dict

    :return: A list of base product sprues.
    :rtype: List[Component]
    :return: A list of edges between base products and base product sprues.
    :rtype: List[Requires]
    """

    # Sets empty lists to collect sprues and edges along with other necessary variables
    base_product_sprues = []
    base_product_sprue_edges = []
    manufacturer_keys = list(manufacturers_dict.keys())

    # Creates all base product sprues and edges
    for i, base_product in enumerate(base_products, start=1):
        logger.debug(f"Base Product {i}:")

        for manufacturer in manufacturer_keys:
            logger.debug(f"{manufacturer} Base Product Sprue:")

            # Creates 'base_product_sprue' Component(Node)
            base_product_sprue = Component(
                name=f"Sprue {FAKER_GEN.bothify(text='???########')}",
                full_product=False,
                product=base_product.id,
                manufacturer=manufacturer,
                locations=FAKER_GEN.random_element(elements=manufacturers_dict[manufacturer]["Locations"]),
                variant=False,
            )

            # Appends 'base_product_sprue' Component(Node) to the overall list of 'base_product_sprues'
            base_product_sprues.append(base_product_sprue)
            logger.debug(base_product_sprue)
            logger.debug("")

            logger.debug(f"{manufacturer} Base Product Sprue Edge:")

            # Creates 'base_product' to 'base_product_sprue' Requires(Edge)
            base_product_sprue_edge = Requires(
                start_node=base_product,
                end_node=base_product_sprue,
                base_model=True,
                lead_time=FAKER_GEN.random_int(1, 1000),    # In Business Days
            )

            # Appends 'base_product_sprue_edge' Requires(Edge) to the overall list of 'base_product_sprue_edges'
            base_product_sprue_edges.append(base_product_sprue_edge)
            logger.debug(base_product_sprue_edge)
            logger.debug("")

    return base_product_sprues, base_product_sprue_edges

# endregion

# -------------------------------------------------------------------------------------------
#                                   BASE_PRODUCT_PARTS
# -------------------------------------------------------------------------------------------
# region BASE_PRODUCT_PARTS

def create_base_product_parts(
    base_products: List[Component], 
    base_product_sprues: List[Component], 
    designations_dict: dict, 
    manufacturers_dict: dict
) -> Tuple[List[Component], List[Requires], List[Component]]:
    """
    Generates a fake dataset of base product parts and part edges and their data.

    :param `base_products`: A list of base products and their data.
    :type `base_products`: List[Component]
    :param `base_product_sprues`: A list of base product sprues and their data.
    :type `base_product_sprues`: List[Component]
    :param `designations_dict`: The 'Designation' category of 'resolved_inputdata'.
    :type `designations_dict`: dict
    :param `manufacturers_dict`: The 'Manufacturer' category of 'resolved_inputdata'.
    :type `manufacturers_dict`: dict

    :return: A list of base product parts.
    :rtype: List[Component]
    :return: A list of edges between base product sprues and base product parts.
    :rtype: List[Requires]
    :return: A list of sprues that contain vital base product parts.
    :rtype: List[Component]
    """

    # Sets empty lists to collect parts, edges, and vital sprues along with other necessary variables
    base_product_parts = []
    base_product_part_edges = []
    vital_base_product_sprues = []
    designation_keys = list(designations_dict.keys())
    manufacturer_keys = list(manufacturers_dict.keys())

    # Creates all base product parts and edges
    for i, base_product in enumerate(base_products, start=1):
        logger.debug(f"Base Product {i}:")

        parts_categories = designations_dict[base_product.metadata["designation"]]["Parts"]
        for part_category, part_list in parts_categories.items():
            for part_type in part_list:
                logger.debug(f"{part_type}:")

                # Generates base product part data
                base_product_part_manufacturer = FAKER_GEN.random_element(elements=list(manufacturer_keys))
                if part_type in designations_dict[base_product.metadata["designation"]]["Vital Parts"]:
                    base_product_part_vital = True
                else:
                    base_product_part_vital = False

                # Creates 'base_product_part' Component(Node)
                base_product_part = Component(
                    name=f"{part_type} {FAKER_GEN.bothify(text='???#####')}",
                    full_product=False,
                    manufacturer=base_product_part_manufacturer,
                    locations=FAKER_GEN.random_element(elements=manufacturers_dict[base_product_part_manufacturer]["Locations"]),
                    product=base_product.id,
                    variant=False,
                    vital=base_product_part_vital,
                    category=part_category,
                    part_type=part_type,
                )

                # Appends 'base_product_part' Component(Node) to the overall list of 'base_product_parts'
                base_product_parts.append(base_product_part)
                logger.debug(base_product_part)
                logger.debug("")

                for base_product_sprue in base_product_sprues:
                    if base_product_part.metadata["product"] == base_product_sprue.metadata["product"] \
                        and base_product_part.manufacturer == base_product_sprue.manufacturer:
                        logger.debug(f"{part_type} Edge:")

                        # Creates 'base_product_sprue' to 'base_product_part' Requires(Edge)
                        base_product_part_edge = Requires(
                            start_node=base_product_sprue,
                            end_node=base_product_part,
                            base_model=True,
                            lead_time=FAKER_GEN.random_int(1, 1000),    # In Business Days
                        )

                        # Appends 'base_product_sprue_edge' Requires(Edge) to the overall list of 'base_product_sprue_edges'
                        base_product_part_edges.append(base_product_part_edge)
                        logger.debug(base_product_part_edge)
                        logger.debug("")

                        # If the part being added to that sprue is vital
                        # Appends 'base_product_sprue' Component(Node) to the overall list of 'vital_base_product_sprues'
                        if base_product_part_vital == True:
                            vital_base_product_sprues.append(base_product_sprue)

    return base_product_parts, base_product_part_edges, vital_base_product_sprues

# endregion

# -------------------------------------------------------------------------------------------
#                               RESOLVE_BASE_PRODUCT_SPRUES
# -------------------------------------------------------------------------------------------
# region RESOLVE_BASE_PRODUCT_SPRUES

def resolve_base_product_sprues(
    base_product_sprues: List[Component],
    base_product_sprue_edges: List[Requires],
    base_product_part_edges: List[Requires],
) -> Tuple[List[Component], List[Requires]]:
    """
    Generates the new resolved lists of sprues and sprue edges to replace the old lists.

    :param `base_product_sprues`: A list of base product sprues and their data.
    :type `base_product_sprues`: List[Component]
    :param `base_product_sprue_edges`: A list of base produuct sprue edges and their data.
    :type `base_product_sprue_edges`: List[Requires]
    :param `base_product_part_edges`: A list of base product part edges and their data.
    :type `base_product_part_edges`: List[Requires]

    :return: A new resolved list of base product sprues.
    :rtype: List[Components]
    :return: A new resolved list of base product sprue edges.
    :rtype: List[Requires]
    """
        
    # Sets empty lists to collect sprues and edges to keep
    base_sprues_keep = []
    base_sprue_edges_keep = []

    # Checks that all sprues are used
    for i, base_product_sprue in enumerate(base_product_sprues, start=1):
        logger.debug(f"Sprue {i}:")
        
        # Checks if a sprue has any edges to parts
        has_edge = any(edge.start_node == base_product_sprue for edge in base_product_part_edges)
        if has_edge:
            # Appends 'base_product_sprue' Component(Node) to the overall new list of 'base_product_sprues'
            base_sprues_keep.append(base_product_sprue)
            logger.debug(f"Kept Sprue {i}")

            # Appends 'base_product_sprue_edge' Requires(Edge) to the overall new list of 'base_product_sprue_edges'
            base_sprue_edges_keep.extend(e for e in base_product_sprue_edges if e.end_node == base_product_sprue)
            logger.debug(f"Kept Edges for Sprue {i}")
            logger.debug("")
        else:
            logger.debug(f"Removed Base Product Sprue {i}:")
            logger.debug(base_product_sprue)
            logger.debug("")

    return base_sprues_keep, base_sprue_edges_keep

# endregion

# -------------------------------------------------------------------------------------------
#                                   NAMING_CONVENTIONS
# -------------------------------------------------------------------------------------------
# region NAMING_CONVENTIONS

def get_next_letter(current_letter):
    """
    Minor Function to get the variant_designation_letter of multi-layer variants.
    :param current_letter: The variant_designation_letter of the variant on its last variation.
    :return: A string of one capital letter to be the next variant_designation_letter.
    """
    # Get the ASCII value of the current letter and adds 1 to get the ASCII of the next
    next_char_code = ord(current_letter) + 1
    
    # If it goes past "Z", wrap around to "A"
    if next_char_code > ord("Z"):
        next_char_code = ord("A")
    
    # Converts back to chr and outputs as a string of a standard capital letter
    return chr(next_char_code)

def get_next_test_output_filename(base_name: str, extension: str, output_dir: Path = Path("output")) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    index = 1
    if not extension.startswith("."):
        extension = "." + extension
    while True:
        filename = output_dir / f"test{index}_{base_name}{extension}"
        if not filename.exists():
            logger.warning(index)
            return filename
        index += 1

# endregion

# -------------------------------------------------------------------------------------------
#                                   VARIANT_PRODUCTS
# -------------------------------------------------------------------------------------------
# region VARIANT_PRODUCTS

def create_variant_products(base_products, num_variants: int = 10)  -> List[Component]:

    # Sets variant variables
    variant_products = []

    # 2. Create list of variants
    for i in range(num_variants):
        logger.debug(f"Variant Product {i}:\n")

        # Assigns variant base_product
        variant_base_product = FAKER_GEN.random_element(elements=base_products)
        assert isinstance(variant_base_product, Component) 

        # Assigns variant designation
        variant_base_designation = variant_base_product.metadata["designation"]
        if variant_base_designation[-1].isdigit():
            variant_designation_letter = "A"
        else:
            variant_designation_letter = get_next_letter(variant_base_designation[-1])
        variant_designation = f"{variant_base_designation}{variant_designation_letter}"
        logger.debug(f"Variant Designation:        {variant_designation}")

        # Assigns variant manufacturer and manufacturer_location
        variant_manufacturer = variant_base_product.manufacturer
        possible_manufacturer_locations = list(MANUFACTURERS[variant_manufacturer]["Locations"])
        variant_manufacturer_location = FAKER_GEN.random_element(elements=possible_manufacturer_locations)
        logger.debug(f"Variant Manufacturer:       {variant_manufacturer}")

        # Creates variant_product node
        variant_product = Component(
            name=f"{variant_base_product.metadata['popular_name']} {variant_designation}", 
            manufacturer=variant_manufacturer,
            locations=variant_manufacturer_location, 
            full_product=True,
            variant=True,
            variant_base_product=variant_base_product.id,
            designation=variant_designation, 
            popular_name=variant_base_product.metadata["popular_name"]
            )

        # Appends variant_product to the overall list of variant_products
        variant_products.append(variant_product)

        logger.debug("/n")
    
    return variant_products

# endregion

# -------------------------------------------------------------------------------------------
#                                    MAIN_FUNCTION
# -------------------------------------------------------------------------------------------
# region MAIN_FUNCTION

def main(num_products: int = 40, variant_distribution: float = 0.25):
    """
    Main Function to generate a fake supply chain.

    :param num_products: The total number of unique model aircraft products to include in the supply chain.
                         Defaults to 40.
    :param variant_distribution: A float (0.0 to 1.0) controlling the proportion of products that will have variants.
                         Defaults to 0.25, meaning roughly 25% of products will be variations.
    :return: A dictionary representing the supply chain.
    """

    logger.info("Main Start")

    # Validates and resolves 'inputdata.json'
    try:
        inputdata = validate_inputdata()
    except Exception as e:
        logger.critical(f"{type(e).__name__}: {e}")
        raise SystemExit(FAILURE)

    resolved_inputdata = resolve_inputdata(inputdata)
    logger.info("Inputs Accepted")

    # Sets overall variables
    logger.debug("Local Main Variables: ")
    logger.debug(f"Num_Products:        {num_products}")
    logger.debug(f"Variant_Distribution:        {variant_distribution}")
    num_variants = int(num_products * variant_distribution)
    logger.debug(f"Num_Variants:        {num_variants}")
    num_base_products = num_products - num_variants
    logger.debug(f"Num_Base_Products:        {num_base_products}")
    designations_dict = resolved_inputdata["Designations"]
    manufacturers_dict = resolved_inputdata["Manufacturers"]
    logger.info("Local Main Variables Set")

    base_products = create_base_products(num_base_products, designations_dict, manufacturers_dict)
    logger.info("Base Products Created")
    base_product_sprues, base_product_sprue_edges = create_base_product_sprues(base_products)
    logger.info("Base Product Sprues Created")
    base_product_parts, base_product_part_edges, vital_base_product_sprues = create_base_product_parts(base_products, base_product_sprues)
    logger.info("Base Product Parts Created")
    resolved_base_product_sprues, resolved_base_product_sprue_edges = resolve_base_product_sprues(base_product_sprues, base_product_sprue_edges, base_product_part_edges)
    logger.info("Base Product Sprues Resolved")
    variant_products = create_variant_products(base_products, num_variants)
    logger.info("Variant Products Created")

    # Collect all components and edges
    base_components = base_products + resolved_base_product_sprues + base_product_parts
    variant_components = variant_products
    components = base_components + variant_components
    base_edges = resolved_base_product_sprue_edges + base_product_part_edges
    logger.info("Lists Consolidated")

    # Write to CSV
    Component.write_to_csv(components, get_next_test_output_filename("components", "csv"))
    Requires.write_to_csv(base_edges, get_next_test_output_filename("edges", "csv"))
    logger.info("CSV Files Created")

    logger.info("Main End")

# endregion

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        logger.warning(f"{type(e).__name__}: Input Processing Interrupted by User -- Exiting")
        raise SystemExit(INTERRUPTED)

logger.info("Program End")
