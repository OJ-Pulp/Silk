"""
OVERALL CHAINWEAVER
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

logger.info("Program Start")

FAKER_GEN = faker.Faker()
logger.info("Global Variables Set")

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
    designation_keys = list(designations_dict.keys())
    manufacturer_keys = list(manufacturers_dict.keys())
    designation_counter = {designation_type: 0 for designation_type in designation_keys}

    # Creates all base products
    for i in range(num_base_products):
        logger.debug(f"Base Product {i}:")

        # Generates base product data
        selected_designation = FAKER_GEN.random_element(elements=designation_keys)
        designation_counter[selected_designation] += 1
        designation = f"{selected_designation}-{designation_counter[selected_designation]}"
        popular_name = FAKER_GEN.word(part_of_speech="noun").capitalize()
        manufacturer = FAKER_GEN.random_element(elements=manufacturer_keys)

        # Creates 'base_product' Component(Node)
        base_product = Component(
            name=f"{popular_name} {designation}",
            full_product=True,
            variant=False,
            manufacturer=manufacturer,
            locations=FAKER_GEN.random_element(elements=list(manufacturers_dict[manufacturer]["Locations"])),
            designation=selected_designation,
            popular_name=popular_name,
        )

        # Appends 'base_product' Component(Node) to the overall list of 'base_products'
        base_products.append(base_product)
        logger.debug(base_product)
        logger.debug("")

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

    # Creates all base product sprues and edges
    for i, base_product in enumerate(base_products, start=1):
        logger.debug(f"Base Product {i}:")

        for manufacturer in manufacturer_keys:
            logger.debug(f"{manufacturer} Base Product Sprue:")

            # Creates 'base_product_sprue' Component(Node)
            base_product_sprue = Component(
                name=f"Sprue {FAKER_GEN.bothify(text='???########')}",
                full_product=False,
                product=base_product.id,
                manufacturer=manufacturer,
                locations=FAKER_GEN.random_element(elements=manufacturers_dict[manufacturer]["Locations"]),
                variant=False,
            )

            # Appends 'base_product_sprue' Component(Node) to the overall list of 'base_product_sprues'
            base_product_sprues.append(base_product_sprue)
            logger.debug(base_product_sprue)
            logger.debug("")

            logger.debug(f"{manufacturer} Base Product Sprue Edge:")

            # Creates 'base_product' to 'base_product_sprue' Requires(Edge)
            base_product_sprue_edge = Requires(
                start_node=base_product,
                end_node=base_product_sprue,
                base_model=True,
                lead_time=FAKER_GEN.random_int(1, 1000),    # In Business Days
            )

            # Appends 'base_product_sprue_edge' Requires(Edge) to the overall list of 'base_product_sprue_edges'
            base_product_sprue_edges.append(base_product_sprue_edge)
            logger.debug(base_product_sprue_edge)
            logger.debug("")

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
    # designation_keys = list(designations_dict.keys())
    manufacturer_keys = list(manufacturers_dict.keys())

    # Creates all base product parts and edges
    for i, base_product in enumerate(base_products, start=1):
        logger.debug(f"Base Product {i}:")

        parts_categories = designations_dict[base_product.metadata["designation"]]["Parts"]
        for part_category, part_list in parts_categories.items():
            for part_type in part_list:
                logger.debug(f"{part_type}:")

                # Generates base product part data
                base_product_part_manufacturer = FAKER_GEN.random_element(elements=list(manufacturer_keys))
                if part_type in designations_dict[base_product.metadata["designation"]]["Vital Parts"]:
                    base_product_part_vital = True
                else:
                    base_product_part_vital = False

                # Creates 'base_product_part' Component(Node)
                base_product_part = Component(
                    name=f"{part_type} {FAKER_GEN.bothify(text='???#####')}",
                    full_product=False,
                    manufacturer=base_product_part_manufacturer,
                    locations=FAKER_GEN.random_element(elements=manufacturers_dict[base_product_part_manufacturer]["Locations"]),
                    product=base_product.id,
                    variant=False,
                    vital=base_product_part_vital,
                    category=part_category,
                    part_type=part_type,
                )

                # Appends 'base_product_part' Component(Node) to the overall list of 'base_product_parts'
                base_product_parts.append(base_product_part)
                logger.debug(base_product_part)
                logger.debug("")

                for base_product_sprue in base_product_sprues:
                    if base_product_part.metadata["product"] == base_product_sprue.metadata["product"] \
                        and base_product_part.manufacturer == base_product_sprue.manufacturer:
                        logger.debug(f"{part_type} Edge:")

                        # Creates 'base_product_sprue' to 'base_product_part' Requires(Edge)
                        base_product_part_edge = Requires(
                            start_node=base_product_sprue,
                            end_node=base_product_part,
                            base_model=True,
                            lead_time=FAKER_GEN.random_int(1, 1000),    # In Business Days
                        )

                        # Appends 'base_product_sprue_edge' Requires(Edge) to the overall list of 'base_product_sprue_edges'
                        base_product_part_edges.append(base_product_part_edge)
                        logger.debug(base_product_part_edge)
                        logger.debug("")

                        # If the part being added to that sprue is vital
                        # Appends 'base_product_sprue' Component(Node) to the overall list of 'vital_base_product_sprues'
                        if base_product_part_vital:
                            vital_base_product_sprues.append(base_product_sprue)

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
    base_sprues_keep = []
    base_sprue_edges_keep = []

    # Checks that all sprues are used
    for i, base_product_sprue in enumerate(base_product_sprues, start=1):
        logger.debug(f"Sprue {i}:")
        
        # Checks if a sprue has any edges to parts
        has_edge = any(edge.start_node == base_product_sprue for edge in base_product_part_edges)
        if has_edge:
            # Appends 'base_product_sprue' Component(Node) to the overall new list of 'base_product_sprues'
            base_sprues_keep.append(base_product_sprue)
            logger.debug(f"Kept Sprue {i}")

            # Appends 'base_product_sprue_edge' Requires(Edge) to the overall new list of 'base_product_sprue_edges'
            base_sprue_edges_keep.extend(e for e in base_product_sprue_edges if e.end_node == base_product_sprue)
            logger.debug(f"Kept Edges for Sprue {i}")
            logger.debug("")
        else:
            logger.debug(f"Removed Base Product Sprue {i}:")
            logger.debug(base_product_sprue)
            logger.debug("")

    return base_sprues_keep, base_sprue_edges_keep

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

def get_next_test_output_filename(base_name: str, extension: str, output_dir: Path = Path("output")) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    index = 1
    if not extension.startswith("."):
        extension = "." + extension
    while True:
        filename = output_dir / f"test{index}_{base_name}{extension}"
        if not filename.exists():
            logger.warning(index)
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
    
    :param current_letter: The current variant designation string (e.g., 'A', ..., 'Z', 'AA', ...)
    :return: The next variant designation string.
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
    INSERT STUFF
    """

    # Sets empty list to collect variant products along with other necessary variables
    variant_products = []
    manufacturer_keys = list(manufacturers_dict.keys())

    # Creates all variant products
    for i in range(num_variants):
        logger.debug(f"Variant Product {i}:")

        # Picks a random base product to create a variant of
        variant_base_product = FAKER_GEN.random_element(elements=base_products)
        # Generates variant product data
        variant_designation = next_variant_designation(variant_base_product, variant_products)
        variant_manufacturer = FAKER_GEN.random_element(elements=manufacturer_keys)

        # Creates 'variant_product' Component(Node)
        variant_product = Component(
            name=f"{variant_base_product.metadata['popular_name']} {variant_designation}", 
            manufacturer=variant_manufacturer,
            locations=FAKER_GEN.random_element(elements=list(manufacturers_dict[variant_manufacturer]["Locations"])),
            full_product=True,
            variant=True,
            variant_base_product=variant_base_product.id,
            designation=variant_designation, 
            popular_name=variant_base_product.metadata["popular_name"]
            )

        # Appends 'variant_product' Component(Node) to the overall list of 'variant_products'
        variant_products.append(variant_product)
        logger.debug(variant_product)
        logger.debug("")
    
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
    manufacturers_dict: dict,
    part_types_list: list
)  -> Tuple[List[Component], List[Requires], dict]:
    """
    INSERT STUFF
    """

    # Sets empty list to collect variant sprues and edges along with other necessary variables
    variant_sprues = []
    variant_sprue_edges = []
    manufacturer_keys = list(manufacturers_dict.keys())
    needed_parts = {}

    # Creates all base product sprues and edges
    for i, variant_product in enumerate(variant_products, start=1):
        logger.debug(f"Variant Product {i}:")

        individual_needed_parts = part_types_list
        needed_manufacturers = list(manufacturers_dict.keys())

        for vital_sprue in vital_base_product_sprues:
            if variant_product.metadata["variant_base_product"] == vital_sprue.metadata["product"]:
                variant_sprues.append(vital_sprue)
                
                variant_sprue_edge = Requires(
                    start_node=variant_product,
                    end_node=vital_sprue,
                    base_model=True,
                    lead_time=FAKER_GEN.random_int(1, 1000),    # In Business Days
                )

                variant_sprue_edges.append(variant_sprue_edge)
                if vital_sprue.manufacturer in needed_manufacturers:
                    needed_manufacturers.remove(vital_sprue.manufacturer)

                for base_product_part_edge in base_product_part_edges:
                    if base_product_part_edge.start_node == vital_sprue:
                        if base_product_part_edge.end_node.metadata["part_type"] in individual_needed_parts:
                            individual_needed_parts.remove(base_product_part_edge.end_node.metadata["part_type"])

        needed_parts[variant_product.id] = individual_needed_parts

        for manufacturer in needed_manufacturers:
            logger.debug(f"{manufacturer} Variant Sprue:")

            variant_sprue = Component(
                name=f"Sprue {FAKER_GEN.bothify(text='???########')}",
                full_product=False,
                product=variant_product.id,
                manufacturer=manufacturer,
                locations=FAKER_GEN.random_element(elements=manufacturers_dict[manufacturer]["Locations"]),
                variant=True,
            )

            variant_sprues.append(variant_sprue)

            logger.debug(f"{manufacturer} Variant Sprue Edge:")

            # Creates 'base_product' to 'base_product_sprue' Requires(Edge)
            variant_sprue_edge = Requires(
                start_node=variant_product,
                end_node=variant_sprue,
                base_model=True,
                lead_time=FAKER_GEN.random_int(1, 1000),    # In Business Days
            )

            variant_sprue_edges.append(variant_sprue_edge)
    
    return variant_sprues, variant_sprue_edges, needed_parts

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
    part_types_list = []
    for designation in resolved_inputdata["Designations"].values():
        parts = designation.get("Parts", {})
        for part_list in parts.values():
            part_types_list.extend(part_list)
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
    variant_sprues, variant_sprue_edges, needed_parts = create_variant_product_sprues(
        variant_products,
        vital_base_product_sprues, 
        base_product_part_edges, 
        manufacturers_dict, 
        part_types_list
    )

    # Collect all components and edges
    base_components = base_products + resolved_base_product_sprues + base_product_parts
    variant_components = variant_products
    components = base_components + variant_components
    base_edges = resolved_base_product_sprue_edges + base_product_part_edges
    logger.info("Lists Consolidated")

    # Write to CSV
    Component.write_to_csv(components, get_next_test_output_filename("components", "csv"))
    Requires.write_to_csv(base_edges, get_next_test_output_filename("edges", "csv"))
    logger.info("CSV Files Created")

    logger.info("Main End")

# endregion

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        logger.warning(f"{type(e).__name__}: Input Processing Interrupted by User -- Exiting")
        raise SystemExit(INTERRUPTED)

logger.info("Program End")
