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
from typing import Union, Tuple, Any

# -------------------------------------------------------------------------------------------
#                                   LOGGING_SETTINGS
# -------------------------------------------------------------------------------------------
# region LOGGING_SETTINGS

# SystemExit codes
SUCCESS = 0
FAILURE = 1
INTERRUPTED = 130

SUCCESS_LEVEL_NUM = 15

logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")

def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kwargs)

logging.Logger.success = success

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
    import magic
    from jsonschema import validate
    from jsonschema import ValidationError as SchemaValidationError
except ModuleNotFoundError as e:
    logger.critical(f"{type(e).__name__}: Missing Required Module '{e.name}' -- Try 'python -m pip install {e.name}' -- Exiting")
    raise SystemExit(FAILURE)


# -------------------------------------------------------------------------------------------
#                                   EXCEPTION_CLASSES
# -------------------------------------------------------------------------------------------
# region EXCEPTION_CLASSES

class InputError(Exception): 
    """
    Base class for input-related errors.

    :attr `message`: The error message.
    :type `message`: str
    :attr `value`: The value that caused the error.
    :type `value`: Any
    """

    def __init__(self, message: str = "Invalid Input", value: Any = None, seperate: bool = True) -> None: 
        self.message = message
        self.value = value 
        self.seperate = seperate
        super().__init__(message) 
    
    def __str__(self) -> str: 
        parts = ["InputError"]

        if self.__class__.__name__ != "InputError":
            parts.append(self.__class__.__name__)

        parts.append(self.message)

        # [ ] Consolidate -- break out if self.value?
        if self.seperate is True:  
            if self.value is not None:
                parts.append(repr(self.value)) 
            return ": ".join(parts)
        else:
            main_message = ": ".join(parts)
            full_message = [main_message]
            if self.value is not None:
                full_message.append(self.value)
                return " -- ".join(full_message)
            return main_message
    
class SanitationError(InputError):
    """
    Raised when an input fails sanitation rules.
    Standard Message Prefix - 'Unaccepted Characters Inputed in'

    :attr `message`: The name or use of the input that failed.
    :type `message`: str
    :attr `value`: The input with the unaccepted characters.
    :type `value`: Any
    """

    def __init__(self, message: str = "Str", value: Any = None) -> None:
        super().__init__(f"Unaccepted Characters Inputed in {message}", value)

class NotFoundError(InputError):
    """
    Raised when an input fails sanitation rules.
    Standard Message Suffix - ' Not Found'

    :attr `message`: The name or use of the directory or file that failed.
    :type `message`: str
    :attr `value`: The directory or file name or path.
    :type `value`: Any
    """

    def __init__(self, message: str = "Input Location", value: Any = None, issue_type: str = None) -> None:
        full_seperate = True
        if issue_type == "File":
            full_message = f"'{message}' Not Found -- Try Ensuring '{message}' is in '{INPUT_DIR}'"
            full_value = f"{value}" if value is not None else None
        elif issue_type == "Extension":
            full_message = f"'{message}' Extension Not Found"
            full_value = f"Input Changed to '{value}'" if value is not None else None
            full_seperate = False if value is not None else True
        # [ ] Change here later -- add more -- change else
        else:
            full_message = f"'{message}' Not Found"
            full_value = f"{value}" if value is not None else None
        super().__init__(full_message, full_value, full_seperate)

