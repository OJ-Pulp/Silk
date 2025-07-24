"""
OVERALL CHAINWEAVER
"""

# Standard
import re
from pathlib import Path
from typing import List, Tuple

# Local
from Weavers.Chain.data_model import Component, Requires
from Weavers.Chain.input_utils import resolve_json
from Weavers.Weaver import Weaver, logger, SUCCESS, FAILURE, INTERRUPTED, FAKER_GEN

logger.info("Program Start")


class NamingError(Exception):
    pass


class ChainWeaver(Weaver):
    def __init__(self, num_products: int = 40, variant_distribution: float = 0.25):
        super().__init__()
        self.num_products = num_products
        self.variant_distribution = variant_distribution

        # Validates and resolves 'inputdata.json'
        try:
            resolved_inputdata = resolve_json("inputdata.json")
        except Exception as e:
            logger.critical(f"{type(e).__name__}: {e}")
            raise SystemExit(FAILURE)

        logger.info("Inputs Accepted")

        self.designations = resolved_inputdata["Designations"]
        self.manufacturers = resolved_inputdata["Manufacturers"]

        self.base_edges = []
        self.variant_edges = []
        self.base_components = []
        self.variant_components = []

    # -------------------------------------------------------------------------------------------
    #                                      BASE_PRODUCTS
    # -------------------------------------------------------------------------------------------
    # region BASE_PRODUCTS
    def create_base_products(
        self,
        num_base_products: int,
    ) -> List[Component]:
        """
        Generates a fake dataset of base products and their data.

        :param `num_base_products`: The total number of unique base products to include in the supply chain.
        :type `num_base_products`: int

        :return: A list of base products.
        :rtype: List[Component]
        """

        # Sets empty lists to collect products along with other necessary variables
        base_products = []
        designation_keys = self.designations.keys()
        manufacturer_keys = self.manufacturers.keys()
        designation_counter = {
            designation_type: 0 for designation_type in designation_keys
        }

        # Creates all base products
        for i in range(num_base_products):
            logger.debug(f"Base Product {i}:")

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
                "substitutions": [
                    FAKER_GEN.bothify("???###")
                    for _ in range(FAKER_GEN.random_int(0, 3))
                ],
                "breakability": round(FAKER_GEN.random_number(digits=2) / 100, 2),
                "year_range": [
                    FAKER_GEN.random_int(1990, 2024)
                    for _ in range(FAKER_GEN.random_int(1, 3))
                ],
            }
            base_product = Component(**component_data)

            self.write_node(base_product)

            # Appends 'base_product' Component(Node) to the overall list of 'base_products'
            base_products.append(base_product)
            logger.debug(base_product)
            logger.debug("")

        return base_products

    # endregion

    # -------------------------------------------------------------------------------------------
    #                                   BASE_PRODUCT_SPRUES
    # -------------------------------------------------------------------------------------------
    # region BASE_PRODUCT_SPRUES

    def create_base_product_sprues(
        self,
        base_products: List[Component],
    ) -> Tuple[List[Component], List[Requires]]:
        """
        Generates a fake dataset of base product sprues and sprue edges and their data.

        :param `base_products`: A list of base products and their data.
        :type `base_products`: List[Component]
        :param `manufacturers_dict`: The 'Manufacturer' category of 'resolved_inputdata'.
        :type `manufacturers_dict`: dict

        :return: A list of base product sprues.
        :rtype: List[Component]
        :return: A list of edges between base products and base product sprues.
        :rtype: List[Requires]
        """

        # Sets empty lists to collect sprues and edges along with other necessary variables
        base_product_sprues = []
        base_product_sprue_edges = []
        manufacturer_keys = list(self.manufacturers.keys())

        # Creates all base product sprues and edges
        for i, base_product in enumerate(base_products, start=1):
            logger.debug(f"Base Product {i}:")

            for manufacturer in manufacturer_keys:
                logger.debug(f"{manufacturer} Base Product Sprue:")

                # Creates 'base_product_sprue' Component(Node)
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
                    "substitutions": [
                        FAKER_GEN.bothify("???###")
                        for _ in range(FAKER_GEN.random_int(0, 3))
                    ],
                    "breakability": round(FAKER_GEN.random_number(digits=2) / 100, 2),
                    "year_range": [
                        FAKER_GEN.random_int(1990, 2024)
                        for _ in range(FAKER_GEN.random_int(1, 3))
                    ],
                }
                base_product_sprue = Component(**component_data)

                # Appends 'base_product_sprue' Component(Node) to the overall list of 'base_product_sprues'
                base_product_sprues.append(base_product_sprue)
                logger.debug(base_product_sprue)
                logger.debug("")

                logger.debug(f"{manufacturer} Base Product Sprue Edge:")

                # Creates 'base_product' to 'base_product_sprue' Requires(Edge)
                base_product_sprue_edge = Requires(
                    start_node=base_product,
                    end_node=base_product_sprue,
                    base_model=True,
                    lead_time=FAKER_GEN.random_int(1, 1000),  # In Business Days
                )

                # Appends 'base_product_sprue_edge' Requires(Edge) to the overall list of 'base_product_sprue_edges'
                base_product_sprue_edges.append(base_product_sprue_edge)
                logger.debug(base_product_sprue_edge)
                logger.debug("")

        return base_product_sprues, base_product_sprue_edges

    # endregion

    # -------------------------------------------------------------------------------------------
    #                                   BASE_PRODUCT_PARTS
    # -------------------------------------------------------------------------------------------
    # region BASE_PRODUCT_PARTS

    def create_base_product_parts(
        self,
        base_products: List[Component],
        base_product_sprues: List[Component],
    ) -> Tuple[List[Component], List[Requires], List[Component]]:
        """
        Generates a fake dataset of base product parts and part edges and their data.
        Supports recursive subcomponent generation for parts that have their own parts.

        :param `base_products`: A list of base products and their data.
        :type `base_products`: List[Component]
        :param `base_product_sprues`: A list of base product sprues and their data.
        :type `base_product_sprues`: List[Component]

        :return: A list of base product parts.
        :rtype: List[Component]
        :return: A list of edges between base product sprues and base product parts.
        :rtype: List[Requires]
        :return: A list of sprues that contain vital base product parts.
        :rtype: List[Component]
        """

        # Sets empty lists to collect parts, edges, and vital sprues along with other necessary variables
        base_product_parts = []
        base_product_part_edges = []
        vital_base_product_sprues = []
        manufacturer_keys = list(self.manufacturers.keys())

        def generate_subparts(
            parent_part, parent_category, parent_designation, parent_manufacturer
        ):
            # If this part type is also a designation, generate its subparts
            if parent_part.metadata["part_type"] in self.designations:
                sub_designation = self.designations[parent_part.metadata["part_type"]]
                sub_parts_categories = sub_designation.get("Parts", {})
                for sub_category, sub_part_list in sub_parts_categories.items():
                    for sub_part_type in sub_part_list:
                        sub_part_manufacturer = FAKER_GEN.random_element(
                            manufacturer_keys
                        )
                        component_data = {
                            "name": f"{sub_part_type} {FAKER_GEN.bothify('???#####')}",
                            "manufacturer": sub_part_manufacturer,
                            "locations": FAKER_GEN.random_element(
                                self.manufacturers[sub_part_manufacturer]["Locations"]
                            ),
                            "full_product": False,
                            "component_type": "Part",
                            "variant": False,
                            "product": parent_part.metadata["product"],
                            "variant_base_product": None,
                            "vital": False,
                            "category": sub_category,
                            "part_type": sub_part_type,
                            "dimensions": [
                                FAKER_GEN.random_int(10, 100),
                                FAKER_GEN.random_int(10, 100),
                                FAKER_GEN.random_int(10, 100),
                            ],
                            "cost": round(FAKER_GEN.random_number(digits=4), 2),
                            "failure_rate": round(
                                FAKER_GEN.random_number(digits=2) / 100, 4
                            ),
                            "substitutions": [
                                FAKER_GEN.bothify("???###")
                                for _ in range(FAKER_GEN.random_int(0, 3))
                            ],
                            "breakability": round(
                                FAKER_GEN.random_number(digits=2) / 100, 2
                            ),
                            "year_range": [
                                FAKER_GEN.random_int(1990, 2024)
                                for _ in range(FAKER_GEN.random_int(1, 3))
                            ],
                        }
                        sub_part = Component(**component_data)
                        base_product_parts.append(sub_part)
                        # Edge from parent_part to sub_part
                        edge = Requires(
                            start_node=parent_part,
                            end_node=sub_part,
                            base_model=True,
                            lead_time=FAKER_GEN.random_int(1, 1000),
                        )
                        base_product_part_edges.append(edge)
                        # Recurse further if needed
                        generate_subparts(
                            sub_part,
                            sub_category,
                            parent_part.metadata["part_type"],
                            sub_part_manufacturer,
                        )

        for i, base_product in enumerate(base_products, start=1):
            logger.debug(f"Base Product {i}:")
            parts_categories = self.designations[base_product.metadata["designation"]][
                "Parts"
            ]
            for part_category, part_list in parts_categories.items():
                for part_type in part_list:
                    logger.debug(f"{part_type}:")
                    base_product_part_manufacturer = FAKER_GEN.random_element(
                        list(manufacturer_keys)
                    )
                    base_product_part_vital = (
                        True
                        if part_type
                        in self.designations[base_product.metadata["designation"]][
                            "Vital Parts"
                        ]
                        else False
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
                        "vital": base_product_part_vital,
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
                        "substitutions": [
                            FAKER_GEN.bothify("???###")
                            for _ in range(FAKER_GEN.random_int(0, 3))
                        ],
                        "breakability": round(
                            FAKER_GEN.random_number(digits=2) / 100, 2
                        ),
                        "year_range": [
                            FAKER_GEN.random_int(1990, 2024)
                            for _ in range(FAKER_GEN.random_int(1, 3))
                        ],
                    }
                    base_product_part = Component(**component_data)
                    base_product_parts.append(base_product_part)
                    logger.debug(base_product_part)
                    logger.debug("")
                    for base_product_sprue in base_product_sprues:
                        if (
                            base_product_part.metadata["product"]
                            == base_product_sprue.metadata["product"]
                            and base_product_part.manufacturer
                            == base_product_sprue.manufacturer
                        ):
                            logger.debug(f"{part_type} Edge:")
                            base_product_part_edge = Requires(
                                start_node=base_product_sprue,
                                end_node=base_product_part,
                                base_model=True,
                                lead_time=FAKER_GEN.random_int(1, 1000),
                            )
                            base_product_part_edges.append(base_product_part_edge)
                            logger.debug(base_product_part_edge)
                            logger.debug("")
                            if base_product_part_vital:
                                vital_base_product_sprues.append(base_product_sprue)
                    # Recursively generate subparts if this part is also a designation
                    generate_subparts(
                        base_product_part,
                        part_category,
                        base_product.metadata["designation"],
                        base_product_part_manufacturer,
                    )

        return base_product_parts, base_product_part_edges, vital_base_product_sprues

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
            logger.debug(f"Sprue {i}:")

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
                logger.debug(f"Kept Edges for Sprue {i}")
                logger.debug("")
            else:
                logger.debug(f"Removed Base Product Sprue {i}:")
                logger.debug(base_product_sprue)
                logger.debug("")

        return resolved_base_sprues, resolved_base_sprue_edges

    # endregion

    # -------------------------------------------------------------------------------------------
    #                                   NAMING_CONVENTIONS
    # -------------------------------------------------------------------------------------------
    # region NAMING_CONVENTIONS

    def get_next_letter(self, current_letter):
        """
        Minor Function to get the variant_designation_letter of multi-layer variants.
        :param current_letter: The variant_designation_letter of the variant on its last variation.
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
            if (
                variant_product.metadata.get("variant_base_product")
                == variant_base_product.id
            ):
                designation = variant_product.metadata.get("designation")
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
            return variant_base_product.metadata["designation"] + "A"

        match = re.search(r"([A-Z]+)$", current_designation)
        if not match:
            raise SystemExit(FAILURE)
        current_letter = match.group(1)
        letters = list(current_letter)
        logger.info(f"INPUT: Letters:         {letters}")
        i = len(letters) - 1
        logger.debug(f"I:       {i}")

        while i >= 0:
            if letters[i] != "Z":
                start_letter = letters[i]
                letters[i] = chr(ord(letters[i]) + 1)
                changed_letter = letters[i]
                logger.info(
                    f"Start Letter of '{start_letter}' Changed to '{changed_letter}'"
                )
                logger.debug(f"Letters:         {letters}")
                logger.debug(f"OUTPUT: New Letters:         {letters}")
                break
            else:
                start_letter = letters[i]
                letters[i] = "A"
                changed_letter = letters[i]
                logger.info(
                    f"Start Letter of '{start_letter}' Changed to '{changed_letter}'"
                )
                logger.debug(f"Letters:         {letters}")
                i -= 1
                logger.debug(f"I:       {i}")

        # If all characters were 'Z', we need to add a new 'A' at the beginning
        if i < 0:
            letters.insert(0, "A")
        next_letters = "".join(letters)
        next_designation = re.sub(r"([A-Z]+)$", next_letters, current_designation)
        logger.info(f"OUTPUT: New Letters:         {letters}")
        logger.info(f"Next Designation:         {next_designation}")
        return next_designation

    def create_variant_products(
        self, base_products: List[Component], num_variants: int = 10
    ) -> List[Component]:
        """
        INSERT STUFF
        """

        # Sets empty list to collect variant products along with other necessary variables
        variant_products = []
        manufacturer_keys = list(self.manufacturers.keys())

        # Creates all variant products
        for i in range(num_variants):
            logger.debug(f"Variant Product {i}:")

            # Picks a random base product to create a variant of
            variant_base_product = FAKER_GEN.random_element(base_products)
            # Generates variant product data
            variant_designation = self.next_variant_designation(
                variant_base_product, variant_products
            )
            variant_manufacturer = FAKER_GEN.random_element(manufacturer_keys)

            # Creates 'base_product' Component(Node)
            component_data = {
                "name": f"{variant_base_product.metadata['popular_name']} {variant_designation}",
                "manufacturer": variant_manufacturer,
                "locations": FAKER_GEN.random_element(
                    list(self.manufacturers[variant_manufacturer]["Locations"])
                ),
                "full_product": True,
                "component_type": "Product",
                "variant": True,
                "variant_base_product": variant_base_product.id,
                "designation": variant_base_product.metadata["designation"],
                "popular_name": variant_base_product.metadata["popular_name"],
                "dimensions": [
                    FAKER_GEN.random_int(10, 100),
                    FAKER_GEN.random_int(10, 100),
                    FAKER_GEN.random_int(10, 100),
                ],
                "cost": round(FAKER_GEN.random_number(digits=4), 2),
                "failure_rate": round(FAKER_GEN.random_number(digits=2) / 100, 4),
                "substitutions": [
                    FAKER_GEN.bothify("???###")
                    for _ in range(FAKER_GEN.random_int(0, 3))
                ],
                "breakability": round(FAKER_GEN.random_number(digits=2) / 100, 2),
                "year_range": [
                    FAKER_GEN.random_int(1990, 2024)
                    for _ in range(FAKER_GEN.random_int(1, 3))
                ],
            }
            variant_product = Component(**component_data)

            # Appends 'variant_product' Component(Node) to the overall list of 'variant_products'
            variant_products.append(variant_product)
            logger.debug(variant_product)
            logger.debug("")

        return variant_products

    # endregion

    # -------------------------------------------------------------------------------------------
    #                                   VARIANT_SPRUES
    # -------------------------------------------------------------------------------------------
    # region VARIANT_SPRUES

    def create_variant_product_sprues(
        self,
        variant_products: List[Component],
        vital_base_product_sprues: List[Component],
        base_product_part_edges: List[Requires],
    ) -> Tuple[List[Component], List[Requires], dict, dict]:
        """
        INSERT STUFF
        """

        # Sets empty list to collect variant sprues and edges along with other necessary variables
        variant_sprues = []
        variant_sprue_edges = []
        needed_parts = {}
        needed_manufacturers = {}

        # Creates all base product sprues and edges
        for i, variant_product in enumerate(variant_products, start=1):
            logger.debug(f"Variant Product {i}:")

            individual_needed_parts = set()
            designation = self.designations.get(variant_product.metadata["designation"])
            if designation:
                parts = designation.get("Parts")
                for part_list in parts.values():
                    individual_needed_parts.update(part_list)

            individual_needed_manufacturers = set(self.manufacturers.keys())

            for vital_sprue in vital_base_product_sprues:
                if (
                    variant_product.metadata["variant_base_product"]
                    == vital_sprue.metadata["product"]
                ):
                    variant_sprues.append(vital_sprue)

                    variant_sprue_edge = Requires(
                        start_node=variant_product,
                        end_node=vital_sprue,
                        base_model=True,
                        lead_time=FAKER_GEN.random_int(1, 1000),  # In Business Days
                    )

                    variant_sprue_edges.append(variant_sprue_edge)

                    individual_needed_manufacturers.discard(vital_sprue.manufacturer)

                    for base_product_part_edge in base_product_part_edges:
                        if base_product_part_edge.start_node == vital_sprue:
                            individual_needed_parts.discard(
                                base_product_part_edge.end_node.metadata["part_type"]
                            )

            needed_parts[variant_product.id] = individual_needed_parts
            needed_manufacturers[variant_product.id] = individual_needed_manufacturers

            for manufacturer in individual_needed_manufacturers:
                logger.debug(f"{manufacturer} Variant Sprue:")

                # Creates 'base_product_sprue' Component(Node)
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
                    "substitutions": [
                        FAKER_GEN.bothify("???###")
                        for _ in range(FAKER_GEN.random_int(0, 3))
                    ],
                    "breakability": round(FAKER_GEN.random_number(digits=2) / 100, 2),
                    "year_range": [
                        FAKER_GEN.random_int(1990, 2024)
                        for _ in range(FAKER_GEN.random_int(1, 3))
                    ],
                }
                variant_sprue = Component(**component_data)

                variant_sprues.append(variant_sprue)

                logger.debug(f"{manufacturer} Variant Sprue Edge:")

                # Creates 'base_product' to 'base_product_sprue' Requires(Edge)
                variant_sprue_edge = Requires(
                    start_node=variant_product,
                    end_node=variant_sprue,
                    base_model=True,
                    lead_time=FAKER_GEN.random_int(1, 1000),  # In Business Days
                )

                variant_sprue_edges.append(variant_sprue_edge)

        return variant_sprues, variant_sprue_edges, needed_parts, needed_manufacturers

    # endregion

    # -------------------------------------------------------------------------------------------
    #                                   VARIANT_PARTS
    # -------------------------------------------------------------------------------------------
    # region VARIANT_PARTS

    def create_variant_parts(
        self,
        variant_products: List[Component],
        variant_sprues: List[Component],
        needed_parts: dict,
        needed_manufacturers: dict,
    ) -> Tuple[List[Component], List[Requires]]:
        """
        INSERT HERE
        """

        variant_parts = []
        variant_part_edges = []

        # Creates all variant product parts and edges
        for i, variant_product in enumerate(variant_products, start=1):
            logger.debug(f"Variant Product {i}:")

            parts_categories = self.designations[
                variant_product.metadata["designation"]
            ]["Parts"]
            for part_category, _ in parts_categories.items():
                for part_type in needed_parts[variant_product.id]:
                    logger.debug(f"{part_type}:")

                    # Generates variant product part data
                    variant_part_manufacturer = FAKER_GEN.random_element(
                        needed_manufacturers[variant_product.id]
                    )

                    # Creates 'variant_product_part' Component(Node)
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
                        "substitutions": [
                            FAKER_GEN.bothify("???###")
                            for _ in range(FAKER_GEN.random_int(0, 3))
                        ],
                        "breakability": round(
                            FAKER_GEN.random_number(digits=2) / 100, 2
                        ),
                        "year_range": [
                            FAKER_GEN.random_int(1990, 2024)
                            for _ in range(FAKER_GEN.random_int(1, 3))
                        ],
                    }
                    variant_part = Component(**component_data)

                    variant_parts.append(variant_part)

                    for variant_sprue in variant_sprues:
                        if (
                            variant_part.metadata["product"]
                            == variant_sprue.metadata["product"]
                            and variant_part.manufacturer == variant_sprue.manufacturer
                        ):
                            logger.debug(f"{part_type} Edge:")

                            # Creates 'base_product_sprue' to 'base_product_part' Requires(Edge)
                            variant_part_edge = Requires(
                                start_node=variant_sprue,
                                end_node=variant_part,
                                base_model=True,
                                lead_time=FAKER_GEN.random_int(
                                    1, 1000
                                ),  # In Business Days
                            )

                            # Appends 'base_product_sprue_edge' Requires(Edge) to the overall list of 'base_product_sprue_edges'
                            variant_part_edges.append(variant_part_edge)

        return variant_parts, variant_part_edges

    def weave(self):
        """
        Weave to generate a fake supply chain.

        :param num_products: The total number of unique model aircraft products to include in the supply chain.
                            Defaults to 40.
        :param variant_distribution: A float (0.0 to 1.0) controlling the proportion of products that will have variants.
                            Defaults to 0.25, meaning roughly 25% of products will be variations.
        :return: A dictionary representing the supply chain.
        """
        logger.info("Main Start")

        # Sets overall variables
        logger.debug("Local Main Variables: ")
        logger.debug(f"Num_Products:        {self.num_products}")
        logger.debug(f"Variant_Distribution:        {self.variant_distribution}")
        num_variants = int(self.num_products * self.variant_distribution)
        logger.debug(f"Num_Variants:        {num_variants}")
        num_base_products = self.num_products - num_variants
        logger.debug(f"Num_Base_Products:        {num_base_products}")
        logger.info("Local Main Variables Set")

        base_products = self.create_base_products(num_base_products)
        logger.info("Base Products Created")
        base_product_sprues, base_product_sprue_edges = self.create_base_product_sprues(
            base_products
        )
        logger.info("Base Product Sprues Created")
        base_product_parts, base_product_part_edges, vital_base_product_sprues = (
            self.create_base_product_parts(base_products, base_product_sprues)
        )
        logger.info("Base Product Parts Created")
        resolved_base_product_sprues, resolved_base_product_sprue_edges = (
            self.resolve_base_product_sprues(
                base_product_sprues, base_product_sprue_edges, base_product_part_edges
            )
        )
        logger.info("Base Product Sprues Resolved")
        variant_products = self.create_variant_products(base_products, num_variants)
        
        del base_products # Free up memory by removing base products from the list

        logger.info("Variant Products Created")
        variant_sprues, variant_sprue_edges, needed_parts, needed_manufacturers = (
            self.create_variant_product_sprues(
                variant_products, vital_base_product_sprues, base_product_part_edges
            )
        )
        logger.info("Variant Sprues Created")
        variant_parts, variant_part_edges = self.create_variant_parts(
            variant_products, variant_sprues, needed_parts, needed_manufacturers
        )
        logger.info("Variant Parts Created")

        # Collect all components and edges
        # self.base_components = (
        #     base_products + resolved_base_product_sprues + base_product_parts
        # )
        # self.variant_components = variant_products + variant_sprues + variant_parts
        # self.components = self.base_components + self.variant_components
        # self.base_edges = resolved_base_product_sprue_edges + base_product_part_edges
        # self.variant_edges = variant_sprue_edges + variant_part_edges
        # self.edges = self.base_edges + self.variant_edges
        # logger.info("Lists Consolidated")

    def generate_nodes(self) -> dict:
        return {"base": self.base_components, "variant": self.variant_components}

    def generate_edges(self) -> dict:
        return {"base": self.base_edges, "variant": self.variant_edges}

    # def write_to_csv(self, path: str = "output"):
    #     if not self.components or not self.base_edges:
    #         logger.warning("No components or edges to write. Did you call weave()?")
    #         return
    #     Component.write_to_csv(self.components, self.get_next_test_output_filename("components", "csv", Path(path)))
    #     Requires.write_to_csv(self.base_edges + self.variant_edges, self.get_next_test_output_filename("edges", "csv", Path(path)))
    #     logger.info("CSV Files Created")


def main(num_products: int = 40, variant_distribution: float = 0.25):
    weaver = ChainWeaver(num_products, variant_distribution)
    weaver.set_writers(Component, Requires)
    weaver.weave()
    weaver.node_output_file.close()
    weaver.edge_output_file.close()


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
