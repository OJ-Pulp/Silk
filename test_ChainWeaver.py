import json
import uuid
import faker
import logging
from data_model import Component, Requires
from typing import List, Tuple, Optional

logging.basicConfig(
    level=logging.DEBUG,  # Show DEBUG and above messages
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# Suppress debug messages from Faker library
logging.getLogger("faker").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Program Start")

INPUTDATA = json.load(open(f"C:/Users/bgarringer/Desktop/GitHub/Silk/inputdata.json", "r"))
DESIGNATIONS = INPUTDATA["Designations"] # List of Dicts
MANUFACTURERS = INPUTDATA["Manufacturers"] # List of Dicts
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
    for i in range(num_base_products):

        logger_count += 1
        logger.debug(f"Base Product {logger_count}:")

        # Assigns base_product designation
        designation_mm = faker_gen.random_element(elements=designation_keys)
        designation_num[designation_mm] += 1
        base_product_designation_num = designation_num[designation_mm]
        base_product_designation = f"{designation_mm}-{base_product_designation_num}"
        logger.debug(f"Base Product Designation:        {base_product_designation}")

        # Assigns base_product popular_name and name
        base_product_popular_name = faker_gen.word(part_of_speech='noun').capitalize()
        logger.debug(f"Base Product Popular Name:       {base_product_popular_name}")

        # Assigns base_product manufacturer and manufacturer_location
        base_product_manufacturer = faker_gen.random_element(elements=manufacturer_keys)
        logger.debug(f"Base Product Manufacturer:       {base_product_manufacturer}")
        possible_manufacturer_locations = list(MANUFACTURERS[base_product_manufacturer]["Locations"])
        base_product_manufacturer_location = faker_gen.random_element(elements=possible_manufacturer_locations)

        # Creates base_product node
        base_product = Component(
            name=f"{base_product_popular_name} {base_product_designation}", 
            full_product=True,
            variant=False,
            manufacturer=base_product_manufacturer,
            locations=base_product_manufacturer_location, 
            designation=designation_mm, 
            popular_name=base_product_popular_name
            )

        # Appends base_product to the overall list of base_products
        base_products.append(base_product)

        logger.debug(f"")

    return base_products

    # endregion


# -------------------------------------------------------------------------------------------
#                                   BASE_PRODUCT_SPRUES
# -------------------------------------------------------------------------------------------
# region BASE_PRODUCT_SPRUES

def create_base_product_sprues(base_products: List[Component]) -> Tuple[List[Component], List[Requires]]:
    
    # Sets base_product_sprues variables
    base_product_sprues = []
    base_product_sprue_edges = []

    logger_count = 0

    for base_product in base_products:
        
        logger_count += 1
        logger.debug(f"Base Product {logger_count}:")
        logger.debug(f"")

        for manufacturer in MANUFACTURERS:

            # Creates base_product_sprue node
            base_product_sprue = Component(
                name=f"Sprue {random_upper()}{random_upper()}{random_upper()}{str(faker_gen.random_int(10, 1000000000))}", 
                full_product=False,
                product=base_product,
                manufacturer=manufacturer,
                locations=faker_gen.random_element(elements=MANUFACTURERS[manufacturer]["Locations"]), 
                variant=False
                )
            logger.debug(f"Base Product Sprue:")
            logger.debug(base_product_sprue)
            logger.debug(f"")

            # Appends part to the overall list of parts for this product
            base_product_sprues.append(base_product_sprue)

            # Creates base_product to base_product_sprue edge
            base_product_sprue_edge = Requires(
                    start_node=base_product,
                    end_node=base_product_sprue,
                    base_model=True,
                    # In Business Days
                    lead_time=faker_gen.random_int(1, 1000)
            )

            logger.debug(f"Base Product Sprue Edge:")
            logger.debug(base_product_sprue_edge)
            logger.debug(f"")

            base_product_sprue_edges.append(base_product_sprue_edge)

    return base_product_sprues, base_product_sprue_edges

# endregion

# -------------------------------------------------------------------------------------------
#                                   BASE_PRODUCT_PARTS
# -------------------------------------------------------------------------------------------
# region BASE_PRODUCT_PARTS

def create_base_product_parts(base_products: List[Component], base_product_sprues: List[Component]) -> Tuple[List[Component], List[Requires]]:
    
    # Sets base_product_parts variables
    base_product_parts = []
    base_product_part_edges = []

    for base_product in base_products:

        PARTS_CATEGORIES = DESIGNATIONS[base_product.metadata["designation"]]["Parts"]

        for part_category, part_list in PARTS_CATEGORIES.items():

            # According to the inputdata.json list of desired parts for that product
            for part_type in part_list:

                # Assigns part manufacturer and manufacturer location
                base_product_part_manufacturer = faker_gen.random_element(elements=list(MANUFACTURERS.keys()))

                # Creates part node
                base_product_part = Component(
                    name=f"{part_type} {random_upper()}{random_upper()}{random_upper()}{str(faker_gen.random_int(10, 10000))}",
                    full_product=False,
                    manufacturer=base_product_part_manufacturer,
                    locations=faker_gen.random_element(elements=MANUFACTURERS[base_product_part_manufacturer]["Locations"]), 
                    product=base_product,
                    variant=False,
                    category=part_category,
                    part_type=part_type
                    )
                
                logger.debug(f"Base Product Part:")
                logger.debug(base_product_part)
                logger.debug(f"")

                # Appends part to the overall list of parts for this product
                base_product_parts.append(base_product_part)

                for base_product_sprue in base_product_sprues:

                    if base_product_part.metadata["product"] == base_product_sprue.metadata["product"] and base_product_part.manufacturer == base_product_sprue.manufacturer:

                        # Creates base_product to base_product_sprue edge
                        base_product_part_edge = Requires(
                            start_node=base_product_sprue,
                            end_node=base_product_part,
                            base_model=True,
                            # In Business Days
                            lead_time=faker_gen.random_int(1, 1000)
                        )

                logger.debug(f"Base Product Part Edge:")
                logger.debug(base_product_part_edge)
                logger.debug(f"")

                base_product_part_edges.append(base_product_part_edge)

    return base_product_parts, base_product_part_edges

# endregion

# -------------------------------------------------------------------------------------------
#                               RESOLVE_BASE_PRODUCT_SPRUES
# -------------------------------------------------------------------------------------------
# region RESOLVE_SPRUES
def resolve_base_product_sprues(base_product_sprues: List[Component], base_product_sprue_edges: List[Requires], base_product_part_edges: List[Requires]):
    
    for base_product_sprue in base_product_sprues:

        edge_count = 0
        
        for base_product_part_edge in base_product_part_edges:

            assert isinstance(base_product_part_edge, Requires)

            if base_product_part_edge.start_node == base_product_sprue:

                edge_count += 1

        if edge_count == 0:

            base_product_sprues.remove(base_product_sprue)

            logger.debug(f"Removed Sprue:")
            logger.debug(base_product_sprue)
            logger.debug(f"")

            for base_product_sprue_edge in base_product_sprue_edges:
            
                if base_product_sprue_edge.end_node == base_product_sprue:

                    base_product_sprue_edges.remove(base_product_sprue_edge)

                    logger.debug(f"Removed Sprue Edge:")
                    logger.debug(base_product_sprue)
                    logger.debug(f"")

    return base_product_sprues, base_product_sprue_edges

# endregion

base_products = create_base_products(500)
base_product_sprues, base_product_sprue_edges = create_base_product_sprues(base_products)
base_product_parts, base_product_part_edges = create_base_product_parts(base_products, base_product_sprues)
base_product_sprues, base_product_sprue_edges = resolve_base_product_sprues(base_product_sprues, base_product_sprue_edges, base_product_part_edges)