class ValidationError(InputError):

    def __init__(self, message: str = None, value: Any = None, issue_type: str = None) -> None:
        full_seperate = True
        if issue_type == "File":
            full_message = f"'{message}' is Not a File" if message is not None else "Input is Not a File"
            full_value = f"Try Checking '{value}'" if value is not None else None
            full_seperate = False if value is not None else True
        elif issue_type == "Mimetype":
            full_message = f"Mimetype '{value}' of '{message}' Not Accepted" if value is not None and message is not None else "Mimetype Not Accepted"
            full_value = None
        elif issue_type == "Extension":
            full_message = f"Extension '{value}' of '{message}' Not Accepted" if value is not None and message is not None else "Extension Not Accepted"
            full_value = None
        elif issue_type == "Matching":
            full_message = f"'{message}' and '{value}' Do Not Match" if value is not None and message is not None else "Suffix and Mimetype Do Not Match"
            full_value = None
        elif issue_type == "Filename":
            full_message = f"'{message}' Not Accepted" if message is not None else "Filename Not Accepted"
            full_value = f"Renamed to '{value}'" if value is not None else None
            full_seperate = False if full_value is not None else True
        # [ ] Change here later -- add more -- change else
        else:
            full_message = f"{message}" if message is not None else "Input Not Accepted"
            full_value = f"{value}" if value is not None else None
        super().__init__(full_message, full_value, full_seperate)


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
    logger.success(f"ModuleNameFound: {calling_module_name}")
    project_dir = calling_module_name.parts[-2]
    """

    # [ ] Change for being called in ChainWeaver  SEE ABOVE
    project_dir = "Chain"

    # [ ] Add logger tool for INPUT or ENTER
    if project_dir != re.sub(r"[^a-zA-Z0-9_-]", "_", project_dir):
        raise SanitationError("Project Directory Name", project_dir)
    
    input_dir = Path(__file__).parent.resolve() / project_dir / "inputs"

    if not input_dir.exists():
        raise NotFoundError("Input Directory", input_dir)

    return input_dir

try:
    INPUT_DIR = set_input_dir()
except Exception as e:
    logger.critical(e)
    raise SystemExit(FAILURE)
logger.success(f"Input Directory:         '{INPUT_DIR}'")

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
    try:
        path = INPUT_DIR / filename
        logger.debug(f"'{filename}' Path:       '{path}'")
        if not path.exists():
            raise NotFoundError(filename, path)
        if not path.is_file():
            raise ValidationError(filename, path, "File")
        return path
    except NotFoundError as e:
        logger.warning(e)
        filename_stem = Path(filename).stem
        logger.debug(f"'{filename}' Stem:       '{filename_stem}'")
        filename_stem_matches = list(INPUT_DIR.glob(f"{filename_stem}.*"))
        logger.debug(f"'{filename}' Stem Matches:       '{filename_stem_matches}'")
        if filename_stem_matches == []:
            try:
                raise NotFoundError(filename, issue_type="File")
            except Exception as e:
                logger.critical(e)
                raise SystemExit(FAILURE)
        path = (filename_stem_matches[0]).resolve()
        try:
            raise NotFoundError(filename, path.name, "Extension")
        except Exception as e:
            logger.warning(e)
        logger.debug(f"'{path.name}' Path:       '{path}'")
        return path
    # [ ] Change to where called?
    except Exception as e:
        logger.critical(e)
        raise SystemExit(FAILURE)


def sanitize(filename) -> str:
    path = preload(filename)
    filename = path.name
    mimetype = MIME.from_file(str(path))  
    logger.debug(f"'{filename}' Mimetype:       '{mimetype}'")  
    suffix = path.suffix.lower()
    logger.debug(f"'{filename}' Suffix:       '{suffix}'")
    sanitized_stem = re.sub(r"[^a-zA-Z0-9_-]", "_", path.stem.replace(".", "_"))
    logger.debug(f"'{filename}' Sanitized Stem:       '{sanitized_stem}'")

    if not any(mimetype in types for types in ALLOWED_FILE_TYPES.values()):
        raise ValidationError(filename, mimetype, "Mimetype")
    if suffix:
        if suffix not in ALLOWED_FILE_TYPES.keys():
            raise ValidationError(filename, suffix, "Extension")
        if mimetype not in ALLOWED_FILE_TYPES[suffix]:
            raise ValidationError(suffix, mimetype, "Matching")
        sanitized_filename = sanitized_stem + suffix  
    else:
        sanitized_filename = sanitized_stem
    logger.debug(f"'{filename}' Sanitized Filename:         '{sanitized_filename}'")

    if Path(filename).name != sanitized_filename:
        try:
            raise ValidationError(Path(filename).name, sanitized_filename, "Filename")
        except Exception as e:
            logger.warning(e)

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
        logger.critical(e)
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

