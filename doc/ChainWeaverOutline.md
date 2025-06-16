OVERVIEW - This script generates a fake supply chain for model aircrafts and outputs it to a json file.

IMPORT - json, uuid, faker, WeaverDir

Define data types and categories from inputdata.json
[x] check correspondance
RESOLUTION - Made definition for Company and utilized that for the dataset
[ ] consolidate inputdata.json

MAIN FUNCTION - weave
    Main Function to generate a fake supply chain for model aircrafts.
        :param num_products: The total number of unique model aircraft products to include in the supply chain.
                            Defaults to 40.
        :param variant_distribution: A float (0.0 to 1.0) controlling the proportion of products that will have variants.
                            Defaults to 0.25, meaning roughly 25% of products will be variations.
        :return: A dictionary representing the supply chain.

    Set the faker_gen tool to later generate random or fake data.
    Set num_variants according to the desired variant_distribution.
    Set num_base_products through the seperation from variants in the overall num_products.

    Set base_products list.
    Set each designation type shortcut to a num of 1.
        [x] decide to add before or after
        RESOLUTION - add before

    for all base_products

        Pick a designation randomly from inputdata.json.
            [x] create designation section
                [x] pick a set of designations
                    Mission Modifiers
                        Bomber
                        Fighter
                        Cargo
                        Attack
                        Patrol
                        Reconnaissance
                        Trainer
                        Tanker (K)
                        Observation
                        [ ] EXTEN. Add Electronic Warfare? 
                            (Extra before modifier)
                        MEDEVAC (H)
                        Cold Weather (L)
                        Multimission
                        Utility
                        Weather
                        Anti-Submarine Warfare (S)
                    [ ] EXTEN. Vehicle Types?
                    Some Mission Modifiers would not work with certian types.
                        Plane (No modifier) - 75% of the time
                        Helicopter
                        Unmanned Aerial Vehicle (Q)
                        Vertical Take-Off/Short Take-Off
                        Glider
                        Lighter-than-Air (Z)
                        Spaceplane
                [x] pick part_types per designation
                [x] pick a num_parts per designation
                Ensure NO MUTUALLY EXCLUSIVE PARTS.
        Assign base_product_designation as the designation type shorcut "-" shortcut num.
            Ex. B-17 or F-16
        Reset that designation's type shortcut num to the current val + 1.

        Generate a random capitalized noun as base_product_popular_name.
            [ ] EXTEN. include adjective noun option?
        Assign base_product_name as the base_product_designation " " base_product_popular_name.
        Assign base_product_name to base_product.

        Pick a company randomly from inputdata.json.
            [x] review and edit company section
            [ ] EXTEN. normal distribution
        Assign base_product_company to base_product.

        Generate a random uuid as base_product_base_uuid.
        Assign base_product_id as the first three letters of the company name (lowercase) + uuid.
        Assign base_product_id to base_product.

        Pick a location randomly from the chosen company's options in inputdata.json.
            [x] review and edit location section
        Assign base_product_company_location to base_product.

        Assign base_product as a dictionary of all currently generated data with standard fields.
        [ ] LATER way to add parts
        Append base_product to the overall list of base_products.

    Set variants list.

    for all variants

        Pick a random base_product from the base_products list.
        Assign variant_base_product as the random base_product for this variant.

        Assign variant_designation as the variant_base_product["Designation"] "" iteration letter.
            if the last value in the variant_base_product["Designation"] is a number
            then Append "A"
            else if the last value is a letter
            then Append the next capital letter in the sequence

        Assign variant_popular_name as the variant_base_product["Popular Name"].
        Assign variant_name as the variant_base_product["Popular Name"] " " variant_designation.
        Assign variant_name to variant_product.
        OR
        Assign variant_name as the variant_base_product["Popular Name"] " " variant_designation.
        Assign variant_name to variant_product.

        Assign variant_company as variant_base_product_company["Company"].
        Pick a location randomly from the variant_company's options in inputdata.json.
        Assign variant_company_location to variant_product.
        OR
        Assign variant_base_product_company["Company"] to variant_product.
        Pick a location randomly from the variant_base_product_company["Company"]'s options in inputdata.json.
        Assign variant_company_location to variant_product.

        Generate a random variant_base_uuid.
        Assign the variant_id as the first three characters of the variant_base_product["ID"] "" variant_base_uuid.
        Assign variant_id to variant_product.
        OR
        Assign variant_id as the first three letters of the variant_company name (lowercase) + uuid.
        Assign variant_id to variant_product.

        Assign variant_product as a dictionary of all currently generated data with standard fields.
        [ ] LATER way to add parts
        Append variant_product to the overall list of variant_products.
        [ ] EXTEN. multi-layer variants
        [x] CHECK how to call metadata

        Combine base_products and variant_products lists into products.

        for all products

            Set parts list.

            Pick a random product from the products list.

            Assign product_designation as product["Metadata"]["Designation"].
            Assign product_num_parts as DESIGNATIONS[product_designation]["Number of Parts"].

            for all part

                Generate a random uuid as part_id.

                Pick a random manufacturer as part_manufacturer.
                Pick a random manufacturer location as part_manufacturer_location.

                Assign part_base_name as the first part in the parts list for that designation.
                Assign part_name as part_base_name " " random letter "" random number.

                Assign product as a dictionary of all currently generated data with standard fields.









        




**** Series Letter for Variants

    



