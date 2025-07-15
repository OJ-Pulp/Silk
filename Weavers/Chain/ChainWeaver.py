"""
ChainWeaver.py

ChainWeaver is a module that generates a supply chain graph structure using fake data. It outputs the supply chain as a dictionary containing nodes (components) and edges (relationships between components). The module supports base products, parts, and variants, allowing for complex supply chain modeling.
"""

# Standard
import logging
import re
from pathlib import Path
from typing import List, Tuple

# -------------------------------------------------------------------------------------------
#                                   LOGGING_SETTINGS
# -------------------------------------------------------------------------------------------
# region LOGGING_SETTINGS

SUCCESS = 0
FAILURE = 1
INTERRUPTED = 130

# Configures for logging showing messages level INFO and above
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Suppresses debug messages from faker library
logging.getLogger("faker").setLevel(logging.INFO)

# endregion

# Third-Party
try:
    import faker
except ModuleNotFoundError as e:
    logger.critical(f"{type(e).__name__}: Missing Required Module '{e.name}' -- Try 'python -m pip install {e.name}' -- Exiting")
    raise SystemExit(FAILURE)

# Local
try:
    from Weavers.Chain.data_model import Component, Requires
    from Weavers.Chain.input_utils import resolve_json
except ModuleNotFoundError as e:
    logger.critical(f"{type(e).__name__}: Missing Required Local Module '{e.name}' -- Check that '{e.name}.py' is in the Same Directory as 'ChainWeaver.py' -- Exiting")
    raise SystemExit(FAILURE)

FAKER = faker.Faker()

# -------------------------------------------------------------------------------------------
#                                      BASE_PRODUCTS
# -------------------------------------------------------------------------------------------
# region BASE_PRODUCTS

def create_base_products(
    num_base_products: int, 
    designations_dict: dict, 
    manufacturers_dict: dict
) -> List[Component]:
    """
    Generates a fake dataset of base products and their data.

    :param `num_base_products`: The total number of unique base products to include in the supply chain.
    :type `num_base_products`: int
    :param `designations_dict`: The 'Designation' category of 'resolved_inputdata'.
    :type `designations_dict`: dict
    :param `manufacturers_dict`: The 'Manufacturer' category of 'resolved_inputdata'.
    :type `manufacturers_dict`: dict

    :return: A list of base products.
    :rtype: List[Component]
    """

    # Sets empty lists to collect products along with other necessary variables
    base_products = []

    logger.info("Base Product Initialization")

    # Creates all base products
    for _ in range(num_base_products):
        manufacturer = FAKER.random_element(list(manufacturers_dict.keys()))
        locations = FAKER.random_element(manufacturers_dict[manufacturer]["Locations"])
        designation = FAKER.random_element(list(designations_dict.keys()))
        popular_name = FAKER.word("noun").capitalize()
        component_data = {
            "name": popular_name + " " + FAKER.bothify("???###"),
            "manufacturer": manufacturer,
            "locations": locations,
            "full_product": True,
            "component_type": "base_product",
            "product": None,
            "variant": False,
            "variant_base_product": None,
            "vital": FAKER.boolean(),
            "designation": designation,
            "popular_name": popular_name,
            "category": designations_dict[designation]["Type"],
            "part_type": None,
            "dimensions": [
                FAKER.random_int(10, 100),
                FAKER.random_int(10, 100),
                FAKER.random_int(10, 100)
            ],
            "cost": round(FAKER.random_number(digits=4), 2),
            "failure_rate": round(FAKER.random_number(digits=2) / 100, 4),
            "substitutions": [FAKER.bothify("???###") for _ in range(FAKER.random_int(0, 3))],
            "breakability": round(FAKER.random_number(digits=2) / 100, 2),
            "year_range": [FAKER.random_int(1990, 2024) for _ in range(FAKER.random_int(1, 3))],
        }
        base_product = Component(**component_data)

        # Appends 'base_product' Component(Node) to the overall list of 'base_products'
        base_products.append(base_product)

    logger.info("Base Products Created")

    return base_products

# endregion

# -------------------------------------------------------------------------------------------
#                                   BASE_PRODUCT_SPRUES
# -------------------------------------------------------------------------------------------
# region BASE_PRODUCT_SPRUES

