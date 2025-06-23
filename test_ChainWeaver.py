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
random_uppercase = {str(faker_gen.random_letter().upper())}
logger.info("Opening Variables Set")

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
            designation=base_product_designation, 
            popular_name=base_product_popular_name
            )

        # Appends base_product to the overall list of base_products
        base_products.append(base_product)

        logger.debug(f"")

    return base_products

    # endregion

(create_base_products(1))