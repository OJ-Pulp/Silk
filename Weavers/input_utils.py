"""
OVERALL INPUT SANITATION AND VALIDATION
"""

# Standard
import copy
import json
import logging
import re
import shutil
import traceback
import uuid
from pathlib import Path
from typing import Union, Tuple, Any, Optional

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

FILE_NAME = "/input_utils.py"
PARENT_DIR = "/Weavers"


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

    def __init__(
        self, 
        message: Optional[str] = "Invalid Input", 
        value: Optional[Any] = None, 
        extra: Optional[Any] = None,
        seperate: Optional[bool] = False
    ) -> None: 
        # [ ] Decide if Space or Docstring or what here
        self.message = message
        self.value = str(value) 
        self.extra = str(extra)
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
            if self.extra is not None:
                parts.append(repr(self.extra))
            return ": ".join(parts)
        else:
            main_message = ": ".join(parts)
            full_message = [main_message]
            if self.value is not None:
                full_message.append(self.value)
            if self.extra is not None:
                full_message.append(self.extra)
            return " -- ".join(full_message)

class SanitationError(InputError):
    """
    Raised when an input fails sanitation rules.
    Standard Message Prefix - 'Unaccepted Characters Inputed in'

    :attr `message`: The name or use of the input that failed.
    :type `message`: str
    :attr `value`: The input with the unaccepted characters.
    :type `value`: Any
    """

    def __init__(
        self, 
        message: Optional[str] = "Str", 
        value: Optional[Any] = None,
        extra: Optional[Any] = None
    ) -> None:
        super().__init__(f"Unaccepted Characters Inputed in {message}", value, extra)

# [ ] potentially add elifs for messages with messages and values blown out

class NotFoundError(InputError):
    """
    Raised when an input fails sanitation rules.
    Standard Message Suffix - ' Not Found'

    :attr `message`: The name or use of the directory or file that failed.
    :type `message`: str
    :attr `value`: The directory or file name or path.
    :type `value`: Any
    """

    def __init__(
        self, 
        message: Optional[Union[str, Path]] = None, 
        value: Optional[Any] = None, 
        extra: Optional[Any] = None,
        issue_type: Optional[str] = None
    ) -> None:
        full_value = f"{value}" if value is not None else None
        full_extra = f"{extra}" if extra is not None else None
        full_seperate = False
        if issue_type == "File":
            full_message = f"'{message}' Not Found" if message is not None else "File Not Found"
            full_value = f"Try Ensuring '{message}' is in '{value}'" if message is not None and value is not None else "Try Ensuring File is in the Input Directory"
            full_extra = f"{value}" if message is None and value is not None else f"{extra}"
        elif issue_type == "Extension":
            full_message = f"'{message}' Extension Not Found" if message is not None else "Extension Not Found"
            full_value = f"Input Changed to '{value}'" if value is not None else "Input Changed"
        elif issue_type == "Path":
            full_message = f"'{message}' Not Found" if message is not None else "Path Not Found"
            full_value = f"Check that '{message.name}' is in '{message.parent.name}' and that is in '{PARENT_DIR}'" if message is not None and message is Path else "Check Directory Structure"
            full_extra = f"Check that '{FILE_NAME}' is in '{PARENT_DIR}'"
        # [ ] Change here later -- add more -- change else
        else:
            full_message = f"{message} Not Found" if message is not None else "Input Location Not Found"
            full_seperate = True
        super().__init__(full_message, full_value, full_extra, full_seperate)

