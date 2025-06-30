
# -------------------------------------------------------------------------------------------
#                                        INPUTS
# -------------------------------------------------------------------------------------------
# region INPUTS

# Creates an overarching error type for input data
class InputError(Exception):
    pass

# -------------------------------------------------------------------------------------------
#                                    INPUTDATA.JSON
# -------------------------------------------------------------------------------------------
# region INPUTDATA.JSON

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
