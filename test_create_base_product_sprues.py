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

base_products = [Component(
  id='f3c9ad85-a2c3-47fb-930e-48f3ae34482d',
  name='Health K-1',
  manufacturer='Parker Hannifin',
  locations='Basingstoke, UK',
  full_product=True,
  designation='K-1',
  popular_name='Health',
  variant=False,
)]

logger.debug(f"Create Base Product Sprues:")
logger.debug(create_base_product_sprues(base_products))