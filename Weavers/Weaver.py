# Standard
import logging
import csv
from abc import ABC, abstractmethod
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

    node_class: type[Node] = Node
    """The Node subclass used by this Weaver type from its data model. Must be overridden in subclasses."""

    edge_class: type[Edge] = Edge
    """The Edge subclass used by this Weaver type from its data model. Must be overridden in subclasses."""

    def __init__(self):
        """
        Initializes the Weaver with output paths for nodes and edges.
        """

        self.node_output_path: Path
        self.edge_output_path: Path
        self.__set_output_path__()
        self.__set_writers__()

        logger.info("Weaver Initialized")

    def __set_output_path__(self):
        """
        Set the output path for the Weaver's output files.
        """

        self.node_output_path = Weaver._get_output_filename(
            base_name="nodes", extension="csv"
        )
        self.edge_output_path = Weaver._get_output_filename(
            base_name="edges", extension="csv"
        )
        logger.info(
            f"Output path set to {self.node_output_path} and {self.edge_output_path}"
        )

    def __set_writers__(self):
        """
        Set the writers for the node and edge output files.
        This method is called after the output paths are set, typically after
        object instantation.

        Also writes the headers to reduce boilerplate.

        :param node_object: Pass the Node subclass for this Weaver type for headers.
        :param edge_object: Pass the Edge subclass for this Weaver type for headers.
        """

        def merge_annotations(cls):
            merged = {}
            for base in reversed(cls.__mro__):
                merged.update(getattr(base, '__annotations__', {}))
            return merged

        # Merge annotations for node and edge subclasses
        node_fieldnames = list(merge_annotations(self.node_class).keys())
        edge_fieldnames = list(merge_annotations(self.edge_class).keys())

        self.node_output_file = open(file=self.node_output_path, mode="a", newline="")
        self.node_writer = csv.DictWriter(
            self.node_output_file, fieldnames=node_fieldnames
        )
        self.node_writer.writeheader()

        logger.debug("annotation keys: " + str(node_fieldnames))
        logger.info("Node writer created at " + str(self.node_output_path))

        self.edge_output_file = open(file=self.edge_output_path, mode="a", newline="")
        self.edge_writer = csv.DictWriter(
            self.edge_output_file, fieldnames=edge_fieldnames
        )
        self.edge_writer.writeheader()

        self.writers_set = True

        logger.debug("annotation keys: " + str(edge_fieldnames))
        logger.info("Edge writer created at " + str(self.edge_output_path))

    @staticmethod
    def _get_output_filename(
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

    def write_node(self, node: Node):
        """
        Write the generated node to the output CSV file.

        :param node: The Node object to write to the CSV file.
        """

        if self.node_writer is None:
            raise ValueError("Writers not set. Call set_writers() first.")

        self.node_writer.writerow(node.to_dict())

    def write_edge(self, edge: Edge):
        """
        Write the generated edge to the output CSV file.

        :param edge: The Edge object to write to the CSV file.
        """

        if self.edge_writer is None:
            raise ValueError("Writers not set. Call set_writers() first.")

        self.edge_writer.writerow(edge.to_dict())

    def close(self):
        """
        Close the output files for nodes and edges.
        This should be called after all nodes and edges have been written. (After weave() is called)
        """
        if self.node_output_file:
            self.node_output_file.close()
            logger.info(f"Node output file closed: {self.node_output_path}")
        if self.edge_output_file:
            self.edge_output_file.close()
            logger.info(f"Edge output file closed: {self.edge_output_path}")

    @abstractmethod
    def weave(self):
        """
        'Weave' (or create) the nodes and edges of the graph.
        """
