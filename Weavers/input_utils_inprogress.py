"""
OVERALL INPUT SANITATION AND VALIDATION
"""

# Standard Imports
import copy
import inspect
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

# Extra logging level for small procedure successes
SUCCESS_LEVEL_NUM = 15

logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")

def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kwargs)

logging.Logger.success = success

# Configures for logging showing messages level INFO and above
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# endregion

# Third-Party Imports
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
    Base exception raised for input-related errors.

    This class provides a structured way to report input-related issues, 
    including detailed debugging information to aid in problem identifcation.
    """

    def __init__(
        self, 
        message: Optional[str] = "Invalid Input", 
        value: Optional[Any] = None, 
        extra: Optional[Any] = None,
        exit: Optional[bool] = True,
        separate: Optional[bool] = False
    ) -> None: 
        """
        Intitializes a new InputError object.

        :param `message`: A descriptive error message explaining the nature of the input problem.
            Defaults to "Invalid Input".
        :type `message`: str, optional
        :param `value`: The specific value or type of value that caused the error.
            Defaults to None.
        :type `value`: Any, optional
        :param `extra`: Additional information relevant to the error, which can further aid in debugging.
            Defaults to None.
        :type `extra`: Any, optional
        :param `exit`: If True, indicates that the error should signal a critical exit condition for the program.
            Defaults to True.
        :type `exit`: bool, optional
        :param `separate`: Controls the separator used in the error message.
            If True, components are separated by a colon (e.g., "Message: Value").  
            If False, components are separated by a double-hyphen (e.g., "Message -- Value").
            Defaults to False.
        :type `separate`: bool, optional
        """

        self.message = message
        self.value = value 
        self.extra = extra
        self.exit = exit
        self.separate = separate

        # Initializes the base Exception class with the main message
        super().__init__(message) 
    
    def __str__(self) -> str: 
        """
        Returns a string repersentation of the InputError, including detailed information
        based on the error's attributes and separation preference.
        """

        # Builds a list of the class, subclass (if applicable), and message
        parts = ["InputError"]

        # Includes the specific subclass name if InputError is called in another exception
        if self.__class__.__name__ != "InputError":
            parts.append(self.__class__.__name__)

        # Includes the main message
        parts.append(self.message)

        prefix = ": ".join(parts)

        # Builds a list of the applicable additional details
        details = []
        if self.value is not None:
            details.append(repr(self.value))
        if self.extra is not None:
            details.append(repr(self.extra))
        
        # Determines the primary separator for any additional details
        separator = ": " if self.separate else " -- "

        # Builds the full message with all information
        all_info = separator.join([prefix, separator.join(details)]) if details else prefix
        full_message = " -- ".join([all_info, "Exiting"]) if self.exit is True else all_info

        return full_message

class SanitationError(InputError):
    """
    Exception raised when an input value contains unaccepted characters 
    or fails defined sanitation rules.

    The error message includes the prefix "Unaccepted Characters Inputed in".
    """

    def __init__(
        self, 
        message: Optional[str] = "Str", 
        value: Optional[Any] = None,
        extra: Optional[Any] = None
    ) -> None:
        """
        Initializes a new SanitationError object.

        :param `message`: A descriptive name or label for the input that failed sanitation
            (e.g., "J0hn/?D03", "username"). This is what completes the prefix.
            Defaults to "Str".
        :type `message`: str, optional
        :param `value`: The specific value that contained unaccepted characters.
            Defaults to None.
        :type `value`: Any, optional
        :param `extra`: Additional information relevant to the error, 
            such as the specific sanitation rule violated or the expected character set.
            Defaults to None.
        """

        super().__init__(f"Unaccepted Characters Inputed in {message}", value, extra)

class NotFoundError(InputError):
    """
    Exception raised when a specificed input (e.g., file, directory, extension, path) is not found.

    The error message includes the suffix " Not Found".
    """

    def __init__(
        self, 
        message: Optional[Union[str, Path]] = None, 
        value: Optional[Any] = None, 
        extra: Optional[Any] = None,
        issue_type: Optional[str] = None
    ) -> None:
        """
        Initializes a new NotFoundError object.

        This constructor dynamically sets the error message parts based on the `issue_type` provided.

        :param `message`: A descripive name or label for the input that was not found
            (e.g., file, extension, path).
            Defaults to None.
        :type `message`: str or Path, optional
        :param `value`: Additional context or a suggested location related to the missing item.
            Potentially could be the expected location or value of the missing item or what became of it.
            Defaults to None.
        :type `value`: Any, optional
        :param `extra`: Further supplementary information for debugging or user guidance.
            Defaults to None.
        :type `extra`: Any, optional
        :param `issue_type`: Specifies the type of item that was not found, correlating to the error message's
            structure and suggested solutions. Supported types include "File", "Extension", and "Path".
            If not specified, a general "Input Location Not Found" message is used.
            Defaults to None.
        :type `issue_type`: str, optional
        """

        full_value = f"{value}" if value is not None else None
        full_extra = f"{extra}" if extra is not None else None
        full_exit = True
        full_separate = False
        if issue_type == "File":
            full_message = f"'{message}' Not Found" if message is not None else "File Not Found"
            full_value = f"Try Ensuring '{message}' is in '{value}'" if message is not None and value is not None else "Try Ensuring File is in the Input Directory"
            full_extra = f"{value}" if message is None and value is not None else f"{extra}"
        elif issue_type == "Extension":
            full_message = f"'{message}' Extension Not Found" if message is not None else "Extension Not Found"
            full_value = f"Input Changed to '{value}'" if value is not None else "Input Changed"
            full_exit = False
        elif issue_type == "Path":
            full_message = f"'{message}' Not Found" if message is not None else "Path Not Found"
            full_value = f"Check that '{message.name}' is in '{message.parent.name}' and that is in '{PARENT_DIR}'" if message is not None and message is Path else "Check Directory Structure"
            full_extra = f"Check that '{FILE_NAME}' is in '{PARENT_DIR}'"
        else:
            full_message = f"{message} Not Found" if message is not None else "Input Location Not Found"
            full_separate = True
        super().__init__(full_message, full_value, full_extra, full_exit, full_separate)

class ValidationError(InputError):
    """
    Exception raised when an input value fails to meet specific validation criteria.

    This error covers a wide range of validation failures, from incorrect file types
    to data structure mismatches, providing specific messages based on the nature
    of the validation issue.
    """

    def __init__(
        self, 
        message: Optional[str] = None, 
        value: Optional[Any] = None, 
        extra: Optional[Any] = None,
        issue_type: Optional[str] = None
    ) -> None:
        """
        Initializes a new ValidationError object.

        This constructor dynamically sets the error message parts
        based on the `issue_type` provided, allowing for highly specific validation
        error reporting.

        :param `message`: A primary descriptive piece of information related to the validation failure.
            Its meaning varies significantly depending on the `issue_type`.
            Defaults to None.
        :type `message`: str, optional
        :param `value`: A secondary piece of information or the problematic value itself,
            also context-dependent on the `issue_type`.
            Defaults to None.
        :type `value`: Any, optional
        :param `extra`: Additional, supplementary information to further clarify the error or
            provide debugging hints (e.g., allowed values, expected formats).
            Defaults to None.
        :type `extra`: Any, optional
        :param `issue_type`: Defines the specific category of validation error, which dictates
            how the `message`, `value`, and `extra` parameters are interpreted and
            used to construct the final error string. Supported types include:
            """
        # [ ] CHECK THIS IN MORNING
        """

            - **"File"**: Input is not a valid file.
                - `message`: The path or name of the invalid "file."
                - `value`: Suggestion for checking, e.g., a directory.
            - **"Mimetype"**: The MIME type of the input is not accepted.
                - `message`: Name of the file/input with the unaccepted mimetype.
                - `value`: The unaccepted MIME type.
                - `extra`: List of allowed MIME types.
            - **"Extension"**: The file extension is not accepted.
                - `message`: Name of the file/input with the unaccepted extension.
                - `value`: The unaccepted extension.
                - `extra`: List of allowed extensions.
            - **"Matching"**: Mismatch between related values (e.g., suffix and mimetype).
                - `message`: First item that doesn't match (e.g., suffix).
                - `value`: Second item that doesn't match (e.g., mimetype).
                - `extra`: Allowed values for the first item based on the second.
            - **"Filename"**: The filename is not accepted (e.g., due to invalid characters).
                - `message`: The unaccepted filename.
                - `value`: Suggested or resulting renamed filename.
            - **"Path"**: The input path is not accepted.
                - `message`: The unaccepted path.
                - `value`: Suggested or resulting moved path.
            - **"Dict"**: JSON input is valid but not a dictionary.
                - `message`: The JSON string or description.
            - **"Decoding"**: Error occurred during JSON decoding.
                - `message`: The decoding error details.
            - **"Schema"**: The data structure (e.g., file content) does not conform to an expected schema.
                - `message`: Specific details about the schema violation.
            - **"PartNums"**: Mismatch in the number of expected vs. computed parts.
                - `message`: Description of the parts (e.g., "header parts").
                - `value`: Manually specified number of parts.
                - `extra`: Computed number of parts.
            - **"MissingID"**: A required identifier is missing.
                - `message`: Type of ID missing (e.g., "Product").
                - `value`: New ID generated (if applicable).
            - **(Default/Else)**: A general input acceptance failure.
                - `message`: General description of why the input is not accepted.

            Defaults to None, resulting in a general "Input Not Accepted" message.
        :type `issue_type`: str, optional
        """

        full_value = f"{value}" if value is not None else None
        full_extra = f"{extra}" if extra is not None else None
        full_exit = True
        full_separate = False
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
            full_exit = False
        elif issue_type == "Path":
            full_message = f"'{message}' Not Accepted" if message is not None else "Path Not Accepted"
            full_value = f"Moved  to '{value}'" if value is not None else "Moved"
            full_exit = False
        elif issue_type == "Dict":
            full_message = f"'{message}' is JSON but Not Dictionary" if message is not None else "Input is JSON but Not Dictionary"
            full_exit = False
        elif issue_type == "Decoding":
            full_message = f"Error Decoding JSON: {message}" if message is not None else "Error Decoding JSON: Check Foramtting"
            full_exit = False
        # [ ] decide if separate
        elif issue_type == "Schema":
            full_message = f"Invalid File Structure -- {message}" if message is not None else "Invalid File Structure"
        elif issue_type == "PartNums":
            full_message = f"'{message}' Number of Parts Mismatch" if message is not None else "Number of Parts Mismatch"
            full_value = f"manual='{value}', computed='{extra}'" if value is not None and extra is not None else None
            full_extra = None
            full_exit = False
            full_separate = True
        elif issue_type == "MissingID":
            full_message = f"'{message}' ID Missing" if message is not None else "Manufacturer ID Missing"
            full_value = f"Generated New ID: '{value}'" if value is not None else "Generated New ID"
            full_exit = False
        else:
            full_message = f"{message}" if message is not None else "Input Not Accepted"
        super().__init__(full_message, full_value, full_extra, full_exit, full_separate)


class ExistsError(InputError):
    """
    Exception raised when an input value or resource (e.g., file) already exists
    but is not expected to, or prevents a desired operation.

    This error typically signifies a non-critical issue if the existing item
    can be handled (e.g., renamed, overwritten).
    """

    def __init__(
        self, 
        message: Optional[str] = None, 
        value: Optional[Any] = None, 
        extra: Optional[Any] = None,
        issue_type: Optional[str] = None
    ) -> None:
        """
        Initializes a new ExistsError object.

        This constructor adapts the error message parts based on the
        `issue_type` to clearly indicate what already exists and the proposed
        resolution.

        :param `message`: The name or label of the item that already exists.
            For files, this would be the filename. 
            Defaults to None.
        :type `message`: str, optional
        :param `value`: A suggested new name or location for the existing item
            (e.g., 'new_file.txt').
            Defaults to None.
        :type `value`: Any, optional
        :param `extra`: Additional information relevant to the existing item or
            the context of the error. 
            Defaults to None.
        :type `extra`: Any, optional
        :param `issue_type`: Specifies the type of item that already exists.
            Currently supported:
            - **"File"**: A file with the given name already exists.
                - `message`: The name of the file that exists.
                - `value`: The new name to which the file was renamed (if applicable).
                """
        # [ ] CHECK HERE IN THE MORNING
        """
            If no specific `issue_type` is matched, a general "Input Location Not Found"
            message is currently used, which might be a logical inconsistency if the
            error is truly about existence. Consider refining the 'else' case.
            Defaults to None.
        :type `issue_type`: str, optional
        """

        full_value = f"{value}" if value is not None else None
        full_extra = f"{extra}" if extra is not None else None
        full_exit = False
        full_separate = False
        if issue_type == "File":
            full_message = f"'{message}' Already Exists" if message is not None else "File Already Exists"
            full_value = f"Renamed to '{value}'" if value is not None else "Renamed"
        else:
            full_message = f"'{message}' Not Found" if message is not None else "Input Location Not Found"
        super().__init__(full_message, full_value, full_extra, full_exit, full_separate)

class InterruptError(InputError):
    """
    Exception raised when user input processing or an operation is deliberately
    interrupted by the user.

    This signals a graceful or expected termination of a process initiated by the user.
    """

    def __init__(
        self, 
        value: Optional[Any] = None,
        extra: Optional[Any] = None,
        exit: bool = True
    ) -> None:
        """
        Initializes a new InterruptError object.

        This error is typically used to indicate that the program flow should
        be gracefully exited due to user intervention.

        :param `value`: Additional information about the state or input at the
            time of interruption (e.g., the last valid input received).
            Defaults to None.
        :type `value`: Any, optional
        :param `extra`: Any supplementary details about the interruption context,
            such as specific user commands or signals.
            Defaults to None.
        :type `extra`: Any, optional
        :param `exit`: If True, indicates that the error should signal a critical
            exit condition for the program. Given this error represents a user
            interruption, it almost always implies an exit.
            Defaults to True.
        :type `exit`: bool
        """

        super().__init__(f"Input Processing Interrupted by User", value, extra, exit)

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

    # Retrieves the current project directory
    caller_frame = inspect.stack()[1]
    calling_module_name = Path(caller_frame.filename)
    logger.success(f"ModuleNameFound: {calling_module_name}")
    project_dir = calling_module_name.parts[-2]

    # [ ] DELETE THIS LATER
    """
    # [ ] Change for being called in ChainWeaver  SEE ABOVE
    project_dir = "Chain"

    # Ensures that the Project Directory is a safe string
    if project_dir != re.sub(r"[^a-zA-Z0-9_-]", "_", project_dir):
        raise SanitationError("Project Directory Name", project_dir)

    """

    # Defines what the input directory should be and checks that it exists
    input_dir = Path(__file__).parent.resolve() / project_dir / "inputs"
    if not input_dir.exists():
        raise NotFoundError("Input Directory", input_dir)

    return input_dir

# Calls the above function to set the input directory and sets it as a global variable
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

# [ ] WARNING InputError
# [ ] Naming ex. validate or validate_file
# [ ] add more recognized load suffixes
# [ ] error or critical
# [ ] security in load or securing around load
# [ ] logger.debug

# -------------------------------------------------------------------------------------------
#                                       SANITIZE
# -------------------------------------------------------------------------------------------
# region SANITIZE

def sanitize(filename: str) -> str:

    # Gets the stem
    match = re.match(r'(.+?)(?:\.[^.]*)?$', filename)
    if match:
        stem = match.group(1)
    else:
        stem = filename
    # Combats edge cases without at least one number or letter
    if not re.search(r'[a-zA-Z0-9]', stem):
        try:
            raise ValidationError(stem, "input_file", issue_type="Filename")
        except Exception as e:
            logger.warning(e)
        stem = "input_file"
    sanitized_stem = re.sub(r"[^a-zA-Z0-9_]", "_", stem.replace(".", "_"))
    logger.debug(f"'{filename}' Sanitized Stem:       '{sanitized_stem}'")

    # Checks the suffix for validation
    match = re.search(r'(\.[^.]*)$', filename)
    if match:
        suffix = match.group(1)
    else:
        suffix = ""
    logger.debug(f"'{filename}' Suffix:       '{suffix}'")
    if suffix:
        if suffix not in ALLOWED_FILE_TYPES.keys():
            raise ValidationError(filename, suffix, list(ALLOWED_FILE_TYPES.keys()), issue_type="Extension")
        sanitized_filename = sanitized_stem + suffix  
    else:
        sanitized_filename = sanitized_stem
        logger.debug(f"'{filename}' Sanitized Filename:         '{sanitized_filename}'")

    # Compares the given filename and the sanitized one
    if Path(filename).name != sanitized_filename:
        try:
            raise ValidationError(Path(filename).name, sanitized_filename, issue_type="Filename")
        except Exception as e:
            logger.warning(e)

    return sanitized_filename

# endregion

# -------------------------------------------------------------------------------------------
#                                    FIND_EXTENSION
# -------------------------------------------------------------------------------------------
# region FIND_EXTENSION

def find_extension(filename: str) -> Path:
    """
    Locates and validates a file that was not found by straight input by ensuring it has the correct extension.

    This function attempts to find a file that has been inputted with a missing or invalid extension, 
    and if not found, attempts to find it by its stem (name without extension).

    :param `filename`: The name of the inputted.
    :type `filename`: str

    :return: The validated Path object for the file.
    :rtype: Path
    """

    # Attempts to get the extension
    suffix = Path(filename).suffix.lower()

    # If there is a extension, it is validated
    if suffix != "":
        logger.success(f"SuffixFound:       {suffix}")
        if suffix in ALLOWED_FILE_TYPES.keys():
            logger.success(f"SuffixAccepted:        {suffix}")
            logger.debug(f"'{path.name}' Path:       '{path}'")
            return path
        else:
            logger.warning(ValidationError(filename, suffix, ALLOWED_FILE_TYPES.keys(), "Extension"))
    # If there is no extension, warns the user they were missing an extension
    else:
        try:
            raise NotFoundError(filename, path.name, issue_type="Extension")
        except Exception as e:
            logger.warning(e)

    # Finds all files in the Input Directory that share the filename but with any extension
    filename_stem = Path(filename).stem
    logger.debug(f"'{filename}' Stem:       '{filename_stem}'")
    filename_stem_matches = list(INPUT_DIR.glob(f"{filename_stem}.*"))
    logger.debug(f"'{filename}' Stem Matches:       '{filename_stem_matches}'")

    # Errors and exits if there are no files found with the stem at all
    if filename_stem_matches == []:
        try:
            raise NotFoundError(filename, INPUT_DIR, issue_type="File")
        except Exception as e:
            logger.critical(e)
            raise SystemExit(FAILURE)

    # Adjusts the Path to a new stem match
    for i in range(len(filename_stem_matches)):
        # Trys stem match
        path = filename_stem_matches[i]

        # Checks the suffix of that stem match
        suffix = path.suffix.lower()
        if suffix in ALLOWED_FILE_TYPES.keys():
            logger.debug(f"'{path.name}' Path:       '{path}'")
            return path

# endregion

# [ ] decide if try except moves to where called or stays inside FOR ALL
def preload(filename: str, quiet: Optional[bool] = False) -> Path:
    """
    Preloads a file by verifying its existence and validity within INPUT_DIR.

    This function attempts to find the file directly, and if not found,
    attempts to find it by its stem (name without extension).

    :param `filename`: The name of the file to preload.
    :type `filename`: str
    :param `quiet`: If True, suppresses logging to CRITICAL level during execution.
        This is useful for cleaning up the log path when preload is called in other functions.
        Defaults to False.
    :type `quiet`: bool, optional

    :return: The validated Path object for the file.
    :rtype: Path
    """
    
    # Implements the quiet option
    original_level = logger.level
    if quiet:
        logger.setLevel(logging.CRITICAL)
    try:
        # Trys to set the Input Path straightforwardly
        path = INPUT_DIR / filename
        logger.debug(f"'{filename}' Path:       '{path}'")

        # Checks the path exists and leads to a useable file
        if not path.exists():
            raise NotFoundError(path, issue_type="Path")
        if not path.is_file():
            raise ValidationError(filename, path, issue_type="File")
        return path
    # Except if the Path does not exist
    except NotFoundError as e:
        logger.warning(e)

        # Gets best guess of a useable path
        path = find_extension(filename)
        return path
    # Catches and reports all other errors
    except Exception as e:
        logger.critical(e)
        raise SystemExit(FAILURE)
    # Finishes the implementation of the quiet option
    finally:
        if quiet:
            logger.setLevel(original_level)


def sanitize(filename: str) -> str:
    try:
        path = preload(filename)
        filename = path.name
        suffix = path.suffix.lower()
        logger.debug(f"'{filename}' Suffix:       '{suffix}'")
        sanitized_stem = re.sub(r"[^a-zA-Z0-9_-]", "_", path.stem.replace(".", "_"))
        logger.debug(f"'{filename}' Sanitized Stem:       '{sanitized_stem}'")
        mimetype = MIME.from_file(str(path))  
        logger.debug(f"'{filename}' Mimetype:       '{mimetype}'")  

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