def create_base_product_sprues(
    base_products: List[Component], 
    manufacturers_dict: dict
) -> Tuple[List[Component], List[Requires]]:
    """
    Generates a fake dataset of base product sprues and sprue edges and their data.

    :param `base_products`: A list of base products and their data.
    :type `base_products`: List[Component]
    :param `manufacturers_dict`: The 'Manufacturer' category of 'resolved_inputdata'.
    :type `manufacturers_dict`: dict

    :return: A list of base product sprues.
    :rtype: List[Component]
    :return: A list of edges between base products and base product sprues.
    :rtype: List[Requires]
    """

    # Sets empty lists to collect sprues and edges along with other necessary variables
    base_product_sprues = []
    base_product_sprue_edges = []
    manufacturer_keys = list(manufacturers_dict.keys())

    logger.info("Base Product Sprues Initialization")

    # Creates all base product sprues and edges
    for base_product in base_products:

        for manufacturer in manufacturer_keys:

            # Creates 'base_product_sprue' Component(Node)
            base_product_sprue = Component(
                name=f"Sprue {FAKER.bothify('???########')}",
                full_product=False,
                product=base_product.id,
                manufacturer=manufacturer,
                locations=FAKER.random_element(manufacturers_dict[manufacturer]["Locations"]),
                variant=False,
            )

            # Appends 'base_product_sprue' Component(Node) to the overall list of 'base_product_sprues'
            base_product_sprues.append(base_product_sprue)

            # Creates 'base_product' to 'base_product_sprue' Requires(Edge)
            base_product_sprue_edge = Requires(
                start_node=base_product,
                end_node=base_product_sprue,
                base_model=True,
                lead_time=FAKER.random_int(1, 1000),    # In Business Days
            )

            # Appends 'base_product_sprue_edge' Requires(Edge) to the overall list of 'base_product_sprue_edges'
            base_product_sprue_edges.append(base_product_sprue_edge)

    logger.info("Base Product Sprues Created")

    return base_product_sprues, base_product_sprue_edges

# endregion

# -------------------------------------------------------------------------------------------
#                                   BASE_PRODUCT_PARTS
# -------------------------------------------------------------------------------------------
# region BASE_PRODUCT_PARTS

def create_base_product_parts(
    base_products: List[Component], 
    base_product_sprues: List[Component], 
    designations_dict: dict, 
    manufacturers_dict: dict
) -> Tuple[List[Component], List[Requires], List[Component]]:
    """
    Generates a fake dataset of base product parts and part edges and their data.

    :param `base_products`: A list of base products and their data.
    :type `base_products`: List[Component]
    :param `base_product_sprues`: A list of base product sprues and their data.
    :type `base_product_sprues`: List[Component]
    :param `designations_dict`: The 'Designation' category of 'resolved_inputdata'.
    :type `designations_dict`: dict
    :param `manufacturers_dict`: The 'Manufacturer' category of 'resolved_inputdata'.
    :type `manufacturers_dict`: dict

    :return: A list of base product parts.
    :rtype: List[Component]
    :return: A list of edges between base product sprues and base product parts.
    :rtype: List[Requires]
    :return: A list of sprues that contain vital base product parts.
    :rtype: List[Component]
    """

    # Sets empty lists to collect parts, edges, and vital sprues along with other necessary variables
    base_product_parts = []
    base_product_part_edges = []
    vital_base_product_sprues = []
    manufacturer_keys = list(manufacturers_dict.keys())

    logger.info("Base Product Parts Initialization")

    # Creates all base product parts and edges
    for base_product in base_products:
        parts_categories = designations_dict[base_product.metadata["designation"]]["Parts"]
        for part_category, part_list in parts_categories.items():
            for part_type in part_list:

                # Generates base product part data
                base_product_part_manufacturer = FAKER.random_element(list(manufacturer_keys))
                if part_type in designations_dict[base_product.metadata["designation"]]["Vital Parts"]:
                    base_product_part_vital = True
                else:
                    base_product_part_vital = False

                # Creates 'base_product_part' Component(Node)
                base_product_part = Component(
                    name=f"{part_type} {FAKER.bothify('???#####')}",
                    full_product=False,
                    manufacturer=base_product_part_manufacturer,
                    locations=FAKER.random_element(manufacturers_dict[base_product_part_manufacturer]["Locations"]),
                    product=base_product.id,
                    variant=False,
                    vital=base_product_part_vital,
                    category=part_category,
                    part_type=part_type,
                )

                # Appends 'base_product_part' Component(Node) to the overall list of 'base_product_parts'
                base_product_parts.append(base_product_part)

                for base_product_sprue in base_product_sprues:
                    if base_product_part.metadata["product"] == base_product_sprue.metadata["product"] \
                        and base_product_part.manufacturer == base_product_sprue.manufacturer:
                        logger.debug(f"{part_type} Edge:")

                        # Creates 'base_product_sprue' to 'base_product_part' Requires(Edge)
                        base_product_part_edge = Requires(
                            start_node=base_product_sprue,
                            end_node=base_product_part,
                            base_model=True,
                            lead_time=FAKER.random_int(1, 1000),    # In Business Days
                        )

                        # Appends 'base_product_sprue_edge' Requires(Edge) to the overall list of 'base_product_sprue_edges'
                        base_product_part_edges.append(base_product_part_edge)

                        # If the part being added to that sprue is vital
                        # Appends 'base_product_sprue' Component(Node) to the overall list of 'vital_base_product_sprues'
                        if base_product_part_vital:
                            vital_base_product_sprues.append(base_product_sprue)

    logger.info("Base Product Parts Created")

    return base_product_parts, base_product_part_edges, vital_base_product_sprues

