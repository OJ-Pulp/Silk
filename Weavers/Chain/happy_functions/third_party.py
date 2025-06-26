# Third-Party
try:
    import faker
    import pandas as pd
    from jsonschema import validate, ValidationError
except ModuleNotFoundError as e:
    logger.critical(f"{type(e).__name__}: Missing Required Module '{e.name}' -- Try 'python -m pip install {e.name}' -- Exiting")
    sys.exit(1)
except ImportError as e:
    import_of = str(e).split("cannot import name")[1].split("from")[0].strip(" '\"")
    module_of = str(e).split("from")[1].split()[0].strip(" '\"")
    logger.critical(f"{type(e).__name__}: Cannot Import '{import_of}' from '{module_of}' -- Exiting")
    sys.exit(1)