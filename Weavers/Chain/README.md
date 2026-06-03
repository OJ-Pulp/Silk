# ChainWeaver

ChainWeaver is a secialized tool for generating a realistic synthetic supply chain network.

---

## Required Software

### Add VSCode Extensions

- **Python ->** Published by: Microsoft

### Standard Imports

> Do I need to install these?

---

## Vocabulary
| **Program Word** | **Explanation** |
| :---: | :---: |
| Component | Node |  
| Requires | Directed Edge |
| Product | Add Here. |
| Variant | Add Here. |
| Designation | Add Here. |
| Manufacturer | Add Here. |

---

## ChainWeaver.py

> **Info:** Program Start

## Inputs

### Initial Characteristics

| **Characteristic** | **Variable** | **Default** | **Description** |
| :---: | :---: | :---: | :--- |
| Number of Products | `num_products` | 40 | Add Description Here. |
| Variant Distribution | `variant_distribution` | 0.25 | The percentage factor (as a float) used to determine the number of variants. |
| Number of Variants | `num_variants` | 10 | The calculated number of variants based off of the desired distribution (40 * 0.25). |

### Inputdata.json

Here exists a resolve_json functionality pulled from `Weaver.input_utils`.

| **Characteristic** | **Variable** | **Description** |
| :---: | :---: | :---: |
| Designations | `self.designations` | Add Description Here. |
| Manufacturers | `self.manufacturers` | Add Description Here. |

> **Info:** Inputs Accepted

---

## Base Products

Generates a fake dataset of base product components and their data.

| **Characteristic** | **Variable** | **Description** |
| :---: | :---: | :---: |
| Designation Keys | `designation_keys` | Add Description Here. |
| Designation Counter | `designation_counter` | Add Description Here. |
| Manufacturer Keys | `manufacturers_keys` | Add Description Here. |
| Number of Base Products | `num_base_products` | Add Description Here. |

<br>

For each base product data is created and assigned:

| **Characteristic** | **Variable** | **Description** |
| :---: | :---: | :---: |
| Name | `name` | A mix of the Popular Name and the Designation. |
| Manufacturer | `manufacturer` | Randomly selected manufacturer name from a list of potential choices. |
| Locations | `locations` | Randomly selected location from a list predetermined to be associated with the chosen manufacturer. |
| Full Product | `full_product` | A boolean that designates that this is a full, sale-ready component. |
| Component Type | `component_type` | A choice of three strings that designates what level of the supply chain the part is at. |
| Variant | `variant` | A boolean determining whether or not the part is a variant part or product. |
| Selected Designation | `selected_designation` | FIX LATER |
| Designation Counter | `designation_counter` | FIX LATER |
| Designation | `designation` | FIX LATER |
| Popular Name | `popular_name` | A randomly generated and capitalized noun. |
| Dimensions | `dimensions` | Three randomly generated integers between 10 and 100. |
| Cost | `cost` | FIX LATER |
| Failure Rate | `failure_rate` | FIX LATER |
| Breakability | `breakability` | FIX LATER |
| Year Range | `year_range` | FIX LATER |

---

## Base Product Sprues

Generates a fake dataset of base product sprue components based on their respective manufacturers.

| **Characteristic** | **Variable** | **Description** |
| :---: | :---: | :---: |
| Manufacturer Keys | `manufacturer_keys` | A collection of the available manufacturer identifiers extracted from the system profile. |

<br>

For each base product sprue, mock data is created, assigned, and stored as a `Component` node:

| **Characteristic** | **Variable** | **Description** |
| :---: | :---: | :---: |
| Name | `name` | A fake string name generated dynamically using a random pattern of 3 letters and 8 numbers. |
| Manufacturer | `manufacturer` | The explicit manufacturer assigned to this sprue lifecycle iteration. |
| Locations | `locations` | A randomly selected location mapped from the allowed locations assigned to the manufacturer. |
| Full Product | `full_product` | A boolean flag hardcoded to `False`, signifying this is a sub-component rather than a market-ready assembly. |
| Component Type | `component_type` | A string identifier set entirely to `"Sprue"` to classify its position in the supply chain. |
| Variant | `variant` | A boolean flag set to `False` to signal that this represents a foundational part iteration. |
| Product | `product` | The underlying unique identifier (`id`) linking this sprue directly back to its source base product. |
| Dimensions | `dimensions` | A list of three randomly generated integers between 10 and 100 representing physical scale. |
| Cost | `cost` | A randomized financial value up to 4 digits long, formatted cleanly to 2 decimal places. |
| Failure Rate | `failure_rate` | A randomized factory defect metric formatted out to 4 decimal places. |
| Breakability | `breakability` | A randomized physical structural tolerance metric formatted to 2 decimal places. |
| Year Range | `year_range` | A list containing 1 to 3 random integers between 1990 and 2024 representing valid production years. |

---

## Base Product Sprue Edges

Establishes structural supply chain dependencies (`Requires` relationships) linking base products to their respective sprues.