# endregion

# -------------------------------------------------------------------------------------------
#                               RESOLVE_BASE_PRODUCT_SPRUES
# -------------------------------------------------------------------------------------------
# region RESOLVE_BASE_PRODUCT_SPRUES

def resolve_base_product_sprues(
    base_product_sprues: List[Component],
    base_product_sprue_edges: List[Requires],
    base_product_part_edges: List[Requires],
) -> Tuple[List[Component], List[Requires]]:
    """
    Generates the new resolved lists of sprues and sprue edges to replace the old lists.

    :param `base_product_sprues`: A list of base product sprues and their data.
    :type `base_product_sprues`: List[Component]
    :param `base_product_sprue_edges`: A list of base produuct sprue edges and their data.
    :type `base_product_sprue_edges`: List[Requires]
    :param `base_product_part_edges`: A list of base product part edges and their data.
    :type `base_product_part_edges`: List[Requires]

    :return: A new resolved list of base product sprues.
    :rtype: List[Components]
    :return: A new resolved list of base product sprue edges.
    :rtype: List[Requires]
    """
        
    # Sets empty lists to collect sprues and edges to keep
    resolved_base_sprues = []
    resolved_base_sprue_edges = []

    logger.info("Base Product Sprues Resolution Start")

    # Checks that all sprues are used
    for i, base_product_sprue in enumerate(base_product_sprues, start=1):
        logger.debug(f"Sprue {i}:")
        
        # Checks if a sprue has any edges to parts
        has_edge = any(edge.start_node == base_product_sprue for edge in base_product_part_edges)
        if has_edge:
            # Appends 'base_product_sprue' Component(Node) to the overall new list of 'base_product_sprues'
            resolved_base_sprues.append(base_product_sprue)
            logger.debug(f"Kept Sprue {i}")

            # Appends 'base_product_sprue_edge' Requires(Edge) to the overall new list of 'base_product_sprue_edges'
            resolved_base_sprue_edges.extend(e for e in base_product_sprue_edges if e.end_node == base_product_sprue)
            logger.debug(f"Kept Edges for Sprue {i}")
            logger.debug("")
        else:
            logger.debug(f"Removed Base Product Sprue {i}:")
            logger.debug(base_product_sprue)
            logger.debug("")

    logger.info("Base Product Sprues Resolved")

    return resolved_base_sprues, resolved_base_sprue_edges

# endregion

# -------------------------------------------------------------------------------------------
#                                   NAMING_CONVENTIONS
# -------------------------------------------------------------------------------------------
# region NAMING_CONVENTIONS

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

