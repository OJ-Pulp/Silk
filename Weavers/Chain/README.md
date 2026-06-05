# ChainWeaver

ChainWeaver is a specialized tool for generating a realistic synthetic supply chain network.

> Documentation can be found 

---

## Required Software

### VSCode Extensions

- **Python ->** Published by: Microsoft

### Standard Imports

> Add here

This is a supply chain network analyzer that applies **graph theory** and **network analysis** to model and visualize supply chains.

---

## Vocabulary
| **Program Word** | **Explanation** |
| :---: | :--- |
| Component | Node with types of product, sprue, or part. |  
| Requires | Directed Edge showing which components require what other components. |
| Product | A collection of sprues and the final creation. |
| Sprue | Add here |
| Part | Add here |
| Vital Component | A component that cannot change when in a variant because it was deemed that it would fundamentally change the final product. |
| Variant | Add here |
| Designation | Add here |
| Manufacturer | Add here |

---

## ChainWeaver.py

> **Info:** Program Start

## Inputs
 
### Initial Characteristics

| **Name** | **Variable** | **Data Type** | **Default** | **Description** |
| :---: | :---: | :---: | :---: | :--- |
| Number of Products | `num_products` | `int` | 40 | The total target number of unique top-level base products to generate in the dataset. |
| Variant Distribution | `variant_distribution` | `float` | 0.25 | The percentage factor used to determine the number of variants based on the total number of desired products. |
| Number of Variants | `num_variants` | `int` | 10 | The calculated number of variants based off of the desired distribution (40 * 0.25). |

> In the future, it is hoped that the Number of Products will instead reflect the total number of base products and variants. For now, at default, there would be a total of 50 products--40 base products and 10 variants.

### Inputdata.json

Here exists a `resolve_json` functionality pulled from `Weaver.input_utils`.  A failure of this step causes the program to exit.

| **Name** | **Variable** | **Data Type** | **Description** |
| :---: | :---: | :---: | :--- |
| Designations | `self.designations` | `dict` | Configuration profile mapping distinct product types to their parts formats and vital components. |
| Manufacturers | `self.manufacturers` | `dict` | Configuration profile mapping different manufacturers to their location options and ID. |

> **Info:** Inputs Accepted

---

## Base Products

Generates a synthetic dataset of base product components and their data.

| **Name** | **Variable** | **Data Type** | **Description** |
| :---: | :---: | :---: | :--- |
| Designation Keys | `designation_keys` | `list[str]` | A list containing the specific item configuration labels extracted from the configuration rules. |
| Designation Counter | `designation_counter` | `dict` | An operational tracking variable balancing out model volumes evenly across designated archetypes. |
| Manufacturer Keys | `manufacturers_keys` | `list[str]` | A list collection storing all unique active company production keys. |
| Number of Base Products | `num_base_products` | `int` | The absolute target index total representing how many foundational product items must be generated. |

<br>

For each base product data is created and assigned:

| **Name** | **Variable** | **Data Type** | **Description** |
| :---: | :---: | :---: | :--- |
| Name | `name` | `str` | A mix of the Popular Name and the Designation. |
| Manufacturer | `manufacturer` | `str` | Randomly selected manufacturer name from a list of potential choices. |
| Locations | `locations` | `str` | Randomly selected location from a list predetermined to be associated with the chosen manufacturer. |
| Full Product | `full_product` | `bool` | A boolean that designates that this is a full, sale-ready component. |
| Component Type | `component_type` | `str` | A choice of three strings that designates what level of the supply chain the part is at. |
| Variant | `variant` | `bool` | A boolean determining whether or not the part is a variant part or product. |
| Selected Designation | `selected_designation` | `str` | The active configuration pattern index pulled from the structural schema collection. |
| Designation Counter | `designation_counter` | `int` | The running ledger matching and offsetting distribution rates for the active template item. |
| Designation | `designation` | `str` | The assigned identity name defining which component design blueprint applies to this node. |
| Popular Name | `popular_name` | `str` | A randomly generated and capitalized noun. |
| Dimensions | `dimensions` | `list[int]` | Three randomly generated integers between 10 and 100. |
| Cost | `cost` | `float` | A randomized financial baseline pricing value up to 4 digits long, formatted to 2 decimal points. |
| Failure Rate | `failure_rate` | `float` | A randomized quality-control variance factor formatted out to 4 decimal places. |
| Breakability | `breakability` | `float` | A randomized operational damage threshold metric formatted precisely to 2 decimal places. |
| Year Range | `year_range` | `list[int]` | A list of 1 to 3 random production lifespan years bounding manufacturing limits between 1990 and 2024. |

---

## Base Product Sprues

Generates a synthetic dataset of base product sprue components based on their respective manufacturers.

