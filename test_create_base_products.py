import json
import uuid
import faker
from data_model import Component, Requires
from typing import List, Tuple, Optional

print("FLAG: SUCCESS: Program Start")

INPUTDATA = json.load(open(f"C:/Users/bgarringer/Desktop/GitHub/Silk/inputdata.json", "r"))
DESIGNATIONS = INPUTDATA["Designations"] # List of Dicts
MANUFACTURERS = INPUTDATA["Manufacturers"] # List of Dicts
faker_gen = faker.Faker()
random_uppercase = {str(faker_gen.random_letter().upper())}

print("FLAG: SUCCESS: Opening Variables Set")

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

    # Creates a list of Components that are base_products
    for i in range(num_base_products):

        # Assigns base_product designation
        designation_mm = faker_gen.random_element(elements=designation_keys)
        designation_num[designation_mm] += 1
        base_product_designation_num = designation_num[designation_mm]
        base_product_designation = f"{designation_mm}-{base_product_designation_num}"
        print(f"FLAG: BASE_PRODUCT_DESIGNATION: {base_product_designation}")

        # Assigns base_product popular_name and name
        base_product_popular_name = faker_gen.word(part_of_speech='noun').capitalize()
        print(f"FLAG: BASE_PRODUCT_POPULAR_NAME: {base_product_popular_name}")

        # Assigns base_product manufacturer and manufacturer_location
        base_product_manufacturer = faker_gen.random_element(elements=manufacturer_keys)
        print(f"FLAG: BASE_PRODUCT_MANUFACTURER: {base_product_manufacturer}")
        possible_manufacturer_locations = list(MANUFACTURERS[base_product_manufacturer]["Locations"])
        base_product_manufacturer_location = faker_gen.random_element(elements=possible_manufacturer_locations)
        print(f"FLAG: BASE_PRODUCT_MANUFACTURER_LOCATION: {base_product_manufacturer_location}")

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
        print(f"FLAG: BASE_PRODUCT: {base_product}")

        # Appends base_product to the overall list of base_products
        base_products.append(base_product)

    return base_products

    # endregion

print(f"FLAG: CREATE_BASE_PRODUCTS:")
print(create_base_products(5))