class ValidationError(InputError):

    def __init__(
        self, 
        message: Optional[str] = None, 
        value: Optional[Any] = None, 
        extra: Optional[Any] = None,
        issue_type: Optional[str] = None
    ) -> None:
        full_value = f"{value}" if value is not None else None
        full_extra = f"{extra}" if extra is not None else None
        # [ ] decide default true or false and why
        full_seperate = False
        if issue_type == "File":
            full_message = f"'{message}' is Not a File" if message is not None else "Input is Not a File"
            full_value = f"Try Checking '{value}'" if value is not None else None
        elif issue_type == "Mimetype":
            full_message = f"Mimetype '{value}' of '{message}' Not Accepted" if value is not None and message is not None else "Mimetype Not Accepted"
            full_value = None
            full_extra = f"Allowed Mimetypes are '{extra}'" if extra is not None else None
        elif issue_type == "Extension":
            full_message = f"Extension '{value}' of '{message}' Not Accepted" if value is not None and message is not None else "Extension Not Accepted"
            full_value = None
            full_extra = f"Allowed Extensions are '{extra}'" if extra is not None else None
        elif issue_type == "Matching":
            full_message = f"'{message}' and '{value}' Do Not Match" if value is not None and message is not None else "Suffix and Mimetype Do Not Match"
            full_value = None
            full_extra = f"Allowed Mimetypes for '{message}' are '{extra}'" if message is not None and extra is not None else None
        elif issue_type == "Filename":
            full_message = f"'{message}' Not Accepted" if message is not None else "Filename Not Accepted"
            full_value = f"Renamed to '{value}'" if value is not None else "Renamed"
        elif issue_type == "Path":
            full_message = f"'{message}' Not Accepted" if message is not None else "Path Not Accepted"
            full_value = f"Moved  to '{value}'" if value is not None else "Moved"
        elif issue_type == "Dict":
            full_message = f"'{message}' is JSON but Not Dictionary" if message is not None else "Input is JSON but Not Dictionary"
        elif issue_type == "Decoding":
            full_message = f"Error Decoding JSON: {message}" if message is not None else "Error Decoding JSON: Check Foramtting"
        # [ ] decide if seperate
        elif issue_type == "Schema":
            full_message = f"Invalid File Structure -- {message}" if message is not None else "Invalid File Structure"
        elif issue_type == "PartNums":
            full_message = f"'{message}' Number of Parts Mismatch" if message is not None else "Number of Parts Mismatch"
            full_value = f"manual='{value}', computed='{extra}'" if value is not None and extra is not None else None
            full_extra = None
            full_seperate = True
        elif issue_type == "MissingID":
            full_message = f"'{message}' ID Missing" if message is not None else "Manufacturer ID Missing"
            full_value = f"Generated New ID: '{value}'" if value is not None else "Generated New ID"
        # [ ] Change here later -- add more -- change else
        else:
            full_message = f"{message}" if message is not None else "Input Not Accepted"
        super().__init__(full_message, full_value, full_extra, full_seperate)


class ExistsError(InputError):

    def __init__(
        self, 
        message: Optional[str] = None, 
        value: Optional[Any] = None, 
        extra: Optional[Any] = None,
        issue_type: Optional[str] = None
    ) -> None:
        full_value = f"{value}" if value is not None else None
        full_extra = f"{extra}" if extra is not None else None
        full_seperate = False
        if issue_type == "File":
            full_message = f"'{message}' Already Exists" if message is not None else "File Already Exists"
            full_value = f"Renamed to '{value}'" if value is not None else "Renamed"
        # [ ] Change here later -- add more -- change else
        else:
            full_message = f"'{message}' Not Found" if message is not None else "Input Location Not Found"
        super().__init__(full_message, full_value, full_extra, full_seperate)

class InterruptError(InputError):
    def __init__(
        self, 
        message: Optional[str] = None, 
        value: Optional[Any] = None,
        extra: Optional[Any] = None
    ) -> None:
        super().__init__(f"Input Processing Interrupted by User", value, extra)

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

# [ ] decide if try except moves to where called or stays inside FOR ALL
def preload(filename: str, quiet: Optional[bool] = False) -> Path:
    original_level = logger.level
    if quiet:
        logger.setLevel(logging.CRITICAL)
    try:
        path = INPUT_DIR / filename
        logger.debug(f"'{filename}' Path:       '{path}'")
        if not path.exists():
            raise NotFoundError(path, issue_type="Path")
        if not path.is_file():
            raise ValidationError(filename, path, issue_type="File")
        return path
    except NotFoundError as e:
        logger.warning(e)
        filename_stem = Path(filename).stem
        logger.debug(f"'{filename}' Stem:       '{filename_stem}'")
        filename_stem_matches = list(INPUT_DIR.glob(f"{filename_stem}.*"))
        logger.debug(f"'{filename}' Stem Matches:       '{filename_stem_matches}'")
        if filename_stem_matches == []:
            try:
                raise NotFoundError(filename, INPUT_DIR, issue_type="File")
            except Exception as e:
                logger.critical(e)
                raise SystemExit(FAILURE)
        path = INPUT_DIR / filename_stem_matches[0]
        try:
            raise NotFoundError(filename, path.name, issue_type="Extension")
        except Exception as e:
            logger.warning(e)
        logger.debug(f"'{path.name}' Path:       '{path}'")
        return path
    # [ ] Change to where called?
    except Exception as e:
        logger.critical(e)
        raise SystemExit(FAILURE)
    finally:
        if quiet:
            logger.setLevel(original_level)