| **Name** | **Variable** | **Data Type** | **Description** |
| :---: | :---: | :---: | :--- |
| Manufacturer Keys | `manufacturer_keys` | `dict_keys` | A collection of the available manufacturer identifiers extracted from the system profile. |

<br>

For each base product sprue, mock data is created, assigned, and stored as a `Component` node:

| **Name** | **Variable** | **Data Type** | **Description** |
| :---: | :---: | :---: | :--- |
| Name | `name` | `str` | A synthetic string name generated dynamically using a random pattern of 3 letters and 8 numbers (e.g., `???########`). |
| Manufacturer | `manufacturer` | `str` | The explicit manufacturer assigned to this sprue lifecycle iteration. |
| Locations | `locations` | `str` | A randomly selected location mapped from the allowed locations assigned to the manufacturer. |
| Full Product | `full_product` | `bool` | A boolean flag hardcoded to `False`, signifying this is a sub-component rather than a market-ready assembly. |
| Component Type | `component_type` | `str` | A string identifier set entirely to `"Sprue"` to classify its position in the supply chain. |
| Variant | `variant` | `bool` | A boolean flag set to `False` to signal that this represents a foundational part iteration. |
| Product | `product` | `str` / `int` | The underlying unique identifier (`id`) linking this sprue directly back to its source base product. |
| Dimensions | `dimensions` | `list[int]` | A list of three randomly generated integers between 10 and 100 representing physical scale. |
| Cost | `cost` | `float` | A randomized financial value up to 4 digits long, formatted cleanly to 2 decimal places. |
| Failure Rate | `failure_rate` | `float` | A randomized factory defect metric formatted out to 4 decimal places. |
| Breakability | `breakability` | `float` | A randomized physical structural tolerance metric formatted to 2 decimal places. |
| Year Range | `year_range` | `list[int]` | A list containing 1 to 3 random integers between 1990 and 2024 representing valid production years. |

---

## Base Product Sprue Edges

Establishes structural supply chain dependencies (`Requires` relationships) linking base products to their respective sprues.

| **Name** | **Variable** | **Data Type** | **Description** |
| :---: | :---: | :---: | :--- |
| Start Node | `start_node` | `str` | The human-readable string name of the source base product. |
| End Node | `end_node` | `str` | The human-readable string name of the dependent target sprue component. |
| Base Model | `base_model` | `bool` | A boolean flag set to `True` indicating a foundational relationship assignment. |
| Lead Time | `lead_time` | `int` | A randomly selected logistics delay metric ranging between 1 and 1000 intervals. |

---

## Vital Base Product Sprues

Sifts through existing component allocations to flag and yield specific critical sprues designated as vital to the core assembly.

| **Name** | **Variable** | **Data Type** | **Description** |
| :---: | :---: | :---: | :--- |
| Parts Categories | `parts_categories` | `dict` | The comprehensive lists of associated structural categories pulled directly from the base product's design specifications. |
| Base Product Part Manufacturer | `base_product_part_manufacturer` | `str` | A randomized manufacturer assignment chosen out of the pool of active manufacturing keys. |
| Is Vital | `is_vital` | `bool` | A boolean calculation testing if the targeted sub-part sits within the explicit "Vital Parts" registry array for that designation. |

---

## Base Product Parts

Generates a synthetic dataset of base product part components, sorting them structurally based on their manufacturer allocations.

| **Name** | **Variable** | **Data Type** | **Description** |
| :---: | :---: | :---: | :--- |
| Manufacturer Keys | `manufacturer_keys` | `dict_keys` | A collection of the available manufacturer identifiers extracted from the system profile. |
| Parts Categories | `parts_categories` | `dict` | The comprehensive lists of associated structural categories pulled directly from the base product's design specifications. |
| Base Product Part Manufacturer | `base_product_part_manufacturer` | `str` | A randomized manufacturer assignment chosen out of the pool of active manufacturing keys. |

<br>

For each base product part, mock data is created, assigned, and stored as a `Component` node:

| **Name** | **Variable** | **Data Type** | **Description** |
| :---: | :---: | :---: | :--- |
| Name | `name` | `str` | A string name combining the literal part type with a random synthetic pattern of 3 letters and 5 numbers (e.g., `???#####`). |
| Manufacturer | `manufacturer` | `str` | The specific manufacturing entity randomly assigned to produce this individual part. |
| Locations | `locations` | `str` | A randomly selected location mapped from the allowed locations assigned to the chosen part manufacturer. |
| Full Product | `full_product` | `bool` | A boolean flag hardcoded to `False`, signifying this is an individual sub-assembly unit. |
| Component Type | `component_type` | `str` | A string identifier set entirely to `"Part"` to classify its specific position in the supply chain lifecycle. |
| Variant | `variant` | `bool` | A boolean flag set to `False` to signal that this represents a foundational part iteration. |
| Product | `product` | `str` / `int` | The underlying unique identifier (`id`) linking this