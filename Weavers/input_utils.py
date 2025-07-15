"""
OVERALL INPUT SANITATION AND VALIDATION
"""

# Standard
import copy
import json
import logging
import re
import traceback
import uuid
from pathlib import Path
from typing import Union, Tuple

# -------------------------------------------------------------------------------------------
#                                   LOGGING_SETTINGS
# -------------------------------------------------------------------------------------------
# region LOGGING_SETTINGS

# SystemExit codes
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

# endregion

# Third-Party
try:
    from jsonschema import validate, ValidationError
    import magic
except ModuleNotFoundError as e:
    logger.critical(f"{type(e).__name__}: Missing Required Module '{e.name}' -- Try 'python -m pip install {e.name}' -- Exiting")
    raise SystemExit(FAILURE)


# -------------------------------------------------------------------------------------------
#                                   EXCEPTION_CLASSES
# -------------------------------------------------------------------------------------------
# region EXCEPTION_CLASSES

# Creates an overarching error type for inputs
class InputError(Exception):
    pass

# [ ] Add subclasses + stuff inside them

# endregion

# -------------------------------------------------------------------------------------------
#                                  INPUT_DIR_SETTINGS
# -------------------------------------------------------------------------------------------
# region INPUT_DIR_SETTINGS

def set_input_dir() -> Path:
    """
    Sets the Input Directory based on the subsidary of Weaver that is calling the utility.

    :return: The Input Directory Path.
    :rtype: Path
    """

    """
    caller_frame = inspect.stack()[1]
    calling_module_name = Path(caller_frame.filename)
    logger.debug(f"Module Name Found: {calling_module_name}")
    """

    # [ ] Change for being called in ChainWeaver
    project_dir = input("Enter Project Directory: ")
    # [ ] Add logger tool for INPUT or ENTER
    try:
        project_dir == re.sub(r"[^a-zA-Z0-9_-]", "_", project_dir)
    except:
        raise InputError("InputDirectoryError: Unaccepted Characters Inputed in Project Directory Name")
    
    return Path(f"Weavers/{project_dir}/inputs")


INPUT_DIR = set_input_dir()
logger.debug(f"Input Directory:         '/{INPUT_DIR}'")

# endregion

# -------------------------------------------------------------------------------------------
#                                  ALLOWED_FILE_TYPES
# -------------------------------------------------------------------------------------------
# region ALLOWED_FILE_TYPES

ALLOWED_FILE_TYPES = {
    ".json": ["application/json", "text/plain"],
    ".txt": ["text/plain"]
}
logger.debug(f"Allowed Extensions:      {list(ALLOWED_FILE_TYPES.keys())}")
logger.debug(f"Allowed MIME Types:      {list(ALLOWED_FILE_TYPES.values())}")    

# endregion

# [ ] Figure out MIME
MIME = magic.Magic(mime=True)



# [ ] Add types
# [ ] WARNING InputError
# [ ] Naming ex. validate or validate_file
# [ ] add more recognized load suffixes
# [ ] error or critical
# [ ] load Exiting?
# [ ] security in load or securing around load
# [ ] logger.debug


def preload(filename: str) -> Path:
    logger.info("Preload Start")
    try:
        path = (Path(f"{Path(INPUT_DIR)}/{filename}")).resolve()
        logger.debug(f"'{filename}' Path:       '{path}'")
        if not path.exists():
            raise FileNotFoundError
        if not path.is_file():
            raise InputError(f"ValidationError: '{filename}' is Not a File -- Try Checking '{path}' -- Exiting")
        logger.info("Preload End")
        return path
    except FileNotFoundError:
        filename_stem = Path(filename).stem
        logger.debug(f"'{filename}' Stem:       '{filename_stem}'")
        filename_stem_matches = list(Path(INPUT_DIR).glob(f"{filename_stem}.*"))
        logger.debug(f"'{filename}' Stem Matches:       '{filename_stem_matches}'")
        if filename_stem_matches == []:
            logger.critical((f"InputError: '{filename}' Not Found -- Try Ensuring '{filename}' is in the expected directory -- Exiting"))
            raise SystemExit(FAILURE)
        path = (filename_stem_matches[0]).resolve()
        logger.warning(f"InputError: ExtensionNotFoundError: '{filename}' Extension Not Found -- Input Changed to '{path.name}'")
        logger.debug(f"'{path.name}' Path:       '{path}'")
        logger.info("Preload End")
        return path
    except InputError as e:
        logger.critical(f"{type(e).__name__}: {e}")
        raise SystemExit(FAILURE)


