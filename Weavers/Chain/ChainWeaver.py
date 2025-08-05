"""
The `ChainWeaver` class is a specialized tool for generating a realistic, fake supply chain network.

Extending the `Weaver` base class, it constructs a complex graph of `Components` (nodes) and
`Requires` relationships (edges) by leveraging validated input data from JSON files. The class
orchestrates the creation of base products, their sub-components (sprues and parts), and
subsequent product variants.

### Key Features
- **Data Initialization:** The constructor resolves and validates input data from "inputdata.json" to set up
  the foundational information for manufacturers and product designations.
- **Base Product Generation:** Methods are included to create a specified number of unique base products,
  along with their individual sprues and parts.
- **Data Resolution:** A dedicated method, `resolve_base_product_sprues()`, ensures data integrity by
  removing any sprues that are not actively used by parts, thus streamlining the final output.
- **Variant Generation:** The class can generate multiple variants of base products, each with its own
  set of components, creating a more realistic and expansive supply chain.
- **Automated Weaving:** The `weave()` method acts as the main orchestrator, calling all
  the necessary generation and resolution functions in a logical sequence to produce the
  complete supply chain network.
- **Custom Naming Conventions:** The class includes helper methods to handle the generation of
  unique and logical naming conventions for product variants.
- **Robust Exception Handling:** Custom exceptions like `NamingError` are used to handle issues
  specific to the supply chain generation process.

This class is designed to be a self-contained, end-to-end solution for producing a detailed
supply chain dataset for testing, simulation, or data visualization purposes.
"""

# Standard Imports
import re
from typing import List, Tuple, Generator

# Local Imports
from Weavers.Chain.data_model import Component, Requires
from Weavers.input_utils import resolve_json
from Weavers.Weaver import Weaver, logger, FAILURE, INTERRUPTED, FAKER_GEN

logger.info("Program Start")


class NamingError(Exception):
    pass


