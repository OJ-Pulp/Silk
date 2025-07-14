# Standard
from abc import ABC, abstractmethod
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
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Suppresses debug messages from faker library
logging.getLogger("faker").setLevel(logging.INFO)

# endregion


class Weaver(ABC):
    """
    Base class for all weavers.
    A weaver is responsible for weaving together different parts of the application.
    """

    def __init__(self):
        """
        Initialize the Weaver with a name.
        :param name: The name of the weaver.
        """
        logger.info("Weaver Initialized")

    @abstractmethod
    def weave(self):
        """
        Weave the components together.
        This method should be implemented by subclasses.
        """

    @abstractmethod
    def generate_nodes(self) -> dict:
        """
        Generate nodes for the weaver.
        This method should be implemented by subclasses.
        """

    @abstractmethod
    def generate_edges(self) -> dict:
        """
        Generate edges for the weaver.
        This method should be implemented by subclasses.
        """

    @abstractmethod
    def write_to_csv(self, path: str):
        """
        Write the generated nodes and edges to a CSV file.
        This method should be implemented by subclasses.
        :param path: The path to the CSV file.
        """
