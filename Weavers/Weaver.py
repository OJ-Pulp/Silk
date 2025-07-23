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

    def __init__(self):
        """
        Initialize the Weaver with a name.
        :param name: The name of the weaver.
        """

        self.node_output_path: Path
        self.edge_output_path: Path
        self.__set_output_path__()

        self.nodes: List[Node]
        self.edges: List[Edge]

        logger.info("Weaver Initialized")

    def __set_output_path__(self):
        """
        Set the output path for the Weaver's output files.
        """

        self.node_output_path = Weaver.get_output_filename(
            base_name="nodes", extension="csv"
        )
        self.edge_output_path = Weaver.get_output_filename(
            base_name="edges", extension="csv"
        )
        logger.info(
            f"Output path set to {self.node_output_path} and {self.edge_output_path}"
        )

    @staticmethod
    def get_output_filename(
        base_name: str, extension: str, output_dir: Path = Path("output")
    ) -> Path:
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

    def write_to_csv(self, data: Node | Edge):
        """
        Write the generated node / edge to the output CSV file.

        :param data: The Node or Edge object to write to the CSV file.
        """

        if isinstance(data, Node):
            node_output_file = open(self.node_output_path, "a", newline="")
            node_writer = csv.DictWriter(
                node_output_file, fieldnames=data.__dict__.keys()
            )

            # Only write header if file is empty
            if node_output_file.tell() == 0:
                node_writer.writeheader()

            node_writer.writerow(data.to_dict())
            node_output_file.close()  # Don’t forget to close the file!

        else:  # isinstance(data, Edge):
            edge_output_file = open(self.edge_output_path, "a", newline="")
            edge_writer = csv.DictWriter(
                edge_output_file, fieldnames=data.__dict__.keys()
            )

            # Only write header if file is empty
            if edge_output_file.tell() == 0:
                edge_writer.writeheader()

            edge_writer.writerow(data.to_dict())
            edge_output_file.close()  # Don’t forget to close the file!

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
