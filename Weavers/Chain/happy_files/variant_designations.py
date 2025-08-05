
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