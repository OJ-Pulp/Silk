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
| :---: | :---: | :---: | :--- |
| Designations | `self.designations` | Add Description Here. |
| Manufacturers | `self.manufacturers` | Add Description Here. |

> **Info:** Inputs Accepted