class ChainWeaver(Weaver):
    node_class = Component
    edge_class = Requires

    def __init__(self, num_products: int = 40, variant_distribution: float = 0.25):
        super().__init__()
        self.num_products = num_products
        logger.debug(f"Num_Products:        {self.num_products}")
        self.variant_distribution = variant_distribution
        logger.debug(f"Variant_Distribution:        {self.variant_distribution}")
        self.num_variants = int(self.num_products * self.variant_distribution)
        logger.debug(f"Num_Variants:        {self.num_variants}")
        logger.info("Local Main Variables Set")

        # Validates and resolves 'inputdata.json'
        try:
            resolved_inputdata = resolve_json("inputdata.json")
        except Exception as e:
            logger.critical(e)
            raise SystemExit(FAILURE)

        self.designations = resolved_inputdata["Designations"]
        self.manufacturers = resolved_inputdata["Manufacturers"]

        logger.info("Inputs Accepted")

    # -------------------------------------------------------------------------------------------
    #                                      BASE_PRODUCTS
    # -------------------------------------------------------------------------------------------
    # region BASE_PRODUCTS
    def generate_base_products(self) -> Generator[Component, None, None]:
        """
        Generates a fake dataset of base products and their data.

        :return: A generator yielding base products.
        :rtype: Generator[Component, None, None]
        """

        # Sets empty lists to collect products along with other necessary variables
        designation_keys = self.designations.keys()
        manufacturer_keys = self.manufacturers.keys()
        designation_counter = {
            designation_type: 0 for designation_type in designation_keys
        }

        num_base_products = self.num_products
        logger.debug(f"Num_Base_Products:        {num_base_products}")

        # Creates all base products
        for _ in range(num_base_products):
            # Generates base product data
            popular_name = FAKER_GEN.word(part_of_speech="noun").capitalize()
            selected_designation = FAKER_GEN.random_element(designation_keys)
            designation_counter[selected_designation] += 1
            designation = (
                f"{selected_designation}-{designation_counter[selected_designation]}"
            )
            manufacturer = FAKER_GEN.random_element(manufacturer_keys)

            # Creates 'base_product' Component(Node)
            component_data = {
                "name": f"{popular_name} {designation}",
                "manufacturer": manufacturer,
                "locations": FAKER_GEN.random_element(
                    list(self.manufacturers[manufacturer]["Locations"])
                ),
                "full_product": True,
                "component_type": "Product",
                "variant": False,
                "designation": selected_designation,
                "popular_name": popular_name,
                "dimensions": [
                    FAKER_GEN.random_int(10, 100),
                    FAKER_GEN.random_int(10, 100),
                    FAKER_GEN.random_int(10, 100),
                ],
                "cost": round(FAKER_GEN.random_number(digits=4), 2),
                "failure_rate": round(FAKER_GEN.random_number(digits=2) / 100, 4),
                "breakability": round(FAKER_GEN.random_number(digits=2) / 100, 2),
                "year_range": [
                    FAKER_GEN.random_int(1990, 2024)
                    for _ in range(FAKER_GEN.random_int(1, 3))
                ],
            }
            base_product = Component(**component_data)

            # Records base products
            self.write_node(base_product)
            logger.info("Generating Base Products")

            yield base_product

    # endregion

    # -------------------------------------------------------------------------------------------
    #                                   BASE_PRODUCT_SPRUES
    # -------------------------------------------------------------------------------------------
    # region BASE_PRODUCT_SPRUES

    def generate_base_product_sprues(
        self,
        base_products: Generator[Component, None, None],
    ) -> Generator[Component, None, None]:
        """
        Yields base product sprue components.
        """

        # Creates 'base_product_sprue' Component Nodes based off of manufacturer
        manufacturer_keys = self.manufacturers.keys()
        for base_product in base_products:
            for manufacturer in manufacturer_keys:
                component_data = {
                    "name": f"Sprue {FAKER_GEN.bothify(text='???########')}",
                    "manufacturer": manufacturer,
                    "locations": FAKER_GEN.random_element(
                        self.manufacturers[manufacturer]["Locations"]
                    ),
                    "full_product": False,
                    "component_type": "Sprue",
                    "variant": False,
                    "product": base_product.id,
                    "dimensions": [
                        FAKER_GEN.random_int(10, 100),
                        FAKER_GEN.random_int(10, 100),
                        FAKER_GEN.random_int(10, 100),
                    ],
                    "cost": round(FAKER_GEN.random_number(digits=4), 2),
                    "failure_rate": round(FAKER_GEN.random_number(digits=2) / 100, 4),
                    "breakability": round(FAKER_GEN.random_number(digits=2) / 100, 2),
                    "year_range": [
                        FAKER_GEN.random_int(1990, 2024)
                        for _ in range(FAKER_GEN.random_int(1, 3))
                    ],
                }
                base_product_sprue = Component(**component_data)

                # Records the base product sprues
                self.write_node(base_product_sprue)
                yield base_product_sprue

    def generate_base_product_sprue_edges(
        self,
        base_products: Generator[Component, None, None],
        base_product_sprues: Generator[Component, None, None],
    ) -> Generator[Requires, None, None]:
        """
        Yields edges between base products and base product sprues.
        """

        # Convert sprues to a list for multiple passes (if needed)
        for base_product in base_products:
            for sprue in base_product_sprues:
                if sprue.product == base_product.id:
                    base_product_sprue_edge = Requires(
                        start_node=base_product.name,
                        end_node=sprue.name,
                        base_model=True,
                        lead_time=FAKER_GEN.random_int(1, 1000),
                    )
                    self.write_edge(base_product_sprue_edge)
                    yield base_product_sprue_edge

    def generate_vital_base_product_sprues(
        self,
        base_products: Generator[Component, None, None],
        base_product_sprues: Generator[Component, None, None],
    ) -> Generator[Component, None, None]:
        """
        Yields vital base product sprues.
        """

        # Defines which sprues are vital
        manufacturer_keys = self.manufacturers.keys()
        for base_product in base_products:
            parts_categories = self.designations[base_product.designation]["Parts"]
            for part_list in parts_categories.items():
                for part_type in part_list:
                    base_product_part_manufacturer = FAKER_GEN.random_element(
                        list(manufacturer_keys)
                    )
                    is_vital = (
                        part_type
                        in self.designations[base_product.designation]["Vital Parts"]
                    )
                    if is_vital:
                        for base_product_sprue in base_product_sprues:
                            if (
                                base_product.id == base_product_sprue.product
                                and base_product_part_manufacturer
                                == base_product_sprue.manufacturer
                            ):
                                yield base_product_sprue

    # endregion

    # -------------------------------------------------------------------------------------------
    #                                   BASE_PRODUCT_PARTS
    # -------------------------------------------------------------------------------------------
    # region BASE_PRODUCT_PARTS

    def generate_base_product_parts(
        self,
        base_products: Generator[Component, None, None],
    ) -> Generator[Component, None, None]:
        """
        Yields base product part components.
        """

        # Generates base product parts and sorts them into the sprues matching their manufacturer
        manufacturer_keys = self.manufacturers.keys()
        for base_product in base_products:
            parts_categories = self.designations[base_product.designation]["Parts"]
            for part_category, part_list in parts_categories.items():
                for part_type in part_list:
                    base_product_part_manufacturer = FAKER_GEN.random_element(
                        list(manufacturer_keys)
                    )
                    component_data = {
                        "name": f"{part_type} {FAKER_GEN.bothify('???#####')}",
                        "manufacturer": base_product_part_manufacturer,
                        "locations": FAKER_GEN.random_element(
                            self.manufacturers[base_product_part_manufacturer][
                                "Locations"
                            ]
                        ),
                        "full_product": False,
                        "component_type": "Part",
                        "variant": False,
                        "product": base_product.id,
                        "variant_base_product": None,
                        "vital": part_type
                        in self.designations[base_product.designation]["Vital Parts"],
                        "category": part_category,
                        "part_type": part_type,
                        "dimensions": [
                            FAKER_GEN.random_int(10, 100),
                            FAKER_GEN.random_int(10, 100),
                            FAKER_GEN.random_int(10, 100),
                        ],
                        "cost": round(FAKER_GEN.random_number(digits=4), 2),
                        "failure_rate": round(
                            FAKER_GEN.random_number(digits=2) / 100, 4
                        ),
                        "breakability": round(
                            FAKER_GEN.random_number(digits=2) / 100, 2
                        ),
                        "year_range": [
                            FAKER_GEN.random_int(1990, 2024)
                            for _ in range(FAKER_GEN.random_int(1, 3))
                        ],
                    }
                    base_product_part = Component(**component_data)

                    # Records base product parts
                    self.write_node(base_product_part)
                    yield base_product_part

    def generate_base_product_part_edges(
        self,
        base_product_parts: Generator[Component, None, None],
        base_product_sprues: Generator[Component, None, None],
    ) -> Generator[Requires, None, None]:
        """
        Yields edges between base product sprues and base product parts.
        """

        # Generates Requires edges between base product parts and sprues
        for base_product_part in base_product_parts:
            for base_product_sprue in base_product_sprues:
                if (
                    base_product_part.product == base_product_sprue.product
                    and base_product_part.manufacturer
                    == base_product_sprue.manufacturer
                ):
                    base_product_part_edge = Requires(
                        start_node=base_product_sprue.name,
                        end_node=base_product_part.name,
                        base_model=True,
                        lead_time=FAKER_GEN.random_int(1, 1000),
                    )

                    # Records Requires edges
                    self.write_edge(base_product_part_edge)
                    yield base_product_part_edge

    # endregion

    # -------------------------------------------------------------------------------------------
    #                               RESOLVE_BASE_PRODUCT_SPRUES
    # -------------------------------------------------------------------------------------------
    # region RESOLVE_BASE_PRODUCT_SPRUES

    def resolve_base_product_sprues(
        self,
        base_product_sprues: List[Component],
        base_product_sprue_edges: List[Requires],
        base_product_part_edges: List[Requires],
    ) -> Tuple[List[Component], List[Requires]]:
        """
        Generates the new resolved lists of sprues and sprue edges to replace the old lists.

        :param `base_product_sprues`: A list of base product sprues and their data.
        :type `base_product_sprues`: List[Component]
        :param `base_product_sprue_edges`: A list of base produuct sprue edges and their data.
        :type `base_product_sprue_edges`: List[Requires]
        :param `base_product_part_edges`: A list of base product part edges and their data.
        :type `base_product_part_edges`: List[Requires]

        :return: A new resolved list of base product sprues.
        :rtype: List[Components]
        :return: A new resolved list of base product sprue edges.
        :rtype: List[Requires]
        """

        # Sets empty lists to collect sprues and edges to keep
        resolved_base_sprues = []
        resolved_base_sprue_edges = []

        # Checks that all sprues are used
        for i, base_product_sprue in enumerate(base_product_sprues, start=1):
            # Checks if a sprue has any edges to parts
            has_edge = any(
                edge.start_node == base_product_sprue
                for edge in base_product_part_edges
            )
            if has_edge:
                # Appends 'base_product_sprue' Component(Node) to the overall new list of 'base_product_sprues'
                resolved_base_sprues.append(base_product_sprue)
                logger.debug(f"Kept Sprue {i}")

                # Appends 'base_product_sprue_edge' Requires(Edge) to the overall new list of 'base_product_sprue_edges'
                resolved_base_sprue_edges.extend(
                    e
                    for e in base_product_sprue_edges
                    if e.end_node == base_product_sprue
                )

        return resolved_base_sprues, resolved_base_sprue_edges

    # endregion

    # -------------------------------------------------------------------------------------------
    #                                   NAMING_CONVENTIONS
    # -------------------------------------------------------------------------------------------
    # region NAMING_CONVENTIONS

    def get_next_letter(self, current_letter):
        """
        Minor Function to get the variant_designation_letter of multi-layer variants.
        :param `current_letter`: The variant_designation_letter of the variant on its last variation.
        :return: A string of one capital letter to be the next variant_designation_letter.
        """
        # Get the ASCII value of the current letter and adds 1 to get the ASCII of the next
        next_char_code = ord(current_letter) + 1

        # If it goes past "Z", wrap around to "A"
        if next_char_code > ord("Z"):
            next_char_code = ord("A")

        # Converts back to chr and outputs as a string of a standard capital letter
        return chr(next_char_code)

    # endregion

    # -------------------------------------------------------------------------------------------
    #                                   VARIANT_PRODUCTS
    # -------------------------------------------------------------------------------------------
    # region VARIANT_PRODUCTS

    def current_designation_value(self, current_designation):
        match = re.search(r"([A-Z]+)$", current_designation)
        if not match:
            return 0
        current_letters = match.group(1)
        value = 0
        for i, char in enumerate(reversed(current_letters)):
            value += (ord(char) - ord("A") + 1) * (26**i)
        return value

    def find_current_designation(
        self, variant_base_product: Component, variant_products: List[Component]
    ) -> str:
        current_designations = []
        for variant_product in variant_products:
            if variant_product.variant_base_product == variant_base_product.id:
                designation = variant_product.designation
                if designation:
                    current_designations.append(designation)

        if not current_designations:
            raise NamingError(
                f"VariantNameIdentificationError: {variant_base_product.id} has No Preexisting Variants"
            )
        current_designation = max(
            current_designations, key=self.current_designation_value
        )
        return current_designation

    def next_variant_designation(
        self, variant_base_product: Component, variant_products: List[Component]
    ) -> str:
        """
        Returns the next variant designation letter in a base-26 alphabetical sequence.
        After 'Z', it continues with 'AA', 'AB', etc.

        :param current_letter: The current variant designation string (e.g., 'A', ..., 'Z', 'AA', ...)
        :return: The next variant designation string.
        """

        try:
            current_designation = self.find_current_designation(
                variant_base_product, variant_products
            )
        except NamingError as e:
            logger.warning(f"{type(e).__name__}: {e}")
            assert variant_base_product.designation, str
            return variant_base_product.designation + "A"

        match = re.search(r"([A-Z]+)$", current_designation)
        if not match:
            raise SystemExit(FAILURE)
        current_letter = match.group(1)
        letters = list(current_letter)
        i = len(letters) - 1

        while i >= 0:
            if letters[i] != "Z":
                start_letter = letters[i]
                letters[i] = chr(ord(letters[i]) + 1)
                changed_letter = letters[i]
                logger.info(
                    f"Start Letter of '{start_letter}' Changed to '{changed_letter}'"
                )
                break
            else:
                start_letter = letters[i]
                letters[i] = "A"
                changed_letter = letters[i]
                logger.info(
                    f"Start Letter of '{start_letter}' Changed to '{changed_letter}'"
                )
                i -= 1

        # If all characters were 'Z', we need to add a new 'A' at the beginning
        if i < 0:
            letters.insert(0, "A")
        next_letters = "".join(letters)
        next_designation = re.sub(r"([A-Z]+)$", next_letters, current_designation)
        return next_designation

    def generate_variant_products(
        self, base_products: Generator[Component, None, None]
    ) -> Generator[Component, None, None]:
        """
        Generates variant products sequentially from base products.
        """

        manufacturer_keys = list(self.manufacturers.keys())

        # [ ] FLAG -- don't want all num of variants for every base product -- want to choose one randomly total num times
        for base_product in base_products:
            for i in range(self.num_variants):
                # Generate designation based on counter
                variant_designation = f"{base_product.designation}{chr(ord('A') + i)}"
                variant_manufacturer = FAKER_GEN.random_element(manufacturer_keys)

                component_data = {
                    "name": f"{base_product.popular_name} {variant_designation}",
                    "manufacturer": variant_manufacturer,
                    "locations": FAKER_GEN.random_element(
                        list(self.manufacturers[variant_manufacturer]["Locations"])
                    ),
                    "full_product": True,
                    "component_type": "Product",
                    "variant": True,
                    "variant_base_product": base_product.id,
                    "designation": base_product.designation,
                    "popular_name": base_product.popular_name,
                    "dimensions": [
                        FAKER_GEN.random_int(10, 100),
                        FAKER_GEN.random_int(10, 100),
                        FAKER_GEN.random_int(10, 100),
                    ],
                    "cost": round(FAKER_GEN.random_number(digits=4), 2),
                    "failure_rate": round(FAKER_GEN.random_number(digits=2) / 100, 4),
                    "breakability": round(FAKER_GEN.random_number(digits=2) / 100, 2),
                    "year_range": [
                        FAKER_GEN.random_int(1990, 2024)
                        for _ in range(FAKER_GEN.random_int(1, 3))
                    ],
                }
                variant_product = Component(**component_data)

                # Records the variant products
                self.write_node(variant_product)
                yield variant_product

    # endregion

    # -------------------------------------------------------------------------------------------
    #                                   VARIANT_SPRUES
    # -------------------------------------------------------------------------------------------
    # region VARIANT_SPRUES

    def generate_variant_product_sprues(
        self,
        variant_products: Generator[Component, None, None],
        vital_base_product_sprues: Generator[Component, None, None],
    ) -> Generator[Component, None, None]:
        """
        Yields variant sprue components.
        """
        variant_products_list = list(variant_products)
        vital_sprues_list = list(vital_base_product_sprues)
        manufacturer_keys = list(self.manufacturers.keys())

        for variant_product in variant_products_list:
            individual_needed_manufacturers = set(manufacturer_keys)
            for vital_sprue in vital_sprues_list:
                if variant_product.variant_base_product == vital_sprue.product:
                    individual_needed_manufacturers.discard(vital_sprue.manufacturer)
            for manufacturer in individual_needed_manufacturers:
                component_data = {
                    "name": f"Sprue {FAKER_GEN.bothify(text='???########')}",
                    "manufacturer": manufacturer,
                    "locations": FAKER_GEN.random_element(
                        self.manufacturers[manufacturer]["Locations"]
                    ),
                    "full_product": False,
                    "component_type": "Sprue",
                    "variant": True,
                    "product": variant_product.id,
                    "dimensions": [
                        FAKER_GEN.random_int(10, 100),
                        FAKER_GEN.random_int(10, 100),
                        FAKER_GEN.random_int(10, 100),
                    ],
                    "cost": round(FAKER_GEN.random_number(digits=4), 2),
                    "failure_rate": round(FAKER_GEN.random_number(digits=2) / 100, 4),
                    "breakability": round(FAKER_GEN.random_number(digits=2) / 100, 2),
                    "year_range": [
                        FAKER_GEN.random_int(1990, 2024)
                        for _ in range(FAKER_GEN.random_int(1, 3))
                    ],
                }
                variant_sprue = Component(**component_data)
                self.write_node(variant_sprue)
                yield variant_sprue

    def generate_variant_product_sprue_edges(
        self,
        variant_products: Generator[Component, None, None],
        variant_sprues: Generator[Component, None, None],
        vital_base_product_sprues: Generator[Component, None, None],
    ) -> Generator[Requires, None, None]:
        """
        Yields edges between variant products and their sprues (including vital sprues).
        """
        variant_products_list = list(variant_products)
        variant_sprues_list = list(variant_sprues)
        vital_sprues_list = list(vital_base_product_sprues)

        for variant_product in variant_products_list:
            for vital_sprue in vital_sprues_list:
                if variant_product.variant_base_product == vital_sprue.product:
                    variant_sprue_edge = Requires(
                        start_node=variant_product.name,
                        end_node=vital_sprue.name,
                        base_model=True,
                        lead_time=FAKER_GEN.random_int(1, 1000),
                    )
                    self.write_edge(variant_sprue_edge)
                    yield variant_sprue_edge
            for variant_sprue in variant_sprues_list:
                if variant_sprue.product == variant_product.id:
                    variant_sprue_edge = Requires(
                        start_node=variant_product.name,
                        end_node=variant_sprue.name,
                        base_model=True,
                        lead_time=FAKER_GEN.random_int(1, 1000),
                    )
                    self.write_edge(variant_sprue_edge)
                    yield variant_sprue_edge

    # endregion

    # -------------------------------------------------------------------------------------------
    #                                   VARIANT_PARTS
    # -------------------------------------------------------------------------------------------
    # region VARIANT_PARTS

    def get_needed_parts(self, variant_products):
        needed_parts = {}
        for vp in variant_products:
            parts = []
            parts_categories = self.designations[vp.designation]["Parts"]
            for part_list in parts_categories.values():
                parts.extend(part_list)
            needed_parts[vp.id] = parts
        return needed_parts

    def get_needed_manufacturers(self, variant_products):
        needed_manufacturers = {}
        manufacturer_keys = list(self.manufacturers.keys())
        for vp in variant_products:
            # You can customize this logic as needed
            needed_manufacturers[vp.id] = manufacturer_keys
        return needed_manufacturers

    def generate_variant_parts(
        self,
        variant_products: Generator[Component, None, None],
    ) -> Generator[Component, None, None]:
        """
        Yields variant part components.
        """

        needed_parts = self.get_needed_parts(variant_products)
        needed_manufacturers = self.get_needed_manufacturers(variant_products)

        for variant_product in variant_products:
            parts_categories = self.designations[variant_product.designation]["Parts"]
            for part_category, _ in parts_categories.items():
                for part_type in needed_parts[variant_product.id]:
                    variant_part_manufacturer = FAKER_GEN.random_element(
                        needed_manufacturers[variant_product.id]
                    )
                    component_data = {
                        "name": f"{part_type}{FAKER_GEN.bothify('???#####')}",
                        "manufacturer": variant_part_manufacturer,
                        "locations": FAKER_GEN.random_element(
                            self.manufacturers[variant_part_manufacturer]["Locations"]
                        ),
                        "full_product": False,
                        "component_type": "Part",
                        "product": variant_product.id,
                        "variant": True,
                        "category": part_category,
                        "part_type": part_type,
                        "dimensions": [
                            FAKER_GEN.random_int(10, 100),
                            FAKER_GEN.random_int(10, 100),
                            FAKER_GEN.random_int(10, 100),
                        ],
                        "cost": round(FAKER_GEN.random_number(digits=4), 2),
                        "failure_rate": round(
                            FAKER_GEN.random_number(digits=2) / 100, 4
                        ),
                        "breakability": round(
                            FAKER_GEN.random_number(digits=2) / 100, 2
                        ),
                        "year_range": [
                            FAKER_GEN.random_int(1990, 2024)
                            for _ in range(FAKER_GEN.random_int(1, 3))
                        ],
                    }
                    variant_part = Component(**component_data)
                    self.write_node(variant_part)
                    yield variant_part

    def generate_variant_part_edges(
        self,
        variant_parts: Generator[Component, None, None],
        variant_sprues: Generator[Component, None, None],
    ) -> Generator[Requires, None, None]:
        """
        Yields edges between variant sprues and variant parts.
        """
        variant_sprues_list = list(variant_sprues)
        for variant_part in variant_parts:
            for variant_sprue in variant_sprues_list:
                if (
                    variant_part.product == variant_sprue.product
                    and variant_part.manufacturer == variant_sprue.manufacturer
                ):
                    variant_part_edge = Requires(
                        start_node=variant_sprue.name,
                        end_node=variant_part.name,
                        base_model=True,
                        lead_time=FAKER_GEN.random_int(1, 1000),
                    )
                    self.write_edge(variant_part_edge)
                    yield variant_part_edge

    # endregion

    def weave(self):
        """
        Weave to generate a fake supply chain.
        """
        # Base products
        base_products = self.generate_base_products()

        # Base products sprues and edges
        base_product_sprues = self.generate_base_product_sprues(base_products)
        base_product_sprue_edges = self.generate_base_product_sprue_edges(
            base_products, base_product_sprues
        )
        vital_base_product_sprues = self.generate_vital_base_product_sprues(
            base_products, base_product_sprues
        )

        # Base product parts and edges
        base_product_parts = self.generate_base_product_parts(base_products)
        base_product_part_edges = self.generate_base_product_part_edges(
            base_product_parts, base_product_sprues
        )

        # TODO: Find a way to resolve base product sprues and edges inside of their creation function
        # resolved_base_product_sprues, resolved_base_product_sprue_edges = (
        #     self.resolve_base_product_sprues(
        #         base_product_sprues, base_product_sprue_edges, base_product_part_edges
        #     )
        # )
        # logger.info("Base Product Sprues Resolved")

        # Variant products
        variant_products = self.generate_variant_products(base_products)

        # Variant sprues
        variant_sprues = self.generate_variant_product_sprues(
            variant_products, vital_base_product_sprues
        )
        variant_sprue_edges = self.generate_variant_product_sprue_edges(
            variant_products, variant_sprues, vital_base_product_sprues
        )

        # Variant parts
        variant_parts = self.generate_variant_parts(variant_products)
        variant_part_edges = self.generate_variant_part_edges(
            variant_parts, variant_sprues
        )


def main():
    weaver = ChainWeaver(num_products=10, variant_distribution=0.25)
    weaver.weave()
    weaver.close()


# endregion

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        logger.warning(
            f"{type(e).__name__}: Input Processing Interrupted by User -- Exiting"
        )
        raise SystemExit(INTERRUPTED)

logger.info("Program End")