def get_next_output_filename(base_name: str, extension: str, output_dir: Path = Path("output")) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    index = 1
    if not extension.startswith("."):
        extension = "." + extension
    while True:
        filename = output_dir / f"test{index}_{base_name}{extension}"
        if not filename.exists():
            logger.info("Creating new output file: %s at index %s", filename, index)
            return filename
        index += 1

# endregion

# -------------------------------------------------------------------------------------------
#                                   VARIANT_PRODUCTS
# -------------------------------------------------------------------------------------------
# region VARIANT_PRODUCTS

class NamingError(Exception):
    pass


def current_designation_value(current_designation):
    match = re.search(r'([A-Z]+)$', current_designation)
    if not match:
        return 0
    current_letters = match.group(1)
    value = 0
    for i, char in enumerate(reversed(current_letters)):
        value += (ord(char) - ord("A") + 1) * (26 ** i)
    return value


def find_current_designation(
    variant_base_product: Component,
    variant_products: List[Component]
) -> str:
    """ Finds the current designation of a variant base product by checking existing variant products.
    :param variant_base_product: The base product for which the current designation is being found.
    :type variant_base_product: Component
    :param variant_products: A list of existing variant products to determine the current designation.
    :type variant_products: List[Component]

    :return: The current designation string of the variant base product.
    :rtype: str
    """

    current_designations = []
    for variant_product in variant_products:
        if variant_product.metadata.get("variant_base_product") == variant_base_product.id:
            designation = variant_product.metadata.get("designation")
            if designation:
                current_designations.append(designation)

    if not current_designations:
        raise NamingError(f"VariantNameIdentificationError: {variant_base_product.id} has No Preexisting Variants")
    current_designation = max(current_designations, key=current_designation_value)
    return current_designation

def next_variant_designation(
    variant_base_product: Component,
    variant_products: List[Component]
) -> str:
    """
    Returns the next variant designation letter in a base-26 alphabetical sequence.
    After 'Z', it continues with 'AA', 'AB', etc.
    
    :param variant_base_product: The base product for which the next variant designation is being generated.
    :type variant_base_product: Component
    :param variant_products: A list of existing variant products to determine the current designation.
    :type variant_products: List[Component]

    :return: The next variant designation string.
    :rtype: str
    """

    try:
        current_designation = find_current_designation(variant_base_product, variant_products)
    except NamingError as e:
        logger.warning(f"{type(e).__name__}: {e}")
        return variant_base_product.metadata["designation"] + "A"

    match = re.search(r'([A-Z]+)$', current_designation)
    if not match:
        raise SystemExit(FAILURE)
    current_letter = match.group(1)
    letters = list(current_letter)
    logger.info(f"INPUT: Letters:         {letters}")
    i = len(letters) - 1
    logger.debug(f"I:       {i}")

    while i >= 0:
        if letters[i] != "Z":
            start_letter = letters[i]
            letters[i] = chr(ord(letters[i]) + 1)
            changed_letter = letters[i]
            logger.info(f"Start Letter of '{start_letter}' Changed to '{changed_letter}'")
            logger.debug(f"Letters:         {letters}")
            logger.debug(f"OUTPUT: New Letters:         {letters}")
            break
        else:
            start_letter = letters[i]
            letters[i] = "A"
            changed_letter = letters[i]
            logger.info(f"Start Letter of '{start_letter}' Changed to '{changed_letter}'")
            logger.debug(f"Letters:         {letters}")
            i -= 1
            logger.debug(f"I:       {i}")

    # If all characters were 'Z', we need to add a new 'A' at the beginning
    if i <0:
        letters.insert(0, "A")
    next_letters = "".join(letters)
    next_designation = re.sub(r'([A-Z]+)$', next_letters, current_designation)
    logger.info(f"OUTPUT: New Letters:         {letters}")
    logger.info(f"Next Designation:         {next_designation}")
    return next_designation


