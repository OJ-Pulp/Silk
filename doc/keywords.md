# Keywords

The purpose of this document is to list keywords used throughout the project and their purposes.

## Keywords Descriptions

- **Products:** A complete and finished collection of parts;  will have no outgoing `:REQUIRE` edges; a **kit**
    - **Base Products:** The zeroth variation of a **product** or **kit**; no previous versions
    - **Variants:** The nth variations of a **product** or **kit**; n previous versions; the first previous version was a **base product**
 - **Designation:** The type of product; Ex. Bomber, Fighter, etc.
 - **Company:** A business that is the final seller of the **product** or **kit**; the brand
 - **Company Location:** The location where the final seller assembles all relevant **parts** 

- **Parts:** Components of another higher-level part, or parts of a finished product. Will have incoming and outgoing `:REQUIRE` edges.
- **Suppliers:**
- **Manufacturers:**
- **Companies:**
- **Customers:** The end user that receives the product. Will not have edges related to parts, only edges related to finished products.
