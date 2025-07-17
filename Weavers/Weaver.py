# Standard
import logging
import json
from abc import ABC, abstractmethod
from typing import List

# Third-Party
from kafka import KafkaProducer
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

    @abstractmethod
    def write_to_csv(self, path: str):
        """
        Write the generated nodes and edges to a CSV file.
        This method should be implemented by subclasses.
        :param path: The path to the CSV file.
        """

    # I need to reimplement this to avoid filling the memory with nodes and edges, and instead publish them directly to Kafka stream in the loops.
    # I am not sure how this will work with the current implementation of ChainWeaver
    def publish_to_kafka(
        self,
        kafka_bootstrap_servers="localhost:9092"
    ):
        producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        for node in self.nodes:
            producer.send("nodes", node.metadata)
        for edge in self.edges:
            producer.send(
                "edges",
                {
                    "start_node": edge.start_node.id,
                    "end_node": edge.end_node.id,
                },
            )
        producer.flush()
        producer.close()
