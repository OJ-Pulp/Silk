import sys
import os
import json
import faker
import logging
import pandas as pd
from typing import List, Tuple

# Imports data_model from its location outside of /test
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from data_model import Component, Requires

# Config for logging showing messages level DEBUG and above
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Suppress debug messages from faker library
logging.getLogger("faker").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Program Start")

try:
    json_path = os.path.join(os.path.dirname(__file__), "../..", "inputdata.json")
    with open(json_path, "r") as f:
        INPUTDATA = json.load(f)
except FileNotFoundError:
    logger.error("inputdata.json not found -- Exiting")
    sys.exit(1)

DESIGNATIONS = INPUTDATA["Designations"]  # List of Dicts
MANUFACTURERS = INPUTDATA["Manufacturers"]  # List of Dicts

faker_gen = faker.Faker()
logger.info("Opening Variables Set")

def random_upper():
    return str(faker_gen.random_letter().upper())

# -------------------------------------------------------------------------------------------
#                                     GET_NEXT_LETTER
# -------------------------------------------------------------------------------------------
# region GET_NEXT_LETTER

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

# endregion

# -------------------------------------------------------------------------------------------
#                                    VARIANT_PRODUCTS
# -------------------------------------------------------------------------------------------
# region VARIANT_PRODUCTS

def create_variant_products(base_products, num_variants: int = 10)  -> List[Component]:

    # Sets variant variables
    variant_products = []

    # 2. Create list of variants
    for i in range(num_variants):

        # Assigns variant base_product
        variant_base_product = faker_gen.random_element(elements=base_products)
        assert isinstance(variant_base_product, Component) 

        # Assigns variant designation
        variant_base_designation = variant_base_product.metadata["designation"]
        if variant_base_designation[-1].isdigit():
            variant_designation_letter = "A"
        else:
            variant_designation_letter = get_next_letter(variant_base_designation[-1])
        variant_designation = f"{variant_base_designation}{variant_designation_letter}"

        # Assigns variant manufacturer and manufacturer_location
        variant_manufacturer = variant_base_product.manufacturer
        possible_manufacturer_locations = list(MANUFACTURERS[variant_manufacturer]["Locations"])
        variant_manufacturer_location = faker_gen.random_element(elements=possible_manufacturer_locations)

        # Creates variant_product node
        variant_product = Component(
            name=f"{variant_base_product.metadata['popular_name']} {variant_designation}", 
            manufacturer=variant_manufacturer,
            location=variant_manufacturer_location, 
            full_product=True,
            variant=True,
            variant_base_product=variant_base_product,
            designation=variant_designation, 
            popular_name=variant_base_product.metadata["popular_name"]
            )

        # Appends variant_product to the overall list of variant_products
        variant_products.append(variant_product)
    
    return variant_products

    # endregion