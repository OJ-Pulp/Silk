"""
This script generates a fake supply chain for model aircrafts and outputs it to a json file.

"""

# Corbin - 
# [x] other information
# Neoj4 Alternatives: https://memgraph.com/blog/neo4j-alternative-what-are-my-open-source-db-options
# Memgraph OSS Github: https://github.com/memgraph/memgraph
# Memgraph Cypher Examples: https://memgraph.com/docs/querying
# Memgraph GOT Example: https://playground.memgraph.com/sandbox/game-of-thrones-deaths
# Capt. Terry -
# Possibly good, possibly build from the ground up
# Brooke - 
# [ ] other information cont. 
# Another database option to explore is Oracle Database with 23ai
# I believe that the Air Force has a liscense that we could use or we could use the free version.
# I would be happy to send over more information upon request.
# Corbin -
# [x] alternative node types
# Other nodes could be used in the graph instead of keeping all relevant data in one node.
# Ex. a Location node, a Company  node, a Manufacturer node
# Capt. Terry -
# Good point, unsure if the project intent was advanced Q&A or metrics portion
# Corbin -
# [x] alternative edge types
# Different edge types could be used to denote different relationships.
# Ex. Manufactured by, Located in, Owned by

import json
import uuid
import faker
from config import WeaverDir
from data_model import Component, Requires

INPUTDATA = json.load(open(f"{WeaverDir}/Chain/inputdata.json", "r"))
DESIGNATIONS = INPUTDATA["Designations"] # List of Dicts
COMPANIES = INPUTDATA["Companies"] # List of Dicts
MANUFACTURERS = INPUTDATA["Manufacturers"] # List of Dicts

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