def create_variant_products(
    base_products: List[Component],
    manufacturers_dict: dict,
    num_variants: int = 10
)  -> List[Component]:
    """
    Creates a list of variant products based on the base products. Variants are any products that are not the original base product, but are based on it. Many of the components will be similar.

    Ex. Shelby Mustang GT500 is a variant of the Ford Mustang, but has different performance parts and other components.
    Ex. A variant of a base product with designation "A" will have a designation of "A", "B", "C", etc. for each variant, and the popular name will be the same as the base product.

    :param base_products: A list of base products and their data.
    :type base_products: List[Component]
    :param manufacturers_dict: The 'Manufacturer' category of 'resolved_inputdata'.
    :type manufacturers_dict: dict   
    :param num_variants: The total number of unique variant products to include in the supply chain.
                         Defaults to 10.
    :type num_variants: int

    :return: A list of variant products.
    """

    # Sets empty list to collect variant products along with other necessary variables
    variant_products = []
    manufacturer_keys = list(manufacturers_dict.keys())

    logger.info("Variant Products Initialization")

    # Creates all variant products
    for _ in range(num_variants):

        # Picks a random base product to create a variant of
        variant_base_product = FAKER.random_element(base_products)
        # Generates variant product data
        variant_designation = next_variant_designation(variant_base_product, variant_products)
        variant_manufacturer = FAKER.random_element(manufacturer_keys)

        # Creates 'variant_product' Component(Node)
        variant_product = Component(
            name=f"{variant_base_product.metadata['popular_name']} {variant_designation}", 
            manufacturer=variant_manufacturer,
            locations=FAKER.random_element(list(manufacturers_dict[variant_manufacturer]["Locations"])),
            full_product=True,
            variant=True,
            variant_base_product=variant_base_product.id,
            designation=variant_base_product.metadata["designation"],
            popular_name=variant_base_product.metadata["popular_name"]
            )

        # Appends 'variant_product' Component(Node) to the overall list of 'variant_products'
        variant_products.append(variant_product)
    
    logger.info("Variant Products Created")

    return variant_products

# endregion

# -------------------------------------------------------------------------------------------
#                                   VARIANT_SPRUES
# -------------------------------------------------------------------------------------------
# region VARIANT_SPRUES

def create_variant_product_sprues(
    variant_products: List[Component],
    vital_base_product_sprues: List[Component],
    base_product_part_edges: List[Requires],
    designations_dict: dict,
    manufacturers_dict: dict
)  -> Tuple[List[Component], List[Requires], dict, dict]:
    """
    Creates a list of variant product sprues based on the variant products. Variants are any products that are not the original base product, but are based on it. Many of the components will be similar.

    :param variant_products: A list of variant products and their data.
    :type variant_products: List[Component]
    :param vital_base_product_sprues: A list of vital base product sprues and their data.
    :type vital_base_product_sprues: List[Component]
    :param base_product_part_edges: A list of base product part edges and their data.
    :type base_product_part_edges: List[Requires]
    :param designations_dict: The 'Designation' category of 'resolved_inputdata'.
    :type designations_dict: dict
    :param manufacturers_dict: The 'Manufacturer' category of 'resolved_inputdata'.
    :type manufacturers_dict: dict

    :return: A list of variant product sprues.
    :rtype: List[Component]
    :return: A list of edges between variant products and variant product sprues.
    :rtype: List[Requires]
    :return: A dictionary of needed parts for each variant product.
    :rtype: dict
    :return: A dictionary of needed manufacturers for each variant product.
    :rtype: dict
    """

    # Sets empty list to collect variant sprues and edges along with other necessary variables
    variant_sprues = []
    variant_sprue_edges = []
    needed_parts = {}
    needed_manufacturers = {}

    logger.info("Variant Product Sprues Initialization")

    # Creates all base product sprues and edges
    # Iterates through each variant product and determines its needed parts and manufacturers
    for variant_product in variant_products:

        # Individual sets to collect needed parts and manufacturers for each variant product
        # Implemented as sets to avoid duplicates (I remembered sets) - CGH
        individual_needed_parts = set()
        designation = designations_dict.get(variant_product.metadata["designation"])

        # If the designation exists, get the parts for that designation
        if designation:
            parts = designation.get("Parts")
            for part_list in parts.values():
                individual_needed_parts.update(part_list)
        
        individual_needed_manufacturers = set(manufacturers_dict.keys())

        # If the variant product is a variant of a base product, it will have the 'variant_base_product' metadata field
        for vital_sprue in vital_base_product_sprues:

            # Check vital base product sprues to see if the variant product is based on a vital base product
            if variant_product.metadata["variant_base_product"] == vital_sprue.metadata["product"]:
                variant_sprues.append(vital_sprue)
                
                variant_sprue_edge = Requires(
                    start_node=variant_product,
                    end_node=vital_sprue,
                    base_model=True,
                    lead_time=FAKER.random_int(1, 1000),    # In Business Days
                )

                variant_sprue_edges.append(variant_sprue_edge)

                individual_needed_manufacturers.discard(vital_sprue.manufacturer)

                for base_product_part_edge in base_product_part_edges:
                    if base_product_part_edge.start_node == vital_sprue:
                        individual_needed_parts.discard(base_product_part_edge.end_node.metadata["part_type"])

        needed_parts[variant_product.id] = individual_needed_parts
        needed_manufacturers[variant_product.id] = individual_needed_manufacturers

        for manufacturer in individual_needed_manufacturers:

            variant_sprue = Component(
                name=f"Sprue {FAKER.bothify('???########')}",
                full_product=False,
                product=variant_product.id,
                manufacturer=manufacturer,
                locations=FAKER.random_element(manufacturers_dict[manufacturer]["Locations"]),
                variant=True,
            )

            variant_sprues.append(variant_sprue)

            # Creates 'base_product' to 'base_product_sprue' Requires(Edge)
            variant_sprue_edge = Requires(
                start_node=variant_product,
                end_node=variant_sprue,
                base_model=True,
                lead_time=FAKER.random_int(1, 1000),    # In Business Days
            )

            variant_sprue_edges.append(variant_sprue_edge)
 
    logger.info("Variant Product Sprues Created")

    return variant_sprues, variant_sprue_edges, needed_parts, needed_manufacturers