def sanitize(filename) -> str:
    path = preload(filename)
    logger.info("Sanitize Start")
    filename = path.name
    #mimetype = MIME.from_file(str(path))    
    suffix = path.suffix.lower()
    logger.debug(f"'{filename}' Suffix:       '{suffix}'")
    sanitized_stem = re.sub(r"[^a-zA-Z0-9_-]", "_", path.stem.replace(".", "_"))
    logger.debug(f"'{filename}' Sanitized Stem:       '{sanitized_stem}'")

    #if mimetype not in ALLOWED_FILE_TYPES.values():
    #    raise InputError(f"ValidationError: Mimetype '{mimetype}' of '{filename}' Not Accepted -- Exiting")
    if suffix:
        if suffix not in ALLOWED_FILE_TYPES.keys():
            raise InputError(f"ValidationError: Extension '{suffix}' of '{filename}' Not Accepted -- Exiting")
    #    if ALLOWED_FILE_TYPES[suffix] != mimetype:
    #        raise InputError(f"Validation Error: '{suffix}' and '{mimetype}' Do Not Match -- Exiting")
        sanitized_filename = sanitized_stem + suffix  
    else:
        sanitized_filename = sanitized_stem
    logger.debug(f"'{filename}' Sanitized Filename:         '{sanitized_filename}'")

    if Path(filename).name != sanitized_filename:
        logger.warning(f"InputError: ValidationError: '{Path(filename).name}' Not Accepted -- Renamed to '{sanitized_filename}'")


    logger.info("Sanitize End")
    return sanitized_filename
    

def sanitize_path(filename: str) -> Tuple[str, Path]:
    sanitized_filename = sanitize(filename)
    logger.info("Sanitize Path Start")
    sanitized_path = (Path(f"{Path(INPUT_DIR)}/{sanitized_filename}")).resolve()
    logger.debug(f"'{sanitized_filename}' Sanitized Path:         '{sanitized_path}'")
    path = Path(preload(filename)).resolve()
    logger.debug(f"'{filename}' Path:         '{path}'")

    if path != sanitized_path:
        if sanitized_path.exists():
            old_sanitized_path = sanitized_path
            sanitized_path = sanitized_path.with_name(f"{sanitized_path.stem}_{uuid.uuid4()}{sanitized_path.suffix}")
            logger.warning(f"InputError: FileExistsError: '{old_sanitized_path.name}' Already Exists -- Renamed to '{sanitized_path.name}'")
        logger.warning(f"InputError: ValidationError: '{path}' Not Accepted -- Moved to '{sanitized_path}'")

        sanitized_path.parent.mkdir(parents=True, exist_ok=True)

        path.rename(sanitized_path)

    return sanitized_path.name, sanitized_path


def load(filename: str) -> Union[dict, str]:
    try:
        sanitized_filename, path = sanitize_path(filename)
    except Exception as e:
        logger.critical(f"{type(e).__name__}: {e}")
        raise SystemExit(FAILURE)
    try:
        with path.open("r", encoding="utf-8") as f:
            if path.suffix.lower() == ".json":
                try:
                    json_file = json.load(f)
                    if not isinstance(json_file, dict):
                        raise InputError(f"TypeError: '{sanitized_filename}' is Json but Not Dictionary -- Exiting")
                    return json_file
                except json.JSONDecodeError as e:
                    raise InputError(f"{type(e).__name__}: Error Decoding JSON: {e} -- Exiting") from e
            else:
                return f.read()
    except FileNotFoundError as e:
        raise InputError(f"{type(e).__name__}: '{path}' Not Found -- Check that '/inputs' is in the Same Directory as 'input_utils.py' -- Check that '{sanitized_filename}' is in '/inputs/' -- Exiting") from e


def validate_json(json_file: str) -> dict:
    inputdata = load(json_file)
    assert isinstance(inputdata, dict), f"TypeError: '{json_file}' is Not a Dictionary -- Exiting"

    try:
        validate(inputdata, DATA_SCHEMA)
    except ValidationError as e:
        raise InputError(f"{type(e).__name__}: Invalid File Structure -- {e.message} -- Exiting -- {traceback.format_exc()}")

    return inputdata


def resolve_json(json_file: str) -> dict:
    try:
        inputdata = validate_json(json_file)
    except Exception as e:
        logger.critical(f"{type(e).__name__}: {e}")
        raise SystemExit(FAILURE)

    resolved_inputdata = copy.deepcopy(inputdata)
    inputdata_path = (Path(INPUT_DIR) / json_file).resolve()
    resolved_inputdata_path = Path(INPUT_DIR) / f"resolved_{inputdata_path.name}"

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
    with resolved_inputdata_path.open("w", encoding="utf-8") as f:
        json.dump(resolved_inputdata, f, indent=4)

    return resolved_inputdata


def main():
    resolved_inputdata = resolve_json("inputdata")
    logger.info(resolved_inputdata)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        logger.warning(f"{type(e).__name__}: Input Processing Interrupted by User -- Exiting")
        raise SystemExit(INTERRUPTED)

