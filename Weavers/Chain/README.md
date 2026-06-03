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