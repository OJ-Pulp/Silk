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