# endregion

# -------------------------------------------------------------------------------------------
#                                   VARIANT_PARTS
# -------------------------------------------------------------------------------------------
# region VARIANT_PARTS

def create_variant_parts(
    variant_products: List[Component], 
    variant_sprues: List[Component], 
    needed_parts: dict, 
    needed_manufacturers: dict,
    designations_dict: dict,
    manufacturers_dict: dict
) -> Tuple[List[Component], List[Requires]]:
    """
    Creates a list of variant product parts based on the variant products. Variants are any products that are not the original base product, but are based on it. Many of the components will be similar. 

    :param variant_products: A list of variant products and their data.
    :type variant_products: List[Component]
    :param variant_sprues: A list of variant product sprues and their data.
    :type variant_sprues: List[Component]
    :param needed_parts: A dictionary of needed parts for each variant product.
    :type needed_parts: dict
    :param needed_manufacturers: A dictionary of needed manufacturers for each variant product.
    :type needed_manufacturers: dict
    :param designations_dict: The 'Designation' category of 'resolved_inputdata'.
    :type designations_dict: dict    
    :param manufacturers_dict: The 'Manufacturer' category of 'resolved_inputdata'.
    :type manufacturers_dict: dict

    :return: A list of variant product parts.
    :rtype: List[Component]
    :return: A list of edges between variant products and variant product parts.
    :rtype: List[Requires]
    """

    variant_parts = []
    variant_part_edges = []

    logger.info("Variant Parts Initialization")

    # Creates all base product parts and edges
    for variant_product in variant_products:

        parts_categories = designations_dict[variant_product.metadata["designation"]]["Parts"]
        for part_category, _ in parts_categories.items():
            for part_type in needed_parts[variant_product.id]:

                # Generates base product part data
                variant_part_manufacturer = FAKER.random_element(needed_manufacturers[variant_product.id])

                # Creates 'base_product_part' Component(Node)
                variant_part = Component(
                    name=f"{part_type} {FAKER.bothify('???#####')}",
                    full_product=False,
                    manufacturer=variant_part_manufacturer,
                    locations=FAKER.random_element(manufacturers_dict[variant_part_manufacturer]["Locations"]),
                    product=variant_product.id,
                    variant=True,
                    category=part_category,
                    part_type=part_type,
                )

                variant_parts.append(variant_part)

                for variant_sprue in variant_sprues:
                    if variant_part.metadata["product"] == variant_sprue.metadata["product"] \
                        and variant_part.manufacturer == variant_sprue.manufacturer:

                        # Creates 'base_product_sprue' to 'base_product_part' Requires(Edge)
                        variant_part_edge = Requires(
                            start_node=variant_sprue,
                            end_node=variant_part,
                            base_model=True,
                            lead_time=FAKER.random_int(1, 1000),    # In Business Days
                        )

                        # Appends 'base_product_sprue_edge' Requires(Edge) to the overall list of 'base_product_sprue_edges'
                        variant_part_edges.append(variant_part_edge)
    
    logger.info("Variant Parts Created")

    return variant_parts, variant_part_edges

