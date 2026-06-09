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

## ChainWeaver.py Process

> **Info:** Program Start

## Inputs
 
### Initial Characteristics

| **Name** | **Variable** | **Data Type** | **Default** | **Description** |
| :---: | :---: | :---: | :---: | :--- |
| Number of Products | `num_products` | `int` | 40 | The total target number of unique top-level base products to generate in the dataset. |
| Variant Distribution | `variant_distribution` | `float` | 0.25 | The percentage factor used to determine the number of variants based on the total number of desired products. |
| Number of Variants | `num_variants` | `int` | 10 | The calculated number of variants based off of the desired distribution (40 * 0.25). |

> In the future, it is hoped that the Number of Products will instead reflect the total number of base products and variants. For now, at default, there would be a total of 50 products--40 base products and 10 variants.

### From Inputdata.json

Here exists a `resolve_json` functionality pulled from `Weaver.input_utils`.  A failure of this step causes the program to exit. <br>
Recieves `designations` and `manufacturers` dictionaries.

<br>

> **Info:** Inputs Accepted

---

## Base Products

Generates a synthetic dataset of base product components and their data.

Values such as `designation_keys`, `designation_counter`, `manufacturers_keys`, `num_base_products` are used to set up values for the `Component` data.

For each base product, data is created, assigned, and stored as a `Component` node.

> **Info:** Generating Base Products

---

## Base Product Sprues

Generates a synthetic dataset of base product sprue components based on their respective manufacturers.

Values such as `manufacturer_keys` are used to set up values for the `Comopnent` data.

For each base product sprue, data is created, assigned, and stored as a `Component` node.  For each `base_product.id`, one sprue is made for each `manufacturer`.  Then the rest of the data is added.

> In the future, it is hoped that sprues will be direct collections of corresponding parts (e.g. an engine sprue would have pistons as parts).  For now, sprues are created based off of the idea that all the parts coming from one manufacturer would be bundled into one sprue grouping.

---

## Base Product Sprue Edges

Establishes structural supply chain dependencies (`Requires` relationships) linking base products to their respective sprues.

`start_node` -> Product <br>
`end_node`-> Sprue

```
                                                      +------------------+
                                                      |     Product      |
                                                      +---------+--------+
                                                                |
                                        +-----------------------+-----------------------+
                                        |                       |                       |
                                        |                       |                       |
                                        v                       v                       v
                                        v                       v                       v
                               +------------------+    +------------------+    +------------------+
                               |      Sprue       |    |      Sprue       |    |      Sprue       |
                               |  Manufacturer 1  |    |  Manufacturer 2  |    |  Manufacturer 3  |
                               +------------------+    +------------------+    +------------------+
```

---

## Vital Base Product Sprues

Defines which sprues are vital.  Being vital means that if a product is a variant of a base product, it must have these items in common.  

> In the future, it is hoped that there will be a better definition of what parts should be vital or if there should be variants at all.  For now, this is the balance to answer the "If you replace every part on the ship is it still the same ship?" question.

Add here about logic.

---

## Base Product Parts

Generates a synthetic dataset of base product part components.

For each part in the parts list for that designation, a manufacturer is chosen then all the rest of the data is filled in. 

---

## Base Product Part Edges

Sorts base product parts structurally into sprues based on their manufacturer allocations.

> In the future, it is hoped that parts will be organized into sprues that server as coherent collections of parts.  For now, parts are given to the sprue that shares the same manufacturer as them.