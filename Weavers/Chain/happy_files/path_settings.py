# -------------------------------------------------------------------------------------------
#                                    PATH_SETTINGS
# -------------------------------------------------------------------------------------------
# region PATH_SETTINGS

def find_directory_named(name: str, start_path: Path) -> Path:
    for parent in [start_path, *start_path.parents]:
        if parent.name == name:
            return parent
    raise FileNotFoundError(f"'{name}/' not found -- Exiting")


try:
    CHAIN_PATH = find_directory_named("Chain", Path(__file__).resolve().parent)
    logger.info(f"Found /Chain/ at: {CHAIN_PATH}")
    sys.path.append(str(CHAIN_PATH))
except FileNotFoundError as e:
    logger.error(e)
    sys.exit(1)

# endregion

# Imports data_model from /Silk/
from data_model import Component, Requires