# endregion

# -------------------------------------------------------------------------------------------
#                                    MAIN_FUNCTION
# -------------------------------------------------------------------------------------------
# region MAIN_FUNCTION

def main(num_products: int = 40, variant_distribution: float = 0.25):
    """
    Main Function to generate a fake supply chain.

    :param num_products: The total number of unique model aircraft products to include in the supply chain.
                         Defaults to 40.
    :param variant_distribution: A float (0.0 to 1.0) controlling the proportion of products that will have variants.
                         Defaults to 0.25, meaning roughly 25% of products will be variations.
    :return: A dictionary representing the supply chain.
    """

    logger.info("Main Start")

    # Validates and resolves 'inputdata.json'
    try:
        resolved_inputdata = resolve_json("inputdata.json")
    except Exception as e:
        logger.critical(f"{type(e).__name__}: {e}")
        raise SystemExit(FAILURE)

    logger.info("Inputs Accepted")

    # Sets overall variables
    logger.debug("Local Main Variables: ")
    logger.debug(f"Num_Products:        {num_products}")
    logger.debug(f"Variant_Distribution:        {variant_distribution}")
    num_variants = int(num_products * variant_distribution)
    logger.debug(f"Num_Variants:        {num_variants}")
    num_base_products = num_products - num_variants
    logger.debug(f"Num_Base_Products:        {num_base_products}")
    designations_dict = resolved_inputdata["Designations"]
    manufacturers_dict = resolved_inputdata["Manufacturers"]
    logger.info("Local Main Variables Set")

    base_products = create_base_products(num_base_products, designations_dict, manufacturers_dict)
    logger.info("Base Products Created")
    base_product_sprues, base_product_sprue_edges = create_base_product_sprues(base_products, manufacturers_dict)
    logger.info("Base Product Sprues Created")
    base_product_parts, base_product_part_edges, vital_base_product_sprues =  create_base_product_parts(base_products, base_product_sprues, designations_dict, manufacturers_dict)
    logger.info("Base Product Parts Created")
    resolved_base_product_sprues, resolved_base_product_sprue_edges = resolve_base_product_sprues(base_product_sprues, base_product_sprue_edges, base_product_part_edges)
    logger.info("Base Product Sprues Resolved")
    variant_products = create_variant_products(base_products, manufacturers_dict, num_variants)
    logger.info("Variant Products Created")
    variant_sprues, variant_sprue_edges, needed_parts, needed_manufacturers = create_variant_product_sprues(variant_products, vital_base_product_sprues, base_product_part_edges, designations_dict, manufacturers_dict)
    logger.info("Variant Sprues Created")
    variant_parts, variant_part_edges = create_variant_parts(variant_products, variant_sprues, needed_parts, needed_manufacturers, designations_dict, manufacturers_dict)
    logger.info("Variant Parts Created")

    # Collect all components and edges
    base_components = base_products + resolved_base_product_sprues + base_product_parts
    variant_components = variant_products + variant_sprues + variant_parts
    components = base_components + variant_components
    base_edges = resolved_base_product_sprue_edges + base_product_part_edges
    variant_edges = variant_sprue_edges + variant_part_edges
    edges = base_edges + variant_edges
    logger.info("Lists Consolidated")

    # Write to CSV
    Component.write_to_csv(components, get_next_output_filename("components", "csv"))
    Requires.write_to_csv(base_edges, get_next_output_filename("edges", "csv"))
    logger.info("CSV Files Created")

    logger.info("Main End")

# endregion

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        logger.warning(f"{type(e).__name__}: Input Processing Interrupted by User -- Exiting")
        raise SystemExit(INTERRUPTED)