def sanitize(filename) -> str:
    try:
        path = preload(filename)
        filename = path.name
        mimetype = MIME.from_file(str(path))  
        logger.debug(f"'{filename}' Mimetype:       '{mimetype}'")  
        suffix = path.suffix.lower()
        logger.debug(f"'{filename}' Suffix:       '{suffix}'")
        sanitized_stem = re.sub(r"[^a-zA-Z0-9_-]", "_", path.stem.replace(".", "_"))
        logger.debug(f"'{filename}' Sanitized Stem:       '{sanitized_stem}'")

        if not any(mimetype in types for types in ALLOWED_FILE_TYPES.values()):
            raise ValidationError(filename, mimetype, list(ALLOWED_FILE_TYPES.values()), issue_type="Mimetype")
        if suffix:
            if suffix not in ALLOWED_FILE_TYPES.keys():
                raise ValidationError(filename, suffix, list(ALLOWED_FILE_TYPES.keys()), issue_type="Extension")
            if mimetype not in ALLOWED_FILE_TYPES[suffix]:
                raise ValidationError(suffix, mimetype, ALLOWED_FILE_TYPES[suffix], issue_type="Matching")
            sanitized_filename = sanitized_stem + suffix  
        else:
            sanitized_filename = sanitized_stem
        logger.debug(f"'{filename}' Sanitized Filename:         '{sanitized_filename}'")

        if Path(filename).name != sanitized_filename:
            try:
                raise ValidationError(Path(filename).name, sanitized_filename, issue_type="Filename")
            except Exception as e:
                logger.warning(e)

        return sanitized_filename
    except Exception as e:
        logger.critical(e)
        raise SystemExit(FAILURE)
    

def sanitize_path(filename: str) -> Tuple[str, Path]:
    try:
        sanitized_filename = sanitize(filename)
        sanitized_path = INPUT_DIR / sanitized_filename
        logger.debug(f"'{sanitized_filename}' Sanitized Path:         '{sanitized_path}'")
        path = preload(filename, True)
        logger.debug(f"'{filename}' Path:         '{path}'")

        if path != sanitized_path:
            if sanitized_path.exists():
                old_sanitized_path = sanitized_path
                sanitized_path = sanitized_path.with_name(f"{sanitized_path.stem}_{uuid.uuid4()}{sanitized_path.suffix}")
                try:
                    raise ExistsError(old_sanitized_path.name, sanitized_path.name, "File")
                except Exception as e:
                    logger.warning(e)
            try:
                raise ValidationError(path, sanitized_path, issue_type="Path")
            except Exception as e:
                logger.warning(e)

            sanitized_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(path, sanitized_path)

        return sanitized_path.name, sanitized_path
    except Exception as e:
        logger.critical(e)
        raise SystemExit(FAILURE)


def load(filename: str) -> Union[dict, str]:
    sanitized_filename, path = sanitize_path(filename)
    # [ ] decide about extra try inside of function
    try:    
        try:
            with path.open("r", encoding="utf-8") as f:
                if path.suffix.lower() == ".json":
                    try:
                        json_file = json.load(f)
                        if not isinstance(json_file, dict):
                            raise ValidationError(sanitized_filename, issue_type="Dict")
                        return json_file
                    except json.JSONDecodeError as e:
                        raise ValidationError(e, issue_type="Decoding")
                else:
                    return f.read()
        except FileNotFoundError:
            raise NotFoundError(path, issue_type="Path")
    except Exception as e:
        logger.critical(e)
        raise SystemExit(FAILURE)


def validate_json(
    json_file: str = "inputdata", 
    json_schema: str = "inputdata_schema"
) -> dict:
    inputdata = load(json_file)
    inputdata_schema = load(json_schema)

    # [ ] talk to corbin about in inputs or DATA_SCHEMA
    try:
        validate(inputdata, inputdata_schema)
    except SchemaValidationError as e:
        raise ValidationError(e.message, traceback.format_exc(), issue_type="Schema")

    return inputdata


def resolve_json(
    json_file: str = "inputdata", 
    json_schema: str = "inputdata_schema"
) -> dict:
    try:
        inputdata = validate_json(json_file, json_schema)
    except Exception as e:
        logger.critical(e)
        raise SystemExit(FAILURE)

    resolved_inputdata = copy.deepcopy(inputdata)
    resolved_inputdata_path = INPUT_DIR / f"resolved_{json_file}"

    # Resolves 'Number of Parts' for each designation by adding it if missing or warning the user if incorrect
    for designation, data in resolved_inputdata["Designations"].items():
        parts_count = sum(len(part_list) for part_list in data["Parts"].values())
        if "Number of Parts" in data:
            if data["Number of Parts"] != parts_count:
                try:
                    raise ValidationError(designation, data['Number of Parts'], parts_count, issue_type="PartNums")
                except Exception as e:
                    logger.warning(e)
        else:
            data["Number of Parts"] = parts_count
            logger.info(f"{designation} Number of Parts Added:      {parts_count}")

    # Resolves 'ID' for each manufacturer by adding it if it is missing
    for manufacturer, data in resolved_inputdata["Manufacturers"].items():
        if "ID" not in data:
            generated_id = str(uuid.uuid4())
            data["ID"] = generated_id
            try:
                raise ValidationError(manufacturer, generated_id, issue_type="MissingID")
            except Exception as e:
                logger.warning(e)

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
        try:
            raise InterruptedError()
        except Exception as e:
            logger.warning(e)
        raise SystemExit(INTERRUPTED)

