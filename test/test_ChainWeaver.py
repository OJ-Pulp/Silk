import uuid
import faker
from config import WeaverDir
from data_model import Component, Requires
from typing import List, Tuple, Optional

INPUTDATA = json.load(open(f"{WeaverDir}/Chain/inputdata.json", "r"))
DESIGNATIONS = INPUTDATA["Designations"] # List of Dicts
MANUFACTURERS = INPUTDATA["Manufacturers"] # List of Dicts
faker_gen = faker.Faker()
random_uppercase = {str(faker_gen.random_letter().upper())}

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
    designation_num = {designation_type: 0 for designation_type in DESIGNATIONS.keys()}

    # Creates a list of Components that are base_products
    for i in range(num_base_products):

        # Assigns base_product designation
        designation_mm = faker_gen.random_element(elements=list(DESIGNATIONS.keys()))
        designation_num[designation_mm] += 1
        base_product_designation_num = designation_num[designation_mm]
        base_product_designation = f"{designation_mm}-{base_product_designation_num}"

        # Assigns base_product popular_name and name
        base_product_popular_name = faker_gen.word(part_of_speech='noun').capitalize()

        # Assigns base_product manufacturer and manufacturer_location
        base_product_manufacturer = faker_gen.random_element(elements=list(MANUFACTURERS.keys()))

        # Creates base_product node
        base_product = Component(
            name=f"{base_product_popular_name} {base_product_designation}", 
            full_product=True,
            variant=False,
            manufacturer=base_product_manufacturer,
            location=faker_gen.random_element(elements=MANUFACTURERS[base_product_manufacturer]), 
            designation=base_product_designation, 
            popular_name=base_product_popular_name
            )

        # Appends base_product to the overall list of base_products
        base_products.append(base_product)

    return base_products

    # endregion

# -------------------------------------------------------------------------------------------
#                                   BASE_PRODUCT_SPRUES
# -------------------------------------------------------------------------------------------
# region BASE_PRODUCT_SPRUES

def create_base_product_sprues(base_products: List[Component]) -> Tuple[List[Component], List[Requires]]:
    
    # Sets base_product_sprues variables
    base_product_sprues = []
    base_product_sprue_edges = []

    for base_product in base_products:
        
        for manufacturer in MANUFACTURERS:

            # Creates base_product_sprue node
            base_product_sprue = Component(
                name=f"Sprue {random_uppercase}{random_uppercase}{random_uppercase}{str(faker_gen.random_int(10, 1000000000))}", 
                full_product=False,
                product=base_product,
                manufacturer=manufacturer,
                location=faker_gen.random_element(elements=MANUFACTURERS[manufacturer]), 
                variant=False
                )

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

            base_product_sprue_edges.append(base_product_sprue_edge)

    return base_product_sprues, base_product_sprue_edges

# endregion

# -------------------------------------------------------------------------------------------
#                                   BASE_PRODUCT_PARTS
# -------------------------------------------------------------------------------------------
# region BASE_PRODUCT_PARTS

def create_base_product_parts(base_products: List[Component], base_product_sprues: List[Component]) -> Tuple[List[Component], List[Requires]]:
    
    # Sets base_product_parts variables
    base_product_parts = []
    base_product_part_edges = []

    for base_product in base_products:

        # [ ] FIX HERE LATER
        #product_num_parts = DESIGNATIONS[product_designation]["Number of Parts"]
        PARTS_CATEGORIES = DESIGNATIONS[base_product.metadata["designation"]]["Parts"]

        # 3a. Creates parts
        for part_category, part_list in PARTS_CATEGORIES.items():

            # According to the inputdata.json list of desired parts for that product
            for part_type in part_list:

                # Assigns part manufacturer and manufacturer location
                base_product_part_manufacturer = faker_gen.random_element(elements=list(MANUFACTURERS.keys()))

                # Creates part node
                base_product_part = Component(
                    name=f"{part_type} {random_uppercase}{random_uppercase}{random_uppercase}{str(faker_gen.random_int(10, 10000))}",
                    full_product=False,
                    manufacturer=base_product_part_manufacturer,
                    location=faker_gen.random_element(elements=MANUFACTURERS[base_product_part_manufacturer]), 
                    product=base_product,
                    variant=False,
                    category=part_category,
                    part_type=part_type
                    )

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

                base_product_part_edges.append(base_product_part_edge)

    return base_product_parts, base_product_part_edges

# endregion

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

            for base_product_sprue_edge in base_product_sprue_edges:
            
                if base_product_sprue_edge.end_node == base_product_sprue:

                    base_product_sprue_edges.remove(base_product_sprue_edge)

    return base_product_sprues, base_product_sprue_edges

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
        variant_manufacturer_location = faker_gen.random_element(elements=MANUFACTURERS[variant_manufacturer])

        # Creates variant_product node
        variant_product = Component(
            name=f"{variant_base_product.metadata["popular_name"]} {variant_designation}", 
            full_product=True,
            manufacturer=variant_manufacturer,
            location=variant_manufacturer_location, 
            variant=True,
            variant_base_product=variant_base_product,
            designation=variant_designation, 
            popular_name=variant_base_product.metadata["popular_name"]
            )

        # Appends variant_product to the overall list of variant_products
        variant_products.append(variant_product)
    
    return variant_products

    # endregion

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
#                                    MAIN_FUNCTION
# -------------------------------------------------------------------------------------------
# region MAIN_FUNCTION

 # [ ] not a dict

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
    num_variants = int(num_products * variant_distribution)
    num_base_products = num_products - num_variants

    base_products = create_base_products(num_base_products)
    base_product_sprues, base_product_sprue_edges = create_base_product_sprues(base_products)
    base_product_parts, base_product_part_edges = create_base_product_parts(base_products, base_product_sprues)
    base_product_sprues, base_product_sprue_edges = resolve_base_product_sprues(base_product_sprues, base_product_sprue_edges, base_product_part_edges)
