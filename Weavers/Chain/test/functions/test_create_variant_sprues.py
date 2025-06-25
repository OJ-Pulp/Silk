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

INPUTDATA = json.load(open(f"C:/Users/bgarringer/Desktop/GitHub/Silk/Weavers/Chain/inputdata.json", "r"))
DESIGNATIONS = INPUTDATA["Designations"] # List of Dicts
MANUFACTURERS = INPUTDATA["Manufacturers"] # List of Dicts
FAKER_GEN = faker.Faker()
logger.info("Opening Variables Set")

# -------------------------------------------------------------------------------------------
#                                   variant_SPRUES
# -------------------------------------------------------------------------------------------
# region variant_SPRUES

def create_variant_sprues(variant_products: List[Component]) -> Tuple[List[Component], List[Requires]]:
    # Sets variant_sprues variables
    variant_sprues = []
    variant_sprue_edges = []

    for i, variant_product in enumerate(variant_products, start=1):
        logger.debug(f"Variant Product {i}:\n")

        for manufacturer in MANUFACTURERS:
            # Creates variant_sprue node
            variant_sprue = Component(
                name=f"Sprue {FAKER_GEN.bothify(text='???########')}",
                full_product=False,
                product=variant_product.id,
                manufacturer=manufacturer,
                locations=FAKER_GEN.random_element(
                    elements=MANUFACTURERS[manufacturer]["Locations"]
                ),
                variant=False,
            )
            logger.debug(f"Base Product Sprue: {variant_sprue}\n")

            # Appends part to the overall list of parts for this product
            variant_sprues.append(variant_sprue)

            # Creates variant to variant_sprue edge
            variant_sprue_edge = Requires(
                start_node=variant_product,
                end_node=variant_sprue,
                base_model=True,
                # In Business Days
                lead_time=FAKER_GEN.random_int(1, 1000),
            )

            logger.debug(f"Variant Sprue Edge: {variant_sprue_edge}\n")

            variant_sprue_edges.append(variant_sprue_edge)

    return variant_sprues, variant_sprue_edges

# endregion

variant_products = [Component(
  id='29df94f6-3798-4025-88ea-7c18640189f7',
  name='Health K-1A',
  manufacturer='Parker Hannifin',
  location='Cleveland, Ohio, USA',
  full_product=True,
  designation='K-1A',
  popular_name='Health',
  variant=True,
  variant_base_product='f3c9ad85-a2c3-47fb-930e-48f3ae34482d',
)]

logger.debug(f"Create Variant Sprues:")
logger.debug(create_variant_sprues(variant_products))