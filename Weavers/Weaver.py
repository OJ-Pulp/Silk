# Standard
import logging
import json
import csv
from abc import ABC, abstractmethod
from typing import List
from pathlib import Path

# Third-Party
import faker

# Local
from Weavers.graph_model import Edge, Node

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

FAKER_GEN = faker.Faker()
logger.info("Module Variables Set")

class Weaver(ABC):
    """
    Base class for all weavers.
    A weaver creates nodes and edges for a graph structure based on specific logic for each subclass.
    Examples include ChainWeaver, DocWeaver, MapWeaver, etc.
    """


    def __init__(
        self,
        nodes: List[Node],
        edges: List[Edge]
    ):
        """
        Initialize the Weaver with a name.
        :param name: The name of the weaver.
        """

        self.nodes = nodes
        self.edges = edges

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
    
    @staticmethod
    def get_output_filename(base_name: str, extension: str, output_dir: Path = Path("output")) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        index = 1
        if not extension.startswith("."):
            extension = "." + extension
        while True:
            filename = output_dir / f"test{index}_{base_name}{extension}"
            if not filename.exists():
                logger.warning(index)
                return filename
            index += 1

    def write_to_csv(self, data: List[dict]):
        """
        Write the generated nodes and edges to a CSV file.
        This method should be implemented by subclasses.
        :param path: The path to the CSV file.
        """

        path = Weaver.get_output_filename(base_name="components", extension="csv")
        file = open(path, "a", newline="") # Open file once

        writer = csv.DictWriter(file, fieldnames=data[0].keys())

        # Only write header if file is empty
        if file.tell() == 0:
            writer.writeheader()

        for dicts in data:
            writer.writerow(dicts)

        file.close() # Don’t forget to close the file!

