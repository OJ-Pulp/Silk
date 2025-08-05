import logging
import re
from typing import List, Union

# -------------------------------------------------------------------------------------------
#                                   LOGGING_SETTINGS
# -------------------------------------------------------------------------------------------
# region LOGGING_SETTINGS

SUCCESS = 0
FAILURE = 1
INTERRUPTED = 130

# Configures for logging showing messages level INFO and above
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Suppresses debug messages from faker library
logging.getLogger("faker").setLevel(logging.INFO)

# endregion

# Local
try:
    from Weavers.Chain.data_model import Component, Requires
    #import input_utils
except ModuleNotFoundError as e:
    logger.critical(f"{type(e).__name__}: Missing Required Local Module '{e.name}' -- Check that '{e.name}.py' is in the Same Directory as 'ChainWeaver.py' -- Exiting")
    raise SystemExit(FAILURE)

class NamingError(Exception):
    pass


def current_designation_value(current_designation):
    current_letters = re.search(r'([A-Z]+)$', current_designation).group(1)
    value = 0
    for i, char in enumerate(reversed(current_letters)):
        value += (ord(char) - ord("A") + 1) * (26 ** i)
    return value


def find_current_designation(
    variant_base_product: Component,
    variant_products: List[Component]
) -> str:
    
    base_designation = variant_base_product.metadata["designation"]
    current_designations = []
    for variant_product in variant_products:
        if variant_product.metadata["variant_base_product"] == variant_base_product.id:
            current_designations.append(re.search(r'([A-Z]+)$', variant_product.metadata["designation"]))

    try:
        current_designation = max(current_designations, key=current_designation_value())
        return current_designation
    except:
        raise NamingError(f"VariantNameIdentificationError: {variant_base_product.id} has No Preexisting Variants")


def main(
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
        return variant_base_product.metadata("designation") + "A"

    current_letters = re.search(r'([A-Z]+)$', current_designation).group(1)
    letters = list(current_letters)
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

if __name__ == "__main__":
    main("C-17AEZ")