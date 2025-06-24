"""
This script generates a fake supply chain for model aircrafts and outputs it to a json file.

"""

import json
import uuid
import faker
from config import WeaverDir

DATA = json.load(open(f"{WeaverDir}/Chain/data.json", "r"))
COMPANIES = DATA["Companies"] # List of Dicts
MANUFACTURERS = DATA["Manufacturers"] # List of Dicts
PART_CATEGORIES = DATA["Parts"]

def weave(num_products: int = 40, variant_distribution: float = 0.25) -> dict:
    """
    Main Function to generate a fake supply chain for model aircrafts.
    :param num_parts: Number of parts to generate in the supply chain.
    :return: A dictionary representing the supply chain.
    """
    faker_gen = faker.Faker()
    num_variants = int(num_products * variant_distribution)
    num_base_products = num_products - num_variants
    num_parts = num_products * sum(len(PART_CATEGORIES[category]) for category in PART_CATEGORIES)
    # 1. Create list of base products
    products = []
    for i in range(num_base_products):
        # Generate UUID for the product
        product_id = str(uuid.uuid4())
        # Generate Random Product Name (Noun) with a character and numbers
        product_name = faker_gen.word(part_of_speech='noun').capitalize()
        # Choose a random company from a normal distribution
        company = faker_gen.random_element(elements=list(COMPANIES.keys()))
        # Choose a random location from a normal distribution
        location = faker_gen.random_element(elements=COMPANIES[company])
        product = {
            "ID": product_id,
            "Name": product_name,
            "Full_Product": True,
            "Company": company,
            "Location": location,
            "Metadata": {},
            "Parts": []
        }
        products.append(product)
    
    # 2. Create list of variants
    for i in range(num_variants):
        # Sample a random product from the products list
        base_product = faker_gen.random_element(elements=products)
        # Generate UUID for the variant
        variant_id = str(uuid.uuid4())
        # Generate Random Product Name (Noun) with a character and numbers
        variant_name = base_product["Name"] + " " + str(faker_gen.random_letter()) + " " + str(faker_gen.random_int(10, 1000))
        # Resample the location
        location = faker_gen.random_element(elements=COMPANIES[base_product["Company"]])
        # Create the variant product
        variant_product = {
            "ID": variant_id,
            "Name": variant_name,
            "Full_Product": True,
            "Company": base_product["Company"],
            "Location": location,
            "Metadata": {},
            "Parts": [base_product["ID"]]
        }
        products.append(variant_product)

    # 3. Create list of parts
    parts = []
    ## We want completely random locations for the base parts
    ## The assumption is that while the companies assemble the kits and products, the individual parts were sourced from various manufacturing locations
    for i in range(num_products):
        # For every product create a part for each part in each category
        for category, part_list in PART_CATEGORIES.items():
            for part in part_list:
                # Generate UUID for the part
                part_id = str(uuid.uuid4())
                # Company
                manufacturer = faker_gen.random_element(elements=list(MANUFACTURERS.keys()))

                part_data = {
                    "ID": part_id,
                    "Name": part + " " + str(faker_gen.random_letter()) + " " + str(faker_gen.random_int(10, 1000)),
                    "Full_Product": False,
                    "Company": manufacturer,
                    "Location": faker_gen.random_element(elements=MANUFACTURERS[manufacturer]),
                    "Metadata": {
                        "Category": category,
                        "Type": part
                    }
                }
                parts.append(part_data)
    # 4. A company has a list of parts needed for an 
    #    aircraft, so they randomly go to each manufacturer and show them the list. The manufacturer says that they can provide
    #    some of the parts that they will make into a kit. The company agrees and then crosses the items in the kit off the list.
    #    The company then goes to the next manufacturer and does the same thing until they have all the parts they need.
    for product in products:
        check_list = [part for _category, part_list in PART_CATEGORIES.items() for part in part_list]
        # Randomly select manufacturers to provide parts
        manufacturer = faker_gen.random_element(elements=list(MANUFACTURERS.keys()))
        while check_list:
            # Get list of parts that the manufacturer can provide
            available_parts = [part for part in parts if part["Company"] == manufacturer and part["Metadata"]["Type"] in check_list]
            if not available_parts:
                # If no parts are available, choose a new manufacturer
                manufacturer = faker_gen.random_element(elements=list(MANUFACTURERS.keys()))
            else:
                # Create a kit with the available parts
                kit_id = str(uuid.uuid4())
                # Kit names are random letter of the alphabet and a number
                kit_name = faker_gen.random_letter().upper() + " " + str(faker_gen.random_int(10, 1000))
                # Location is the same as the manufacturer
                kit_location = faker_gen.random_element(elements=MANUFACTURERS[manufacturer])
                kit_data = {
                    "ID": kit_id,
                    "Name": kit_name,
                    "Full_Product": False,
                    "Company": manufacturer,
                    "Location": kit_location,
                    "Metadata": {
                        "Category": "Kit",
                        "Type": "Assembly Kit"
                    },
                    "Parts": [part["ID"] for part in available_parts]
                }
                parts.append(kit_data)
                product["Parts"].append(kit_id)