def weave(num_products: int = 40, variant_distribution: float = 0.25) -> dict:
    """
    Main Function to generate a fake supply chain for model aircrafts.
    :param num_products: The total number of unique model aircraft products to include in the supply chain.
                         Defaults to 40.
    :param variant_distribution: A float (0.0 to 1.0) controlling the proportion of products that will have variants.
                         Defaults to 0.25, meaning roughly 25% of products will be variations.
    :return: A dictionary representing the supply chain.
    """
    # Sets overall variables
    faker_gen = faker.Faker()
    num_variants = int(num_products * variant_distribution)
    num_base_products = num_products - num_variants
    
    # Sets base_product variables
    base_products = []
    designation_num = {designation_type: 0 for designation_type in DESIGNATIONS.keys()}

    # 1. Create list of base products
    for i in range(num_base_products):

        # Assigns base_product designation
        designation_mm = faker_gen.random_element(elements=list(DESIGNATIONS.keys()))
        designation_num[designation_mm] += 1
        base_product_designation_num = designation_num[designation_mm]
        base_product_designation = f"{designation_mm}-{base_product_designation_num}"

        # Assigns base_product popular_name and name
        base_product_popular_name = faker_gen.word(part_of_speech='noun').capitalize()
        base_product_name = f"{base_product_popular_name} {base_product_designation}"

        # Assigns base_product company and company_location
        base_product_company = faker_gen.random_element(elements=list(COMPANIES.keys()))
        base_product_company_location = faker_gen.random_element(elements=COMPANIES[base_product_company])

        """
        # Assigns base_product id
        base_product_base_uuid = str(uuid.uuid4())
        base_product_id = f"{base_product_company[0:3].lower()}{base_product_base_uuid}"

        # Assigns base_product
        base_product = {
            "ID": base_product_id,
            "Name": [base_product_name],
            "Full_Product": True,
            "Company": base_product_company,
            "Location": base_product_company_location,
            "Metadata": {"Designation": base_product_designation,
                         "Popular Name": base_product_popular_name},
            "Parts": []
        }
        """

        base_product = Component(base_product)

        # Appends base_product to the overall list of base_products
        base_products.append(base_product)

    # Sets variant variables
    variant_products = []

    # 2. Create list of variants
    for i in range(num_variants):

        # Assigns variant base_product
        variant_base_product = faker_gen.random_element(elements=base_products)

        # Assigns variant designation
        variant_base_designation = variant_base_product["Metadata"]["Designation"]
        if variant_base_designation[-1].isdigit():
            variant_designation_letter = "A"
        else:
            variant_designation_letter = get_next_letter(variant_base_designation[-1])
        variant_designation = f"{variant_base_designation}{variant_designation_letter}"

        # Assigns variant name and carries on variant_base_product's popular_name
        variant_name = f"{variant_base_product["Metadata"]["Popular Name"]} {variant_designation}"

        # Assigns variant company and company_location
        variant_company = variant_base_product["Company"]
        variant_company_location = faker_gen.random_element(elements=COMPANIES[variant_company])

        # Assigns variant id
        variant_base_uuid = str(uuid.uuid4())
        variant_id = f"{variant_company[0:3].lower()}{variant_base_uuid}"

        # Assigns variant
        variant_product = {
            "ID": variant_id,
            "Name": variant_name,
            "Full_Product": True,
            "Company": variant_company,
            "Location": variant_company_location,
            "Metadata": {"Designation": variant_designation,
                         "Popular Name": variant_base_product["Metadata"]["Popular Name"]},
            "Parts": []
        }

        # Appends variant_product to the overall list of variant_products
        variant_products.append(variant_product)

    # Combines all products together as equals
    # [ ] FIX HERE LATER
    # products = base_products + variant_products
    parts = []

    # 3. Creates parts and sprues
    for product in base_products:

        # Sets parts variables
        product_parts = []
        product_designation = product["Metadata"]["Designation"]
        # product_num_parts = DESIGNATIONS[product_designation]["Number of Parts"]
        PARTS_CATEGORIES = DESIGNATIONS[product_designation]["Parts"]

        # 3a. Creates parts
        for category, part_list in PARTS_CATEGORIES.items():

            # According to the inputdata.json list of desired parts for that product
            for part in part_list:

                # Assigns part id
                part_id = str(uuid.uuid4())

                # Assigns part name
                part_name = f"{part} {str(faker_gen.random_letter())} {str(faker_gen.random_int(10, 1000))}"

                # Assigns part manufacturer and manufacturer location
                part_manufacturer = faker_gen.random_element(elements=list(MANUFACTURERS.keys()))
                part_manufacturer_location = faker_gen.random_element(elements=MANUFACTURERS[part_manufacturer])

                # Assigns part
                part = {
                    "ID": part_id,
                    "Name": part_name,
                    "Full_Product": False,
                    "Manufacturer": part_manufacturer,
                    "Location": part_manufacturer_location,
                    "Metadata": {
                        "Category": category,
                        "Type": part
                    },
                    "Parts": []
                }

                # Appends part to the overall list of parts for this product
                parts.append(part)
                product_parts.append(part_id)


        # [ ] Interconnect Locations
        # Components are manufactured at multiple locatios

        # Sets categorization variables
        checklist = [part for _category, part_list in PARTS_CATEGORIES.items() for part in part_list]
        complete_checklist = {}
        sprues = []

        # 3b. Creates sprues
        for current_manufacturer in MANUFACTURERS:

            sprue = {
                "ID": str(uuid.uuid4()),
                "Name": f"Sprue {str(faker_gen.random_letter())} {str(faker_gen.random_int(10, 1000))}",
                "Full_Product": False,
                "Manufacturer": current_manufacturer,
                "Parts": []
            }
            

            # 3bsub. Creates subsprues
            for current_location in MANUFACTURERS[current_manufacturer]:

                # Sets subsprue variables
                sub_location = []

                # Assigns sub_sprue
                sub_sprue = {
                    "ID": str(uuid.uuid4()),
                    "Name": f"Sub_Sprue {str(faker_gen.random_letter())} {str(faker_gen.random_int(10, 1000))}",
                    "Full_Product": False,
                    "Manufacturer": current_manufacturer,
                    "Location": current_location,
                    "Parts": []
                }

                # Groups parts with their locations and manufacturers
                for item in checklist:

                    # Sets consolidation variables
                    parts_by_id = {current_part["ID"]: current_part for current_part in parts}
                    current_part = parts_by_id[item]

                    # Checks if the current part belongs to the current group
                    if current_part["Manufacturer"] == current_manufacturer and current_part["Location"] == current_location:
                        
                        # LINKAGE - Adds the current part to the parts of the current sub sprue and checklist
                        sub_location.append(current_part)
                        sub_sprue["Parts"].append(current_part)

                        """
                        OR

                        sprue["Parts"].append(current_part)

                        And take out a bunch of other stuff.
                        """

                # LINKAGE - Adds the current sub sprue to the parts of the current sprue for checklist
                sprue_manufacturer[current_location] = sub_location
                sub_sprues.append(sub_sprue)
            
            # LINKAGE - Adds the current sub sprue to the parts of the current sprue
            sprues["Parts"].append(sub_sprues)

            # List of parts organized by manufacturer then location
            complete_checklist[current_manufacturer] = sprue_manufacturer
            
            products[product]["Parts"].append(sprues)
   
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
    # Brooke -
    # [x] companies vs manufacturers
    # These would be some more key terms to define in an opening comment.
    # The format of the data.json file concerning these two is particularly confusing.
    # It needs to be consolidated and better defined.
    # Both have a category of a company with manufacturing locations.
    # Capt. Terry -
    # Wanted to differentiate 
    # Manufacturers have different names than companies
    # Companies - assemble the aircraft
    # Manufacturers - assemble the sprues
    # Possibly mix and match a bit
    # Derek
    # Suppliers vs Manufacturers
    # Make vocab sheet
    # Later make way to customize different stuff about data?
    # How to figure out if a thing is supplier or manufacturer?
    # We want completely random locations for the parts
    # The assumption is that while the companies assemble the kits and products, the individual parts were sourced from various manufacturing locations
    # Brooke -
    # [ ] sprues vs kits vs parts cont.
    # Here sprues are refered to as kits, according to our current definitions.
    

                
