"""
This script generates a fake supply chain for model aircrafts and outputs it to a json file.

"""

# Corbin - 
# [ ] other information
# Neoj4 Alternatives: https://memgraph.com/blog/neo4j-alternative-what-are-my-open-source-db-options
# Memgraph OSS Github: https://github.com/memgraph/memgraph
# Memgraph Cypher Examples: https://memgraph.com/docs/querying
# Memgraph GOT Example: https://playground.memgraph.com/sandbox/game-of-thrones-deaths
# Corbin -
# [ ] alternative node types
# Other nodes could be used in the graph instead of keeping all relevant data in one node.
# Ex. a Location node, a Company node, a Manufacturer node
# Corbin -
# [ ] alternative edge types
# Different edge types could be used to denote different relationships.
# Ex. Manufactured by, Located in, Owned by

import json
import uuid
import faker
from config import WeaverDir

DATA = json.load(open(f"{WeaverDir}/Chain/data.json", "r"))
COMPANIES = DATA["Companies"] # List of Dicts
MANUFACTURERS = DATA["Manufacturers"] # List of Dicts
PART_CATEGORIES = DATA["Parts"]

# Brooke -
# [ ] num_products vs num_parts
# Did you intend for there to be a discrepency between the function parameter and the comment?
def weave(num_products: int = 40, variant_distribution: float = 0.25) -> dict:
    """
    Main Function to generate a fake supply chain for model aircrafts.
    :param num_parts: Number of parts to generate in the supply chain.
    :return: A dictionary representing the supply chain.
    """
    faker_gen = faker.Faker()
    num_variants = int(num_products * variant_distribution)
    num_base_products = num_products - num_variants
    # Brooke -
    # [ ] # of parts per product
    # From what I understand, this means that all products will have the same number of parts which is inaccurate.
    # Is that intended or should we randomize?
    # Brooke - 
    # [ ] mutually exclusive parts
    # This is counting all parts in each category, but some parts like methods of propulsion will be mutually exclusive.
    # Ex. Propeller and Jet Engine
    num_parts = num_products * sum(len(PART_CATEGORIES[category]) for category in PART_CATEGORIES)

    # 1. Create list of base products
    products = []
    for i in range(num_base_products):
        # Generate UUID for the product
        # Brooke -
        # [ ] uuid format
        # This shouldn't be an issue for our made up data set, but product codes for model airplanes are a different format.
        # Ex. tam61040
        # This includes the first three letters of the manufacturer and an approx. 5 digit code
        product_id = str(uuid.uuid4())
        # Brooke -
        # [ ] product_name format
        # This product_name does not fit the description of a (one) character with numbers.
        # This change in formatting should not be an issue as long as it is consistent.
        # Generate Random Product Name (Noun) with a character and numbers
        product_name = faker_gen.word(part_of_speech='noun').capitalize()
        # Brooke -
        # [ ] normal distribution of companies
        # What represents your normal distribution? 
        # Have you assigned weights to the companies or defined a range?
        # Choose a random company from a normal distribution
        company = faker_gen.random_element(elements=list(COMPANIES.keys()))
        # Brooke -
        # [ ] normal distribution of locations
        # Same thing here
        # Choose a random location from a normal distribution
        location = faker_gen.random_element(elements=COMPANIES[company])
        # Brooke -
        # [ ] supply chain flow
        # There is no currently set way to add the manufacturer/company's set of parts to the product parts list.
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
        # Brooke - 
        # [ ] uuid format cont.
        # Generate UUID for the variant
        variant_id = str(uuid.uuid4())
        # Brooke - 
        # [ ] product_name format cont.
        # The Noun is not randomly generated at this step unlike the comment's statment due to being taken from the base.
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
        # Brooke - 
        # [ ] multi-layer variants?
        # This will cause the variant_product to be treated as base_product in the next iteration.
        # Ex. variant_name = Applec45b300
        # Brooke + Corbin -
        # [ ] variant structure
        # Currently a variant is just the base_product going into a new product with no other changes.
        # This code looks as if the intent is to later ADD parts in conjunction with the base_product.
        # It would be more consice and more accurate to take the consistent sprues over from the base_product.
        # Then other different or replacement sprues could be added to the parts of the variant.
        # This would take away the base_product as a part of the variant.
        # It would also avoid a more tree like structure and stay consistent to the desired sprawling graph.
        # It would also be far easier to identify what parts go into multiple different products.
        # This would avoid an odd flow and interconnection of nodes.
        # This would make it consistent that a full_product could be identified by not being an input part for anything.
        # Therefore, it would likely no longer be necessary to keep the booleans signifying a full_product.
        # This could potentially save space as long as another process was in place to use these factors to identify one.
        products.append(variant_product)

    # Brooke + Corbin -
    # [ ] sprue variant structure
    # Looking to the future, if the variant structure above is concured with, there would need to be a defined sprue variant structure.
    # Consider if there are three bottom level parts (1a, 1b, 1c,) that make up sprue 1 and similarly formatted sprues 2 + 3 that make up part Apple.
    # Variant Applex300 would have the shared sprues of 2 + 3 and a different sprue of 300 which is made up of 1a, 1b, and 300x.  
    # (The congruencies with the letters and numbers of 300 and x are examples that are not inherent to the structure though their consistency is.)
    # Therefore, instead of an entirely new sprue, sprue 300 would share parts 1a and 1b with sprue 1 and have one extra part.
    # Sprue 300 would then be one of the parts for Applex300.
    # Brooke + Corbin -
    # [ ] 3 < layer part structure
    # Our data set on model airplanes will have only three functioning parts layers (parts, sprues, kits).
    # For real airplanes, there would be many more layers.
    # Therefore, throught the design process we need to keep that functionality in mind.
    # Brooke -
    # [ ] sprues vs kits vs parts
    # It may be beneficial to consolidate term usage in an opening comment.
    # Refering to them all as parts could cause confusion but would be beneficial for multi-layered use cases.
    # Brooke + Corbin -
    # [ ] linkage of parts
    # In both our and real world scale, is the linkage of parts itself considered a part?
    # Are we certain that it is best overall to define the next collection of parts through the manufacturer/company?
    # Currently our thoughts are leading to yes, as a sprue is the linkage of smaller parts.
    # However, we are linking them through manufacturer/company instead of location category.
    # Depending to the degree that this is true, different parts categories could be considered as parts themselves.
    # 3. Create list of parts
    parts = []
    # Brooke -
    # [ ] companies vs manufacturers
    # These would be some more key terms to define in an opening comment.
    # The format of the data.json file concerning these two is particularly confusing.
    # It needs to be consolidated and better defined.
    # Both have a category of a company with manufacturing locations.

    # We want completely random locations for the parts
    # The assumption is that while the companies assemble the kits and products, the individual parts were sourced from various manufacturing locations
    for i in range(num_products):
        # Brooke -
        # [ ] mutually exclusive parts cont.
        # Same as before, although this is probably a more proper location.
        # For every product create a part for each part in each category
        for category, part_list in PART_CATEGORIES.items():
            for part in part_list:
                # Generate UUID for the part
                part_id = str(uuid.uuid4())
                # Brooke -
                # [ ] companies vs manufacturers cont.
                # Here company is used as the comment explanation even though manufacturer is used as the variable and data. 
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
    # Brooke -
    # [ ] sprues vs kits vs parts cont.
    # Here sprues are refered to as kits, according to our current definitions.
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
                # Brooke -
                # [ ] naming structures
                # A comment or text document to be used as a key for different nameing structures may be useful.
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

                
