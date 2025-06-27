"""
OVERALL INPUT SANITATION AND VALIDATION
"""

# Standard
import json
import logging
import mimetypes
import re
import sys
from pathlib import Path
from typing import Union, List, Tuple

# -------------------------------------------------------------------------------------------
#                                   LOGGING_SETTINGS
# -------------------------------------------------------------------------------------------
# region LOGGING_SETTINGS

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
    from jsonschema import validate, ValidationError
except ModuleNotFoundError as e:
    logger.critical(f"{type(e).__name__}: Missing Required Module '{e.name}' -- Try 'python -m pip install {e.name}' -- Exiting")
    sys.exit(1)

logger.info("Program Start")

ALLOWED_EXTENSIONS = {"json"}
logger.debug(f"Allowed Extensions:      {ALLOWED_EXTENSIONS}")
ALLOWED_MIME_TYPES = {"application/json"}
logger.debug(f"Allowed MIME Types:      {ALLOWED_MIME_TYPES}")

# Creates an overarching error type for input data
class InputError(Exception):
    pass

# [ ] Add types
# [ ] WARNING InputError
# [ ] validate or validate_file
# [ ] secure or secure_filename
# [ ] load or load_file
# [ ] add more recognized load suffixes
# [ ] error or critical
# [ ] load Exiting?
# [ ] security in load or securing around load
# [ ] logger.debug

def sanitize(filename: str) -> Tuple[str, Path]:
    path = Path(filename)
    if not path.exists():
        raise InputError(f"FileNotFoundError: '{filename}' Not Found -- Exiting")
    suffix = path.suffix.lower()
    sanitized_stem = re.sub(r"[^a-zA-Z0-9_-]", "_", path.stem.replace(".", "_"))

    if suffix:
        if suffix not in ALLOWED_EXTENSIONS:
            raise InputError(f"ValidationError: '{suffix}' Not Accepted -- Exiting")
        sanitized_filename = sanitized_stem + suffix  
    else:
        sanitized_filename = sanitized_stem

    if filename != sanitized_filename:
        logger.warning(f"InputError: ValidationError: '{filename}' Not Accepted -- Renamed to '{sanitized_filename}'")

    semi_sanitized_path = Path("inputs") / sanitized_filename
    sanitized_path = semi_sanitized_path.resolve()

    if path.resolve() != sanitized_path:
        if sanitized_path.exists():
            sanitized_path_stem = sanitized_path.stem
            sanitized_path_suffix = sanitized_path.suffix
            index = 1
            while True:
                sanitized_path = Path(f"{sanitized_path_stem}_{index}{sanitized_path_suffix}")
                if not sanitized_path.exists():
                    break
                logger.debug(f"FileExistsError: '{sanitized_path}' Already Exists")
                index += 1
        if sanitized_filename != sanitized_path.name:
            logger.warning(f"InputError: ValidationError: '{sanitized_path}' Not Accepted -- Renamed to '{sanitized_path.name}'")
        logger.warning(f"InputError: ValidationError: '{path.resolve()}' Not Accepted -- Moved to '{sanitized_path}'")

    sanitized_path.parent.mkdir(parents=True, exist_ok=True)

    path.rename(sanitized_path.resolve())

    return sanitized_path.name, sanitized_path


def load(filename: str) -> Union[dict, str]:
    try:
        file, path = sanitize(filename)
    except Exception as e:
        logger.critical(f"{type(e).__name__}: {e}")
        sys.exit(1)
    try:
        with path.open("r", encoding="utf-8") as f:
            if path.suffix.lower() == ".json":
                try:
                    json_file = json.load(f)
                    if not isinstance(json_file, dict):
                        raise InputError(f"TypeError: '{file}' is Json but Not Dictionary -- Exiting")
                    return json_file
                except json.JSONDecodeError as e:
                    raise InputError(f"{type(e).__name__}: Error Decoding JSON: {e} -- Exiting") from e
            else:
                return f.read()
    except FileNotFoundError as e:
        raise InputError(f"{type(e).__name__}: '{path}' Not Found -- Check that '/inputs' is in the Same Directory as 'input_utils.py' -- Check that '{file}' is in '/inputs/' -- Exiting") from e
        

