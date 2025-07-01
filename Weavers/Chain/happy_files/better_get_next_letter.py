import logging
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

def main(current_letter):
    """
    Returns the next variant designation letter in a base-26 alphabetical sequence.
    After 'Z', it continues with 'AA', 'AB', etc.
    
    :param current_letter: The current variant designation string (e.g., 'A', ..., 'Z', 'AA', ...)
    :return: The next variant designation string.
    """
    letters = list(current_letter)
    logger.info(f"INPUT Letters:         {letters}")
    i = len(letters) - 1
    logger.debug(f"I:       {i}")

    while i >= 0:
        if letters[i] != "Z":
            start_letter = letters[i]
            letters[i] = chr(ord(letters[i]) + 1)
            new_letter = letters[i]
            logger.info(f"Start Letter of '{start_letter}' Changed to New Letter of '{new_letter}'")
            logger.debug(f"Letters:         {letters}")
            logger.debug(f"OUTPUT Letters:         {letters}")
            return "".join(letters)
        else:
            start_letter = letters[i]
            letters[i] = "A"
            new_letter = letters[i]
            logger.info(f"Start Letter of '{start_letter}' Changed to New Letter of '{new_letter}'")
            logger.debug(f"Letters:         {letters}")
            i -= 1
            logger.debug(f"I:       {i}")

    # If all characters were 'Z', we need to add a new 'A' at the beginning
    logger.info(f"OUTPUT Letters:         {list('A' + ''.join(letters))}")
    return "A" + "".join(letters)

if __name__ == "__main__":
    logger.info(main("ZZZ"))