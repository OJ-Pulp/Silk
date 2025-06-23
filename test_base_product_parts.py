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
                    location=faker_gen.random_element(elements=MANUFACTURERS[base_product_part_manufacturer]), 
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

logger.debug(f"Create Base Product Parts:")
print(create_base_product_parts())