def sanitize(filename: str) -> bool:
    if filename != secure_filename(filename):
        raise InputError(f"ValidationError: '{filename}' Not Accepted -- Try Checking '{filename}' for Unaccepted Characters")
    file = load(filename)
    if file.mimetype in ALLOWED_MIME_TYPES:
        if "." not in filename:
            mimetypes.guess_extension(filename)
            logger.warning(f"No Extension Found: Missing '.' in '{filename}' -- ")
            filename += mimetypes.guess_extension(filename)
        elif filename.count(".") == 1:
            extension = 
            return True
    else:
        raise InputError(f"ValidationError: '{filename}' MIME Type Not Allowed") 
    
    
    if "." in filename == False:
        logger.warning(f"No Extension Found: Missing '.' in '{filename}' -- ")
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def take_json_input(input_file: Path) -> dict:
    if not extension.startswith("."):
        extension = "." + extension
    while True:
        filename = output_dir / f"test{index}_{base_name}{extension}"
        if not filename.exists():
            logger.warning(index)
            return filename
        try:
            with Path("[{}.json").open("r", encoding="utf-8") as f:
            inputdata = json.load(f)
        except FileNotFoundError as e:
            raise InputError(f"{type(e).__name__}: 'inputdata.json' Not Found -- Check that 'inputdata.json' is in the Same Directory as 'ChainWeaver.py' -- Exiting") from e
        except json.JSONDecodeError as e:
            raise InputError(f"{type(e).__name__}: Error Decoding JSON: {e} -- Exiting") from e


def validate_inputdata() -> dict:
    """
    Validates that the required input file of 'inputdata.json' is present, decoded correctly, and matching the desired structure of the schema.
    
    :raises InputError: If 'inputdata.json' is not found, decoded incorrectly, not matching the desired structure of the schema.

    :return: The validated information of 'inputdata.json'.
    :rtype: dict
    """

    # Validates that the required input file of 'inputdata.json' is present and decoded correctly
    try:
        with Path("inputdata.json").open("r", encoding="utf-8") as f:
            inputdata = json.load(f)
    except FileNotFoundError as e:
        raise InputError(f"{type(e).__name__}: 'inputdata.json' Not Found -- Check that 'inputdata.json' is in the Same Directory as 'ChainWeaver.py' -- Exiting") from e
    except json.JSONDecodeError as e:
        raise InputError(f"{type(e).__name__}: Error Decoding JSON: {e} -- Exiting") from e

    # Validates that the required input file of 'inputdata.json' matches the desired structure of the schema
    try:
        validate(inputdata, inputdata_schema)
    except ValidationError as e:
        raise InputError(f"{type(e).__name__}: Invalid 'inputdata.json' Structure -- {e.message} -- Exiting -- {traceback.format_exc()}")

    return inputdata


def resolve_inputdata(inputdata):
    """
    Resolves the input file of 'inputdata.json' by filling the 'Number of Parts' and 'ID' fields.

    :param inputdata: The validated information from the 'inputdata.json' input file.
    :type inputdata: dict

    :raises WARNING: If manual 'Number of Parts' and computer 'Number of Parts' do not match.

    :return: The resolved information of 'inputdata.json'.
    :rtype: dict
    """

    # Creates a new dictionary that is a copy of inputdata that is editable by the program
    resolved_inputdata = copy.deepcopy(inputdata)

    # Resolves 'Number of Parts' for each designation by adding it if missing or warning the user if incorrect
    for designation, data in resolved_inputdata["Designations"].items():
        parts_count = sum(len(part_list) for part_list in data["Parts"].values())
        if "Number of Parts" in data:
            if data["Number of Parts"] != parts_count:
                logger.warning(f"{designation} Number of Parts Mismatch:        manual={data['Number of Parts']}, computed={parts_count}")
        else:
            data["Number of Parts"] = parts_count
            logger.info(f"{designation} Number of Parts Added:      {parts_count}")

    # Resolves 'ID' for each manufacturer by adding it if it is missing
    for manufacturer, data in resolved_inputdata["Manufacturers"].items():
        if "ID" not in data:
            generated_id = str(uuid.uuid4())
            data["ID"] = generated_id
            logger.info(f"{manufacturer} ID Missing -- Generated New ID:       {generated_id}")

    # Writes resolved_inputdata to 'resolved_inputdata.json' so the user can see both inputdata files
    with Path("resolved_inputdata.json").open("w", encoding="utf-8") as f:
        json.dump(resolved_inputdata, f, indent=4)

    return resolved_inputdata

# endregion

# endregion