| **Characteristic** | **Variable** | **Description** |
| :---: | :---: | :---: |
| Start Node | `start_node` | The human-readable string name of the source base product. |
| End Node | `end_node` | The human-readable string name of the dependent target sprue component. |
| Base Model | `base_model` | A boolean flag set to `True` indicating a foundational relationship assignment. |
| Lead Time | `lead_time` | A randomly selected logistics delay metric ranging between 1 and 1000 intervals. |

---

## Vital Base Product Sprues

Sifts through existing component allocations to flag and yield specific critical sprues designated as vital to the core assembly.

| **Characteristic** | **Variable** | **Description** |
| :---: | :---: | :---: |
| Parts Categories | `parts_categories` | The comprehensive lists of associated structural categories pulled directly from the base product's design specifications. |
| Base Product Part Manufacturer | `base_product_part_manufacturer` | A randomized manufacturer assignment chosen out of the pool of active manufacturing keys. |
| Is Vital | `is_vital` | A boolean calculation testing if the targeted sub-part sits within the explicit "Vital Parts" registry array for that designation. |

---

## Base Product Parts

Generates a fake dataset of base product part components, sorting them structurally based on their manufacturer allocations.

| **Characteristic** | **Variable** | **Description** |
| :---: | :---: | :---: |
| Manufacturer Keys | `manufacturer_keys` | A collection of the available manufacturer identifiers extracted from the system profile. |
| Parts Categories | `parts_categories` | The comprehensive lists of associated structural categories pulled directly from the base product's design specifications. |
| Base Product Part Manufacturer | `base_product_part_manufacturer` | A randomized manufacturer assignment chosen out of the pool of active manufacturing keys. |

<br>

For each base product part, mock data is created, assigned, and stored as a `Component` node:

| **Characteristic** | **Variable** | **Description** |
| :---: | :---: | :---: |
| Name | `name` | A string name combining the literal part type with a random pattern of 3 letters and 5 numbers. |
| Manufacturer | `manufacturer` | The specific manufacturing entity randomly assigned to produce this individual part. |
| Locations | `locations` | A randomly selected location mapped from the allowed locations assigned to the chosen part manufacturer. |
| Full Product | `full_product` | A boolean flag hardcoded to `False`, signifying this is an individual sub-assembly unit. |
| Component Type | `component_type` | A string identifier set entirely to `"Part"` to classify its specific position in the supply chain lifecycle. |
| Variant | `variant` | A boolean flag set to `False` to signal that this represents a foundational part iteration. |
| Product | `product` | The underlying unique identifier (`id`) linking this part directly back to its source parent product. |
| Variant Base Product | `variant_base_product` | Explicitly set to `None`, indicating this part is mapped directly to a standard model. |
| Vital | `vital` | A boolean calculation testing if the targeted `part_type` sits within the explicit "Vital Parts" registry array for that designation. |
| Category | `category` | The broad assembly grouping identifier assigned to the part. |
| Part Type | `part_type` | The specific model nomenclature string indicating what kind of part was created. |
| Dimensions | `dimensions` | A list of three randomly generated integers between 10 and 100 representing physical scale. |
| Cost | `cost` | A randomized financial value up to 4 digits long, formatted cleanly to 2 decimal places. |
| Failure Rate | `failure_rate` | A randomized factory defect metric formatted out to 4 decimal places. |
| Breakability | `breakability` | A randomized physical structural tolerance metric formatted to 2 decimal places. |
| Year Range | `year_range` | A list containing 1 to 3 random integers between 1990 and 2024 representing valid production years. |

---

## Base Product Part Edges

Establishes structural supply chain dependencies (`Requires` relationships) linking production sprues to their matching individual parts.

| **Characteristic** | **Variable** | **Description** |
| :---: | :---: | :---: |
| Start Node | `start_node` | The human-readable string name of the source base product sprue. |
| End Node | `end_node` | The human-readable string name of the dependent target base product part. |
| Base Model | `base_model` | A boolean flag set to `True` indicating a foundational relationship assignment. |
| Lead Time | `lead_time` | A randomly selected logistics delay metric ranging between 1 and 1000 intervals. |

---

## Resolve Base Product Sprues

Filters out unused sprue components and their corresponding incoming product edges, ensuring that only sprues connected to actual parts are kept in the final dataset.

| **Characteristic** | **Variable** | **Description** |
| :---: | :---: | :---: |
| Resolved Base Sprues | `resolved_base_sprues` | A list containing only the subset of sprues that are actively required by parts. |
| Resolved Base Sprue Edges | `resolved_base_sprue_edges` | A list of incoming dependency edges (`Requires`) pointing to the retained sprues. |

<br>

During the filtering process, each sprue and its downstream relationships are evaluated:

| **Characteristic** | **Variable** | **Description** |
| :---: | :---: | :---: |
| Has Edge | `has_edge` | A boolean check confirming whether the sprue acts as a `start_node` for any edge in the part edge collection. |
| Edge Match Iteration | `e` | A temporary iterator used to extract and extend matching parent-product edges (`end_node == base_product_sprue`) into the resolved edge collection. |